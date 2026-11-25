#!/usr/bin/env python3
"""Análisis de potencia, autonomía, carga, rizado y térmica (Capítulo 5, hardware) — v0.2.

Uso (desde anteproyecto/hw):  python3 -I analisis_potencia.py
Genera resultados/resumen_hw.txt, resultados/ocv.csv y resultados/autonomia.csv.

TODOS los consumos son supuestos (orden de magnitud de hojas de datos); se reemplazan por mediciones en
PU-HW-02 y EN-07. Los supuestos del ESP32-S3 se tomaron conservadores: en modo punto de acceso la radio no
duerme (recepción continua) y la CPU corre a 240 MHz con dos núcleos.
"""
import os

OUT = 'resultados'
os.makedirs(OUT, exist_ok=True)
rep = open(os.path.join(OUT, 'resumen_hw.txt'), 'w')


def out(s=''):
    rep.write(s + '\n')


# ── 1) Presupuesto de consumo por modo (mA en 3,3 V) ──
CARGAS = [  # nombre, modo medición, modo reposo, peor caso
    ('ESP32-S3 + Wi-Fi AP (recepción continua)', 145.0, 130.0, 170.0),
    ('Pantalla TFT: controlador', 5.0, 5.0, 5.0),
    ('Pantalla TFT: retroiluminación (PWM)', 20.0, 8.0, 40.0),
    ('microSD (promedio con escrituras)', 1.0, 0.5, 3.0),
    ('LED bicolor (promedio)', 2.0, 1.0, 5.0),
    ('Micrófono ICS-43434 (alto desempeño)', 0.49, 0.0, 0.49),
    ('Transmisión Wi-Fi a 4 paneles (Cap. 6, supuesto)', 7.0, 1.0, 7.0),
    ('RTC con cristal (I2C, en marcha)', 0.01, 0.01, 0.01),
    ('Reposo de reguladores, comparador y divisor', 0.2, 0.2, 0.2),
]
out('== 1) Presupuesto de consumo (supuestos) ==')
tot = [0.0, 0.0, 0.0]
for n, *v in CARGAS:
    out(f'{n:45s} | {v[0]:6.2f} | {v[1]:6.2f} | {v[2]:6.2f}')
    tot = [t + x for t, x in zip(tot, v)]
out(f'{"TOTAL [mA]":45s} | {tot[0]:6.1f} | {tot[1]:6.1f} | {tot[2]:6.1f}')
I_PICO = 450.0
out(f'Pico supuesto (transmisión Wi-Fi + resto): {I_PICO:.0f} mA')

# ── 2) OCV típica Li-ion ──
OCV = [(100, 4.20), (95, 4.13), (90, 4.06), (80, 3.98), (70, 3.92), (60, 3.87), (50, 3.82), (40, 3.79),
       (30, 3.77), (20, 3.74), (15, 3.71), (10, 3.68), (7, 3.60), (5, 3.50), (3, 3.40), (1, 3.25), (0, 3.00)]
with open(os.path.join(OUT, 'ocv.csv'), 'w') as f:
    for soc, v in OCV:
        f.write(f'{soc},{v}\n')


def soc_at(v):
    for (s1, v1), (s2, v2) in zip(OCV, OCV[1:]):
        if v2 <= v <= v1:
            return s2 + (v - v2) / (v1 - v2) * (s1 - s2)
    return 0.0 if v < OCV[-1][1] else 100.0


# Resistencia serie total entre la celda y VSYS (supuestos):
R_PARTES = [('Celda 18650 (resistencia interna)', 0.080), ('Protección de la celda (MOSFET dobles)', 0.050),
            ('MOSFET de protección de polaridad', 0.025), ('FET BAT→OUT del cargador', 0.050),
            ('Conmutador de encendido y contactos del portapila', 0.045)]
R_INT = sum(r for _, r in R_PARTES)
out('\n== 2) Resistencia serie batería → VSYS ==')
for n, r in R_PARTES:
    out(f'{n:50s} {r * 1000:5.0f} mΩ')
out(f'{"TOTAL":50s} {R_INT * 1000:5.0f} mΩ')

V_CORTE = 3.50     # V: VSYS con carga, filtrado, en el que el firmware cierra y apaga
VDO = 0.25         # V: caída del LDO principal al pico de corriente (valor de diseño único)
out('\n== 3) Corte por batería baja y fracción utilizable ==')
ocv_corte = V_CORTE + tot[0] / 1000 * R_INT
vsys_pico = ocv_corte - I_PICO / 1000 * R_INT
v3_pico = min(3.3, vsys_pico - VDO)
use_ldo = 100 - soc_at(ocv_corte)
out(f'Corte del firmware: VSYS con carga ≤ {V_CORTE:.2f} V (promedio de 1 s, histéresis 100 mV)')
out(f'OCV en el corte: {ocv_corte:.3f} V → carga utilizable {use_ldo:.1f} %')
out(f'En el corte, durante un pico de {I_PICO:.0f} mA: VSYS = {vsys_pico:.2f} V; 3V3_D = {v3_pico:.2f} V '
    f'(ESP32-S3: 3,0 a 3,6 V; el LDO puede entrar brevemente en caída sin riesgo)')
out(f'Riel del micrófono (LP5907, caída de pocos mV a 0,5 mA): 3,3 V mientras VSYS ≥ 3,35 V → '
    f'{"OK" if vsys_pico >= 3.35 else "NO"} en el pico')
# buck-boost
v_min_bb = 3.2 + I_PICO / 1000 * R_INT
use_bb = 100 - soc_at(v_min_bb)
k_bb = 3.3 / (0.90 * 3.80)
ratio = (use_bb / k_bb) / use_ldo
out(f'Buck-boost: carga utilizable {use_bb:.1f} %, corriente relativa {k_bb:.3f} → autonomía ×{ratio:.2f} '
    f'(+{(ratio - 1) * 100:.0f} %; el LDO da {(1 / ratio - 1) * 100:.0f} %)')

# ── 4) Autonomía y sensibilidad ──
out('\n== 4) Autonomía con LDO ==')
BATS = [('18650 2600 mAh', 2600), ('18650 3000 mAh', 3000), ('LiPo 3000 mAh', 3000)]
DEGR = [('nueva, 25 °C', 1.00, 1.0), ('fin de vida (80 %)', 0.80, 1.5), ('fin de vida y 10 °C', 0.72, 2.0)]


def usable(rmult):
    r = R_INT * rmult
    ocv = V_CORTE + tot[0] / 1000 * r
    return 100 - soc_at(ocv)


for bn, cap in BATS:
    for dn, k, rm in DEGR:
        u = usable(rm)
        c = cap * u / 100 * k
        out(f'{bn:16s} | {dn:22s} | útil {u:4.1f} % | medición {c / tot[0]:5.1f} h | reposo {c / tot[1]:5.1f} h | '
            f'peor caso {c / tot[2]:5.1f} h')
out('Sensibilidad (18650 3000 mAh, fin de vida y 10 °C, peor caso):')
c = 3000 * usable(2.0) / 100 * 0.72
for dI in (0, 20, 40, 60):
    out(f'  ESP32-S3 +{dI:2d} mA → {c / (tot[2] + dI):4.1f} h')
with open(os.path.join(OUT, 'autonomia.csv'), 'w') as f:
    for i in range(100, 281, 5):
        row = [i]
        for _, cap in BATS[:2]:
            row += [cap * usable(1.0) / 100 / i, cap * usable(2.0) / 100 * 0.72 / i]
        f.write(','.join(f'{x:.2f}' for x in row) + '\n')

# ── 5) Carga ──
out('\n== 5) Carga (BQ24074: ISET fija la corriente de carga; EN1/EN2 e ILIM limitan la de entrada) ==')
ISET = 0.80
cap = 3000
for nombre, i_in, sistema in (('Fuente ≥ 1,5 A (ILIM = 1,5 A), equipo apagado', 1.5, 0.0),
                              ('Fuente ≥ 1,5 A (ILIM = 1,5 A), equipo encendido', 1.5, tot[0] / 1000),
                              ('Fuente por defecto (USB500), equipo apagado', 0.5, 0.0),
                              ('Fuente por defecto (USB500), equipo encendido', 0.5, tot[0] / 1000)):
    ich = min(ISET, i_in - sistema)
    out(f'{nombre:50s}: I_carga = {ich * 1000:4.0f} mA → t ≈ {0.8 * cap / (ich * 1000) + 0.6:4.1f} h')

# ── 6) Térmica ──
out('\n== 6) Disipación ==')
V_OUT_USB = 4.4    # V: regulación de OUT del BQ24074 con entrada USB
for vs, cond in ((4.2, 'batería llena, sin USB'), (V_OUT_USB, 'USB conectado (OUT = 4,4 V)')):
    p = (vs - 3.3) * tot[2] / 1000
    out(f'LDO, {cond}, peor caso {tot[2]:.0f} mA: P = {p * 1000:.0f} mW; ΔT = {p * 90:.0f} °C (SOT-89/DFN ≈ 90 °C/W)')
RTH_BQ = 44.5      # °C/W (QFN-16 con almohadilla, hoja de datos)
for vbat in (3.0, 3.5, 4.0):
    p = (5.0 - vbat) * ISET + (5.0 - V_OUT_USB) * tot[0] / 1000
    out(f'Cargador a {ISET:.1f} A, V_bat = {vbat} V, equipo encendido: P = {p:.2f} W; ΔT_J = {p * RTH_BQ:.0f} °C')
A_gab = 2 * (0.16 * 0.08 + 0.16 * 0.035 + 0.08 * 0.035)
h_conv = 6.0
p_tot = (5.0 - 3.5) * ISET + 0.6 * tot[0] / 1000 + (V_OUT_USB - 3.3) * tot[0] / 1000 + 3.3 * tot[0] / 1000
out(f'Gabinete: área {A_gab * 1e4:.0f} cm², h ≈ {h_conv} W/m²K → R_th ≈ {1 / (h_conv * A_gab):.1f} K/W; '
    f'cargando y midiendo P ≈ {p_tot:.2f} W → ΔT interior medio ≈ {p_tot / (h_conv * A_gab):.0f} °C')

# ── 7) Rizado admisible en el micrófono ──
out('\n== 7) Rizado admisible en VDD del micrófono ==')
target = 13.5 - 10.0 - 120.0
v_adm = 100.0 * 10 ** ((target - (-100.0)) / 20)
out(f'Objetivo {target:.1f} dBFS → admisible ≈ {v_adm:.0f} mVpp (escalado lineal desde la PSR; supuesto)')
rip_bat = 0.30 * R_INT * 1000
out(f'Escalón de 300 mA × {R_INT:.2f} Ω = {rip_bat:.0f} mVpp en VSYS → con PSRR de 60 dB: {rip_bat:.0f} µVpp en VDD')

# ── 8) Capacitor de reserva del riel digital ──
out('\n== 8) Reserva del riel de 3,3 V ==')
dI, dt, dV = 0.35, 10e-6, 0.10
out(f'C ≥ ΔI·Δt/ΔV = {dI}·{dt * 1e6:.0f} µs/{dV} V = {dI * dt / dV * 1e6:.0f} µF → 47 µF + 10 µF + 100 nF junto al módulo')

# ── 9) Apagado ──
out('\n== 9) Corriente de batería con el equipo apagado ==')
OFF = [('Protección de la celda', 3.0), ('Cargador sin entrada (IBAT(PDWN) típ. 4,3 / máx. 6,5)', 6.5),
       ('Divisor de batería 2 × 1 MΩ', 2.1), ('Conmutador de encendido y fugas', 1.0),
       ('RTC en respaldo desde la celda (típ. 45 nA)', 0.05)]
s = sum(i for _, i in OFF)
for n, i in OFF:
    out(f'{n:55s} {i:5.2f} µA')
out(f'{"TOTAL (con la fuga máxima del cargador)":55s} {s:5.2f} µA (RD-12: ≤ 100 µA)')
quim = cap * 0.03 * 3
elec = s * 24 * 91 / 1000
out(f'3 meses: química ≈ {quim:.0f} mAh + electrónica {elec:.0f} mAh → queda ≈ {100 - (quim + elec) / cap * 100:.0f} %')

# ── 10) Masa ──
out('\n== 10) Presupuesto de masa ==')
MASA = [('Celda 18650 3000 mAh', 47), ('Portapila', 6), ('PCB con componentes', 25), ('Pantalla TFT 2,8"', 30),
        ('Gabinete PETG (paredes de 2 mm)', 105), ('Vástago, placa satélite y cable', 20),
        ('Pulsadores, tornillos, tapas', 15)]
for n, m in MASA:
    out(f'{n:40s} {m:4d} g')
out(f'{"TOTAL":40s} {sum(m for _, m in MASA):4d} g (≤ 350 g)')
rep.close()
print(open(os.path.join(OUT, 'resumen_hw.txt')).read())
