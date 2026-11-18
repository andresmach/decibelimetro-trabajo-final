#!/usr/bin/env python3
"""Diagrama de la arquitectura multitasa del banco de octavas (SVG, sin markers)."""
import sys
W, H = 1400, 860
o = []
a = o.append
a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Arial, Helvetica, sans-serif">')
a(f'<rect width="{W}" height="{H}" fill="#fff"/>')
def box(x, y, w, h, t1, t2=None, fill='#fff', st='#333'):
    a(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{fill}" stroke="{st}" stroke-width="2"/>')
    if t2:
        a(f'<text x="{x+w/2}" y="{y+h/2-4}" font-size="21" font-weight="bold" text-anchor="middle" fill="#111">{t1}</text>')
        a(f'<text x="{x+w/2}" y="{y+h/2+19}" font-size="17" text-anchor="middle" fill="#444">{t2}</text>')
    else:
        a(f'<text x="{x+w/2}" y="{y+h/2+6}" font-size="21" font-weight="bold" text-anchor="middle" fill="#111">{t1}</text>')
def arrow(x1, y1, x2, y2, c='#333'):
    a(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{c}" stroke-width="2.2"/>')
    if x1 == x2:
        s = 1 if y2 > y1 else -1
        a(f'<polygon points="{x2},{y2} {x2-7},{y2-14*s} {x2+7},{y2-14*s}" fill="{c}"/>')
    else:
        s = 1 if x2 > x1 else -1
        a(f'<polygon points="{x2},{y2} {x2-14*s},{y2-7} {x2-14*s},{y2+7}" fill="{c}"/>')
def text(x, y, s, size=16, anchor='middle', color='#333', weight='normal'):
    a(f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" fill="{color}" font-weight="{weight}">{s}</text>')

bands = ['8 kHz', '4 kHz', '2 kHz', '1 kHz', '500 Hz', '250 Hz', '125 Hz']
rates = ['48 kHz', '24 kHz', '12 kHz', '6 kHz', '3 kHz', '1,5 kHz', '750 Hz']
box(30, 40, 200, 70, 'Micrófono I2S', '24 bits · 48 kHz', '#dceaf7', '#1e5e9f')
X0 = 330           # columna de la línea de tasa
y0 = 75
dy = 108
arrow(230, y0, X0 - 10, y0)
text(1240, 30, 'Leq por banda', 17, weight='bold', color='#1e5e9f')
for i, (bn, r) in enumerate(zip(bands, rates)):
    y = y0 + i * dy
    a(f'<circle cx="{X0}" cy="{y}" r="6" fill="#333"/>')
    text(X0 - 20, y - 12, r, 18, 'end', '#7a4800', 'bold')
    arrow(X0, y, 520, y)
    box(520, y - 32, 250, 64, f'Pasabanda {bn}', 'Butterworth orden 8', '#fff7e6', '#c77700')
    arrow(770, y, 850, y)
    box(850, y - 28, 170, 56, 'Σ x²[n]', 'energía por bloque', '#eef5e9', '#2e7d32')
    arrow(1020, y, 1090, y)
    box(1090, y - 28, 290, 56, f'Leq {bn} [dB SPL]', 'promedio + calibración', '#e5f4e8', '#2e7d32')
    if i < 6:
        yd = y + dy / 2
        box(X0 - 115, yd - 22, 230, 44, 'antialias + ↓2', None, '#f3e8f7', '#6a1b9a')
        a(f'<line x1="{X0}" y1="{y+6}" x2="{X0}" y2="{yd-22}" stroke="#333" stroke-width="2.2"/>')
        arrow(X0, yd + 22, X0, y + dy - 7)
text(X0 - 110, H - 40, 'Antialias: elíptico de orden 6 (3 SOS), ondulación 0,01 dB, rechazo ≥ 80 dB desde 0,382·f_entrada', 18, "start", "#6a1b9a")
text(X0 - 110, H - 16, 'Todas las bandas trabajan con la misma relación f_m / f_s ≈ 1/6 (radio máximo de polos ≈ 0,90)', 18, "start", "#444")
a('</svg>')
open(sys.argv[1], 'w').write('\n'.join(o))
