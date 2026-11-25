#!/usr/bin/env python3
"""Capítulo 6 — Cálculos de comunicaciones (Python puro, sin dependencias).

Uso (desde anteproyecto/comunicaciones):  python3 -I analisis_comunicaciones.py
Salidas: resultados/resumen_com.txt, resultados/sesgo_db.csv, resultados/margen_enlace.csv

Todos los valores marcados como SUPUESTO se reemplazan por mediciones (pruebas PU-COM).
"""
import json
import math
import os
import random
import struct

OUT = 'resultados'
os.makedirs(OUT, exist_ok=True)
L = []


def p(s=''):
    L.append(s)


BANDAS = [125, 250, 500, 1000, 2000, 4000, 8000]

# ───────────── 1) Promedio aritmético de niveles frente a L_eq (hallazgo H6.3) ─────────────
p('== 1) Promedio aritmético de niveles en dB (servidor del prototipo) frente a L_eq energético ==')


def leq(levels):
    return 10 * math.log10(sum(10 ** (x / 10) for x in levels) / len(levels))


rng = random.Random(8253)
N = 20000
rows = []
for s10 in range(0, 61, 5):
    s = s10 / 10
    lv = [30 + rng.gauss(0, s) for _ in range(N)]
    mean = sum(lv) / N
    rows.append((s, leq(lv) - mean, 0.1151 * s * s))
for s, sim, teo in rows:
    p(f'Fluctuación gaussiana σ = {s:3.1f} dB → L_eq − promedio = {sim:5.2f} dB (aprox. teórica 0,115·σ² = {teo:5.2f})')
with open(f'{OUT}/sesgo_db.csv', 'w') as f:
    f.write('sigma,sesgo_sim,sesgo_teo\n')
    for s, sim, teo in rows:
        f.write(f'{s:.1f},{sim:.4f},{teo:.4f}\n')

# ruido intermitente: fondo 20 dB, evento de +15 dB una fracción del tiempo
p('Ruido intermitente (fondo 20 dB SPL; evento de 35 dB SPL una fracción del tiempo):')
inter = []
for frac in (0.02, 0.05, 0.10, 0.20):
    n_ev = int(1000 * frac)
    lv = [35.0] * n_ev + [20.0] * (1000 - n_ev)
    m = sum(lv) / len(lv)
    inter.append((frac, leq(lv), m))
    p(f'  {frac * 100:4.0f} % del tiempo: L_eq = {leq(lv):5.1f} dB; promedio de niveles = {m:5.1f} dB; '
      f'subestimación = {leq(lv) - m:4.1f} dB')
f10, l10, m10 = inter[2]
p(f'Frente al límite de trabajo de 25 dB SPL (banda de 250 Hz), el evento del {f10 * 100:.0f} % da L_eq = {l10:.1f} dB '
  f'(NO APTA) y un promedio de niveles de {m10:.1f} dB (APTA): el error va en la dirección insegura.')
p()

# ───────────── 2) Mensajes: tamaño y ocupación del canal ─────────────
p('== 2) Tamaño de los mensajes y ocupación del canal ==')
snap = {
    'v': 1, 'tipo': 'inst', 'seq': 123456, 't_ms': 3600123, 'estado': 'MIDIENDO',
    'sesion': 'A1B2-000123', 'prog': 0.45,
    'lp': [27.3, 19.8, 16.4, 20.1, 25.9, 29.4, 34.2],   # L_eq parcial (ventana de 234,7 ms)
    'la': [27.9, 20.2, 16.9, 20.4, 26.2, 29.9, 34.8],   # L_eq acumulado de la sesión
    'marca': [0, 0, 1, 0, 0, 0, 0],                     # 1 = cerca del piso de ruido
    'ver': 'PARCIAL_APTA', 'perd': 0, 'bat': 87,
}
js = json.dumps(snap, separators=(',', ':'), ensure_ascii=True)
n_json = len(js.encode())
# binario empaquetado: v,tipo (2 B), seq u32, t_ms u32, estado u8, prog u8, 14 × int16 (décimas de dB),
# marcas u8 (bits), veredicto u8, pérdidas u16, batería u8, id de sesión 8 B
n_bin = len(struct.pack('<BBIIBB14hBBHB8s', 1, 1, 123456, 3600123, 3, 45, *([0] * 14), 4, 2, 0, 87, b'A1B2-123'))
p(f'Ejemplo de instantánea JSON compacta: {n_json} B')
p(f'Misma información en binario empaquetado: {n_bin} B ({n_json / n_bin:.1f} veces menos)')
WS_H = 2 if n_json < 126 else 4          # servidor → cliente: sin máscara
TCPIP = 20 + 20                           # IPv4 + TCP sin opciones (12 B más con marca de tiempo)
MAC = 24 + 8 + 16 + 4                     # cabecera MAC QoS aprox. + LLC/SNAP + CCMP + FCS
tot = n_json + WS_H + TCPIP + 12 + MAC
p(f'Trama en el aire (JSON + WS {WS_H} B + IP/TCP {TCPIP + 12} B + 802.11/CCMP {MAC} B): {tot} B')
PER = 0.2347                              # período de publicación: 11 bloques de 21,33 ms
fps = 1 / PER
for nc in (1, 4):
    p(f'{nc} cliente(s): {nc * fps:.2f} tramas/s; carga útil {nc * n_json * fps * 8 / 1000:.1f} kbit/s; '
      f'en el aire {nc * tot * fps * 8 / 1000:.1f} kbit/s')


def airtime_us(nbytes, rate_mbps, ofdm=True):
    if ofdm:   # preámbulo + SIGNAL 20 µs, símbolos de 4 µs, 22 bits de servicio y cola
        nsym = math.ceil((16 + 6 + 8 * nbytes) / (rate_mbps * 4))
        return 34 + 68 + 20 + 4 * nsym + 16 + 44   # DIFS + backoff medio + trama + SIFS + ACK a 6 Mbit/s
    return 50 + 310 + 192 + 8 * nbytes / rate_mbps + 10 + 304   # DIFS + backoff + DSSS largo + SIFS + ACK


p('Ocupación del canal con 4 clientes (tramas de datos + ACK; balizas de ≈ 300 B a 1 Mbit/s cada 102,4 ms):')
beacon = (192 + 300 * 8 / 1) / 102400
occ = {}
for rate, ofdm in ((1, False), (6, True), (24, True), (65, True)):
    t = airtime_us(tot, rate, ofdm)
    o = 4 * fps * t / 1e6 + beacon
    occ[rate] = o
    p(f'  {rate:2d} Mbit/s: {t:7.0f} µs por trama → ocupación {o * 100:5.2f} % (balizas {beacon * 100:.2f} %)')
# ciclo de transmisión de la radio del equipo (solo sus propias tramas y balizas)
tot_bin = n_bin + 2 + TCPIP + 12 + MAC
occ_bin = 4 * fps * airtime_us(tot_bin, 6) / 1e6 + beacon
p(f'Binario empaquetado a 6 Mbit/s con 4 clientes: trama de {tot_bin} B → ocupación {occ_bin * 100:.2f} % '
  f'(JSON: {occ[6] * 100:.2f} %)')
p('Los ACK de TCP del celular agregan una trama corta por cada una o dos tramas de datos (≈ +40 % de tiempo de aire '
  'sobre lo anterior, aún < 5 % del canal).')
tx_duty = 4 * fps * airtime_us(tot, 6) / 1e6 + beacon
I_TX, I_RX = 300.0, 100.0                 # SUPUESTO: mA de la radio en TX (≈ 13–20 dBm) y en RX
p(f'Ciclo de trabajo del transmisor del equipo (6 Mbit/s, 4 clientes): {tx_duty * 100:.2f} % → aporte medio de la '
  f'transmisión ≈ {tx_duty * (I_TX - I_RX):.1f} mA sobre la recepción continua')
p('Conclusión: bajar la potencia de transmisión casi no cambia la autonomía; sirve para reducir picos de corriente, '
  'acoplamiento al micrófono e interferencia con otros equipos.')
p()

# ───────────── 3) Margen del enlace con el equipo dentro de la cabina ─────────────
p('== 3) Presupuesto del enlace descendente (equipo → celular), 2,437 GHz (canal 6) ==')
F = 2.437e9
C0 = 299792458.0


def fspl(d):
    return 20 * math.log10(4 * math.pi * d * F / C0)


G_ESP = 0.0      # SUPUESTO: ganancia efectiva de la antena del módulo dentro del gabinete (dBi)
G_TEL = -3.0     # SUPUESTO: celular en la mano (dBi efectivos)
L_CUERPO = 3.0   # SUPUESTO: pérdidas por el cuerpo y la orientación
S_TEL = -85.0    # SUPUESTO conservador: sensibilidad del celular a la menor tasa usada (dBm)
M_DES = 10.0     # margen de desvanecimiento exigido (dB)
p(f'Supuestos: antena del equipo {G_ESP:+.0f} dBi, celular {G_TEL:+.0f} dBi, cuerpo {L_CUERPO:.0f} dB, '
  f'sensibilidad del celular {S_TEL:.0f} dBm, margen de desvanecimiento {M_DES:.0f} dB')
rows = []
for d in (2, 3, 5, 10):
    for ptx in (8.5, 13.0, 19.5):
        prx = ptx + G_ESP + G_TEL - L_CUERPO - fspl(d)
        a_max = prx - S_TEL - M_DES
        rows.append((d, ptx, fspl(d), prx, a_max))
for d, ptx, fl, prx, a_max in rows:
    p(f'  d = {d:2d} m, P_TX = {ptx:4.1f} dBm: pérdida en espacio libre {fl:5.1f} dB; P_RX sin cabina {prx:6.1f} dBm; '
      f'atenuación máxima admisible de la cabina {a_max:5.1f} dB')
with open(f'{OUT}/margen_enlace.csv', 'w') as f:
    f.write('atenuacion,m_3m_8,m_3m_13,m_3m_19,m_10m_13\n')
    for att in range(0, 61, 2):
        vals = []
        for d, ptx in ((3, 8.5), (3, 13.0), (3, 19.5), (10, 13.0)):
            prx = ptx + G_ESP + G_TEL - L_CUERPO - fspl(d) - att
            vals.append(prx - S_TEL)
        f.write(f'{att},' + ','.join(f'{v:.2f}' for v in vals) + '\n')
p('Enlace ascendente (celular → equipo): el celular transmite con ≈ 15 dBm y el ESP32-S3 tiene mejor sensibilidad que '
  'el supuesto del celular, de modo que el enlace limitante es el descendente.')
p()

# ───────────── 4) Latencia de extremo a extremo ─────────────
p('== 4) Latencia desde el fin de una ventana de 234,7 ms hasta que el panel la dibuja ==')
lat = [
    ('Fin del bloque → T_DSP termina (R_DSP pesimista, Cap. 4)', 0.5, 3.2, 6.3),
    ('T_DSP → T_APP (q_res) y respuesta de T_APP (R = 3,6 ms)', 0.1, 1.0, 3.6),
    ('T_APP → publicación en T_NET (respuesta de T_NET, Cap. 4: 106,1 ms)', 0.5, 5.0, 106.1),
    ('Serialización y envío por lwIP (4 clientes)', 0.3, 1.0, 3.0),
    ('Aire: acceso al canal y reintentos', 0.3, 2.0, 15.0),
    ('Cliente en ahorro de energía (intervalo de escucha; SUPUESTO ≤ 3 balizas)', 0.0, 20.0, 307.2),
    ('Navegador: decodificación y próximo cuadro (60 Hz)', 1.0, 8.0, 16.7),
]
tots = [0, 0, 0]
for name, a_, b_, c_ in lat:
    p(f'  {name:68s} {a_:6.1f} {b_:6.1f} {c_:6.1f} ms')
    tots = [tots[0] + a_, tots[1] + b_, tots[2] + c_]
p(f'  {"TOTAL (mejor / típico / peor)":68s} {tots[0]:6.1f} {tots[1]:6.1f} {tots[2]:6.1f} ms')
LAT_PEOR = tots[2]
p(f'Antigüedad máxima del dato en pantalla del panel: período + latencia = {234.7 + LAT_PEOR:.0f} ms')
p()

# ───────────── 5) Búfer de envío TCP y política de descarte ─────────────
p('== 5) Búfer de envío TCP por cliente (lwIP de ESP-IDF 5.4) ==')
SND = 5760
MSS = 1440
LOWAT = min(max(SND // 2, 2 * MSS + 1), SND - 1)
fr = n_json + WS_H
p(f'TCP_SND_BUF = {SND} B; TCP_SNDLOWAT = {LOWAT} B: select() informa "escribible" solo con más de {LOWAT} B libres')
QLEN = (4 * SND + MSS - 1) // MSS
QLOWAT = max(QLEN // 2, 5)
p(f'TCP_SND_QUEUELEN = {QLEN} pbufs; TCP_SNDQUEUELOWAT = {QLOWAT}: también se exige tener menos de {QLOWAT} pbufs '
  'en cola')
n_by_buf = (SND - LOWAT) // fr + 1
n_by_q = QLOWAT // 2          # cada trama WS = 2 send(): cabecera y carga (httpd_ws.c)
n_w = min(n_by_buf, n_by_q)
p(f'Trama WS de {fr} B en 2 envíos: deja de ser escribible tras {n_by_buf} tramas por espacio o {n_by_q} por cola de '
  f'pbufs → {n_w} tramas sin confirmar')
T_NOW = 2.0
for nombre, per in (('MIDIENDO (234,7 ms)', PER), ('REPOSO (1 s)', 1.0)):
    p(f'  {nombre}: no escribible a los {n_w * per:.1f} s; cierre tras {T_NOW:.0f} s más sin poder escribir → '
      f'{n_w * per + T_NOW:.1f} s')
p('Con envío bloqueante y send_wait_timeout = 5 s (valor por defecto), un cliente fuera de alcance detendría la tarea '
  'del servidor hasta 5 s por trama: se usa la comprobación de escritura y el descarte.')
p('Además: cierre inmediato ante WIFI_EVENT_AP_STADISCONNECTED y ping de aplicación cada 5 s con plazo de 10 s.')
p()

# ───────────── 6) Memoria de red estimada ─────────────
p('== 6) Memoria interna estimada para la red (SUPUESTOS a medir con heap_caps_get_minimum_free_size) ==')
mem = [
    ('Wi-Fi: 10 búferes estáticos de recepción × 1,6 kB', 16.0),
    ('Wi-Fi: búferes dinámicos en uso (pico supuesto 12 × 1,6 kB)', 19.2),
    ('Wi-Fi, WPA2/WPA3 y estructuras del controlador', 30.0),
    ('lwIP: pila de la tarea TCP/IP y PCB', 4.5),
    ('Datos en vuelo: 7 sockets × búfer de envío lleno (pico)', 7 * 5.76),
    ('Ventana de recepción TCP durante la OTA', 5.76),
    ('cJSON: análisis de un comando de ≤ 512 B (memoria dinámica acotada)', 2.0),
    ('SAE (WPA3): estado de los saludos en curso', 4.0),
    ('Pila de T_XFER (8 kB: verificación RSA-3072 de la imagen)', 8.0),
    ('Servidor HTTP: pila de 6 kB + estructuras (7 sockets)', 8.0),
    ('Búfer de la instantánea serializada y de los mensajes recibidos', 1.5),
    ('Bloque de recepción de OTA (4 kB) y verificación', 5.0),
]
tm = 0
for n_, v in mem:
    p(f'  {n_:62s} {v:6.1f} kB')
    tm += v
p(f'  {"TOTAL (pico)":62s} {tm:6.1f} kB')
p()

# ───────────── 7) Seguridad ─────────────
p('== 7) Seguridad: contraseña del Wi-Fi y PIN de técnico ==')
ALF = 32       # alfabeto sin caracteres ambiguos (sin 0/O, 1/l/I)
LEN = 12
bits = LEN * math.log2(ALF)
p(f'Contraseña aleatoria de {LEN} caracteres sobre {ALF} símbolos: {bits:.0f} bits')
# ataque fuera de línea a WPA2-PSK (PBKDF2 de 4096 iteraciones) con una GPU de ≈ 1e6 intentos/s
rate = 2e6
anos = 2 ** (bits - 1) / rate / 3.156e7
p(f'Ataque de diccionario fuera de línea a WPA2 con 2·10⁶ intentos/s: tiempo medio ≈ {anos:.1e} años')
PIN = 10 ** 6
v_int = 3 / 300.0          # 3 intentos cada 5 min de bloqueo (CU-07)
t_pin = PIN / 2 / v_int / 3.156e7
p(f'PIN de 6 dígitos con 3 intentos y bloqueo de 5 min: tiempo medio por fuerza bruta en línea ≈ {t_pin:.1f} años')
p('Con un PIN de 4 dígitos el mismo cálculo da ≈ {:.0f} días.'.format(10 ** 4 / 2 / v_int / 86400))
p()

# ───────────── 8) Actualización OTA ─────────────
p('== 8) Tiempo de una actualización OTA (SUPUESTOS: imagen de 1,6 MB, partición de 4 MB) ==')
IMG = 1.6e6
SECT = 4096
T_ERASE = 0.045            # s por sector de 4 kB (típico de flash NOR SPI)
PAGE = 256
T_PROG = 0.0007            # s por página de 256 B (típico)
t_flash = IMG / SECT * T_ERASE + IMG / PAGE * T_PROG
for mbps in (1.0, 2.0, 5.0):
    t_tx = IMG * 8 / (mbps * 1e6)
    p(f'  Transferencia a {mbps:.0f} Mbit/s efectivos: {t_tx:5.1f} s; borrado + escritura {t_flash:5.1f} s; '
      f'total (sin solapar) {t_tx + t_flash:5.1f} s')
E = 0.20 * 60 / 3600 * 1000
p(f'Energía de una actualización (200 mA durante 60 s): {E:.1f} mAh — la condición de batería > 50 % protege del corte, '
  'no de la falta de energía.')
p('Tamaño de la partición: la imagen debe ocupar ≤ 75 % de 4 MB (3 MB) para dejar margen a versiones futuras.')
p()

# ───────────── 9) Fecha y hora ─────────────
p('== 9) Fecha y hora sin internet ==')
for name, ppm in (('Cristal principal de 40 MHz (±10 ppm), equipo encendido', 10),
                  ('RTC externo con cristal de 32 kHz (±5 ppm, SUPUESTO)', 5)):
    p(f'  {name:58s}: {ppm * 1e-6 * 86400:5.2f} s/día; {ppm * 1e-6 * 86400 * 365 / 60:5.1f} min/año')
p('  Equipo apagado por el enclavamiento (POWER_HOLD liberado): el ESP32-S3 queda sin alimentación y pierde la hora.')
RTC_I = 0.045e-3            # mA, RTC de nanopotencia (SUPUESTO: 45 nA)
p(f'  Un RTC alimentado desde la celda suma {RTC_I * 1e3:.3f} µA al consumo apagado (12,6 µA, Cap. 5): despreciable.')

p()
# ───────────── 10) Buses internos ─────────────
p('== 10) Buses internos: capacidad frente a demanda ==')
bclk = 48000 * 64
p(f'I2S: BCLK = 48 kHz × 64 = {bclk / 1e6:.3f} MHz; datos útiles de un canal de 24 bits = {48000 * 24 / 1e6:.3f} Mbit/s '
  '(el bus es síncrono y de ocupación fija: no hay margen que administrar)')
px = 320 * 240 * 16
for f_spi in (10e6, 40e6):
    p(f'SPI2 a {f_spi / 1e6:.0f} MHz: cuadro completo de 320 × 240 × 16 bits = {px / f_spi * 1e3:5.1f} ms; '
      f'solo las 7 barras (≈ 25 % del área) = {0.25 * px / f_spi * 1e3:5.1f} ms')
ses = 2048                 # SUPUESTO: archivo de sesión ≈ 2 kB (cabecera, 7 bandas, piso, marcas, CRC)
for f_sd in (20e6, 40e6):
    p(f'SDMMC de 1 bit a {f_sd / 1e6:.0f} MHz: {f_sd / 8 / 1e6:.1f} MB/s brutos; una sesión de {ses} B ≈ '
      f'{ses * 8 / f_sd * 1e3:.2f} ms de bus (dominan la latencia de la tarjeta y la FAT, 10–100 ms)')
p(f'I2C a 400 kHz: lectura de 7 registros de hora del RTC ≈ {(1 + 1 + 1 + 7) * 9 / 400e3 * 1e3:.2f} ms')
p('USB Serial/JTAG (12 Mbit/s): carga de firmware, consola y volcado de memoria; no transporta datos de medición.')

open(f'{OUT}/resumen_com.txt', 'w').write('\n'.join(L) + '\n')
print('\n'.join(L))
