#!/usr/bin/env python3
"""Análisis temporal del firmware (Capítulo 4, tiempo real).

Uso (desde anteproyecto/rtos):  python3 -I analisis_temporal.py

Genera en resultados/:
  resumen_rt.txt      presupuesto de cómputo, análisis de tiempo de respuesta, dimensionamiento DMA
  ocupacion_*.csv     simulación de ocupación del anillo DMA ante una detención del núcleo DSP
  carrera_previo.csv  simulación del pool de buffers del prototipo (detección de sobrescritura)

Supuestos (a medir en el equipo, ensayo EN-06 / PU-RT-02):
  - 10 ciclos por multiplicación-acumulación en el banco de filtros (cota conservadora)
  - CPU a 240 MHz; tick de FreeRTOS a 1 kHz
"""
import math
import os

OUT = 'resultados'
os.makedirs(OUT, exist_ok=True)
rep = open(os.path.join(OUT, 'resumen_rt.txt'), 'w')


def out(s=''):
    rep.write(s + '\n')


FS = 48000
BLK = 1024                     # muestras por bloque de entrada
T_BLK = BLK / FS * 1000        # ms
F_CPU = 240e6
MULT_S = 3.32e6                # multiplicaciones/s (Capítulo 3, N = 4)
CYC_MAC = 10

# ── 1) Presupuesto de cómputo de la tarea DSP por bloque ──
mult_blk = MULT_S * T_BLK / 1000
band_samples = sum(BLK / 2 ** k for k in range(7))       # muestras procesadas por las 7 bandas
cyc_filters = mult_blk * CYC_MAC
cyc_convert = BLK * 6                                     # desplazamiento, conversión a float, escala
cyc_accum = band_samples * 4                              # cuadrado y suma
cyc_overhead = 20000                                      # llamadas, colas, contadores, lectura I2S
C_nom = (cyc_filters + cyc_convert + cyc_accum + cyc_overhead) / F_CPU * 1000
C_pes = 2 * C_nom                                         # factor 2: caché, contención de bus
out('== 1) Presupuesto de la tarea DSP ==')
out(f'Período de bloque T = {T_BLK:.3f} ms ({BLK} muestras a {FS} Hz)')
out(f'Multiplicaciones por bloque: {mult_blk:,.0f}; muestras de banda por bloque: {band_samples:.0f}')
out(f'Ciclos: filtros {cyc_filters:,.0f} + conversión {cyc_convert:,.0f} + acumulación {cyc_accum:,.0f} + '
    f'sobrecarga {cyc_overhead:,.0f}')
out(f'C nominal = {C_nom:.2f} ms  (U = {C_nom / T_BLK * 100:.1f} %)')
out(f'C pesimista (x2) = {C_pes:.2f} ms  (U = {C_pes / T_BLK * 100:.1f} %)')

# ── 2) Análisis de tiempo de respuesta en el núcleo 1 ──
# Interferencias de mayor prioridad que la tarea DSP en el núcleo 1:
#   tick de FreeRTOS (1 kHz), ISR del DMA del I2S (una por descriptor), tarea IPC (esporádica)
interf = [  # (nombre, período ms, costo ms, jitter ms) — valores supuestos, a medir
    ('Tick FreeRTOS', 1.0, 0.003, 0.0),
    ('ISR GDMA del I2S', 512 / FS * 1000, 0.005, 0.0),
    ('Tarea IPC1 (prio 24, esporádica)', 10.0, 0.020, 0.0),
]
B_SMP = 0.050   # bloqueo por secciones críticas del kernel compartidas entre núcleos (supuesto, a medir)


def rta(C, hp, B=0.0, J=0.0):
    R = C + B
    for _ in range(200):
        Rn = C + B + sum(math.ceil((R + j) / T) * c for _, T, c, j in hp)
        if abs(Rn - R) < 1e-9:
            return Rn + J
        R = Rn
    return R + J


out('\n== 2) Análisis de tiempo de respuesta (núcleo 1) ==')
out('Interferencias consideradas: ' + '; '.join(f'{n} (T = {T:.2f} ms, C = {c * 1000:.0f} µs)' for n, T, c, _ in interf))
out(f'Bloqueo SMP supuesto B = {B_SMP * 1000:.0f} µs; jitter de activación J_DSP = 0,005 ms (latencia de la ISR)')
U_int = sum(c / T for _, T, c, _ in interf)
for lbl, C in (('nominal', C_nom), ('pesimista', C_pes)):
    R = rta(C, interf, B_SMP, 0.005)
    out(f'R_DSP ({lbl}) = {R:.3f} ms  ≤  D = {T_BLK:.3f} ms  → holgura {T_BLK - R:.2f} ms')
out(f'Utilización de las interferencias: {U_int * 100:.2f} %')
U_tot_nom = C_nom / T_BLK + U_int
U_tot_pes = C_pes / T_BLK + U_int
out(f'Utilización total núcleo 1: nominal {U_tot_nom * 100:.1f} %, pesimista {U_tot_pes * 100:.1f} %')

# ── 3) Dimensionamiento del anillo DMA ──
out('\n== 3) Anillo DMA: la cola del driver tiene desc_num − 1 entradas → Q = (N−1)·512; S_max = Q/fs − C ==')
out('desc × frames | Q [muestras] | capacidad [ms] | memoria [kB] | S_max nominal [ms] | S_max pesimista [ms]')
for nd in (4, 8, 12, 16):
    Q = (nd - 1) * 512
    cap = Q / FS * 1000
    out(f'{nd:4d} × 512    | {Q:6d}       | {cap:7.1f}        | {nd * 512 * 4 / 1024:5.1f}        | '
        f'{cap - C_nom:7.1f}            | {cap - C_pes:7.1f}')

# ── 4) Simulación de ocupación del anillo ante una detención ──


def simular(n_desc, stall_t0=100.0, stall_len=100.0, C=C_pes, t_end=400.0, dt=0.05):
    Q = (n_desc - 1) * 512   # capacidad útil de la cola de mensajes del driver
    occ = 0.0           # muestras en el anillo (completadas por el DMA)
    partial = 0.0       # muestras del descriptor en curso
    busy_until = -1.0
    lost = 0
    rows = []
    t = 0.0
    while t <= t_end:
        partial += FS * dt / 1000
        if partial >= 512:                # el DMA completa un descriptor
            partial -= 512
            if occ + 512 > Q:
                lost += 512               # la ISR descarta el descriptor más antiguo y llama a on_recv_q_ovf
            else:
                occ += 512
        stalled = stall_t0 <= t < stall_t0 + stall_len
        if not stalled and t >= busy_until and occ >= BLK:
            occ -= BLK
            busy_until = t + C
        rows.append((t, occ / Q * 100, lost))
        t += dt
    return rows, lost


out('\n== 4) Simulación: detención de 100 ms del núcleo 1 en t = 100 ms (C pesimista) ==')
U_p = C_pes / T_BLK
out(f'Tiempo de recuperación tras una detención S: t_r = S·U/(1−U); con U = {U_p:.3f}: S = 100 ms → {100 * U_p / (1 - U_p):.0f} ms')
for nd in (8, 16):
    for S in range(40, 260, 2):
        _, lost = simular(nd, stall_len=S)
        if lost:
            out(f'{nd} descriptores: primera pérdida con detención de {S} ms')
            break
for nd in (8, 16):
    rows, lost = simular(nd)
    with open(os.path.join(OUT, f'ocupacion_{nd}.csv'), 'w') as f:
        for t, o, l in rows[::4]:
            f.write(f'{t:.2f},{o:.2f},{l}\n')
    out(f'{nd} descriptores: ocupación máxima {max(r[1] for r in rows):.0f} %, muestras perdidas {lost}')

# ── 5) Carrera del pool de buffers del prototipo ──
# Productor: escribe un bloque cada T en pool[i % 4] y lo encola (cola de 4).
# Consumidor: toma un bloque y lo procesa en C_c; si C_c crece (p. ej. UART bloqueante), se atrasa.
out('\n== 5) Pool de 4 buffers del prototipo: sobrescritura del bloque en proceso ==')
T_p = 1024 / 51200 * 1000


def pool_sim(C_c, n=400):
    """Devuelve (procesados, procesados con datos alterados, descartados).
    Un bloque procesado está alterado si el productor reescribió su buffer (k' ≡ k mod 4)
    antes de que el consumidor terminara de procesarlo."""
    queue = []          # [(k, t_llegada)]
    t_free = 0.0
    done = []           # (k, t_fin)
    drops = 0
    for k in range(n):
        t = k * T_p
        while queue and t_free <= t:
            kk, ta = queue.pop(0)
            start = max(t_free, ta)
            t_free = start + C_c
            done.append((kk, t_free))
        if len(queue) >= 4:
            drops += 1
        else:
            queue.append((k, t))
    # el productor escribe pool[k % 4] en t = k·T_p (aunque luego descarte el bloque)
    altered = 0
    for kk, tf in done:
        nxt = kk + 4                                  # próxima escritura sobre el mismo buffer
        if nxt * T_p < tf:
            altered += 1
    return len(done), altered, drops


out(f'Período del prototipo: {T_p:.1f} ms')
with open(os.path.join(OUT, 'carrera_previo.csv'), 'w') as f:
    for C_c in (5, 15, 19, 21, 25, 30, 40, 60, 80):
        pr, alt, dr = pool_sim(C_c)
        f.write(f'{C_c},{pr},{alt},{dr}\n')
        out(f'C_consumidor = {C_c:3d} ms: procesados {pr:3d}, alterados {alt:3d} ({alt / max(pr, 1) * 100:3.0f} %), '
            f'descartados {dr:3d} (de 400)')

# ── 5b) RTA del núcleo 0 (valores supuestos; demuestra el método, se reemplazan por mediciones) ──
out('\n== 5b) Núcleo 0: análisis de tiempo de respuesta con supuestos explícitos ==')
core0 = [  # (nombre, prioridad, T ms, C ms, D ms)
    ('Tarea Wi-Fi (ráfaga)', 23, 10.0, 1.5, None),
    ('esp_timer', 22, 10.0, 0.05, None),
    ('lwIP tcpip', 18, 10.0, 1.0, None),
    ('T_APP', 10, 50.0, 1.0, 50.0),
    ('T_UI', 8, 234.7, 40.0, 234.7),
    ('T_STOR', 6, 1000.0, 30.0, 1000.0),
    ('T_NET', 5, 234.7, 5.0, 234.7),
    ('T_XFER', 4, 1000.0, 20.0, 1000.0),
    ('T_MON', 2, 1000.0, 1.0, 1000.0),
]
U0 = sum(c / T for _, _, T, c, _ in core0)
out(f'Utilización supuesta del núcleo 0: {U0 * 100:.1f} %')
for i, (n, pr, T, C, D) in enumerate(core0):
    if D is None:
        continue
    hp = [(nn, TT, cc, 0.0) for nn, pp, TT, cc, _ in core0 if pp > pr]
    R = rta(C, hp, B_SMP)
    out(f'{n:7s} prio {pr:2d}: C = {C:5.1f} ms, R = {R:6.1f} ms, D = {D:6.1f} ms → {"cumple" if R <= D else "NO cumple"}')

# ── 6) Latencias de extremo a extremo ──
out('\n== 6) Latencias ==')
N_UPD = 11
upd = N_UPD * T_BLK
out(f'Intervalo de actualización: {N_UPD} bloques = {upd:.1f} ms (RD-06: ≤ 250 ms)')
lat_cmd = T_BLK + C_pes
out(f'Latencia de un comando hasta aplicarse en la tarea DSP: ≤ T + C = {lat_cmd:.1f} ms (se aplica en el borde de bloque)')
render = 40.0
out(f'Latencia muestra → pantalla: ≤ {upd:.0f} (integración) + {C_pes:.1f} (DSP) + {render:.0f} (dibujo, a medir) = '
    f'{upd + C_pes + render:.0f} ms')
rep.close()
print(open(os.path.join(OUT, 'resumen_rt.txt')).read())
