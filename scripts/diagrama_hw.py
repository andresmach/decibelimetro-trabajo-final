#!/usr/bin/env python3
"""Diagramas del Capítulo 5: árbol de alimentación y concepto mecánico (SVG sin markers).

Uso: python3 -I diagrama_hw.py <alimentacion.svg> <mecanica.svg> <bloques_hw.svg>
"""
import math
import sys

o = []
a = o.append


def head(w, h):
    o.clear()
    a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
      'font-family="Arial, Helvetica, sans-serif">')
    a(f'<rect width="{w}" height="{h}" fill="#fff"/>')


def text(x, y, s, size=16, anchor='middle', color='#222', weight='normal', italic=False):
    st = ' font-style="italic"' if italic else ''
    a(f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" fill="{color}" font-weight="{weight}"{st}>{s}</text>')


def box(x, y, w, h, lines, fill='#fff', st='#333', sw=2, size=17):
    a(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{fill}" stroke="{st}" stroke-width="{sw}"/>')
    n = len(lines)
    y0 = y + h / 2 - (n - 1) * 10.5 + 6
    for i, ln in enumerate(lines):
        text(x + w / 2, y0 + i * 21, ln, size if i == 0 else size - 3, weight='bold' if i == 0 else 'normal',
             color='#111' if i == 0 else '#444')


def arrow(pts, c='#333', sw=2.4, dash=False, label=None, lpos=None):
    d = ' stroke-dasharray="7,5"' if dash else ''
    a(f'<polyline points="{" ".join(f"{x},{y}" for x, y in pts)}" fill="none" stroke="{c}" stroke-width="{sw}"{d}/>')
    (x1, y1), (x2, y2) = pts[-2], pts[-1]
    L = math.hypot(x2 - x1, y2 - y1)
    ux, uy = (x2 - x1) / L, (y2 - y1) / L
    bx, by = x2 - ux * 13, y2 - uy * 13
    a(f'<polygon points="{x2},{y2} {bx - uy * 6.5:.1f},{by + ux * 6.5:.1f} {bx + uy * 6.5:.1f},{by - ux * 6.5:.1f}" fill="{c}"/>')
    if label:
        text(lpos[0], lpos[1], label, 14, color=c, weight='bold')


# ───────────── árbol de alimentación ─────────────
head(1400, 860)
text(700, 36, 'Árbol de alimentación y señales de gestión de energía (v0.2)', 23, weight='bold')
box(30, 110, 180, 120, ['USB-C', 'CC1/CC2: 5,1 kΩ', 'TVS en VBUS, D±, CC'], '#f2f2f2', '#666')
box(280, 100, 240, 150, ['Cargador BQ24074', 'camino de potencia', 'ISET = 0,8 A · ILIM = 1,5 A', 'OUT = 4,4 V con USB',
                         'TS ← NTC 10 kΩ'], '#f3e8f7', '#6a1b9a')
arrow([(210, 170), (278, 170)], '#6a1b9a', label='VBUS', lpos=(244, 160))
box(280, 360, 240, 120, ['Celda 18650 3000 mAh', 'protegida, en portapila', 'NTC acoplada a la celda'], '#f3e8f7', '#6a1b9a')
box(290, 290, 220, 46, ['P-MOSFET: polaridad'], '#fff', '#d62728', size=15)
arrow([(390, 288), (390, 252)], '#6a1b9a')
arrow([(410, 252), (410, 288)], '#6a1b9a')
a('<line x1="400" y1="336" x2="400" y2="358" stroke="#6a1b9a" stroke-width="2.4"/>')
text(470, 275, 'BAT', 14, color='#6a1b9a', weight='bold')
# comparador CC
box(30, 300, 210, 110, ['Comparador de CC', 'nanopotencia, desde OUT', 'CC > 0,66 V → fuente ≥ 1,5 A'], '#fff', '#555', size=15)
a('<polyline points="120,230 120,298" fill="none" stroke="#555" stroke-width="2" stroke-dasharray="6,4"/>')
arrow([(240, 330), (262, 330), (262, 210), (278, 210)], '#555', dash=True)
text(30, 440, 'EN1/EN2 por resistencias: USB500 por defecto;', 13, 'start', '#555')
text(30, 458, 'el comparador pasa a ILIM sin el ESP32', 13, 'start', '#555')
# conmutador de encendido
box(600, 120, 210, 110, ['Conmutador de encendido', 'P-MOSFET con enclavamiento', 'pulsador + POWER_HOLD'], '#fff', '#c77700', size=15)
arrow([(520, 170), (598, 170)], '#6a1b9a', label='OUT', lpos=(560, 160))
a('<line x1="810" y1="170" x2="860" y2="170" stroke="#6a1b9a" stroke-width="2.4"/>')
text(840, 160, 'VSYS', 14, color='#6a1b9a', weight='bold')
a('<circle cx="860" cy="170" r="5" fill="#6a1b9a"/>')
box(900, 100, 220, 100, ['LDO 3,3 V digital', '≥ 600 mA · SOT-89/DFN', '47 µF + 10 µF + 100 nF'], '#fff7e6', '#c77700', size=15)
arrow([(860, 150), (898, 150)], '#6a1b9a')
box(1170, 70, 200, 70, ['ESP32-S3-WROOM-1', 'N16R8 (3,3 V)'], '#dceaf7', '#1e5e9f', size=16)
box(1170, 160, 200, 60, ['TFT · microSD · LED'], '#f2f2f2', '#666', size=15)
arrow([(1120, 140), (1145, 140), (1145, 105), (1168, 105)], '#c77700', label='3V3_D', lpos=(1145, 92))
arrow([(1145, 140), (1145, 190), (1168, 190)], '#c77700')
# micrófono
a('<polyline points="860,170 860,330 890,330" fill="none" stroke="#6a1b9a" stroke-width="2.4"/>')
box(890, 300, 120, 60, ['RC 10 Ω · 10 µF'], '#fff', '#2e7d32', size=14)
box(1040, 290, 160, 80, ['LP5907-3.3', '6,5 µVrms'], '#e5f4e8', '#2e7d32', size=16)
arrow([(1010, 330), (1038, 330)], '#2e7d32')
box(1230, 285, 140, 90, ['ICS-43434', 'ferrita + 100 nF'], '#dceaf7', '#1e5e9f', size=15)
arrow([(1200, 330), (1228, 330)], '#2e7d32')
text(1215, 395, '3V3_MIC', 14, color='#2e7d32', weight='bold')
# señales
box(600, 520, 250, 100, ['Divisor 2 × 1 MΩ desde BAT', '+ 100 nF → ADC1 (GPIO1)', 'mide la celda aun cargando'], '#fff', '#555', size=15)
a('<polyline points="520,420 560,420 560,570 598,570" fill="none" stroke="#6a1b9a" stroke-width="2" stroke-dasharray="6,4"/>')
box(880, 520, 490, 100, ['Firmware (T_MON)', 'lee VBAT, /CHG, /PGOOD y "fuente ≥ 1,5 A"; corta con VSYS ≤ 3,50 V',
                          '(promedio de 1 s, histéresis 100 mV) liberando POWER_HOLD'], '#eef5fb', '#1e5e9f', size=15)
a('<polyline points="705,230 705,495 1000,495 1000,518" fill="none" stroke="#1e5e9f" stroke-width="2" stroke-dasharray="6,4"/>')
text(850, 488, 'POWER_HOLD / botón', 13, color='#1e5e9f')
text(700, 690, 'Apagado: protección 3 µA + cargador ≤ 6,5 µA + divisor 2,1 µA + conmutador 1 µA + RTC 0,05 µA ≈ 12,65 µA (RD-12: ≤ 100 µA).',
     15, color='#333')
text(700, 715, 'Pull-up de /CHG y /PGOOD a 3V3_D (salidas de drenador abierto: sin realimentación con el ESP32 apagado).',
     15, color='#333')
text(700, 740, 'Valores indicativos: se confirman con las hojas de datos al capturar el esquemático (E4).', 15, color='#333')
a('</svg>')
open(sys.argv[1], 'w').write('\n'.join(o))

# ───────────── concepto mecánico ─────────────
head(1400, 760)
text(700, 36, 'Concepto mecánico (cotas en mm, aproximadas)', 23, weight='bold')
# vista frontal
X0, Y0, S = 140, 300, 2.0    # escala px/mm
W, H = 80 * S, 160 * S
a(f'<rect x="{X0}" y="{Y0}" width="{W}" height="{H}" rx="18" fill="#f7f7f7" stroke="#333" stroke-width="3"/>')
a(f'<rect x="{X0 + 12 * S}" y="{Y0 + 12 * S}" width="{56 * S}" height="{42 * S}" fill="#1e3a5f" stroke="#111" stroke-width="2"/>')
text(X0 + W / 2, Y0 + 36 * S, 'TFT de 2,8 in', 17, color='#fff', weight='bold')
for i, lab in enumerate(['MEDIR', 'CAL', 'MENÚ']):
    cx = X0 + (18 + i * 22) * S
    a(f'<circle cx="{cx}" cy="{Y0 + 72 * S}" r="{6 * S}" fill="#ddd" stroke="#333" stroke-width="2"/>')
    text(cx, Y0 + 84 * S, lab, 13)
a(f'<circle cx="{X0 + W / 2}" cy="{Y0 + 95 * S}" r="{3 * S}" fill="#2ca02c" stroke="#333"/>')
text(X0 + W / 2 + 12, Y0 + 96 * S + 4, 'LED', 13, 'start')
a(f'<rect x="{X0 + 15 * S}" y="{Y0 + 135 * S}" width="{50 * S}" height="{18 * S}" fill="none" stroke="#1e5e9f" '
  f'stroke-width="2" stroke-dasharray="6,4"/>')
text(X0 + W / 2, Y0 + 146 * S, 'antena del módulo', 13, color='#1e5e9f')
# vástago y micrófono
bx = X0 + W / 2
a(f'<rect x="{bx - 4 * S}" y="{Y0 - 100 * S}" width="{8 * S}" height="{100 * S}" fill="#ccc" stroke="#333" stroke-width="2"/>')
a(f'<circle cx="{bx}" cy="{Y0 - 100 * S}" r="{9 * S}" fill="#bfbfbf" stroke="#333" stroke-width="2"/>')
a(f'<circle cx="{bx}" cy="{Y0 - 100 * S}" r="{11 * S}" fill="none" stroke="#888" stroke-width="2" stroke-dasharray="3,3"/>')
text(bx + 34 * S, Y0 - 100 * S + 5, 'micrófono en placa satélite + pantalla antiviento', 14, 'start')
text(bx + 34 * S, Y0 - 50 * S, 'vástago de ≈ 100 mm (cable apantallado de 6 hilos)', 14, 'start')
a(f'<line x1="{X0 - 30}" y1="{Y0}" x2="{X0 - 30}" y2="{Y0 + H}" stroke="#555"/>')
text(X0 - 40, Y0 + H / 2, '160', 15, 'end')
a(f'<line x1="{X0}" y1="{Y0 + H + 25}" x2="{X0 + W}" y2="{Y0 + H + 25}" stroke="#555"/>')
text(X0 + W / 2, Y0 + H + 45, '80', 15)
text(X0 + W / 2, 740, 'Vista frontal', 17, weight='bold')
# vista lateral
X1 = 760
D = 35 * S
a(f'<rect x="{X1}" y="{Y0}" width="{D}" height="{H}" rx="10" fill="#f7f7f7" stroke="#333" stroke-width="3"/>')
a(f'<rect x="{X1 + 5 * S}" y="{Y0 + 70 * S}" width="{22 * S}" height="{70 * S}" rx="8" fill="#f3e8f7" stroke="#6a1b9a" stroke-width="2"/>')
text(X1 + 16 * S, Y0 + 108 * S, '18650', 14, color='#6a1b9a', weight='bold')
a(f'<rect x="{X1 + 28 * S}" y="{Y0 + 8 * S}" width="{3 * S}" height="{145 * S}" fill="#2e7d32"/>')
text(X1 + D + 14, Y0 + 30 * S, 'PCB de 4 capas', 14, 'start', '#2e7d32')
a(f'<rect x="{X1 + D}" y="{Y0 + 120 * S}" width="{4 * S}" height="{10 * S}" fill="#666"/>')
text(X1 + D + 14, Y0 + 126 * S, 'USB-C', 14, 'start')
a(f'<rect x="{X1 + D}" y="{Y0 + 100 * S}" width="{3 * S}" height="{12 * S}" fill="#999"/>')
text(X1 + D + 14, Y0 + 107 * S, 'microSD', 14, 'start')
a(f'<rect x="{X1 + 10 * S}" y="{Y0 + H}" width="{14 * S}" height="{5 * S}" fill="#999"/>')
text(X1 + D + 14, Y0 + H + 6, 'rosca 1/4" para trípode', 14, 'start')
a(f'<rect x="{X1 + D / 2 - 4 * S}" y="{Y0 - 100 * S}" width="{8 * S}" height="{100 * S}" fill="#ccc" stroke="#333" stroke-width="2"/>')
a(f'<line x1="{X1}" y1="{Y0 + H + 25}" x2="{X1 + D}" y2="{Y0 + H + 25}" stroke="#555"/>')
text(X1 + D / 2, Y0 + H + 45, '35', 15)
text(X1 + D / 2, 740, 'Vista lateral', 17, weight='bold')
# notas
notes = ['• Micrófono alejado del cuerpo: reduce reflexiones y', '  difracción del gabinete en las bandas altas.',
         '• Antena en el extremo opuesto al micrófono:', '  menos acople de RF al cable y a la cápsula.',
         '• Portapila accesible: batería reemplazable.', '• Gabinete prototipo impreso en 3D (PETG).']
for i, n in enumerate(notes):
    text(1000, 300 + i * 30, n, 15, 'start', '#333')
a('</svg>')
open(sys.argv[2], 'w').write('\n'.join(o))


# ───────────── diagrama de hardware por bloques ─────────────
head(1400, 820)
text(700, 36, 'Diagrama de hardware por bloques: buses, tensiones y conectores', 23, weight='bold')
box(520, 250, 360, 250, ['ESP32-S3-WROOM-1 N16R8', '240 MHz · 2 núcleos · Wi-Fi', '16 MB flash · 8 MB PSRAM',
                         'USB-Serial/JTAG nativo', 'antena en el borde de la placa'], '#dceaf7', '#1e5e9f', sw=3)
box(60, 90, 300, 110, ['Placa satélite (J2)', 'ICS-43434 · 3V3_MIC', 'pull-down 100 kΩ en SD; filtros RF'], '#dceaf7', '#1e5e9f', size=16)
arrow([(360, 140), (450, 140), (450, 300), (518, 300)], '#1e5e9f', label='I2S: BCLK, WS, SD (33 Ω serie)', lpos=(300, 232))
text(300, 252, 'cable apantallado 5 cond. + malla, ≈ 15 cm', 13, color='#1e5e9f')
box(1040, 90, 300, 90, ['Pantalla TFT de 2,8 in', 'controlador ILI9341 (o similar)'], '#f2f2f2', '#666', size=16)
arrow([(880, 300), (950, 300), (950, 135), (1038, 135)], '#555', label='SPI2: CS, MOSI, SCLK, DC, PWM', lpos=(1080, 220))
box(560, 90, 280, 90, ['RTC con cristal 32 kHz', 'respaldo desde la celda · ≈ 45 nA'], '#fff7e6', '#c77700', size=15)
arrow([(700, 180), (700, 248)], '#c77700', label='I2C: SDA 13, SCL 21', lpos=(780, 222))
box(1040, 330, 300, 90, ['Zócalo microSD', 'detección de tarjeta'], '#f2f2f2', '#666', size=16)
arrow([(880, 375), (1038, 375)], '#555', label='SDMMC 1 bit', lpos=(960, 365))
box(1040, 470, 300, 90, ['Pulsadores (3) · LED bicolor', 'TVS en las entradas'], '#f2f2f2', '#666', size=16)
arrow([(880, 460), (960, 460), (960, 515), (1038, 515)], '#555', label='GPIO', lpos=(990, 450))
box(60, 350, 300, 120, ['USB-C (J1)', 'D+/D− → USB nativo', 'VBUS, CC → cargador y comparador'], '#f2f2f2', '#666', size=16)
arrow([(360, 400), (518, 400)], '#555', label='USB 2.0 FS (D+/D−)', lpos=(440, 390))
box(60, 560, 300, 130, ['Alimentación (Fig. 5.2)', 'BQ24074 · 18650 · conmutador', 'LDO 3,3 V · LP5907 3,3 V'], '#f3e8f7', '#6a1b9a', size=16)
arrow([(360, 600), (700, 600), (700, 502)], '#6a1b9a', label='3V3_D', lpos=(560, 590))
arrow([(60, 625), (35, 625), (35, 145), (58, 145)], '#2e7d32', label='3V3_MIC', lpos=(80, 530))
arrow([(360, 650), (780, 650), (780, 502)], '#555', dash=True, label='VBAT, /CHG, /PGOOD, fuente ≥ 1,5 A, POWER_HOLD', lpos=(560, 640))
box(1040, 610, 300, 90, ['Puntos de prueba', 'VSYS, 3V3_D, 3V3_MIC, I2S, UART0'], '#fff', '#888', size=15)
text(700, 780, 'Conectores: J1 USB-C · J2 vástago del micrófono (6 contactos) · J3 portapila. Pines en la Tabla 5.7.',
     15, color='#333')
a('</svg>')
open(sys.argv[3], 'w').write('\n'.join(o))
