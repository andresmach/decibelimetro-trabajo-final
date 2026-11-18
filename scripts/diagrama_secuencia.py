#!/usr/bin/env python3
"""Diagrama de secuencia de una medición (Capítulo 4). Uso: python3 -I diagrama_secuencia.py <salida.svg>"""
import math
import sys

W, H = 1400, 1110
o = []
a = o.append
a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Arial, Helvetica, sans-serif">')
a(f'<rect width="{W}" height="{H}" fill="#fff"/>')


def text(x, y, s, size=16, anchor='middle', color='#222', weight='normal', italic=False):
    st = ' font-style="italic"' if italic else ''
    a(f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" fill="{color}" font-weight="{weight}"{st}>{s}</text>')


def msg(x1, x2, y, label, dash=False, color='#222'):
    d = ' stroke-dasharray="7,5"' if dash else ''
    a(f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{color}" stroke-width="2"{d}/>')
    s = 1 if x2 > x1 else -1
    a(f'<polygon points="{x2},{y} {x2 - 13 * s},{y - 6} {x2 - 13 * s},{y + 6}" fill="{color}"/>')
    text((x1 + x2) / 2, y - 7, label, 14, color=color)


def note(x, y, w, h, lines, fill='#fff2cc', st='#b07a00'):
    a(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{st}" stroke-width="1.5"/>')
    for i, ln in enumerate(lines):
        text(x + 8, y + 19 + i * 18, ln, 13.5, 'start', '#333')


text(700, 34, 'Secuencia de una medición de cabina (CU-02)', 22, weight='bold')
parts = [('Pulsador', 'ISR GPIO', 90), ('T_APP', 'núcleo 0 · p10', 330), ('T_DSP', 'núcleo 1 · p20', 590),
         ('T_UI / T_NET', 'núcleo 0 · p8 / p5', 860), ('T_STOR', 'núcleo 0 · p6', 1090), ('NVS / flash', '', 1300)]
X = {}
for n, sub, x in parts:
    X[n] = x
    a(f'<rect x="{x - 85}" y="60" width="170" height="54" rx="6" fill="#eef5fb" stroke="#1e5e9f" stroke-width="2"/>')
    text(x, 84, n, 16, weight='bold')
    if sub:
        text(x, 104, sub, 13, color='#555')
    a(f'<line x1="{x}" y1="114" x2="{x}" y2="{H - 30}" stroke="#999" stroke-width="1.5" stroke-dasharray="5,5"/>')
y = 150
msg(X['Pulsador'], X['T_APP'], y, 'q_evt: MEDIR'); y += 40
note(X['T_APP'] - 70, y - 12, 230, 44, ['REPOSO → ESPERA (3 s)', 'candado PM: CPU_FREQ_MAX'])
y += 64
msg(X['T_APP'], X['T_DSP'], y, 'q_cmd: PREPARAR'); y += 30
note(X['T_DSP'] - 80, y - 12, 250, 44, ['i2s_channel_enable()', 'filtra sin acumular (transitorio)'], '#fff7e6', '#c77700')
y += 70
note(X['T_APP'] - 70, y - 12, 200, 26, ['temporizador 3 s'])
y += 40
msg(X['T_APP'], X['T_DSP'], y, 'q_cmd: INICIAR (T_int, K, C_b)'); y += 30
note(X['T_DSP'] - 80, y - 12, 250, 26, ['modo acumular: Σx² por banda'], '#fff7e6', '#c77700')
y += 50
for k in range(2):
    msg(X['T_DSP'], X['T_APP'], y, f'q_res: L_eq parcial #{k + 1} (cada 11 bloques ≈ 235 ms)', dash=True, color='#1e5e9f')
    y += 32
    msg(X['T_APP'], X['T_UI / T_NET'], y, 'mbx + notificación', dash=True, color='#b07a00')
    y += 44
text(X['T_DSP'], y, '… (un resultado cada 235 ms durante T_int)', 15, color='#555'); y += 34
msg(X['T_DSP'], X['T_APP'], y, 'q_res: final (L_eq de sesión, desbordes, C máx.)', color='#1e5e9f'); y += 30
note(X['T_APP'] - 70, y - 12, 250, 44, ['CU-03: regla de piso y veredicto', 'MIDIENDO → RESULTADO'])
y += 60
msg(X['T_APP'], X['T_DSP'], y, 'q_cmd: REPOSO'); y += 30
note(X['T_DSP'] - 80, y - 12, 250, 26, ['i2s_channel_disable()'], '#fff7e6', '#c77700')
y += 50
msg(X['T_APP'], X['T_UI / T_NET'], y, 'mbx: veredicto APTA / NO APTA'); y += 40
msg(X['T_APP'], X['T_STOR'], y, 'q_stor: registro de sesión'); y += 30
note(X['T_STOR'] - 85, y - 12, 190, 44, ['escritura FAT en microSD', '(no detiene la caché)'], '#e5f4e8', '#2e7d32')
y += 60
msg(X['T_STOR'], X['T_APP'], y, 'q_evt: GUARDADA', dash=True); y += 40
note(X['T_APP'] - 70, y - 12, 250, 26, ['libera candado PM → REPOSO'])
y += 50
msg(X['T_APP'], X['NVS / flash'], y, 'solo en REPOSO: guardar calibración / piso', color='#d62728'); y += 30
text(700, H - 8, 'Línea llena: mensaje con espera del receptor; línea de trazos: mensaje sin espera del emisor '
     '(xQueueSend con plazo 0 o xQueueOverwrite).', 14, color='#333')
a('</svg>')
open(sys.argv[1], 'w').write('\n'.join(o))
