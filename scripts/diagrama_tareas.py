#!/usr/bin/env python3
"""Diagramas del Capítulo 4: arquitectura de tareas y cronograma de un ciclo (SVG sin markers).

Uso: python3 -I diagrama_tareas.py <tareas.svg> <cronograma.svg>
"""
import sys

# ───────────────────────── arquitectura de tareas ─────────────────────────
W, H = 1400, 960
o = []
a = o.append


def head(svg_w, svg_h):
    o.clear()
    a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{svg_w}" height="{svg_h}" viewBox="0 0 {svg_w} {svg_h}" '
      'font-family="Arial, Helvetica, sans-serif">')
    a(f'<rect width="{svg_w}" height="{svg_h}" fill="#fff"/>')


def text(x, y, s, size=17, anchor='middle', color='#222', weight='normal', italic=False):
    st = ' font-style="italic"' if italic else ''
    a(f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" fill="{color}" font-weight="{weight}"{st}>{s}</text>')


def box(x, y, w, h, lines, fill='#fff', st='#333', sw=2, rx=8, size=17):
    a(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{st}" stroke-width="{sw}"/>')
    n = len(lines)
    y0 = y + h / 2 - (n - 1) * 11 + 6
    for i, ln in enumerate(lines):
        bold = 'bold' if i == 0 else 'normal'
        text(x + w / 2, y0 + i * 22, ln, size if i == 0 else size - 3, weight=bold,
             color='#111' if i == 0 else '#444')


def queue(x, y, label, n=4, horiz=True, color='#1e5e9f'):
    """Cola dibujada como celdas."""
    cw, ch = 16, 26
    for i in range(n):
        if horiz:
            a(f'<rect x="{x + i * cw}" y="{y}" width="{cw}" height="{ch}" fill="#e8f0fb" stroke="{color}" stroke-width="1.8"/>')
        else:
            a(f'<rect x="{x}" y="{y + i * cw}" width="{ch}" height="{cw}" fill="#e8f0fb" stroke="{color}" stroke-width="1.8"/>')
    if horiz:
        text(x + n * cw / 2, y - 7, label, 14, color=color, weight='bold')
    else:
        text(x + ch + 6, y + n * cw / 2 + 5, label, 14, 'start', color, 'bold')


def arrow(pts, c='#333', dash=False, sw=2.2):
    d = ' stroke-dasharray="7,5"' if dash else ''
    p = ' '.join(f'{x},{y}' for x, y in pts)
    a(f'<polyline points="{p}" fill="none" stroke="{c}" stroke-width="{sw}"{d}/>')
    (x1, y1), (x2, y2) = pts[-2], pts[-1]
    import math
    L = math.hypot(x2 - x1, y2 - y1)
    ux, uy = (x2 - x1) / L, (y2 - y1) / L
    bx, by = x2 - ux * 13, y2 - uy * 13
    a(f'<polygon points="{x2},{y2} {bx - uy * 6.5:.1f},{by + ux * 6.5:.1f} {bx + uy * 6.5:.1f},{by - ux * 6.5:.1f}" fill="{c}"/>')


head(W, H)
# Núcleos
a('<rect x="20" y="70" width="470" height="650" rx="14" fill="#fff7e6" stroke="#c77700" stroke-width="3"/>')
text(255, 102, 'Núcleo 1 · tiempo real estricto', 21, weight='bold', color='#7a4800')
a('<rect x="520" y="70" width="860" height="650" rx="14" fill="#eef5fb" stroke="#1e5e9f" stroke-width="3"/>')
text(950, 102, 'Núcleo 0 · aplicación, interfaz y comunicaciones', 21, weight='bold', color='#1e5e9f')
text(700, 40, 'Arquitectura de tareas del firmware (FreeRTOS SMP, ESP32-S3)', 23, weight='bold')

# Periféricos (abajo)
box(40, 790, 200, 70, ['Micrófono', 'ICS-43434 · I2S'], '#dceaf7', '#1e5e9f')
box(560, 790, 150, 70, ['Pulsadores', 'GPIO'], '#f2f2f2', '#666')
box(730, 790, 150, 70, ['Pantalla TFT', 'SPI2'], '#f2f2f2', '#666')
box(900, 790, 150, 70, ['microSD', 'SDMMC'], '#f2f2f2', '#666')
box(1070, 790, 150, 70, ['Wi-Fi', 'radio'], '#f2f2f2', '#666')
box(1230, 790, 140, 70, ['Batería', 'ADC'], '#f2f2f2', '#666')

# Núcleo 1
box(50, 560, 410, 120, ['I2S RX + GDMA', 'anillo de 16 × 512 muestras (171 ms)', 'ISR en IRAM · on_recv_q_ovf → contador'],
    '#fff', '#c77700')
box(50, 200, 410, 250, ['T_DSP · prioridad 20', 'bloque de 1024 muestras (21,3 ms)', 'conversión → banco multitasa',
                        'Σx² por banda → Leq parcial', 'sin E/S, sin malloc, sin log', 'código y datos en IRAM/DRAM'],
    '#fff', '#c77700', sw=2.5)
arrow([(140, 790), (140, 682)])
arrow([(255, 560), (255, 452)])
text(265, 512, 'i2s_channel_read()', 15, 'start', '#7a4800', italic=True)

# Núcleo 0 — tareas
box(560, 150, 260, 150, ['T_APP · prioridad 10', 'máquina de estados', 'sesión, veredicto, reglas', 'único dueño del estado'],
    '#fff', '#1e5e9f', sw=2.5)
box(1090, 150, 270, 90, ['NVS (flash)', 'escritura solo fuera de MIDIENDO'], '#fdecea', '#d62728')
arrow([(820, 190), (1088, 190)], '#d62728', dash=True)
text(955, 182, 'calibración, piso, config.', 14, color='#d62728')
bw = 150
cols = [(560, ['ISR GPIO', 'antirrebote', '→ evento']), (730, ['T_UI · p8', 'dibujo por', 'notificación']),
        (900, ['T_STOR · p6', 'dueño de la', 'microSD']), (1070, ['T_NET · p5', 'HTTP + WS', 'Wi-Fi/lwIP (18–23)']),
        (1230, ['T_MON · p2', 'pila, CPU,', 'batería, WDT'])]
for x, ln in cols:
    box(x, 570, bw - 10 if x == 1230 else bw, 110, ln, '#fff', '#1e5e9f', size=17)
# Colas
queue(490, 186, 'q_cmd', 4)
arrow([(560, 199), (462, 199)], '#1e5e9f')
queue(490, 280, 'q_res', 4)
arrow([(462, 293), (558, 293)], '#1e5e9f')
queue(600, 420, 'q_evt (16)', 6)
arrow([(635, 570), (635, 448)], '#1e5e9f')
arrow([(650, 420), (650, 302)], '#1e5e9f')
arrow([(1145, 570), (1145, 520), (700, 520), (700, 448)], '#1e5e9f', dash=True)
text(930, 513, 'comandos remotos', 14, color='#1e5e9f')
# buzón de instantánea
a('<rect x="850" y="250" width="40" height="30" fill="#fff2cc" stroke="#b07a00" stroke-width="2"/>')
text(870, 243, 'mbx', 14, color='#7a5200', weight='bold')
arrow([(820, 265), (848, 265)], '#b07a00')
arrow([(880, 280), (805, 568)], '#b07a00', dash=True)
arrow([(890, 272), (1145, 568)], '#b07a00', dash=True)
queue(930, 400, 'q_stor', 3, color='#2e7d32')
arrow([(820, 290), (935, 398)], '#2e7d32')
arrow([(975, 426), (975, 568)], '#2e7d32')
# periféricos
for x in (635, 805, 975, 1145, 1300):
    arrow([(x, 790), (x, 682)], '#666')

# Leyenda
text(40, 900, 'Colas FreeRTOS: mensajes por valor, sin punteros compartidos. mbx = buzón de longitud 1 (xQueueOverwrite) '
     'con la última instantánea; T_UI y T_NET reciben una notificación de tarea.', 15, 'start', '#333')
text(40, 925, 'Ningún recurso tiene dos dueños: la microSD es solo de T_STOR, el estado solo de T_APP y las muestras '
     'solo de T_DSP; por eso no se necesitan mutex en el camino de tiempo real.', 15, 'start', '#333')
a('</svg>')
open(sys.argv[1], 'w').write('\n'.join(o))

# ───────────────────────── cronograma de un ciclo ─────────────────────────
W2, H2 = 1400, 560
head(W2, H2)
text(700, 36, 'Cronograma de dos bloques (escala real: 1 px = 0,03 ms)', 22, weight='bold')
x0, x1 = 170, 1370
T = 21.333
scale = (x1 - x0) / (2 * T + 0.5)


def X(t):
    return x0 + t * scale


rows = [('DMA I2S', 80), ('ISR (IRAM)', 140), ('T_DSP', 200), ('Inactiva núcleo 1', 260),
        ('T_APP', 360), ('T_UI', 420), ('Wi-Fi / T_NET', 480)]
for name, y in rows:
    text(160, y + 22, name, 16, 'end', weight='bold')
    a(f'<line x1="{x0}" y1="{y + 36}" x2="{x1}" y2="{y + 36}" stroke="#ccc" stroke-width="1"/>')
a(f'<line x1="{x0 - 150}" y1="325" x2="{x1}" y2="325" stroke="#999" stroke-width="1.5" stroke-dasharray="6,4"/>')
text(x0 - 150, 318, 'núcleo 1', 14, 'start', '#7a4800', 'bold')
text(x0 - 150, 345, 'núcleo 0', 14, 'start', '#1e5e9f', 'bold')
# DMA continuo: descriptores cada 10,67 ms
for k in range(5):
    t0 = k * 10.667
    a(f'<rect x="{X(t0):.1f}" y="84" width="{X(min(t0 + 10.667, 2 * T + 0.5)) - X(t0):.1f}" height="28" '
      f'fill="{"#dceaf7" if k % 2 == 0 else "#c9dcf2"}" stroke="#1e5e9f" stroke-width="1"/>')
    text((X(t0) + X(min(t0 + 10.667, 2 * T + 0.5))) / 2, 104, f'desc {k}', 13, color='#123')
    a(f'<rect x="{X(t0 + 10.667) - 1:.1f}" y="146" width="3" height="28" fill="#c77700"/>')
C = 3.09
for k in range(2):
    ts = (k + 1) * T
    if ts + C <= 2 * T + 0.5:
        a(f'<rect x="{X(ts):.1f}" y="204" width="{C * scale:.1f}" height="28" fill="#f6b26b" stroke="#c77700"/>')
        text(X(ts) + C * scale / 2, 224, 'C ≈ 3,1 ms', 13)
    a(f'<rect x="{X(ts - T + (C if k else 0)):.1f}" y="264" width="{(T - (C if k else 0)) * scale:.1f}" height="28" '
      f'fill="#f2f2f2" stroke="#bbb"/>')
a(f'<rect x="{X(0):.1f}" y="204" width="{C * scale:.1f}" height="28" fill="#f6b26b" stroke="#c77700"/>')
text(X(0) + C * scale / 2, 224, 'bloque n−1', 13)
# plazo
for k in range(3):
    a(f'<line x1="{X(k * T):.1f}" y1="60" x2="{X(k * T):.1f}" y2="530" stroke="#d62728" stroke-width="1.5" stroke-dasharray="4,4"/>')
    text(X(k * T) + 4, 64, f'{k * T:.1f} ms', 13, 'start', '#d62728')
# núcleo 0
a(f'<rect x="{X(T + C):.1f}" y="364" width="{0.3 * scale:.1f}" height="28" fill="#9fc5e8" stroke="#1e5e9f"/>')
text(X(T + C) + 30, 384, 'resultado (cada 11 bloques)', 13, 'start')
a(f'<rect x="{X(T + C + 0.4):.1f}" y="424" width="{12 * scale:.1f}" height="28" fill="#b6d7a8" stroke="#2e7d32"/>')
text(X(T + C + 0.4) + 6 * scale, 444, 'dibujo de la pantalla (a medir)', 13)
for t0, d in ((2, 1.5), (9, 0.8), (15.5, 2.5), (27, 1.2), (33, 0.6)):
    a(f'<rect x="{X(t0):.1f}" y="484" width="{d * scale:.1f}" height="28" fill="#d9d2e9" stroke="#674ea7"/>')
text(700, 550, 'El núcleo 1 queda inactivo ≈ 85 % del tiempo; la actividad del núcleo 0 (Wi-Fi, pantalla) no interfiere '
     'con la tarea DSP.', 15, color='#333')
a('</svg>')
open(sys.argv[2], 'w').write('\n'.join(o))
