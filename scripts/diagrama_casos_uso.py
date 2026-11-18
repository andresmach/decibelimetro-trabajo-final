#!/usr/bin/env python3
"""Genera el diagrama de casos de uso UML en SVG (sin dependencias externas).

Uso: python3 -I diagrama_casos_uso.py <salida.svg>
"""
import math
import sys

W, H = 1400, 980
out = []
add = out.append
add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
    'font-family="Arial, Helvetica, sans-serif">')
add(f'<rect width="{W}" height="{H}" fill="#fff"/>')


def text(x, y, s, size=17, weight='normal', anchor='middle', color='#111', italic=False):
    st = ' font-style="italic"' if italic else ''
    add(f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" fill="{color}"{st}>{s}</text>')


def actor(x, y, name, sub=None):
    c = '#222'
    add(f'<circle cx="{x}" cy="{y}" r="17" fill="#fff" stroke="{c}" stroke-width="2.5"/>')
    add(f'<line x1="{x}" y1="{y+17}" x2="{x}" y2="{y+65}" stroke="{c}" stroke-width="2.5"/>')
    add(f'<line x1="{x-30}" y1="{y+35}" x2="{x+30}" y2="{y+35}" stroke="{c}" stroke-width="2.5"/>')
    add(f'<line x1="{x}" y1="{y+65}" x2="{x-25}" y2="{y+100}" stroke="{c}" stroke-width="2.5"/>')
    add(f'<line x1="{x}" y1="{y+65}" x2="{x+25}" y2="{y+100}" stroke="{c}" stroke-width="2.5"/>')
    text(x, y + 125, name, 17, 'bold')
    if sub:
        text(x, y + 146, sub, 15, color='#555')


def uc(cx, cy, uid, name, rx=150, ry=40):
    add(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="#fffbe6" stroke="#b07a00" stroke-width="2.2"/>')
    text(cx, cy - 4, uid, 14, 'bold', color='#7a5200')
    text(cx, cy + 17, name, 16)


def line(x1, y1, x2, y2, dash=False, color='#333'):
    d = ' stroke-dasharray="8,6"' if dash else ''
    add(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="2"{d}/>')


def head(x1, y1, x2, y2, hollow=False, color='#333'):
    d = math.hypot(x2 - x1, y2 - y1)
    ux, uy = (x2 - x1) / d, (y2 - y1) / d
    L, Wd = (20, 12) if hollow else (15, 7)
    bx, by = x2 - ux * L, y2 - uy * L
    pts = f'{x2},{y2} {bx - uy * Wd:.1f},{by + ux * Wd:.1f} {bx + uy * Wd:.1f},{by - ux * Wd:.1f}'
    if hollow:
        add(f'<polygon points="{pts}" fill="#fff" stroke="{color}" stroke-width="2"/>')
    else:
        add(f'<polyline points="{bx - uy * Wd:.1f},{by + ux * Wd:.1f} {x2},{y2} {bx + uy * Wd:.1f},{by - ux * Wd:.1f}" '
            f'fill="none" stroke="{color}" stroke-width="2"/>')


# Límite del sistema
add('<rect x="330" y="20" width="790" height="940" rx="6" fill="#fafcff" stroke="#1e5e9f" stroke-width="2.5"/>')
text(725, 50, 'Analizador de ruido ambiente ISO 8253-1', 19, 'bold', color='#1e5e9f')

L, R = 540, 935
casos = {
    'CU-01': (L, 120, 'Calibrar instrumento'),
    'CU-02': (L, 225, 'Medir cabina'),
    'CU-04': (L, 330, 'Ver medición en tiempo real'),
    'CU-06': (L, 435, 'Consultar historial'),
    'CU-09': (L, 540, 'Exportar registros'),
    'CU-07': (L, 680, 'Configurar instrumento'),
    'CU-10': (L, 785, 'Medir piso de ruido propio'),
    'CU-08': (L, 890, 'Actualizar firmware (OTA)'),
    'CU-03': (R, 225, 'Evaluar conformidad ISO'),
    'CU-05': (R, 435, 'Generar informe de sesión'),
}

# Actores
FX, FY = 130, 250
TX, TY = 130, 640
actor(FX, FY, 'Fonoaudiólogo/a', 'usuario primario')
actor(TX, TY, 'Técnico/a', 'calibración y mantenimiento')
actor(1290, 70, 'Calibrador', 'acústico 94 dB')
actor(1290, 380, 'Servidor de', None)
text(1290, 526, 'gestión', 17, 'bold')

# Asociaciones
for k in ('CU-01', 'CU-02', 'CU-04', 'CU-06', 'CU-09'):
    cx, cy, _ = casos[k]
    line(FX + 35, FY + 40, cx - 150, cy)
for k in ('CU-07', 'CU-10', 'CU-08'):
    cx, cy, _ = casos[k]
    line(TX + 35, TY + 40, cx - 150, cy)
line(1260, 105, L + 150, 120)              # calibrador – CU-01
line(1258, 420, R + 150, 435)              # servidor – CU-05
# Generalización Técnico → Fonoaudiólogo
line(TX, TY - 20, TX, FY + 175)
head(TX, TY - 20, TX, FY + 160, hollow=True)

# «include» CU-02 → CU-03
line(L + 150, 225, R - 150, 225, dash=True)
head(L + 150, 225, R - 150, 225)
text((L + R) / 2, 213, '«include»', 15, italic=True, color='#444')
# «extend» CU-05 → CU-06
line(R - 150, 435, L + 150, 435, dash=True)
head(R - 150, 435, L + 150, 435)
text((L + R) / 2, 423, '«extend»', 15, italic=True, color='#444')
# «extend» CU-05 → CU-02 (informe al finalizar la medición)
line(R - 60, 400, L + 70, 260, dash=True)
head(R - 60, 400, L + 70, 260)
text(770, 315, '«extend»', 15, italic=True, color='#444')

for k, (cx, cy, name) in casos.items():
    uc(cx, cy, k, name)

add('</svg>')
open(sys.argv[1], 'w').write('\n'.join(out))
