#!/usr/bin/env python3
"""Capítulo 6 — Comunicaciones: enlace Wi-Fi, protocolo, integración, seguridad y OTA (v0.2).

Uso (desde anteproyecto/):
  python3 -I scripts/generar_cap6_com.py plantilla/ModeloAnteproyecto.docx figuras capitulos/Cap6_Comunicaciones.docx

Cifras: comunicaciones/resultados/resumen_com.txt (comunicaciones/analisis_comunicaciones.py).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from docx_xml import P, B, H2  # noqa: E402
from cap_common import H1, PB, CAP, KT, CODE, Figuras, ensamblar  # noqa: E402

TPL, FIG, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
FIGURA = Figuras(FIG, 'C6')
VERSION = '0.2.1 (revisada con el método Elephant–Goldfish; cambios propagados a los demás documentos)'

body = []
add = body.extend

# ───────────── Portada ─────────────
add([P('', after=600),
     P('Capítulo 6', size=40, bold=True, align='center', color='1E5E9F', after=120),
     P('Comunicaciones', size=36, bold=True, align='center', color='1E5E9F', after=200),
     P('Enlace Wi-Fi, protocolo de aplicación, integración con el firmware de tiempo real, seguridad y '
       'actualización OTA', size=28, bold=True, align='center', after=400),
     P('Analizador autónomo de ruido ambiente por bandas de octava para la verificación de cabinas '
       'audiométricas según ISO 8253-1', size=24, align='center', after=1200),
     P('**Autor:** Andrés Machtey', size=24, align='left', after=100),
     P('**Director propuesto:** Esp. Víctor Valotto (FIUNER)', size=24, align='left', after=100),
     P(f'**Versión:** {VERSION} · Noviembre de 2026', size=24, align='left', after=100),
     P('**Material reproducible:** comunicaciones/analisis_comunicaciones.py, comunicaciones/graficos_com.gp, '
       'comunicaciones/resultados/ y scripts/diagrama_com.py', size=20, align='left', after=100),
     PB()])

# ───────────── Siglas ─────────────
add([H1('Siglas y convenciones'),
     KT(['Sigla', 'Significado', 'Sigla', 'Significado'],
        [['AP / STA', 'Punto de acceso / estación (cliente) Wi-Fi', 'SSID', 'Nombre de la red Wi-Fi'],
         ['WPA2 / WPA3', 'Seguridad Wi-Fi con clave precompartida (PSK) / con SAE', 'PMF', 'Tramas de gestión protegidas (802.11w)'],
         ['SAE', 'Autenticación simultánea de iguales (WPA3)', 'CCMP', 'Cifrado y autenticación de tramas de WPA2/WPA3 (AES)'],
         ['TIM / DTIM', 'Mapa de tráfico pendiente en cada baliza / intervalo para el tráfico de grupo', 'TU', 'Unidad de tiempo de 802.11 (1024 µs)'],
         ['PHY', 'Capa física de la radio', 'DHCP / DNS', 'Asignación de direcciones / resolución de nombres'],
         ['HTTP / WS', 'Protocolo de hipertexto / WebSocket', 'REST', 'Estilo de API sobre recursos HTTP'],
         ['TLS / HTTPS', 'Seguridad de la capa de transporte / HTTP sobre TLS', 'JSON / CSV', 'Formatos de texto estructurado / tabular'],
         ['OTA', 'Actualización de firmware inalámbrica', 'NVS', 'Almacenamiento no volátil clave-valor de ESP-IDF'],
         ['RTC / NTP', 'Reloj de tiempo real / protocolo de hora de red', 'CRC', 'Código de redundancia cíclica'],
         ['HMAC', 'Código de autenticación de mensajes con clave', 'PBKDF2', 'Derivación de claves a partir de una contraseña'],
         ['PAKE', 'Intercambio de claves autenticado por contraseña', 'Token', 'Credencial aleatoria temporal de una sesión'],
         ['RSSI', 'Potencia de señal recibida', 'dBm / dBi', 'Potencia referida a 1 mW / ganancia de antena'],
         ['FAT', 'Sistema de archivos de la microSD', 'QR', 'Código de barras bidimensional']],
        [1300, 3119, 1300, 3118], size=17),
     P('Los identificadores RD, EN, CU, HU, D3.x, D4.x y D5.x remiten al anteproyecto, al anexo de Ingeniería de '
       'Software y a los Capítulos 3 a 5. Las pruebas nuevas son **PU-COM-xx**, los hallazgos **H6.x** y las '
       'decisiones **D6.x**. Los valores marcados como **supuestos** (ganancias de antena, sensibilidad del '
       'celular, atenuación de la cabina, intervalo de escucha, memoria) se reemplazan por mediciones. Los nombres '
       'de funciones y opciones de configuración corresponden a ESP-IDF 5.4 y se verificaron en su código '
       'fuente [2].', size=20)])

# ───────────── 6.1 ─────────────
add([H1('6.1 Enfoque del capítulo'),
     P('Este capítulo analiza el proyecto desde las **comunicaciones** de un sistema embebido: el enlace de '
       'radio, la pila de protocolos por capas, el protocolo de aplicación entre el equipo y sus clientes, la '
       'integración de la red con el firmware de tiempo real, la seguridad, la actualización remota del '
       'firmware y los buses internos [1]. Parte del análisis de las comunicaciones del prototipo del curso de '
       'DSP —un puerto serie con mensajes JSON y un servidor Python con WebSocket— y llega a un diseño en el que '
       'el instrumento es su propio servidor, sin PC ni infraestructura de red, justificado con cálculos '
       'reproducibles.'),
     H2('Requisitos que condicionan las comunicaciones'),
     KT(['Requisito', 'Enunciado (anteproyecto y anexo)', 'Consecuencia para las comunicaciones'],
        [['RD-06', 'Indicación actualizada cada ≤ 250 ms en pantalla y en el panel web', 'Período de publicación '
          'de 234,7 ms; latencia de extremo a extremo acotada (sección 6.6)'],
         ['RD-07', '0 desbordes en 8 h; CPU del núcleo DSP ≤ 70 %', 'La red no puede bloquear ni demorar a T_DSP '
          '(D4.5, D4.6)'],
         ['RD-08', 'Autonomía ≥ 8 h con Wi-Fi activo', 'El punto de acceso no duerme; costo de la transmisión '
          '(sección 6.4)'],
         ['RD-09', '≥ 1000 sesiones en microSD, sin corrupción ante cortes (CU-06, CU-09: historial y exportación)',
          'Historial paginado y exportación en bloques sin afectar las escrituras'],
         ['RD-10, RD-11', 'Calibración con fecha; OTA con reversión ante falla', 'Hora válida sin internet; '
          'imagen firmada, particiones dobles y autodiagnóstico'],
         ['Interfaz', 'Punto de acceso propio sin internet; panel, historial, CSV e informe', 'Servidor HTTP y '
          'WebSocket embebido; panel incluido en la imagen'],
         ['Ambiente', 'El Wi-Fi propio no degrada la medición (EN-09)', 'Potencia de transmisión y picos de corriente'],
         ['Otros', 'WPA2 con contraseña configurable; sin datos de pacientes', 'Modelo de amenazas, autenticación '
          'del técnico y privacidad'],
         ['CU-04 a CU-09; HU-07 a HU-09, HU-11, HU-12', 'Tiempo real, informe, historial, configuración, OTA y '
          'exportación por el panel', 'Recursos HTTP, mensajes WS, roles y estados en que se admite cada operación']],
        [1500, 3500, 3837], size=17),
     CAP('Tabla 6.1. Requisitos que condicionan el diseño de las comunicaciones.')])

# ───────────── 6.2 ─────────────
add([H1('6.2 Análisis de las comunicaciones del prototipo'),
     P('En el prototipo, el ESP32 enviaba cada resultado como una línea JSON por la UART1 a 921 600 bit/s, '
       'que llegaba a la PC por el conversor USB de la placa gracias a un puente de cable (H5.6). En la PC, un '
       'servidor FastAPI leía el puerto serie en un hilo, guardaba las mediciones en SQLite, las reenviaba por '
       'WebSocket a un panel en el navegador y generaba el informe PDF. La Tabla 6.2 resume los hallazgos.'),
     KT(['ID', 'Hallazgo', 'Evidencia', 'Consecuencia', 'Sev.'],
        [['H6.1', 'El servidor calcula el nivel de la sesión con el promedio aritmético de los niveles en dB '
          '(SQL AVG)', 'database.py: AVG(db_125)…', 'Subestima el L_eq; puede convertir un NO APTA en APTA '
          '(Figura 6.1)', 'Alta'],
         ['H6.2', 'El servidor responde al panel con estados y resultados de calibración fijos («measuring», '
          'medido 94,0, factor 1,0) sin esperar al equipo', 'main.py: route_browser_cmd', 'Dos fuentes de verdad; '
          'el panel puede mostrar una medición que el equipo no inició', 'Alta'],
         ['H6.3', 'Los límites ISO están copiados en el firmware, el servidor y el panel', 'app_config.h, main.py, '
          'index.html', 'Una actualización parcial da veredictos distintos para la misma medición', 'Media'],
         ['H6.4', 'Protocolo de líneas JSON sin versión, sin número de secuencia ni verificación de integridad; '
          'las líneas inválidas solo se registran', 'uart_comm.c, serial_bridge.py', 'Pérdidas y cortes no '
          'detectables; evolución del protocolo frágil', 'Media'],
         ['H6.5', 'El hilo del puerto serie usa asyncio.Queue.get_nowait(), que no es segura entre hilos, y '
          'sondea cada 5 ms', 'serial_bridge.py: _run', 'Condición de carrera esporádica; consumo de CPU en la PC',
          'Media'],
         ['H6.6', 'El campo «cal_ok» que se transmite vale «factor ≠ 1,0», sin relación con la vigencia de la '
          'calibración', 'db_calculator.c', 'El protocolo informa un dato engañoso', 'Baja'],
         ['H6.7', 'Sin autenticación ni roles: cualquier cliente del WebSocket puede iniciar, detener o calibrar',
          'main.py: ws_endpoint', 'Aceptable en un puesto local; inadmisible en un punto de acceso compartido',
          'Media'],
         ['H6.8', 'Al reconectarse, el panel no pide el estado actual', 'index.html: connectWS', 'Pantalla '
          'desactualizada hasta el próximo mensaje', 'Baja'],
         ['H6.9', 'La visualización remota depende de una PC con el servidor y del cable USB', 'README',
          'El instrumento no es autónomo (H5.5)', 'Alta']],
        [700, 3300, 1900, 2137, 800], size=16),
     CAP('Tabla 6.2. Hallazgos en las comunicaciones del prototipo.'),
     P('**H6.1 es un error metrológico, no solo de software.** El nivel equivalente es un promedio de energía, '
       'L_eq = 10·log₁₀(⟨10^(L/10)⟩) [14]. Promediar los niveles en dB da siempre un valor menor o igual, y la '
       'diferencia crece con la fluctuación del ruido: para fluctuaciones gaussianas en dB es ≈ 0,115·σ² '
       '(1,0 dB con σ = 3 dB). Para un ruido intermitente —un fondo de 20 dB SPL con un evento de 35 dB SPL el '
       '10 % del tiempo— el L_eq es 26,1 dB y el promedio de niveles 21,5 dB. Con el límite de trabajo de 25 dB SPL '
       'de la banda de 250 Hz, la cabina resulta NO APTA según el L_eq y APTA según el promedio: **el error va en '
       'la dirección insegura** (Figura 6.1). El diseño nuevo calcula el L_eq de la sesión solo en el firmware, '
       'con acumuladores de energía (D4.7), y el resto del sistema lo transporta sin recalcularlo (D6.3, D6.8).'),
     *FIGURA('cap6_sesgo.png', 12.5,
             'Figura 6.1. Diferencia entre el L_eq y el promedio aritmético de los niveles en dB (hallazgo H6.1).')])

# ───────────── 6.3 ─────────────
add([H1('6.3 Arquitectura y elección de tecnologías'),
     P('La Figura 6.2 muestra la arquitectura propuesta. El equipo genera su propio punto de acceso; el '
       'navegador de un celular o de una PC descarga el panel desde el equipo y abre un canal WebSocket [3]. Todo '
       'el servicio de red corre en el núcleo 0: la tarea del servidor HTTP de ESP-IDF, que en este diseño **es** '
       'T_NET, atiende las operaciones cortas, y una tarea nueva, T_XFER, las transferencias largas. El núcleo 1 '
       'sigue dedicado a T_DSP (D4.6).'),
     *FIGURA('cap6_arquitectura.png', 17,
             'Figura 6.2. Arquitectura de comunicaciones: clientes, enlace, pila de red, tareas y buses internos.'),
     KT(['Opción', 'Consumo adicional', 'Alcance / latencia', 'Cliente y dependencias', 'Evaluación'],
        [['Wi-Fi, punto de acceso propio', '≈ 145 mA: el receptor no duerme (Cap. 5)', '10–30 m en interiores; '
          'decenas de ms', 'Navegador; ninguna infraestructura', '**Elegida**'],
         ['Wi-Fi, cliente de la red del hospital', '≈ 20–40 mA con ahorro por DTIM (supuesto)', 'Toda la red; '
          'decenas de ms', 'Credenciales institucionales, portales cautivos, aislamiento de clientes',
          'Trabajo futuro'],
         ['Bluetooth LE (GATT)', '≈ 5–15 mA (supuesto)', '10–20 m; 7,5 ms o más por intervalo', 'Aplicación '
          'nativa: Safari de iOS no implementa Web Bluetooth', 'Descartada'],
         ['Cable USB', 'Ninguno', 'Cable', 'PC; el cable atraviesa la puerta y rompe el sello acústico de la '
          'cabina', 'Descartada'],
         ['Sondeo HTTP cada 235 ms', '—', '+1 viaje de ida y vuelta; ≈ 400 B de cabeceras por pedido', '4 pedidos/s '
          'por cliente', 'Descartada'],
         ['Eventos del servidor (SSE)', '—', 'Unidireccional', 'Comandos por POST aparte', 'Descartada'],
         ['WebSocket', '—', '2–4 B de cabecera por trama; bidireccional', 'Soporte nativo en esp_http_server y '
          'en los navegadores', '**Elegida**']],
        [2100, 1800, 1900, 2000, 1037], size=16),
     CAP('Tabla 6.3. Comparación de alternativas de enlace y de transporte de tiempo real. MQTT se descartó '
         'porque exige un broker (intermediario de mensajes).'),
     H2('Decisiones por capa'),
     P('La Tabla 6.4 ubica cada decisión en el modelo de capas de Internet [1]. La integridad que faltaba en el '
       'prototipo (H6.4) queda cubierta en varias capas: el código de integridad de CCMP en el enlace, la suma '
       'de verificación y las retransmisiones de TCP en el transporte, y el número de secuencia y el CRC-32 de '
       'cada sesión en la aplicación.'),
     KT(['Capa', 'Elección', 'Integridad y errores', 'Decisión'],
        [['Aplicación', 'HTTP/1.1 [4], WebSocket [3], JSON versionado, API /api/v1', 'seq, ack/nack con motivo, '
          'CRC-32 de cada sesión', 'D6.3, D6.5'],
         ['Transporte', 'TCP de lwIP; envío sin bloqueo', 'Suma de verificación, retransmisión y orden', 'D6.4'],
         ['Red', 'IPv4 192.168.4.0/24; servidor DHCP; DNS propio', 'Suma de verificación de la cabecera IP',
          'D6.2'],
         ['Enlace', '802.11 con CCMP (WPA2/WPA3) y PMF [5, 6]', 'Código de integridad de 64 bits, FCS, '
          'reintentos de la capa MAC', 'D6.2, D6.5'],
         ['Física', '2,4 GHz, canal fijo, 13 dBm', 'Margen del enlace (sección 6.4)', 'D6.2']],
        [1300, 3100, 2900, 1537], size=16),
     CAP('Tabla 6.4. Decisiones ubicadas en el modelo de capas.'),
     P('**Decisión D6.1:** punto de acceso propio con servidor HTTP y WebSocket embebido; el panel web viaja '
       'dentro de la imagen del firmware (D4.3). Corrige H6.9. El modo cliente de la red institucional queda como '
       'trabajo futuro, porque exige gestionar credenciales de terceros y no aporta a los requisitos actuales.')])

# ───────────── 6.4 ─────────────
add([H1('6.4 Enlace de radio'),
     H2('Presupuesto del enlace con el equipo dentro de la cabina'),
     P('El caso de uso CU-04 supone que el equipo queda **dentro** de la cabina audiométrica y la fonoaudióloga '
       'lo sigue desde afuera. Las cabinas son recintos de paneles metálicos con relleno absorbente, ventana de '
       'doble vidrio y puerta con burletes: no se diseñan como jaulas de Faraday, pero atenúan la señal de '
       '2,4 GHz en una magnitud que no figura en ninguna hoja de datos y que depende de la ventana, de las '
       'juntas y de los pasamuros. Es el principal riesgo de las comunicaciones y se trata con un presupuesto '
       'del enlace y una medición temprana (PU-COM-01).'),
     P('El enlace limitante es el descendente (equipo → celular), porque la sensibilidad de un celular es '
       'menos conocida y en general peor que la del ESP32-S3 [7]. Con la pérdida en espacio libre de Friis, '
       'L = 20·log₁₀(4πd/λ) [8], a 2,437 GHz y los supuestos de la Tabla 6.5, la atenuación de la cabina que deja '
       '10 dB de margen de desvanecimiento es:'),
     KT(['Distancia', 'P_TX = 8,5 dBm', 'P_TX = 13 dBm', 'P_TX = 19,5 dBm'],
        [['2 m (celular junto a la ventana)', '31,3 dB', '35,8 dB', '42,3 dB'],
         ['3 m', '27,8 dB', '32,3 dB', '38,8 dB'],
         ['5 m', '23,3 dB', '27,8 dB', '34,3 dB'],
         ['10 m (otra sala, sin contar paredes)', '17,3 dB', '21,8 dB', '28,3 dB']],
        [2837, 2000, 2000, 2000], size=17, center_cols=(1, 2, 3)),
     CAP('Tabla 6.5. Atenuación máxima admisible de la cabina con 10 dB de margen. Supuestos: antena del equipo '
         '0 dBi dentro del gabinete, celular −3 dBi, 3 dB de pérdidas por el cuerpo, sensibilidad del celular '
         '−85 dBm a la menor tasa usada. Una pared interior resta otros 5 a 15 dB.'),
     *FIGURA('cap6_enlace.png', 12.5,
             'Figura 6.3. Margen del enlace equipo → celular en función de la atenuación de la cabina.'),
     P('Si una cabina atenúa más de ≈ 30 dB, el panel puede no funcionar desde la sala contigua aun a máxima '
       'potencia. Por eso el diseño no depende del enlace para medir: la medición, el veredicto y el registro '
       'ocurren en el equipo, que los muestra en su pantalla, y el panel se resincroniza al recuperar la conexión '
       '(sección 6.5). El enlace es una comodidad de CU-04 (prioridad «Should», es decir, deseable), no una '
       'condición de la medición.'),
     H2('Parámetros del punto de acceso'),
     KT(['Parámetro', 'Valor', 'Justificación'],
        [['Seguridad', 'WPA2/WPA3 en transición, PMF habilitado; opción «solo WPA3» (transition_disable)',
          'WPA3 donde el celular lo admite; WPA2 para celulares anteriores; PMF evita las desautenticaciones '
          'falsificadas (sección 6.7)'],
         ['País y canal', 'esp_wifi_set_country_code("AR"); canal fijo 1, 6 u 11, configurable', 'Canales y '
          'potencias de la tabla de país; se elige el canal menos ocupado con un analizador de Wi-Fi'],
         ['Potencia de transmisión', '13 dBm por defecto (ajustable de 8,5 a 19,5 dBm)', 'Margen a 3 m con '
          'cabinas de hasta ≈ 32 dB; menos picos de corriente y acoplamiento al micrófono (D5.5)'],
         ['Baliza y DTIM', '100 TU; DTIM = 1 (valores por defecto)', 'Tráfico de grupo en cada baliza; el '
          'unicast depende del intervalo de escucha del celular (sección 6.6)'],
         ['Clientes', '≤ 4 (max_connection = 4)', 'CU-04, flujo 2b; acota memoria y ocupación del canal'],
         ['Inactividad', '60 s (esp_wifi_set_inactive_time; por defecto 300 s)', 'Libera el lugar de un celular '
          'que se fue sin desasociarse; se prueba con la pantalla del celular apagada (PU-COM-06)'],
         ['Direccionamiento', '192.168.4.1; servidor DHCP (8 direcciones, ≥ 4 clientes); DNS que responde '
          'con la propia dirección', 'Código QR con la red y la dirección en la etiqueta; cualquier nombre lleva '
          'al panel'],
         ['Cambios de estado de la radio', 'Solo en REPOSO', 'El arranque de la radio calibra la capa física y '
          'produce picos de corriente; no debe ocurrir durante una medición (EN-09)']],
        [2000, 2900, 3937], size=16),
     CAP('Tabla 6.6. Configuración del punto de acceso.'),
     H2('Ocupación del canal y energía'),
     P('Una instantánea JSON de 251 B viaja en una trama de ≈ 359 B con las cabeceras de WebSocket, TCP/IP y '
       '802.11 con CCMP. Cada cliente recibe 4,26 tramas/s (17 en total con 4 clientes), ≈ 49 kbit/s en el aire. '
       'A 6 Mbit/s, contando el acceso al medio (DIFS y espera aleatoria) y los ACK de la capa MAC, ocupan el '
       '3,7 % del canal, del cual 2,5 % corresponde a las balizas; los ACK de TCP del celular suman menos de un '
       'punto más. El transmisor del equipo trabaja ese 3,7 % del tiempo, de modo que la transmisión agrega '
       '≈ 7 mA a la recepción continua del punto de acceso (supuesto: 300 mA en transmisión y 100 mA en '
       'recepción). Esa corriente **no estaba** en el presupuesto del Capítulo 5 (145 mA en modo medición, '
       'recepción continua): se suma y deja el peor caso de autonomía en ≈ 8,7 h, todavía por encima de RD-08. '
       '**Bajar la potencia de transmisión casi no cambia la autonomía**; se ajusta por los picos de corriente, '
       'el acoplamiento con el micrófono y la convivencia con otros equipos.'),
     H2('Comportamiento de los celulares'),
     P('Un celular conectado a una red sin internet puede seguir usando los datos móviles como red por '
       'defecto: Android, por ejemplo, avisa que la red «no tiene acceso a internet» y, según la versión y la '
       'configuración, puede dirigir las conexiones del navegador por la red móvil, que no llega a '
       '192.168.4.1. El DNS propio ayuda a que el sistema abra el panel como página de inicio de sesión, pero '
       'el «DNS privado» de Android lo ignora y el navegador reducido que iOS usa para esas páginas tiene '
       'limitaciones. Se verifica con al menos tres celulares (PU-COM-06); el manual indica abrir la dirección '
       'del código QR y «mantener la conexión» o desactivar los datos móviles durante la medición.'),
     H2('Marco regulatorio'),
     P('El prototipo usa un módulo de radio con certificaciones de fábrica (ESP32-S3-WROOM-1 [7]), con la '
       'antena integrada que no se modifica, y configura el código de país «AR» para respetar los canales y '
       'potencias de la tabla de ESP-IDF, que se verifican contra la normativa vigente. Un equipo comercial que '
       'incluya un transmisor requiere la homologación del ENACOM [15]; el prototipo de laboratorio no se '
       'comercializa. En el ámbito hospitalario, el equipo transmite con 13 dBm, menos que un celular, que el '
       'equipamiento médico debe tolerar a corta distancia.'),
     P('**Decisión D6.2:** punto de acceso WPA2/WPA3 con PMF, código de país AR, canal fijo configurable, '
       '13 dBm por defecto, DTIM = 1, hasta 4 clientes, inactividad de 60 s y cambios de estado de la radio solo '
       'en REPOSO. El enlace es una comodidad: ninguna función de medición depende de él.')])

# ───────────── 6.5 ─────────────
add([H1('6.5 Protocolo de aplicación'),
     P('El protocolo separa dos tipos de intercambio. Lo que cambia en el tiempo (niveles, estado, eventos) '
       'viaja por un único WebSocket [3]; lo que se consulta o se descarga (historial, CSV, informe, '
       'configuración, imagen OTA) usa recursos HTTP bajo /api/v1 [4]. Las reglas que corrigen los hallazgos H6.2 '
       'a H6.8 son:'),
     B('**Una sola fuente de verdad:** el equipo calcula el L_eq, aplica la regla de piso de ruido, compara con '
       'la tabla de límites vigente y emite el veredicto. El panel y el servidor de gestión solo lo muestran; '
       'la tabla de límites viaja en el mensaje «hola» para que el panel dibuje las barras, nunca para decidir.'),
     B('**Versión y secuencia:** todo mensaje lleva «v» (versión del protocolo) y las instantáneas un número '
       '«seq» creciente; el panel detecta saltos y los informa sin alterar la sesión, que está completa en el '
       'equipo.'),
     B('**Resincronización:** al abrirse el WebSocket, el equipo envía «hola» con el estado completo; el panel '
       'no supone nada del estado anterior a la desconexión (H6.8).'),
     B('**Comandos con confirmación:** cada comando lleva un identificador elegido por el panel; el equipo '
       'responde «ack» o «nack» con el motivo. El equipo recuerda los últimos 16 identificadores durante 60 s, '
       'de modo que un comando repetido no se ejecuta dos veces. El panel muestra un estado solo cuando lo '
       'confirma el equipo (H6.2).'),
     KT(['Tipo', 'Sentido', 'Cuándo', 'Contenido principal'],
        [['hola', 'Equipo → panel', 'Al abrir el WebSocket y tras un desborde de q_net', 'v, equipo, versión de '
          'firmware, estado, sesión en curso, seq, tabla de límites, fecha y vigencia de la calibración, '
          'hora_valida'],
         ['inst', 'Equipo → panel', 'Cada 234,7 ms en MIDIENDO, CALIBRANDO y MIDIENDO_PISO; cada 1 s en los '
          'demás estados', 'seq, t_ms, L_eq parcial y acumulado por banda (décimas de dB), marcas de piso, '
          'avance, veredicto parcial, descriptores perdidos, batería'],
         ['evento', 'Equipo → panel', 'Cambio de estado, sesión cerrada, alarmas, avance de la OTA', 'tipo y '
          'datos (veredicto, batería baja, microSD, calibración vencida)'],
         ['cmd', 'Panel → equipo', 'Acción del usuario', 'id, op y parámetros (cabina ≤ 16 caracteres, iniciales '
          'del operador); token si la operación es de técnico'],
         ['ack / nack', 'Equipo → panel', 'Respuesta a cada cmd', 'id, resultado y motivo (estado, rol, ocupado, '
          'formato, versión)'],
         ['ping / pong', 'Ambos', 'Cada 5 s', 'Detección de clientes perdidos'],
         ['hora', 'Panel → equipo', 'Al conectar, si hora_valida es falso', 'Hora del navegador (ms desde 1970) y '
          'huso horario (sección 6.9)']],
        [1100, 1500, 2700, 3537], size=16),
     CAP('Tabla 6.7. Mensajes del WebSocket (versión 1 del protocolo). Operaciones de cmd: «medir» y «detener» '
         '(operador), «calibrar» (operador, CU-01; la confirmación del técnico que pide CU-01 se hace en el '
         'equipo o con token), «piso» (técnico, con token, CU-10) y «ping».'),
     P('Ejemplo de instantánea (251 B; la misma información en binario ocuparía 53 B):'),
     CODE(['{"v":1,"tipo":"inst","seq":123456,"t_ms":3600123,"estado":"MIDIENDO",',
           ' "sesion":"A1B2-000123","prog":0.45,',
           ' "lp":[27.3,19.8,16.4,20.1,25.9,29.4,34.2],',
           ' "la":[27.9,20.2,16.9,20.4,26.2,29.9,34.8],',
           ' "marca":[0,0,1,0,0,0,0],"ver":"PARCIAL_APTA","perd":0,"bat":87}']),
     KT(['Método y recurso', 'Rol', 'Función', 'Observaciones'],
        [['GET /, /app.js, /app.css', 'Todos', 'Panel (CU-04)', 'Comprimido con gzip dentro de la imagen; la '
          'versión del firmware invalida la caché'],
         ['GET /ws', 'Todos', 'Canal WebSocket', 'Host y Origin verificados antes del cambio de protocolo; una '
          'quinta conexión (otra pestaña) recibe el cierre 1013 («reintentar más tarde»)'],
         ['GET /api/v1/estado', 'Todos', 'Estado, batería, calibración y versión', 'Respuesta inmediata desde '
          'la última instantánea'],
         ['GET /api/v1/sesiones?desde=…&hasta=…&cabina=…&cursor=…', 'Todos', 'Historial paginado (CU-06, HU-09)',
          '50 sesiones por página; T_XFER'],
         ['GET /api/v1/sesiones/{id} y …/informe', 'Todos', 'Detalle e informe HTML imprimible (CU-05, HU-08)',
          'Incluye el CRC-32 del archivo de sesión; T_XFER'],
         ['GET /api/v1/export.csv?desde=…&hasta=…', 'Todos', 'Exportación (CU-09, HU-12)', 'Una fila por sesión y '
          'una columna por banda, transferida en bloques; T_XFER'],
         ['POST /api/v1/login/desafio y /login', 'Técnico', 'Autenticación (sección 6.7)', 'Devuelve un token de '
          '128 bits con vencimiento'],
         ['GET / PUT /api/v1/config', 'Técnico', 'Límites, integración, Wi-Fi, hora (CU-07)', 'PUT solo en REPOSO; '
          'lo aplica T_APP'],
         ['GET /api/v1/diag', 'Técnico', 'Contadores, pilas, volcado de memoria', 'Diagnóstico de D4.8'],
         ['POST /api/v1/ota', 'Técnico', 'Imagen de firmware (CU-08, HU-11)', 'Solo en REPOSO; T_XFER '
          '(sección 6.8)'],
         ['Cualquier otro Host o ruta de detección de portal', 'Todos', 'Redirección', '302 hacia '
          'http://192.168.4.1/']],
        [2900, 900, 2300, 2737], size=16),
     CAP('Tabla 6.8. Recursos HTTP. Las respuestas son JSON salvo el panel, el informe y el CSV. Las operaciones '
         'de técnico llevan el token en un encabezado propio.'),
     H2('Estados, plazos y errores'),
     KT(['Elemento', 'Estados y transiciones', 'Plazos', 'Errores'],
        [['Conexión WebSocket', 'ABIERTA → (envío de «hola») ACTIVA → CERRADA', 'Sin pong en 10 s, > 2 s sin poder '
          'escribir o desasociación del cliente → CERRADA', 'Mensaje > 512 B: cierre 1009; versión desconocida: '
          'nack y «hola»'],
         ['Reconexión del panel', 'DESCONECTADO → reintento → ACTIVA', 'Espera de 1, 2, 4, 8 y luego 10 s',
          'Salto de seq: aviso en el panel'],
         ['Sesión de técnico', 'ANÓNIMO → DESAFÍO → TÉCNICO → ANÓNIMO; 3 fallas → BLOQUEADO', 'Desafío: 30 s; '
          'token: 15 min sin uso; bloqueo: 5 min, global y persistente', 'nack «rol»; HTTP 401 / 403'],
         ['Comando', 'Recibido → ack / nack', 'Identificadores recordados 60 s (últimos 16)', 'nack «estado», '
          '«ocupado», «formato»; HTTP 409 si el estado no lo admite'],
         ['Transferencia (T_XFER)', 'LIBRE → OCUPADA → LIBRE', 'Una a la vez; OTA sin datos durante 30 s → '
          'esp_ota_abort() → REPOSO', 'HTTP 503 con «reintentar en» si está ocupada; 413 si excede el tamaño']],
        [1700, 2700, 2500, 1937], size=16),
     CAP('Tabla 6.9. Máquina de estados, plazos y errores del protocolo.'),
     P('**JSON frente a binario.** El formato binario ocupa 4,7 veces menos, pero con 4 clientes la ocupación '
       'del canal a 6 Mbit/s baja solo de 3,7 % a 3,2 %, porque dominan las cabeceras y las balizas. JSON se lee '
       'en las herramientas del navegador, se extiende sin romper clientes y simplifica el panel y el servidor de '
       'gestión. La serialización se hace con un formateador propio sobre un búfer estático de tamaño acotado; '
       'los comandos recibidos, cortos y poco frecuentes, se interpretan con el componente cJSON de ESP-IDF, que '
       'usa memoria dinámica acotada (≈ 2 kB por mensaje de hasta 512 B).'),
     P('**Decisión D6.3:** protocolo JSON versionado sobre WebSocket para el tiempo real y API REST /api/v1 '
       'para consultas, descargas, configuración y OTA; el equipo es la única fuente de los niveles y del '
       'veredicto; secuencia, resincronización, comandos idempotentes con confirmación y roles por operación. '
       'Corrige H6.2 a H6.8.')])

# ───────────── 6.6 ─────────────
add([H1('6.6 Integración con el firmware de tiempo real'),
     P('El Capítulo 4 previó una tarea T_NET de prioridad 5 en el núcleo 0, avisada por notificación. Este '
       'capítulo la concreta: **T_NET es la tarea del servidor esp_http_server**, creada con core_id = 0, '
       'prioridad 5 y una pila de 6 kB. El servidor atiende todas sus conexiones en esa única tarea con '
       'select(), y las demás tareas le piden trabajo con httpd_queue_work(), que envía un datagrama a su socket de '
       'control. Por eso **ningún manejador de T_NET puede durar más de unos milisegundos**: mientras uno corre, '
       'no se publica nada. La Figura 6.4 muestra la secuencia.'),
     *FIGURA('cap6_secuencia.png', 16.5,
             'Figura 6.4. Secuencia de conexión del panel, medición iniciada desde el panel, pérdida del cliente '
             'y reconexión.'),
     H2('Publicación sin bloqueo'),
     B('**Instantáneas:** T_APP escribe la instantánea en el buzón mbx (xQueueOverwrite, D4.5) y, si no hay una '
       'publicación pendiente (bandera atómica), llama a httpd_queue_work(). La función de trabajo baja la '
       'bandera al empezar, lee mbx con xQueuePeek, serializa una vez y envía a cada cliente WebSocket. Si '
       'httpd_queue_work() falla (el buzón del socket de control tiene 6 lugares), T_APP baja la bandera y '
       'reintenta en el período siguiente; nunca usa la variante bloqueante.'),
     B('**Respuestas y eventos:** viajan por una cola nueva, q_net (T_APP → T_NET, 8 × 64 B), porque no pueden '
       'perderse; la misma función de trabajo la vacía. Si q_net se llena, T_APP marca un desborde y T_NET envía '
       '«hola» a todos los clientes de inmediato, que así recuperan el estado sin reconectarse.'),
     B('**Comandos:** T_NET los convierte en eventos de q_evt con espera nula; los eventos pasan de 32 a 64 B '
       'para llevar la cabina y las iniciales. Si la cola está llena responde «nack: ocupado». T_APP es la única '
       'que decide si un comando se admite en el estado actual (D4.3).'),
     B('**Transferencias largas:** el historial, el informe, el CSV y la OTA no corren en T_NET. Su manejador '
       'llama a httpd_req_async_handler_begin(), que copia el pedido, y lo entrega a una tarea nueva, **T_XFER** '
       '(núcleo 0, prioridad 4, pila de 8 kB, una transferencia a la vez). T_XFER pide los datos a T_STOR —la '
       'única dueña de la microSD (D4.5)— por una cola nueva, q_lect, y los recibe por un búfer de flujo de 4 kB. '
       'Un cliente lento demora solo a T_XFER; T_NET sigue publicando.'),
     H2('Clientes lentos o perdidos'),
     P('esp_http_server envía con send() bloqueante y un tiempo de espera de 5 s por defecto '
       '(send_wait_timeout). Un celular que se aleja dejaría a T_NET bloqueada hasta 5 s por trama. Por eso cada '
       'socket WebSocket usa una función de envío propia (httpd_sess_set_send_override) con MSG_DONTWAIT, y antes '
       'de cada trama T_NET consulta con select() y tiempo nulo si el socket es escribible. En lwIP eso exige más '
       'de TCP_SNDLOWAT = 2881 B libres y menos de 8 segmentos en cola (TCP_SNDQUEUELOWAT); como cada trama se '
       'envía en dos partes (cabecera y carga), el socket deja de ser escribible tras ≈ 4 tramas sin confirmar. '
       'Entonces la trama se descarta para ese cliente y se cuenta; si pasa más de 2 s sin poder escribir, o si '
       'un envío resulta parcial (lo que desincronizaría el flujo WebSocket), el cliente se cierra con '
       'httpd_sess_trigger_close(). El cierre llega a ≈ 2,9 s durante una medición y ≈ 6 s en REPOSO. Además, el '
       'evento WIFI_EVENT_AP_STADISCONNECTED cierra de inmediato los sockets de la dirección de ese cliente '
       '(esp_netif_dhcps_get_clients_by_mac), el ping de la Tabla 6.7 detecta los sockets medio abiertos, y la '
       'función close_fn quita el descriptor de la lista de clientes, porque los descriptores se reutilizan.'),
     H2('Latencia de extremo a extremo'),
     KT(['Etapa', 'Típico [ms]', 'Peor caso [ms]', 'Fuente'],
        [['Fin del bloque → T_DSP termina', '3,2', '6,3', 'R_DSP pesimista (Cap. 4)'],
         ['T_DSP → T_APP y respuesta de T_APP', '1,0', '3,6', 'Cap. 4, núcleo 0'],
         ['Publicación en T_NET', '5,0', '106,1', 'Respuesta de T_NET (Cap. 4)'],
         ['Serialización y envío por lwIP (4 clientes)', '1,0', '3,0', 'Supuesto (PU-COM-02)'],
         ['Acceso al canal y reintentos', '2,0', '15,0', 'Supuesto'],
         ['Celular en ahorro de energía', '20,0', '307,2', 'Supuesto: intervalo de escucha ≤ 3 balizas'],
         ['Navegador: decodificación y dibujo (60 Hz)', '8,0', '16,7', 'Un cuadro'],
         ['**Total**', '**40**', '**458**', '']],
        [3900, 1300, 1400, 2237], size=17, center_cols=(1, 2)),
     CAP('Tabla 6.10. Latencia desde el fin de una ventana de integración hasta su dibujo en el panel.'),
     P('El DTIM gobierna solo el tráfico de grupo: las tramas dirigidas a un celular que duerme se anuncian en el '
       'TIM de cada baliza y el celular las retira según su **intervalo de escucha**, que elige él [5]. Por eso el '
       'peor caso teórico es de 458 ms y la antigüedad del dato en el panel puede llegar a ≈ 0,7 s. Con la '
       'pantalla encendida y tráfico cada 235 ms, los celulares suelen mantener la radio despierta, lo que da la '
       'cifra típica de 40 ms. El período de actualización (234,7 ms) cumple RD-06 por construcción; para la '
       'latencia se adopta el criterio derivado **≤ 300 ms en el 99 % de las instantáneas con la pantalla '
       'encendida** (PU-COM-02), y el peor caso queda documentado.'),
     H2('Configuración y memoria'),
     KT(['Parámetro', 'Valor', 'Motivo'],
        [['core_id / task_priority / stack_size', '0 / 5 / 6144', 'T_NET del Capítulo 4'],
         ['max_open_sockets', '7', '4 WebSocket + 3 HTTP; las respuestas HTTP cierran la conexión'],
         ['CONFIG_LWIP_MAX_SOCKETS', '16 (por defecto 10)', '7 del servidor + 3 internos + DNS + margen'],
         ['lru_purge_enable', 'false', 'El contador de uso solo se actualiza al recibir: purgaría paneles '
          'que solo reciben'],
         ['send_wait_timeout / recv_wait_timeout', '2 s / 5 s', 'Para HTTP; los WebSocket usan envío sin bloqueo'],
         ['max_uri_handlers / uri_match_fn', '24 / httpd_uri_match_wildcard', 'Tabla 6.8 y rutas de detección de '
          'portal; /sesiones/{id}'],
         ['CONFIG_HTTPD_WS_SUPPORT y …_PRE_HANDSHAKE_CB_SUPPORT', 'y', 'WebSocket (desactivado por defecto) y '
          'verificación de Host y Origin antes del cambio de protocolo']],
        [3200, 2100, 3537], size=16),
     CAP('Tabla 6.11. Configuración de esp_http_server y lwIP.'),
     P('La memoria interna estimada para la red en el peor caso es de ≈ 144 kB (resumen_com.txt, sección 6): '
       'búferes y estructuras del Wi-Fi y de WPA2/WPA3 (≈ 69 kB), lwIP (≈ 5 kB), siete sockets con su búfer de '
       'envío lleno y la ventana de recepción de la OTA (≈ 46 kB), las pilas de T_NET y T_XFER (≈ 16 kB), cJSON y '
       'los búferes propios (≈ 9 kB). Todo queda en RAM interna, como exige D4.3, y se verifica con '
       'heap_caps_get_minimum_free_size() durante 8 h con carga (PU-COM-09).'),
     P('**Decisión D6.4:** T_NET es la tarea de esp_http_server (núcleo 0, prioridad 5, 6 kB) y solo atiende '
       'operaciones cortas; T_XFER (prioridad 4, 8 kB) hace las transferencias largas. Publicación por mbx con '
       'httpd_queue_work() y reintento; respuestas y eventos por q_net; comandos a q_evt sin espera; lecturas de '
       'la microSD por T_STOR; envíos WebSocket sin bloqueo, con descarte y cierre de clientes perdidos.')])

# ───────────── 6.7 ─────────────
add([H1('6.7 Seguridad'),
     P('El equipo no guarda datos de pacientes, pero su resultado respalda una decisión clínica (si la cabina '
       'es apta), su calibración tiene valor metrológico y su firmware puede reemplazarse por la red. El modelo '
       'de amenazas considera a cualquier persona del servicio dentro del alcance del Wi-Fi, con o sin la clave '
       'de la red, y a un sitio web externo abierto en el mismo celular; deja fuera el acceso físico prolongado '
       'al equipo [9, 10].'),
     KT(['Activo', 'Amenaza', 'Control', 'Riesgo residual'],
        [['Medición en curso', 'Un cliente con la clave detiene o reinicia la medición', 'Solo clientes '
          'asociados; Host y Origin verificados; la sesión interrumpida queda registrada como tal', 'Aceptado: '
          'interrupción visible, sin resultado falso'],
         ['Configuración, límites y calibración', 'Cambio no autorizado', 'PIN de técnico, token con vencimiento, '
          'solo en REPOSO, registro de cambios', 'Medio con WPA2 o con un AP falso (ver texto)'],
         ['Firmware', 'Imagen maliciosa o dañada', 'Imagen firmada y verificada antes de arrancarla; token',
          'Bajo por la red; el acceso físico queda fuera del alcance'],
         ['Credenciales del técnico', 'Captura del token o del intercambio de autenticación', 'El PIN nunca viaja '
          '(desafío y respuesta); token asociado a la dirección IP', 'Medio (ver texto)'],
         ['Disponibilidad del panel', 'Desautenticaciones falsas; saturación de clientes', 'PMF; ≤ 4 clientes; la '
          'medición no depende de la red', 'Aceptado'],
         ['Navegador del usuario', 'Un sitio externo usa el equipo desde el mismo celular, incluida la '
          'revinculación de DNS', 'Solo se aceptan Host y Origin 192.168.4.1; token en un encabezado propio '
          '(fuerza la verificación previa del navegador)', 'Bajo'],
         ['Contenido almacenado', 'Lectura de la flash por USB (contraseña, K)', 'Fuera del alcance del '
          'prototipo; en producción, cifrado de la flash y arranque seguro', 'Documentado'],
         ['Privacidad', 'Datos personales en las sesiones', 'Sin pacientes; el operador se registra con '
          'iniciales [13]', 'Bajo']],
        [1600, 2100, 3000, 2137], size=16),
     CAP('Tabla 6.12. Modelo de amenazas simplificado.'),
     H2('Clave de la red'),
     P('Cada equipo sale con una contraseña aleatoria de 12 caracteres sobre un alfabeto de 32 símbolos sin '
       'caracteres ambiguos (60 bits), impresa en la etiqueta junto a un código QR que configura la red en el '
       'celular. Un ataque de diccionario fuera de línea contra WPA2, a 2·10⁶ intentos por segundo, tardaría en '
       'promedio ≈ 9·10³ años. La contraseña, la sal del PIN y el PIN de fábrica se generan en la primera puesta '
       'en marcha con esp_random() **con la radio encendida**, condición para que sea un generador aleatorio '
       'verdadero, y se guardan en la partición cal, que no se borra (sección 6.8). El técnico puede cambiar la '
       'contraseña (CU-07). El SSID incluye los últimos dígitos de la dirección MAC.'),
     H2('Autenticación del técnico'),
     P('El PIN de 6 dígitos no viaja por la red. El equipo guarda K = PBKDF2-HMAC-SHA256(PIN, sal, 2000) en NVS '
       '[11]; al iniciar sesión envía un desafío aleatorio de 128 bits, el panel responde HMAC-SHA256(K, '
       'desafío ‖ nonce del cliente) y el equipo devuelve un token aleatorio de 128 bits, asociado a la dirección '
       'IP del cliente, que vence a los 15 min sin uso. El cálculo se hace en JavaScript propio de ≈ 3 kB, porque '
       '**la API Web Crypto no está disponible en páginas servidas por HTTP** fuera de localhost: no son un '
       'contexto seguro [12]; crypto.getRandomValues() sí lo está y genera el nonce. El bloqueo de 5 min tras 3 '
       'fallas es global (no por cliente) y persiste entre reinicios: se guarda en NVS al volver a REPOSO, porque '
       'durante una medición no se escribe la flash (D4.3). Así, un ataque en línea tarda en promedio ≈ 1,6 años; '
       'con 4 dígitos serían ≈ 6 días.'),
     P('**Limitaciones del esquema.** (a) Con WPA2-PSK, quien conoce la clave de la red y captura el saludo de '
       'otra estación descifra su tráfico: puede tomar el token y usarlo mientras esté vigente, o tomar el desafío '
       'y la respuesta y probar fuera de línea el millón de PINes en minutos. (b) WPA3-SAE impide la escucha '
       'pasiva, pero quien conoce la contraseña puede montar un punto de acceso falso con el mismo nombre, '
       'interponerse y obtener lo mismo; el modo de transición permite además forzar WPA2 [16]. (c) K equivale '
       'a la contraseña: quien lea la flash puede autenticarse sin conocer el PIN. Por eso el riesgo de las '
       'credenciales del técnico se califica como **medio** con cualquier modo. Lo acotan la opción «solo WPA3», '
       'cambiar la contraseña de la red cuando cambia el personal y operar como técnico solo cuando hace falta. '
       'En una versión de producción, un PAKE (SRP o SPAKE2) o HTTPS con un certificado propio verificado por una '
       'aplicación de gestión resolverían el problema.'),
     H2('¿Por qué no HTTPS?'),
     P('Un servidor HTTPS embebido exigiría un certificado autofirmado —que los navegadores rechazan con una '
       'advertencia en cada conexión, inaceptable para el usuario objetivo— o una autoridad propia instalada en '
       'cada celular. Además, cada sesión TLS consume del orden de 30 a 40 kB de RAM interna. Dentro de un '
       'enlace cifrado con WPA2/WPA3, con desafío para el técnico y verificación de Host y Origin, el riesgo '
       'residual de la Tabla 6.12 se considera aceptable para el prototipo.'),
     P('**Decisión D6.5:** red WPA2/WPA3 con PMF y contraseña aleatoria por equipo; técnico autenticado por '
       'desafío y respuesta con token de 15 min; Host y Origin verificados; HTTP sin TLS dentro del enlace '
       'cifrado, con el riesgo residual documentado; sin datos de pacientes.')])

# ───────────── 6.8 ─────────────
add([H1('6.8 Actualización OTA'),
     KT(['Partición', 'Tipo', 'Desplazamiento', 'Tamaño', 'Uso'],
        [['nvs', 'datos / nvs', '0x9000', '24 kB', 'Configuración, K del técnico, contador de sesiones'],
         ['otadata', 'datos / ota', '0xF000', '8 kB', 'Selección de la imagen de arranque'],
         ['cal', 'datos / nvs', '0x11000', '16 kB', 'Calibración, piso, C_b y datos de fábrica: nunca se borra '
          'automáticamente'],
         ['(libre)', '—', '0x15000', '44 kB', 'Alineación de las aplicaciones a 64 kB'],
         ['factory', 'app / factory', '0x20000', '4 MB', 'Imagen de recuperación (la entregada, firmada)'],
         ['ota_0', 'app / ota_0', '0x420000', '4 MB', 'Imagen A'],
         ['ota_1', 'app / ota_1', '0x820000', '4 MB', 'Imagen B'],
         ['coredump', 'datos / coredump', '0xC20000', '64 kB', 'Volcado de la última falla (D4.8)'],
         ['(libre)', '—', '0xC30000', '3,8 MB', 'Reserva']],
        [1300, 1700, 1500, 1100, 3237], size=16, center_cols=(2, 3)),
     CAP('Tabla 6.13. Tabla de particiones propuesta para la flash de 16 MB. Las particiones de aplicación de '
         '4 MB dejan margen para que la imagen, estimada en 1,6 MB, crezca hasta 3 MB (75 %) sin cambiar la '
         'tabla, lo que obligaría a reprogramar por USB.'),
     P('La calibración vive en una partición NVS propia porque el patrón habitual de ESP-IDF borra la partición '
       '«nvs» cuando nvs_flash_init() detecta un formato nuevo o falta de páginas; separarla garantiza el '
       'criterio de HU-11 («conserva la calibración»). Su esquema es aditivo: las claves existentes no cambian '
       'de significado y la imagen factory, aunque sea anterior, lee las que conoce. Además, se guarda una copia '
       'con CRC en la microSD.'),
     H2('Procedimiento'),
     B('**Precondiciones:** estado REPOSO (T_APP pasa a ACTUALIZANDO, D4.3), token de técnico y batería > 50 % '
       'o USB conectado (CU-08). La seguridad ante un corte la da el esquema de dos imágenes; la condición de '
       'batería evita empezar una actualización que el corte por batería baja interrumpiría.'),
     B('**Recepción:** POST /api/v1/ota, atendido por T_XFER en bloques de 4 kB con httpd_req_recv(); '
       'esp_ota_begin() con OTA_WITH_SEQUENTIAL_WRITES borra cada sector antes de escribirlo, sin un borrado '
       'largo inicial. Con una imagen de 1,6 MB, la actualización tarda ≈ 30 s, dominados por el borrado y la '
       'escritura de la flash (≈ 22 s); T_NET sigue libre y publica el avance por WebSocket. Cada borrado '
       'detiene la caché de ambos núcleos durante decenas de milisegundos: por eso la OTA solo ocurre en REPOSO. '
       'Si no llegan datos durante 30 s, esp_ota_abort() descarta lo recibido y T_APP vuelve a REPOSO.'),
     B('**Verificación:** esp_ota_end() comprueba el encabezado, el chip, el tamaño y el SHA-256. Con '
       'CONFIG_SECURE_SIGNED_APPS_NO_SECURE_BOOT y el esquema RSA de Secure Boot V2, la firma se verifica al '
       'actualizar —con este esquema, no en cada arranque— contra la clave pública de la imagen en ejecución, '
       'de modo que la imagen factory también se firma. La imagen debe tener una versión mayor que la actual; '
       'degradar exige confirmación explícita del técnico.'),
     B('**Clave de firma:** la clave privada se guarda fuera de línea, con dos copias cifradas. Si se pierde, '
       'el equipo ya no acepta actualizaciones y solo puede reprogramarse por USB; el prototipo no prevé rotar '
       'la clave.'),
     B('**Arranque y autodiagnóstico:** con CONFIG_BOOTLOADER_APP_ROLLBACK_ENABLE, la imagen nueva arranca en '
       'estado ESP_OTA_IMG_PENDING_VERIFY. El firmware arma un temporizador propio de 60 s y verifica: la '
       'partición cal y su CRC, el montaje de la microSD (si hay tarjeta), 1 s de captura I2S con datos '
       'variables, un vector de prueba del banco de filtros (tono de 1 kHz sintético: banda de 1 kHz dentro de '
       '±0,05 dB de lo esperado), el punto de acceso y la memoria libre. Si todo es correcto llama a '
       'esp_ota_mark_app_valid_cancel_rollback(); si algo falla o vence el temporizador, a '
       'esp_ota_mark_app_invalid_rollback_and_reboot(). Un reinicio por falla o por el perro guardián durante la '
       'verificación también vuelve a la imagen anterior.'),
     B('**Compatibilidad de NVS:** cada versión lee las claves de las anteriores y no cambia el significado de '
       'una clave existente; las claves nuevas se agregan con un número de esquema. Así, tras una reversión, la '
       'imagen anterior sigue leyendo la configuración.'),
     B('**Recuperación de fábrica:** con CONFIG_BOOTLOADER_FACTORY_RESET y CONFIG_BOOTLOADER_OTA_DATA_ERASE, '
       'mantener presionados MENÚ y el pulsador de encendido durante ≈ 6 s desde el encendido (el encendido '
       'sostiene la alimentación hasta que el firmware toma POWER_HOLD; el cargador de arranque cuenta 5 s) borra '
       'otadata, arranca la imagen factory y borra solo la partición «nvs» '
       '(CONFIG_BOOTLOADER_DATA_FACTORY_RESET = "nvs"): la calibración se conserva y el PIN vuelve al de fábrica.'),
     P('La antirreversión por eFuse (CONFIG_BOOTLOADER_APP_ANTI_ROLLBACK) y el arranque seguro por hardware '
       'son irreversibles y no se habilitan en el prototipo; se documentan para una versión de producción.'),
     P('**Decisión D6.6:** particiones factory, ota_0 y ota_1 de 4 MB y partición cal separada; imágenes '
       'firmadas, OTA en T_XFER con abandono por tiempo, reversión automática con autodiagnóstico antes de '
       'confirmar, NVS compatible entre versiones y recuperación de fábrica por pulsadores.')])

# ───────────── 6.9 ─────────────
add([H1('6.9 Sincronización de fecha y hora'),
     P('La fecha y la hora fechan las sesiones (RD-09), la calibración y su vencimiento (RD-10). El equipo no '
       'tiene internet, de modo que no puede usar NTP, y el diseño del Capítulo 5 no incluye un reloj de tiempo '
       'real: al apagarse por el enclavamiento (D5.4), el ESP32-S3 queda sin alimentación y **pierde la hora**. '
       'Este capítulo resuelve la sincronización por la red y propone al Capítulo 5 el complemento de hardware.'),
     B('**Complemento de hardware (adoptado en el Capítulo 5, v0.2.1):** un RTC de nanopotencia con cristal de 32 kHz y conmutación a una '
       'entrada de respaldo (por ejemplo, la familia RV-3028-C7, del orden de 45 nA según su fabricante): la '
       'alimentación principal desde 3V3_D y el respaldo desde la celda. Con el equipo apagado el RTC pasa a '
       'respaldo y deshabilita su interfaz I2C, de modo que los pull-ups, alimentados desde 3V3_D, no realimentan '
       'nada. El consumo apagado sube de 12,6 µA a ≈ 12,65 µA. Al cambiar la celda la hora se pierde y se aplica '
       'la sincronización. GPIO13, que estaba reservado como MISO para un táctil SPI, pasa a ser SDA y GPIO21, '
       'antes reinicio de la pantalla, pasa a ser SCL; el táctil futuro será capacitivo por I2C y la pantalla se '
       'reinicia por comando (Tabla 5.7). El dueño del bus es T_MON.'),
     B('**Sincronización desde el navegador:** «hola» informa hora_valida; si es falso, el panel envía la hora '
       'del celular. El equipo la acepta automáticamente solo si su hora no es válida, si no es anterior a la '
       'última sesión guardada y si cae entre la fecha de compilación del firmware y diez años después. Con hora '
       'válida, ajustarla —incluso hacia atrás, para corregir un celular con la fecha adelantada— exige el token '
       'de técnico y queda registrado. Así nadie puede atrasar el reloj para ocultar una calibración vencida.'),
     B('**Sin hora válida:** la sesión se guarda con el tiempo desde el arranque y el número de arranque, '
       'marcada como «hora no confirmada»; si la hora se sincroniza antes de apagar, el equipo la reconstruye.'),
     P('Mientras el equipo está encendido, el cristal principal de 40 MHz (±10 ppm) deriva ≈ 0,9 s por día; un '
       'RTC con cristal de ±5 ppm, ≈ 2,6 min por año. **Decisión D6.7:** sincronización desde el navegador con '
       'las reglas anteriores y RTC por I2C con respaldo en la celda (Capítulo 5).')])

# ───────────── 6.10 ─────────────
add([H1('6.10 Integración con el servidor de gestión'),
     P('El servidor Python del prototipo se adapta (tarea 5.1 del anteproyecto) al modelo de consulta: cuando '
       'la PC se conecta al punto de acceso, pide GET /api/v1/sesiones?cursor=… desde la última sesión '
       'sincronizada y descarga cada sesión cerrada con su CRC-32. El identificador de sesión combina el '
       'identificador del equipo y un contador persistente (que se escribe en NVS al volver a REPOSO), de modo '
       'que una sesión repetida no se duplica. El servidor **no recalcula niveles**: guarda el L_eq por banda y el '
       'veredicto que emitió el equipo, y si alguna vez promedia sesiones lo hace en energía. El puente serie, la '
       'simulación de estados y la copia de los límites (H6.2, H6.3, H6.5) desaparecen. El informe se genera en '
       'el equipo como HTML imprimible y, si el servidor está disponible, también en PDF. Una PC con una sola '
       'interfaz Wi-Fi pierde internet mientras está conectada al equipo; con Ethernet y Wi-Fi a la vez, no.'),
     P('**Decisión D6.8:** el servidor de gestión sincroniza por consulta incremental e idempotente y no '
       'recalcula niveles ni veredictos. Junto con D4.7, corrige H6.1.')])

# ───────────── 6.11 ─────────────
add([H1('6.11 Buses internos'),
     P('Las comunicaciones del equipo incluyen los buses que unen al microcontrolador con sus periféricos. '
       'Cada uno tiene una sola tarea dueña, en línea con D4.5, y su capacidad supera holgadamente la demanda:'),
     KT(['Bus', 'Periférico', 'Reloj', 'Demanda y ocupación', 'Dueño'],
        [['I2S', 'Micrófono ICS-43434', '3,072 MHz', 'Síncrono y de ocupación fija: 1,152 Mbit/s útiles por DMA',
          'T_DSP'],
         ['SPI2 (DMA)', 'Pantalla TFT', '10–40 MHz según el controlador', 'Siete barras ≈ 25 % del área: 7,7 ms a '
          '40 MHz o 30,7 ms a 10 MHz cada 234,7 ms (3 a 13 %)', 'T_UI'],
         ['SDMMC 1 bit', 'microSD', '20–40 MHz', 'Sesión de ≈ 2 kB: < 1 ms de bus; dominan la latencia de la '
          'tarjeta y la FAT (10 a 100 ms)', 'T_STOR'],
         ['I2C', 'RTC; táctil futuro', '400 kHz', 'Lectura de la hora: 0,23 ms al arrancar y al '
          'sincronizar', 'T_MON'],
         ['USB Serial/JTAG', 'PC de desarrollo', '12 Mbit/s', 'Carga del firmware, consola y volcado de '
          'memoria; no transporta mediciones', '—'],
         ['UART0', 'Puntos de prueba', '115 200 bit/s', 'Registros del cargador de arranque', '—']],
        [1400, 1500, 1500, 3300, 1137], size=16),
     CAP('Tabla 6.14. Buses internos, demanda y tarea dueña.')])

# ───────────── 6.12 ─────────────
add([H1('6.12 Plan de verificación'),
     KT(['ID', 'Procedimiento', 'Criterio de aceptación', 'Verifica'],
        [['PU-COM-01', 'RSSI del equipo dentro y fuera de al menos una cabina real, con el celular a 1, 3 y 5 m, '
          'a 8,5, 13 y 19,5 dBm', 'Atenuación medida; margen ≥ 10 dB a 3 m con 13 dBm o ajuste de D6.2',
          'D6.2 · CU-04 · HU-07'],
         ['PU-COM-02', 'Latencia: t_ms de cada instantánea frente a la hora de recepción en el navegador (desfase '
          'estimado con ping), 30 min con 1 y 4 clientes y la pantalla encendida', 'Período ≤ 250 ms; latencia '
          '≤ 300 ms en el 99 %', 'RD-06 · D6.4'],
         ['PU-COM-03', 'Un cliente se aleja o se apaga sin cerrar, con otros 3 clientes; una quinta pestaña',
          'Los demás reciben ≥ 99 % de las instantáneas; cierre del perdido ≤ 5 s midiendo y ≤ 15 s en REPOSO; la '
          'quinta recibe 1013', 'D6.4 · CU-04'],
         ['PU-COM-04', 'Carga de comunicaciones durante la medición (= PU-RT-04): 4 clientes, CSV, historial y '
          'reconexiones', '0 desbordes; C de T_DSP sin cambios; publicación sin interrupciones durante la descarga',
          'RD-07 · D4.6, D6.4'],
         ['PU-COM-05', 'Mensajes inválidos: JSON mal formado, campos faltantes, > 512 B, versión desconocida, '
          'comandos repetidos, operaciones de técnico sin token', 'Sin reinicio; nack o cierre según la Tabla 6.9; '
          'un id repetido no se ejecuta dos veces', 'D6.3'],
         ['PU-COM-06', 'Panel en 2 versiones de Android (una con DNS privado), 1 de iOS y una PC, con datos móviles '
          'activos y con la pantalla apagada 5 min', 'Comportamiento documentado; panel operativo en todos '
          'siguiendo el manual', 'D6.2 · EN-11'],
         ['PU-COM-07', 'PIN erróneo y bloqueo tras reinicio, token vencido, Host u Origin ajenos, revinculación de '
          'DNS, /config sin token; captura del tráfico con otra estación', 'Rechazos y bloqueo según la Tabla 6.9; '
          'el PIN no aparece en la captura', 'D6.5'],
         ['PU-COM-08', 'OTA (amplía EN-10): imagen sin firmar, con otra clave, truncada, de otro chip, versión '
          'anterior; corte en 5 puntos; reinicio durante el autodiagnóstico; abandono por tiempo; recuperación '
          'de fábrica', 'Siempre arranca una imagen válida; calibración conservada; vuelta a REPOSO', 'RD-11 · '
          'D6.6 · HU-11'],
         ['PU-COM-09', 'Memoria interna mínima durante 8 h con 4 clientes y una OTA en reposo; pilas de T_NET y '
          'T_XFER', '≥ 40 kB libres; deriva ≤ 1 kB/h; ≥ 25 % de pila libre', 'D6.4'],
         ['PU-COM-10', 'Hora: 24 h apagado con RTC; cambio de celda; arranque sin hora; intento de atrasar el reloj '
          'sin token', 'Deriva ≤ 1 s; sesión marcada; ajuste rechazado', 'D6.7 · RD-10'],
         ['PU-COM-11', 'Sincronización del servidor de gestión: sesiones repetidas y L_eq frente al equipo',
          'Sin duplicados; diferencia ≤ 0,01 dB', 'D6.8 · H6.1'],
         ['PU-COM-12', 'Historial con 1000 sesiones: paginación y filtro por cabina; informe HTML; CSV',
          'Lista completa y ordenada; informe con los campos de HU-08; CSV con una fila por sesión y una columna '
          'por banda; CRC correcto', 'RD-09 · CU-05, CU-06, CU-09 · HU-08, HU-09, HU-12'],
         ['EN-07', 'Autonomía con 4 clientes recibiendo', 'Ver anteproyecto', 'RD-08 · D6.2'],
         ['EN-09', 'Piso de ruido con Wi-Fi activo e inactivo, con 4 clientes recibiendo', 'Diferencia ≤ 1 dB',
          'D6.2 · Ambiente']],
        [1150, 3550, 2600, 1537], size=16),
     CAP('Tabla 6.15. Pruebas de comunicaciones y ensayos del anteproyecto relacionados.')])

# ───────────── 6.13 ─────────────
add([H1('6.13 Conclusiones y decisiones'),
     KT(['ID', 'Decisión', 'Justificación', 'Verificación'],
        [['D6.1', 'Punto de acceso propio con HTTP y WebSocket; panel dentro de la imagen', 'Sin dependencia de '
          'la red institucional ni de una PC (H6.9); navegador estándar', 'PU-COM-06'],
         ['D6.2', 'WPA2/WPA3 con PMF, país AR, canal fijo, 13 dBm, DTIM = 1, ≤ 4 clientes; radio solo cambia en '
          'REPOSO', 'Margen hasta ≈ 32 dB de atenuación a 3 m; la medición no depende del enlace; ≈ 7 mA de '
          'transmisión', 'PU-COM-01, EN-07, EN-09'],
         ['D6.3', 'JSON versionado por WebSocket y API REST /api/v1; el equipo, única fuente del veredicto; '
          'estados, plazos y roles definidos', 'Corrige H6.2 a H6.8; ocupación del canal del 3,7 %', 'PU-COM-05, 12'],
         ['D6.4', 'T_NET = tarea de esp_http_server; T_XFER para transferencias; mbx + httpd_queue_work, q_net, '
          'q_lect; envío sin bloqueo', 'Ninguna descarga ni cliente lento detiene la publicación; latencia típica '
          '40 ms', 'PU-COM-02 a 04, 09'],
         ['D6.5', 'Contraseña aleatoria por equipo; PIN por desafío y token; Host y Origin; HTTP sin TLS', 'Modelo '
          'de amenazas; riesgo residual medio documentado', 'PU-COM-07'],
         ['D6.6', 'factory + ota_0/ota_1, partición cal, firma, reversión con autodiagnóstico, recuperación de '
          'fábrica', 'RD-11 y HU-11', 'PU-COM-08, EN-10'],
         ['D6.7', 'Hora desde el navegador con reglas; RTC por I2C con respaldo (Cap. 5)', 'Fechas válidas '
          'para RD-09 y RD-10 sin internet', 'PU-COM-10'],
         ['D6.8', 'Servidor de gestión por consulta incremental, sin recalcular', 'Con D4.7, elimina el sesgo de '
          'H6.1', 'PU-COM-11']],
        [700, 3600, 2800, 1737], size=16),
     CAP('Tabla 6.16. Decisiones de diseño del capítulo y su verificación.'),
     H2('Pendientes'),
     B('Medir la atenuación de cabinas reales (PU-COM-01) lo antes posible: es el principal riesgo del capítulo '
       'y condiciona la potencia de transmisión y las instrucciones de uso.'),
     B('Elegir el táctil I2C, si se incorpora, y confirmar con la hoja de datos el consumo del RTC en respaldo.'),
     B('Medir la memoria, las pilas, el tiempo de serialización y el intervalo de escucha reales (PU-COM-02 y 09) '
       'y ajustar las Tablas 6.10 y 6.11.'),
     H2('Historial de revisión'),
     KT(['Versión', 'Cambios'],
        [['0.1', 'Borrador inicial.'],
         ['0.2', 'Revisión con tres revisores independientes (técnico de comunicaciones, trazabilidad y evaluador '
          'académico): tarea T_XFER para transferencias largas (el servidor tiene una sola tarea); reintento de '
          'httpd_queue_work; envío sin bloqueo con MSG_DONTWAIT y cierre ante envío parcial; umbrales reales de '
          'lwIP (TCP_SNDQUEUELOWAT); ping, desasociación y close_fn; purga LRU desactivada; 16 sockets de lwIP; '
          'DTIM corregido y latencia de peor caso con intervalo de escucha; Host y Origin con redirección y '
          'revinculación de DNS; riesgo de credenciales medio también con WPA3 y AP falso; generación de claves '
          'con la radio encendida; recuperación de fábrica con OTA_DATA_ERASE; firma de la imagen factory y '
          'custodia de la clave; abandono de OTA por tiempo; RTC con respaldo sin realimentación; ≈ 7 mA de '
          'transmisión sumados a RD-08; capas, comparación cuantitativa, máquina de estados del protocolo, roles '
          'por operación, marco regulatorio; PU-COM-12 y casos nuevos; citas, siglas y figuras separadas. '
          'Registro: revision_egm/registro_cap6_v0.2.md.'],
         ['0.2.1', 'Aprobación del autor: RTC incorporado al hardware (Capítulo 5 v0.2.1); cambios propagados al '
          'anteproyecto, al anexo de Ingeniería de Software v0.5 y a los Capítulos 4 (v0.2.2) y 5.']],
        [1100, 7737], size=17),
     H1('Referencias del capítulo'),
     *[P(r, size=20, align='left') for r in [
         '[1] Kurose, J. F.; Ross, K. W. Computer Networking: A Top-Down Approach, 8.ª ed. Pearson, 2021.',
         '[2] Espressif Systems. ESP-IDF Programming Guide v5.4: Wi-Fi, esp_http_server, lwIP, OTA, Secure Boot V2 '
         'y Partition Tables; y código fuente de ESP-IDF v5.4.',
         '[3] Fette, I.; Melnikov, A. RFC 6455 — The WebSocket Protocol. IETF, 2011.',
         '[4] Fielding, R.; Nottingham, M.; Reschke, J. RFC 9110 — HTTP Semantics. IETF, 2022.',
         '[5] IEEE Std 802.11-2020. Wireless LAN Medium Access Control (MAC) and Physical Layer (PHY) '
         'Specifications.',
         '[6] Wi-Fi Alliance. WPA3 Specification, versión 3.x.',
         '[7] Espressif Systems. ESP32-S3 Series Datasheet y ESP32-S3-WROOM-1 Datasheet (características de RF y '
         'certificaciones).',
         '[8] Friis, H. T. A Note on a Simple Transmission Formula. Proceedings of the IRE, 34(5), 1946.',
         '[9] OWASP. Internet of Things Top 10, 2018.',
         '[10] ETSI EN 303 645. Cyber Security for Consumer Internet of Things: Baseline Requirements, 2020.',
         '[11] Krawczyk, H.; Bellare, M.; Canetti, R. RFC 2104 — HMAC: Keyed-Hashing for Message Authentication; '
         'Moriarty, K. et al. RFC 8018 — PKCS #5: Password-Based Cryptography Specification v2.1.',
         '[12] W3C. Secure Contexts y Web Cryptography API.',
         '[13] República Argentina. Ley 25.326 de Protección de los Datos Personales.',
         '[14] IEC 61672-1:2013. Electroacoustics — Sound level meters — Part 1: Specifications (definición del '
         'nivel equivalente).',
         '[15] Ente Nacional de Comunicaciones (ENACOM). Reglamento de homologación de equipos de '
         'telecomunicaciones y normas técnicas para sistemas de espectro ensanchado en la banda de 2,4 GHz.',
         '[16] Vanhoef, M.; Ronen, E. Dragonblood: Analyzing the Dragonfly Handshake of WPA3 and EAP-pwd. IEEE '
         'Symposium on Security and Privacy, 2020.']]])

ensamblar(TPL, body, FIGURA, OUT)
print('OK', OUT)
