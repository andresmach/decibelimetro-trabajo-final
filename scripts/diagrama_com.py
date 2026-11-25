#!/usr/bin/env python3
"""Diagramas del Capítulo 6: arquitectura de comunicaciones y secuencia de una sesión en el panel.

Uso: python3 -I diagrama_com.py <arquitectura.svg> <secuencia.svg>
SVG sin markers (flechas con polígonos) para que ImageMagick lo convierta sin pérdidas.
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


def arrow(pts, c='#333', sw=2.4, dash=False, label=None, lpos=None, both=False, lsize=14):
    d = ' stroke-dasharray="7,5"' if dash else ''
    a(f'<polyline points="{" ".join(f"{x},{y}" for x, y in pts)}" fill="none" stroke="{c}" stroke-width="{sw}"{d}/>')

    def tip(p1, p2):
        (x1, y1), (x2, y2) = p1, p2
        L = math.hypot(x2 - x1, y2 - y1)
        ux, uy = (x2 - x1) / L, (y2 - y1) / L
        bx, by = x2 - ux * 13, y2 - uy * 13
        a(f'<polygon points="{x2},{y2} {bx - uy * 6.5:.1f},{by + ux * 6.5:.1f} {bx + uy * 6.5:.1f},{by - ux * 6.5:.1f}" fill="{c}"/>')
    tip(pts[-2], pts[-1])
    if both:
        tip(pts[1], pts[0])
    if label:
        text(lpos[0], lpos[1], label, lsize, color=c, weight='bold')


# ───────────── Arquitectura ─────────────
head(1500, 960)
text(750, 36, 'Arquitectura de comunicaciones: clientes, enlace, pila de red y tareas', 23, weight='bold')
# clientes
box(30, 110, 300, 150, ['Celular o PC (navegador)', 'panel web: HTML + JS embebidos', 'WebSocket: instantáneas y eventos',
                        'HTTP: historial, CSV, informe', 'login de técnico por desafío'], '#e8f1fb', '#1f5fa0', size=16)
box(30, 300, 300, 110, ['Servidor de gestión (opcional)', 'Python / FastAPI en una PC', 'descarga sesiones por la API',
                        '(modelo de consulta)'], '#e8f1fb', '#1f5fa0', size=16)
box(30, 450, 300, 90, ['Técnico: imagen OTA firmada', 'subida por HTTP con token'], '#e8f1fb', '#1f5fa0', size=16)
# enlace
a('<rect x="360" y="100" width="160" height="450" rx="10" fill="#fff8e1" stroke="#b07a00" stroke-width="2"/>')
for i, ln in enumerate(['Wi-Fi 2,4 GHz', 'punto de acceso', 'propio', '', 'WPA2/WPA3', 'PMF', 'canal fijo', '13 dBm',
                        'DTIM = 1', '≤ 4 clientes', '', '192.168.4.1', 'DNS → 192.168.4.1']):
    text(440, 135 + i * 30, ln, 16 if i else 17, weight='bold' if i == 0 else 'normal')
for y in (185, 355, 495):
    arrow([(332, y), (358, y)], '#b07a00', both=True)
# equipo
a('<rect x="550" y="70" width="920" height="640" rx="12" fill="#fafafa" stroke="#555" stroke-width="2"/>')
text(1010, 98, 'ESP32-S3 — núcleo 0 (red y aplicación) · el núcleo 1 queda dedicado a T_DSP', 18, weight='bold')
box(570, 120, 170, 90, ['Wi-Fi', 'controlador', 'prio 23'], '#fff', '#b07a00', size=16)
box(570, 230, 170, 90, ['lwIP', 'TCP/IP', 'prio 18'], '#fff', '#b07a00', size=16)
arrow([(655, 212), (655, 228)], '#b07a00', both=True)
arrow([(522, 165), (568, 165)], '#b07a00', both=True)
# servidor http
a('<rect x="770" y="120" width="380" height="330" rx="10" fill="#eef6ee" stroke="#2e7d32" stroke-width="2.4"/>')
text(960, 146, 'T_NET = tarea del servidor HTTP', 17, weight='bold', color='#1b5e20')
text(960, 168, 'esp_http_server · núcleo 0 · prio 5 · pila 6 kB', 14, color='#1b5e20')
for i, (t1, t2) in enumerate([('GET /, /app.js …', 'panel comprimido, en la imagen'),
                              ('/ws (WebSocket)', 'v = 1 · seq · hola · inst · evento · cmd/ack'),
                              ('/api/v1/sesiones, /csv, /informe', 'se delega a T_XFER (asíncrono)'),
                              ('/api/v1/login, /config, /diag', 'token de técnico (PIN por desafío)'),
                              ('/api/v1/ota', 'se delega a T_XFER (asíncrono)')]):
    a(f'<rect x="785" y="{182 + i * 52}" width="350" height="46" rx="6" fill="#fff" stroke="#2e7d32" stroke-width="1.3"/>')
    text(960, 201 + i * 52, t1, 16, weight='bold')
    text(960, 221 + i * 52, t2, 14.5, color='#333')
arrow([(742, 275), (768, 275)], '#b07a00', both=True)
# tareas de la aplicación
box(1240, 120, 210, 110, ['T_APP (prio 10)', 'FSM, sesión, NVS', 'pide la publicación', 'con httpd_queue_work'], '#fff', '#333', size=16)
box(1240, 255, 210, 95, ['T_STOR (prio 6)', 'dueña de la microSD', 'responde en bloques', 'a T_XFER'], '#fff', '#333', size=16)
box(1240, 365, 210, 90, ['T_XFER (prio 4)', 'descargas y OTA', 'una a la vez · 8 kB'], '#eef6ee', '#2e7d32', size=16)
arrow([(1152, 140), (1238, 140)], '#2e7d32', label='q_evt', lpos=(1195, 132))
arrow([(1238, 175), (1152, 175)], '#1f5fa0', dash=True, label='mbx', lpos=(1195, 167))
arrow([(1238, 210), (1152, 210)], '#1f5fa0', dash=True, label='q_net', lpos=(1195, 202))
arrow([(1152, 410), (1238, 410)], '#2e7d32', label='pedido', lpos=(1195, 402))
arrow([(1300, 363), (1300, 352)], '#2e7d32')
text(1395, 361, 'q_lect / flujo', 13, color='#2e7d32', weight='bold')
# reglas
box(570, 470, 880, 120, ['Reglas de integración', 'mbx: última instantánea (se serializa una vez); q_net: respuestas y eventos que no se pueden perder',
                          'envío sin bloqueo: cliente no escribible → se descarta la trama; > 2 s sin poder escribir → se cierra',
                          'comandos remotos → q_evt sin espera; T_APP valida el estado y responde ack / nack con motivo'],
    '#fff', '#888', size=16)
box(570, 605, 880, 90, ['Fecha y hora', 'RTC por I2C alimentado desde la celda (propuesto);',
                         'el panel envía la hora del navegador; el equipo la acepta solo si su hora no es válida'],
    '#fff', '#888', size=16)
# buses internos
text(750, 750, 'Buses internos del equipo (sección 6.11)', 19, weight='bold')
for i, (t1, t2, t3) in enumerate([('I2S', 'micrófono ICS-43434', '3,072 MHz'), ('SPI2', 'pantalla TFT', '10–40 MHz'),
                                  ('SDMMC 1 bit', 'microSD', '20–40 MHz'), ('I2C (propuesto)', 'RTC · táctil futuro', '400 kHz'),
                                  ('USB nativo', 'Serial/JTAG: carga y registros', '12 Mbit/s')]):
    box(30 + i * 292, 775, 270, 100, [t1, t2, t3], '#f2f2f2', '#666', size=17)
text(750, 920, 'El recuadro verde es código propio sobre esp_http_server; los ocres son componentes de ESP-IDF fijados al núcleo 0.', 15, color='#555',
     italic=True)
a('</svg>')
open(sys.argv[1], 'w').write('\n'.join(o))

# ───────────── Secuencia ─────────────
W, H = 1500, 1150
head(W, H)
text(W / 2, 36, 'Secuencia: conexión del panel, medición iniciada desde el panel y reconexión', 23, weight='bold')
cols = [('Navegador', 140), ('Wi-Fi / lwIP', 420), ('T_NET (httpd)', 700), ('T_APP', 980), ('T_DSP', 1260)]
for name, x in cols:
    box(x - 110, 60, 220, 50, [name], '#e8f1fb' if name == 'Navegador' else '#eef6ee', '#333', size=17)
    a(f'<line x1="{x}" y1="112" x2="{x}" y2="{H - 30}" stroke="#999" stroke-width="1.6" stroke-dasharray="6,6"/>')


def msg(x1, x2, y, label, dash=False, color='#222'):
    d = ' stroke-dasharray="7,5"' if dash else ''
    a(f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{color}" stroke-width="2"{d}/>')
    s = 1 if x2 > x1 else -1
    a(f'<polygon points="{x2},{y} {x2 - 13 * s},{y - 6} {x2 - 13 * s},{y + 6}" fill="{color}"/>')
    text((x1 + x2) / 2, y - 7, label, 16.5, color=color)


def note(x, y, w, h, lines, fill='#fff2cc', st='#b07a00'):
    a(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{st}" stroke-width="1.5"/>')
    for i, ln in enumerate(lines):
        text(x + 8, y + 19 + i * 19, ln, 15, 'start', '#333')


X = dict((n, x) for n, x in cols)
y = 150
msg(X['Navegador'], X['Wi-Fi / lwIP'], y, 'asociación WPA2/WPA3 · DHCP')
y += 40
msg(X['Navegador'], X['T_NET (httpd)'], y, 'GET / (panel comprimido)')
y += 34
msg(X['T_NET (httpd)'], X['Navegador'], y, '200 · ≈ 60 kB', dash=True)
y += 44
msg(X['Navegador'], X['T_NET (httpd)'], y, 'GET /ws · Upgrade (se verifica Origin)')
y += 34
msg(X['T_NET (httpd)'], X['Navegador'], y, '101 · hola {v, equipo, fw, estado, hora_valida}', dash=True)
y += 40
msg(X['Navegador'], X['T_NET (httpd)'], y, 'hora {epoch_ms} (si hora_valida = falso)')
y += 30
msg(X['T_NET (httpd)'], X['T_APP'], y, 'q_evt: EV_HORA', color='#2e7d32')
y += 50
msg(X['Navegador'], X['T_NET (httpd)'], y, 'cmd {id: 17, op: "medir", cabina}')
y += 30
msg(X['T_NET (httpd)'], X['T_APP'], y, 'q_evt: EV_REMOTO(medir, id 17)', color='#2e7d32')
y += 30
msg(X['T_APP'], X['T_DSP'], y, 'q_cmd: PREPARAR / INICIAR', color='#2e7d32')
y += 30
msg(X['T_APP'], X['T_NET (httpd)'], y, 'q_net: ack 17 + evento ESPERA', dash=True, color='#1f5fa0')
y += 30
msg(X['T_NET (httpd)'], X['Navegador'], y, 'ack {id: 17} · evento {estado: ESPERA}', dash=True)
y += 46
note(720, y - 18, 760, 62, ['Cada 11 bloques (234,7 ms): T_DSP → q_res → T_APP; T_APP escribe en mbx y pide',
                            'la publicación con httpd_queue_work (una pendiente; si falla, se reintenta).'])
y += 66
msg(X['T_DSP'], X['T_APP'], y, 'q_res', color='#2e7d32')
y += 30
msg(X['T_APP'], X['T_NET (httpd)'], y, 'mbx + aviso', dash=True, color='#1f5fa0')
y += 30
msg(X['T_NET (httpd)'], X['Navegador'], y, 'inst {seq: n, lp[7], la[7], marca[7], prog}')
y += 50
note(40, y - 18, 640, 62, ['El celular se aleja: tras ≈ 4 tramas sin confirmar el socket deja de ser',
                           'escribible; T_NET descarta y, tras 2 s más, lo cierra (≈ 3 s en total).'],
     '#fdecea', '#c62828')
y += 70
msg(X['T_NET (httpd)'], X['Navegador'], y, 'inst {seq: n + 5} (trama descartada)', color='#c62828', dash=True)
a(f'<line x1="{X["Navegador"] - 12}" y1="{y - 12}" x2="{X["Navegador"] + 12}" y2="{y + 12}" stroke="#c62828" stroke-width="3"/>')
a(f'<line x1="{X["Navegador"] - 12}" y1="{y + 12}" x2="{X["Navegador"] + 12}" y2="{y - 12}" stroke="#c62828" stroke-width="3"/>')
y += 50
note(820, y - 18, 600, 44, ['La medición sigue en el equipo: la red no tiene ningún camino hacia T_DSP.'],
     '#eef6ee', '#2e7d32')
y += 56
msg(X['Navegador'], X['T_NET (httpd)'], y, 'reconexión (espera creciente: 1, 2, 4 … 10 s) · GET /ws')
y += 34
msg(X['T_NET (httpd)'], X['Navegador'], y, 'hola {estado: MIDIENDO, sesion, seq actual}', dash=True)
y += 34
msg(X['T_NET (httpd)'], X['Navegador'], y, 'inst {seq: m} — el panel detecta el salto de seq y lo informa')
y += 50
msg(X['T_APP'], X['T_NET (httpd)'], y, 'q_net: sesión cerrada, veredicto', dash=True, color='#1f5fa0')
y += 30
msg(X['T_NET (httpd)'], X['Navegador'], y, 'evento {tipo: sesion_cerrada, veredicto: "APTA"}', dash=True)
a('</svg>')
open(sys.argv[2], 'w').write('\n'.join(o))
print('OK', sys.argv[1], sys.argv[2])
