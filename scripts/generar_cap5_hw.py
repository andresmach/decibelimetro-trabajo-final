#!/usr/bin/env python3
"""Capítulo 5 — Diseño de hardware: alimentación, micrófono, PCB y gabinete (v0.2).

Uso (desde anteproyecto/):
  python3 -I scripts/generar_cap5_hw.py "../ModeloAnteproyecto(1).docx" figuras capitulos/Cap5_Hardware.docx

Cifras: hw/resultados/resumen_hw.txt (hw/analisis_potencia.py).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from docx_xml import P, B, H2  # noqa: E402
from cap_common import H1, PB, CAP, EQ, KT, Figuras, ensamblar  # noqa: E402

TPL, FIG, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
FIGURA = Figuras(FIG, 'C5')
VERSION = '0.2 (revisada con el método Elephant–Goldfish)'

body = []
add = body.extend

# ───────────── Portada ─────────────
add([P('', after=600),
     P('Capítulo 5', size=40, bold=True, align='center', color='1E5E9F', after=120),
     P('Diseño de Hardware', size=36, bold=True, align='center', color='1E5E9F', after=200),
     P('Alimentación autónoma, cadena del micrófono, circuito impreso y gabinete', size=28,
       bold=True, align='center', after=400),
     P('Analizador autónomo de ruido ambiente por bandas de octava para la verificación de cabinas '
       'audiométricas según ISO 8253-1', size=24, align='center', after=1200),
     P('**Autor:** Andrés Machtey', size=24, align='left', after=100),
     P('**Director propuesto:** Esp. Víctor Valotto (FIUNER)', size=24, align='left', after=100),
     P(f'**Versión:** {VERSION} · Noviembre de 2026', size=24, align='left', after=100),
     P('**Material reproducible:** hw/analisis_potencia.py, hw/graficos_hw.gp, hw/resultados/ y '
       'scripts/diagrama_hw.py', size=20, align='left', after=100),
     PB()])

# ───────────── Siglas ─────────────
add([H1('Siglas y convenciones'),
     KT(['Sigla', 'Significado', 'Sigla', 'Significado'],
        [['LDO', 'Regulador lineal de baja caída', 'PSRR / PSR', 'Rechazo al rizado de la alimentación'],
         ['OCV', 'Tensión a circuito abierto de la celda', 'SoC', 'Estado de carga de la batería'],
         ['CC', 'Líneas de configuración del conector USB-C', 'ESD / TVS', 'Descarga electrostática / diodo supresor'],
         ['ADC', 'Conversor analógico-digital', 'GPIO', 'Entrada/salida de propósito general'],
         ['I2S', 'Bus serie de audio digital', 'SPI / SDMMC', 'Bus serie / controlador de tarjetas SD'],
         ['PCB', 'Circuito impreso', 'LGA', 'Land Grid Array: contactos planos en la cara inferior'],
         ['NTC', 'Termistor de coeficiente negativo', 'EMC', 'Compatibilidad electromagnética'],
         ['FMEA', 'Análisis de modos de falla y efectos', 'PFM', 'Modulación por frecuencia de pulsos (carga liviana)'],
         ['BOM', 'Lista de materiales', 'PSRAM', 'RAM externa del módulo']],
        [1300, 3119, 1300, 3118], size=17),
     P('Los identificadores RD, EN, CU, D3.x y D4.x remiten al anteproyecto, al anexo de Ingeniería de Software y a '
       'los Capítulos 3 y 4; las pruebas nuevas son **PU-HW-xx**, los hallazgos **H5.x** y las decisiones **D5.x**. '
       '**Todos los consumos son supuestos** tomados de hojas de datos o de práctica habitual, elegidos del lado '
       'conservador; se reemplazan por mediciones (PU-HW-02, EN-07). Los números de parte son candidatos que se '
       'confirman al capturar el esquemático (entregable E4). En las tablas, "modo medición" designa el estado '
       'del equipo, no un valor medido.', size=20)])

# ───────────── 5.1 ─────────────
add([H1('5.1 Enfoque del capítulo'),
     P('Este capítulo analiza el proyecto desde el **diseño de hardware** de sistemas embebidos: la alimentación a '
       'batería y su autonomía, la carga, el encendido y el apagado, la cadena del micrófono, la asignación de '
       'pines, el circuito impreso, el gabinete, el análisis de fallas y la normativa. Parte del análisis del '
       'prototipo del curso de DSP, armado sobre una placa de desarrollo y un protoboard, y llega a una '
       'arquitectura de hardware propia, justificada con cálculos reproducibles [11, 12]. Al tratarse de un diseño '
       'preliminar, el esquemático completo y el PCB son el entregable E4; aquí se fijan la arquitectura, los '
       'cálculos y las decisiones que los condicionan.'),
     H2('Requisitos que condicionan el hardware'),
     KT(['Requisito', 'Enunciado (anteproyecto)', 'Consecuencia para el hardware'],
        [['RD-03', 'Ruido propio por banda ≥ 5 dB bajo el límite ISO', 'Micrófono de bajo ruido; alimentación '
          'del micrófono sin rizado que se sume al piso'],
         ['RD-04', 'Hasta ≥ 100 dB SPL sin saturar', 'Sobrecarga acústica del micrófono ≥ 110 dB SPL'],
         ['RD-08', 'Autonomía ≥ 8 h con Wi-Fi; carga ≤ 4 h por USB-C', 'Capacidad de la celda, regulador, corriente '
          'de carga, comportamiento con el equipo apagado'],
         ['RD-09', 'Sesiones sin corrupción ante cortes', 'Aviso de pérdida de alimentación (/PGOOD, detector de '
          'caída de tensión) y reserva en el riel'],
         ['RD-12', 'Guardado de −10 a 50 °C; consumo apagado ≤ 100 µA', 'Apagado real y comandable; fugas mínimas'],
         ['RD-13', 'Caída de 1 m en el estuche; conectores protegidos', 'Fijación de celda y placa; micrófono protegido'],
         ['Físicas', '≈ 160 × 80 × 35 mm (cuerpo), ≤ 350 g', 'Formato de celda, pantalla y apilado'],
         ['Ambiente', 'Uso de 10 a 35 °C, 25 a 80 % de HR; estabilización de 5 min', 'Térmica del gabinete; '
          'carga solo dentro de la ventana de temperatura de la celda'],
         ['Normativos', 'IEC 61010-1, IEC 61326-1, IEC 62133-2', 'Celda certificada, protecciones, EMC']],
        [1300, 3600, 3937], size=17),
     CAP('Tabla 5.1. Requisitos del anteproyecto que condicionan el diseño de hardware.')])

# ───────────── 5.2 ─────────────
add([H1('5.2 Análisis del hardware previo'),
     P('El prototipo del curso usaba una placa ESP32 DevKit v1 alimentada por el USB de una PC, un módulo con el '
       'micrófono INMP441 conectado con cables Dupont sobre un protoboard y un puente de cable para sacar los datos '
       'por la consola USB. La Tabla 5.2 resume los hallazgos.'),
     KT(['ID', 'Hallazgo', 'Evidencia', 'Consecuencia', 'Sev.'],
        [['H5.1', 'Micrófono alimentado desde el 3V3 de la placa de desarrollo, el mismo regulador que el ESP32 y su '
          'Wi-Fi; la lista de materiales menciona un LDO dedicado que el cableado no usa', 'README: conexión VDD → '
          '3V3; tabla de materiales', 'Rizado digital en la alimentación del micrófono (sección 5.5)', 'Alta'],
         ['H5.2', 'Micrófono INMP441: margen de 3,5 dB en 500 Hz', 'Capítulo 3, sección 3.8', 'No cumple RD-03', 'Alta'],
         ['H5.3', 'Bus I2S con cables Dupont de longitud variable sobre protoboard; reloj de 3,3 MHz sin resistencias '
          'serie', 'README: conexiones', 'Reflexiones e interferencia; fallas intermitentes', 'Media'],
         ['H5.4', 'WS en GPIO15 y BCLK en GPIO14 del ESP32 original: pines de configuración de arranque y de JTAG',
          'app_config.h', 'Comportamiento indefinido durante el arranque', 'Media'],
         ['H5.5', 'Dependencia de la PC: sin batería, sin cargador, sin interfaz propia', 'README: diagrama',
          'No es un instrumento autónomo', 'Alta'],
         ['H5.6', 'Puente de cable D17 → RX0 sobre las líneas de la consola, que también usa el conversor USB de la '
          'placa', 'README: truco de "un solo cable USB"', 'Solución dependiente de la placa; posible conflicto '
          'eléctrico (a verificar)', 'Media'],
         ['H5.7', 'Micrófono en el protoboard, junto a la placa y los cables', 'Montaje', 'Error de nivel en bandas '
          'altas no caracterizado', 'Media'],
         ['H5.8', 'Sin protección ESD propia ni gabinete', 'Montaje', 'No apto para uso en campo', 'Media']],
        [700, 3200, 1900, 2237, 800], size=16),
     CAP('Tabla 5.2. Hallazgos en el hardware del prototipo.'),
     P('Ningún elemento de hardware del prototipo se conserva en el diseño autónomo. La placa de desarrollo se '
       'mantiene solo como plataforma para el firmware hasta disponer del PCB propio (entregables E3 y E4).')])

# ───────────── 5.3 ─────────────
add([H1('5.3 Arquitectura y selección de componentes'),
     P('La Figura 5.1 muestra la arquitectura de hardware con sus buses, tensiones y conectores. El micrófono '
       'digital va en una placa satélite al extremo de un vástago (J2). El módulo ESP32-S3 concentra el '
       'procesamiento, la radio y el USB nativo. La pantalla usa SPI2, la microSD el controlador SDMMC y la '
       'alimentación se detalla en la Figura 5.2.'),
     *FIGURA('cap5_bloques_hw.png', 16.5,
             'Figura 5.1. Diagrama de hardware por bloques: buses, tensiones y conectores.'),
     KT(['Función', 'Alternativas evaluadas', 'Elegido', 'Motivo'],
        [['Procesador y radio', 'Placa de desarrollo; chip suelto; módulo ESP32-S3-WROOM-1',
          'WROOM-1 N16R8 (sin sufijo V)', 'Antena integrada y radio certificada; 16 MB de flash y 8 MB de PSRAM; USB '
          'nativo; GPIO47/48 a 3,3 V (las variantes "V" los llevan a 1,8 V)'],
         ['Micrófono', 'INMP441; ICS-43434; electret + códec', 'ICS-43434', 'SNR 65 dBA (EIN 29 dBA), sobrecarga '
          '120 dB SPL, sensibilidad ±1 dB, 490 µA [3]; misma interfaz I2S (D3.2)'],
         ['Regulador principal', 'LDO; buck-boost', 'LDO 3,3 V ≥ 600 mA', 'Sin rizado PFM ni emisión de '
          'conmutación; el buck-boost daría solo un 8 % más de autonomía (sección 5.4)'],
         ['Regulador del micrófono', 'Riel digital compartido; LDO dedicado', 'LP5907-3.3', '6,5 µVrms, 12 µA de '
          'reposo [4]; aísla las ráfagas del Wi-Fi'],
         ['Cargador', 'TP4056; MCP73831; BQ24074', 'BQ24074', 'Camino de potencia, entrada hasta 1,5 A, corriente de '
          'carga fija por resistencia, entrada TS para termistor [5]'],
         ['Batería', '18650 2600 mAh; 18650 3000 mAh; LiPo 3000 mAh', '18650 3000 mAh protegida',
          'Cumple RD-08 en el peor caso (Tabla 5.5); reemplazable por el usuario'],
         ['Pantalla', 'OLED 1,3"; TFT 2,4–2,8" SPI', 'TFT de 2,8 in SPI', 'Legible y en color para el veredicto; '
          'retroiluminación regulable'],
         ['Almacenamiento', 'Flash interna; microSD por SPI o SDMMC', 'microSD por SDMMC', 'Capacidad, extracción '
          'por el usuario, bus independiente de la pantalla (Capítulo 4)']],
        [1500, 2500, 1900, 2937], size=16),
     CAP('Tabla 5.3. Selección de los componentes principales.')])

# ───────────── 5.4 ─────────────
add([H1('5.4 Alimentación, autonomía y carga'),
     P('La Figura 5.2 muestra el árbol de alimentación: el cargador con camino de potencia alimenta la salida OUT '
       'desde el USB o desde la celda; un conmutador de encendido con enclavamiento entrega VSYS a los dos '
       'reguladores; y el firmware supervisa la batería y puede apagar el equipo.'),
     *FIGURA('cap5_alimentacion.png', 16.5,
             'Figura 5.2. Árbol de alimentación: protección de polaridad, termistor, comparador de CC, conmutador '
             'con enclavamiento, LDO digital y LDO dedicado al micrófono.'),
     H2('Presupuesto de consumo'),
     KT(['Carga', 'Modo medición [mA]', 'Modo reposo [mA]', 'Peor caso [mA]'],
        [['ESP32-S3 con Wi-Fi en punto de acceso (recepción continua, 240 MHz)', '145', '130', '170'],
         ['Pantalla: controlador', '5', '5', '5'],
         ['Pantalla: retroiluminación (PWM)', '20', '8', '40'],
         ['microSD (promedio con escrituras)', '1', '0,5', '3'],
         ['LED bicolor (promedio)', '2', '1', '5'],
         ['Micrófono ICS-43434', '0,49', '0', '0,49'],
         ['Reposo de reguladores, comparador y divisor', '0,2', '0,2', '0,2'],
         ['##Total', '##174', '##145', '##224']],
        [4300, 1500, 1500, 1537], size=17, center_cols=(1, 2, 3)),
     CAP('Tabla 5.4. Presupuesto de consumo supuesto. En modo punto de acceso la radio no entra en suspensión, por '
         'lo que el ESP32-S3 se supuso cerca de su consumo de recepción más la CPU; en reposo se mantiene 240 MHz '
         'como supuesto conservador (el Capítulo 4 reduce la frecuencia). Pico del sistema: 450 mA.'),
     H2('Corte por batería baja y regulador'),
     P('Entre la celda y VSYS hay una resistencia serie que se estimó en **250 mΩ**: resistencia interna de la celda '
       '(80 mΩ), protección de la celda (50 mΩ), MOSFET de polaridad (25 mΩ), FET de batería del cargador (50 mΩ) y '
       'conmutador y contactos (45 mΩ). El firmware cierra la sesión y apaga cuando VSYS con carga, promediado '
       'durante 1 s y con 100 mV de histéresis, baja de **3,50 V**:'),
     EQ('OCV_corte = 3,50 V + 0,174 A · 0,25 Ω = 3,54 V   ⇒   carga utilizable ≈ 94 %', 1),
     P('En ese punto, un pico de 450 mA lleva VSYS a 3,43 V y el riel digital a ≈ 3,18 V (con 0,25 V de caída del '
       'LDO): el LDO sale brevemente de regulación, pero el ESP32-S3 funciona entre 3,0 y 3,6 V, de modo que no es '
       'un límite duro. El riel del micrófono sigue en 3,3 V, porque el LP5907 cae pocos milivoltios con 0,5 mA. '
       'La diferencia de niveles entre el micrófono (3,3 V) y el ESP32 (≥ 3,18 V) queda dentro del margen de '
       '0,3 V de sus entradas.'),
     P('Un buck-boost aprovecharía el 98 % de la carga y tomaría 0,965 veces la corriente de carga (rendimiento del '
       '90 %): **8 % más de autonomía**. **Decisión D5.1: LDO de 3,3 V (≥ 600 mA, caída ≤ 250 mV al pico).** El '
       'argumento no es solo el ruido en el micrófono, que ya tiene su propio LDO, sino que un buck-boost a baja '
       'carga trabaja en modo PFM, con un rizado de frecuencia variable que puede caer en la banda audible y '
       'acoplarse por masa y por el cable del vástago, además de sumar emisión cerca de la antena y del bus I2S. El '
       '8 % no compensa ese riesgo cuando la autonomía con LDO cumple RD-08.'),
     H2('Batería y autonomía'),
     *FIGURA('cap5_autonomia.png', 16.5,
             'Figura 5.3. Izquierda: autonomía según la corriente media, para celdas nuevas y al fin de vida a 10 °C. '
             'Derecha: tensión típica de una celda Li-ion y corte del firmware.'),
     KT(['Batería', 'Condición', 'Modo medición [h]', 'Modo reposo [h]', 'Peor caso [h]'],
        [['18650 2600 mAh', 'Nueva, 25 °C', '14,1', '16,9', '10,9'],
         ['18650 2600 mAh', 'Fin de vida (80 %), 10 °C', '10,1', '12,1', ('7,8', 'F8D7DA')],
         [('18650 3000 mAh', 'D4EDDA'), 'Nueva, 25 °C', '16,3', '19,5', '12,6'],
         [('18650 3000 mAh', 'D4EDDA'), 'Fin de vida (80 %)', '12,9', '15,5', '10,1'],
         [('18650 3000 mAh', 'D4EDDA'), 'Fin de vida (80 %), 10 °C', '11,6', '13,9', '9,0']],
        [2100, 2500, 1400, 1400, 1437], size=17, center_cols=(2, 3, 4)),
     CAP('Tabla 5.5. Autonomía estimada. Para el fin de vida la resistencia serie se multiplica por 1,5 y, a 10 °C, '
         'por 2, lo que sube el corte; "fin de vida y 10 °C" aplica además un factor 0,72 a la capacidad.'),
     P('**Decisión D5.2: celda 18650 de 3000 mAh protegida, en portapila.** La de 2600 mAh no cumple el peor caso '
       'al fin de vida a 10 °C (7,8 h). La de 3000 mAh da 9,0 h. **Sensibilidad:** si el ESP32-S3 consume 20 mA más '
       'que lo supuesto, el peor caso baja a 8,3 h; con 40 mA más, a 7,6 h. En ese caso la mitigación es reducir la '
       'retroiluminación o apagar el Wi-Fi tras un tiempo sin clientes (Capítulo 4), y EN-07 decide.'),
     H2('Carga por USB-C'),
     P('En el BQ24074 la corriente de **carga** la fija una resistencia en ISET, mientras que EN1/EN2 e ILIM limitan '
       'la corriente de **entrada**, que se reparte entre el sistema y la batería [5]. Se eligen ISET = 0,8 A (para '
       'limitar la disipación) e ILIM = 1,5 A. Con resistencias en EN1/EN2 referidas a la entrada, el modo por '
       'defecto es USB500. Un comparador de nanopotencia alimentado desde OUT compara la línea CC activa con '
       '0,66 V, el umbral por encima del cual la fuente anuncia al menos 1,5 A [7], y conmuta a modo ILIM. Así, '
       '**la selección no depende del ESP32 y funciona con el equipo apagado**, que es el caso típico de carga; el '
       'firmware solo lee la salida del comparador.'),
     KT(['Fuente', 'Equipo', 'Corriente de carga', 'Tiempo estimado'],
        [['USB-C que anuncia ≥ 1,5 A', 'Apagado o encendido', '800 mA', ('3,6 h', 'D4EDDA')],
         ['Corriente por defecto (puerto de PC, cargador USB-A con cable A-C)', 'Apagado', '500 mA', '5,4 h'],
         ['Corriente por defecto', 'Encendido (174 mA)', '326 mA', '8,0 h']],
        [3800, 1800, 1600, 1637], size=17, center_cols=(2, 3)),
     CAP('Tabla 5.6. Tiempo de carga de la celda de 3000 mAh (aproximación t ≈ 0,8 · C / I + 0,6 h).'),
     P('**Decisión D5.3:** cargador BQ24074 con ISET = 0,8 A, ILIM = 1,5 A, selección de modo por comparador de CC '
       'y termistor NTC de 10 kΩ acoplado a la celda en la entrada TS, para que no cargue fuera de su ventana de '
       'temperatura (las 18650 protegidas no traen termistor). RD-08 (≤ 4 h) se cumple con una fuente que anuncie '
       '≥ 1,5 A; con una fuente por defecto, el equipo informa el tiempo estimado. Un puerto USB 2.0 solo garantiza '
       '100 mA sin enumeración; tomar 500 mA en modo por defecto es práctica habitual de los cargadores, pero queda '
       'declarado como limitación.'),
     H2('Encendido, apagado y almacenamiento'),
     P('**Decisión D5.4: conmutador de encendido con enclavamiento.** Un P-MOSFET entre OUT y VSYS se enciende con '
       'el pulsador y queda enclavado por la línea POWER_HOLD del ESP32-S3. El firmware apaga el equipo liberando '
       'esa línea, ya sea por una pulsación larga o por batería crítica. Esto materializa el estado APAGADO del '
       'anexo y del Capítulo 4, y evita la descarga profunda que produciría un interruptor manual dejado cerrado. '
       'Con el equipo apagado quedan la protección de la celda (3 µA), la fuga del cargador sin entrada (típica de '
       '4,3 µA, máxima de 6,5 µA [5]), el divisor de batería (2,1 µA) y el conmutador (1 µA): **≈ 12,6 µA** frente a '
       'los 100 µA de RD-12. En 3 meses, la autodescarga química (≈ 270 mAh) y la electrónica (28 mAh) dejan '
       '≈ 90 % de la carga.'),
     P('**Medición de la batería.** El divisor de 2 × 1 MΩ con 100 nF va sobre el nodo BAT, de modo que mide la '
       'celda también mientras carga. Con el ESP32 apagado, la corriente hacia su pin queda limitada a ≈ 2 µA. Las '
       'salidas /CHG y /PGOOD son de drenador abierto con pull-up a 3V3_D, así que tampoco realimentan el ESP32 '
       'cuando está apagado.'),
     P('**Protección de polaridad.** Como la celda la cambia el usuario, un P-MOSFET en serie con la celda impide '
       'que una inserción invertida dañe el cargador y el resto del circuito. Al estar polarizado en conducción con '
       'la celda bien colocada, permite tanto la carga como la descarga; su resistencia (25 mΩ) ya está incluida en '
       'la resistencia serie.')])

# ───────────── 5.5 ─────────────
add([H1('5.5 Cadena del micrófono'),
     H2('Rizado admisible en la alimentación'),
     P('El ICS-43434 especifica un rechazo a la alimentación de −100 dBFS para un rizado de 100 mVpp (onda cuadrada '
       'de 217 Hz) [3], con fondo de escala de unos 120 dB SPL. Se adopta como objetivo que el efecto del rizado '
       'quede 10 dB por debajo del piso del ICS-43434 en 500 Hz (13,5 dB SPL, Capítulo 3), en −116,5 dBFS. Con dos '
       'supuestos explícitos (que la PSR escala linealmente con la amplitud y que una cifra de banda ancha a '
       '217 Hz representa el efecto dentro de una banda de octava):'),
     EQ('V_rizado,adm ≈ 100 mVpp · 10^((−116,5 − (−100)) / 20) ≈ 15 mVpp', 2),
     P('El Wi-Fi en modo punto de acceso transmite balizas cada 102,4 ms (9,77 Hz, con armónicos en todas las '
       'bandas) y ráfagas de datos. Un escalón de 300 mA produce ≈ 75 mVpp en VSYS (300 mA × 0,25 Ω). Un LDO '
       'compartido con el ESP32 respondería a esos escalones con transitorios de decenas de milivoltios según su '
       'respuesta dinámica (a medir), del mismo orden que el valor admisible. Con un LDO dedicado de 60 dB de PSRR '
       'quedan ≈ 75 µVpp en el micrófono. El otro camino de acoplamiento es el retorno común de masa: el riel del '
       'micrófono vuelve por el plano de masa continuo y por la malla del cable, lejos de los retornos del LDO '
       'digital y del cargador.'),
     P('**Decisión D5.5: riel propio para el micrófono.** Un filtro RC (10 Ω, 10 µF) desde VSYS alimenta un '
       'LP5907-3.3 que solo alimenta la placa satélite, a través de una perla de ferrita y con 100 nF junto al '
       'micrófono. Con USB conectado VSYS sube a 4,4 V (salida regulada del cargador) y lleva ruido de la entrada: '
       'el LP5907 lo atenúa igual, pero EN-09 incluye un caso con USB conectado. Medir mientras carga se permite y '
       'queda registrado en la sesión.'),
     H2('Placa satélite e integridad de la señal'),
     B('**Montaje acústico:** el ICS-43434 tiene el puerto acústico en la cara inferior. La placa satélite lleva una '
       'perforación bajo el puerto, una junta que sella el camino acústico y una pantalla antiviento, siguiendo la '
       'nota de aplicación del fabricante [6].'),
     B('**Ensamblado:** el encapsulado LGA de 3,50 × 2,65 × 0,98 mm requiere pasta por plantilla y refusión. Para el '
       'primer prototipo se puede usar un módulo comercial con el ICS-43434 ya montado.'),
     B('**Señales:** el reloj de bit es de 48 kHz × 64 = 3,072 MHz. El cable apantallado tiene 5 conductores (VDD, '
       'GND, BCLK, WS, SD) más la malla, ≈ 15 cm, con GND entre BCLK y SD. Lleva resistencias serie de 33 Ω en el '
       'origen de cada señal (BCLK y WS en el ESP32, SD en el micrófono) y el pull-down de 100 kΩ en SD que '
       'recomienda el fabricante para la línea en alta impedancia. L/R va a GND.'),
     B('**Interferencia de RF:** un micrófono MEMS puede demodular la portadora de 2,4 GHz. Se colocan '
       'capacitores pequeños a masa (decenas de pF) y ferritas en las líneas de la placa satélite. La malla se '
       'conecta a masa **en ambos extremos**: a 2,4 GHz un cuarto de onda mide ≈ 3 cm y una malla conectada en un '
       'solo extremo actuaría como antena. La antena del módulo va en el extremo opuesto al vástago.'),
     B('**Influencia del gabinete:** a 8 kHz la longitud de onda es de ≈ 4,3 cm, comparable al cuerpo del equipo. El '
       'vástago de ≈ 100 mm aleja el micrófono del cuerpo, y el efecto residual se corrige con las correcciones C_b '
       'por banda del Capítulo 3, ajustadas en EN-05.')])

# ───────────── 5.6 ─────────────
add([H1('5.6 Asignación de pines'),
     P('En el módulo ESP32-S3-WROOM-1 N16R8 no se usan: GPIO26 a GPIO32 (flash), GPIO33 a GPIO37 (PSRAM octal), los '
       'pines de configuración de arranque GPIO0, GPIO3, GPIO45 y GPIO46 (salvo GPIO0 como botón interno de '
       'servicio) ni el ADC2, que no está disponible con el Wi-Fi activo. Las entradas analógicas van en el ADC1 '
       '(GPIO1 a GPIO10), la pantalla en los pines dedicados de SPI2 y la microSD en pines libres, porque el '
       'controlador SDMMC del ESP32-S3 se enruta por la matriz de GPIO. GPIO39 a GPIO42 tienen función JTAG por '
       'pines, que no se usa porque la depuración va por el USB nativo. La Tabla 5.7 resume la asignación.'),
     KT(['Función', 'GPIO', 'Función', 'GPIO'],
        [['VBAT (divisor sobre BAT) · ADC1', '1', 'TFT DC', '9'],
         ['POWER_HOLD (enclavamiento)', '2', 'TFT CS (SPI2)', '10'],
         ['Lectura del pulsador de encendido', '4', 'TFT MOSI (SPI2)', '11'],
         ['Cargador /CHG', '5', 'TFT SCLK (SPI2)', '12'],
         ['Cargador /PGOOD', '6', 'Libre (MISO de SPI2, para un táctil futuro)', '13'],
         ['Comparador "fuente ≥ 1,5 A"', '7', 'TFT retroiluminación (PWM)', '14'],
         ['I2S BCLK / WS / SD', '15 / 16 / 17', 'TFT RST', '21'],
         ['Pulsadores MEDIR / CAL / MENÚ', '8 / 18 / 47', 'microSD CMD / CLK / D0', '38 / 39 / 40'],
         ['LED rojo / verde', '42 / 48', 'microSD detección de tarjeta', '41'],
         ['USB nativo D− / D+', '19 / 20', 'UART0 (puntos de prueba)', '43 / 44'],
         ['Botón de servicio (arranque)', '0', 'Sin uso: arranque, flash, PSRAM', '3, 45, 46, 26–37']],
        [3000, 1400, 3000, 1437], size=17, center_cols=(1, 3)),
     CAP('Tabla 5.7. Asignación de pines propuesta (pines dedicados de SPI2 verificados en ESP-IDF 5.4: CS 10, '
         'MOSI 11, CLK 12, MISO 13).'),
     P('Los pulsadores usan pull-up interno, antirrebote por software (Capítulo 4) y diodos TVS. Durante el '
       'reinicio del ESP32-S3 sus pines quedan en alta impedancia: POWER_HOLD lleva un pull-down y la línea del '
       'pulsador de encendido mantiene el MOSFET conduciendo mientras se presiona, de modo que el equipo arranca '
       'aunque el ESP32 todavía no haya tomado el control. Es la decisión **D5.6**.')])

# ───────────── 5.7 ─────────────
add([H1('5.7 Circuito impreso, térmica y gabinete'),
     H2('Circuito impreso'),
     B('**Cuatro capas (D5.7):** señales / masa / alimentación / señales, con plano de masa continuo bajo el módulo, '
       'las pistas rápidas y el riel del micrófono. Se diseña con las reglas del fabricante elegido (ancho y '
       'separación mínimos, vías) y con un panel para el lote de prototipos.'),
     B('**Antena:** el módulo va en el borde de la placa, con la zona libre de cobre que indica su hoja de datos '
       '[2], en el extremo opuesto al vástago.'),
     B('**Desacople y reserva:** el escalón de corriente del Wi-Fi (≈ 350 mA) durante el tiempo de respuesta del '
       'LDO (≈ 10 µs) con una caída admitida de 100 mV requiere C ≥ ΔI · Δt / ΔV ≈ 35 µF; se colocan 47 µF + 10 µF + '
       '100 nF junto al módulo. El pin EN del módulo lleva la red RC de la guía de diseño (10 kΩ, 1 µF) para que el '
       'arranque ocurra con la alimentación estable.'),
     B('**Protección:** diodos TVS en VBUS, D+/D−, CC1/CC2, pulsadores y las líneas del vástago.'),
     B('**Prueba y depuración:** puntos de prueba en VSYS, 3V3_D, 3V3_MIC, BCLK, WS, SD y UART0; programación por el '
       'USB nativo del ESP32-S3 (USB-Serial/JTAG), sin conversor USB-UART.'),
     H2('Térmica'),
     P('El caso peor no es la batería llena sino el **USB conectado**: la salida del cargador sube a 4,4 V y el LDO '
       'disipa (4,4 − 3,3) V × 224 mA ≈ 246 mW. En SOT-89 o DFN (≈ 90 °C/W) eso significa 22 °C sobre el ambiente; '
       'en SOT-23-5 serían ≈ 60 °C, por eso se descarta ese encapsulado. El cargador disipa (5 V − V_bat) · I_carga '
       '+ (5 V − 4,4 V) · I_sistema: entre 1,7 W (celda a 3,0 V) y 0,9 W (celda a 4,0 V). Con 44,5 °C/W su juntura '
       'sube entre 76 y 40 °C; al principio de una carga profunda puede actuar su regulación térmica (125 °C), lo '
       'que alarga la carga y obliga a confirmar el tiempo en EN-07. Elegir ISET = 0,8 A en lugar de 1 A reduce '
       'esa disipación.'),
     P('**Balance del gabinete:** con ≈ 424 cm² de superficie y un coeficiente de convección natural de ≈ 6 W/m²K, la '
       'resistencia térmica es de ≈ 3,9 K/W. Cargando y midiendo a la vez se disipan ≈ 2,1 W, lo que eleva el '
       'interior ≈ 8 °C de media. Con 35 °C de ambiente, el interior rondaría 43 °C, cerca del límite habitual de '
       'carga de una celda Li-ion (≈ 45 °C): el termistor NTC detiene la carga si se supera, y la celda se ubica '
       'lejos del cargador. PU-HW-06 verifica el caso combinado.'),
     H2('Gabinete, masa y apilado'),
     *FIGURA('cap5_mecanica.png', 16,
             'Figura 5.4. Concepto mecánico: vista frontal y lateral, con el vástago, la antena, la batería y los '
             'conectores. Los 160 mm corresponden al cuerpo; el vástago desmontable agrega ≈ 100 mm.'),
     KT(['Apilado (espesor)', 'mm', 'Masa', 'g'],
        [['Pared frontal', '2,0', 'Celda 18650 3000 mAh', '47'],
         ['Módulo TFT', '4,0', 'Portapila', '6'],
         ['PCB', '1,6', 'PCB con componentes', '25'],
         ['Componentes y holgura', '3,0', 'Pantalla', '30'],
         ['Portapila con celda', '21,0', 'Gabinete PETG (paredes de 2 mm)', '105'],
         ['Pared trasera', '2,0', 'Vástago, placa satélite y cable', '20'],
         ['', '', 'Pulsadores, tornillos y tapas', '15'],
         ['##Total', '##33,6 (≤ 35)', '##Total', '##248 (≤ 350)']],
        [2700, 1300, 3600, 1237], size=17, center_cols=(1, 3)),
     CAP('Tabla 5.8. Apilado en espesor y presupuesto de masa estimados.'),
     P('**Decisión D5.8:** gabinete prototipo impreso en 3D (PETG), con portapila accesible desde una tapa, placa '
       'fijada en cuatro puntos para resistir la caída de RD-13, tapas de goma sobre la microSD y el USB-C, rosca de '
       '1/4" para trípode y vástago desmontable. No se esperan problemas por la humedad de uso (25 a 80 % sin '
       'condensación); los 5 min de estabilización térmica de CU-01 cubren la deriva de sensibilidad del '
       'micrófono al pasar del estuche a la cabina.')])

# ───────────── 5.8 ─────────────
add([H1('5.8 Análisis de modos de falla'),
     P('La Tabla 5.9 resume un FMEA cualitativo de los modos de falla más probables del hardware, con severidad (S) '
       'y ocurrencia (O) en escala Alta / Media / Baja, la medida que los mitiga y la prueba que la verifica.'),
     KT(['Modo de falla', 'Efecto', 'S', 'O', 'Mitigación', 'Verificación'],
        [['Celda invertida en el portapila', 'Daño del cargador y del sistema', 'A', 'M', 'P-MOSFET de polaridad; '
          'marcado en el portapila', 'PU-HW-08'],
         ['Descarga profunda de la celda', 'Celda degradada o inservible', 'A', 'M', 'Corte del firmware a 3,50 V y '
          'apagado por enclavamiento; protección de la celda', 'PU-HW-03, PU-HW-04'],
         ['Carga fuera de la ventana de temperatura', 'Degradación o riesgo en la celda', 'A', 'B', 'NTC en TS; '
          'ISET = 0,8 A; celda lejos del cargador', 'PU-HW-06'],
         ['Caída de tensión por picos del Wi-Fi', 'Reinicio o datos corruptos', 'M', 'M', 'Reserva de 57 µF; corte '
          'con margen; detector de caída de tensión', 'PU-HW-01, PU-HW-02'],
         ['Corte de alimentación durante una escritura', 'Sesión corrupta (RD-09)', 'M', 'B', '/PGOOD y detector de '
          'caída de tensión; cierre de archivos (Capítulo 4)', 'EN-08'],
         ['Descarga electrostática en el vástago o el USB', 'Daño del micrófono o del ESP32', 'A', 'M', 'TVS en todas '
          'las líneas externas; malla a masa', 'PU-HW-09'],
         ['Fuente USB débil', 'Carga lenta', 'B', 'A', 'Modo USB500 por defecto; aviso del tiempo estimado',
          'PU-HW-05'],
         ['Interferencia de RF en el micrófono', 'Piso de ruido elevado', 'M', 'M', 'Filtros RF, malla en ambos '
          'extremos, antena opuesta', 'EN-09'],
         ['Vástago desconectado o cable cortado', 'Sin datos de audio', 'M', 'M', 'Detección por plazo de lectura '
          'I2S (Capítulo 4) y aviso', 'PU-HW-07']],
        [2100, 1700, 400, 400, 2600, 1637], size=15, center_cols=(2, 3)),
     CAP('Tabla 5.9. Análisis de modos de falla y efectos (cualitativo).')])

# ───────────── 5.9 ─────────────
add([H1('5.9 Costo, normativa y seguridad'),
     KT(['Ítem', 'USD', 'Ítem', 'USD'],
        [['Módulo ESP32-S3-WROOM-1 N16R8', '5', 'Celda 18650 3000 mAh protegida + portapila', '11,5'],
         ['ICS-43434 + placa satélite', '5', 'microSD (zócalo + tarjeta)', '6'],
         ['Pantalla TFT de 2,8 in SPI', '9', 'Pulsadores, LED, conectores', '4'],
         ['BQ24074 + LDO + LP5907', '4', 'Pasivos y diodos TVS', '5'],
         ['Comparador, MOSFET y NTC', '2,5', 'Gabinete PETG, vástago y cable', '12'],
         ['PCB de 4 capas (parte del lote de 5)', '20', '##Total aproximado', '##≈ 84']],
        [3400, 900, 3600, 937], size=17, center_cols=(1, 3)),
     CAP('Tabla 5.10. Costo estimado de materiales por prototipo, sin envío ni impuestos; dentro de la estimación del '
         'anteproyecto (≈ USD 100, que incluía la placa de desarrollo).'),
     KT(['Norma', 'Aplicación al prototipo'],
        [['IEC 61010-1 (seguridad de equipos de medición)', 'Equipo de baja tensión a batería: temperatura de las '
          'superficies, resistencia mecánica, marcado'],
         ['IEC 62133-2 y UN 38.3 (baterías de litio)', 'Celda comercial certificada, con protección; el equipo '
          'respeta su ventana de carga (NTC) y su corriente máxima; transporte de la celda según UN 38.3'],
         ['IEC 61326-1 (compatibilidad electromagnética)', 'Fuera del alcance certificar; se aplican buenas prácticas y '
          'una prueba informal de descarga electrostática (PU-HW-09, niveles de referencia ±4 kV por contacto y ±8 kV '
          'por aire de IEC 61000-4-2) y de cercanía de un teléfono móvil'],
         ['Radio (ENACOM)', 'El módulo trae certificaciones de origen; la homologación local queda fuera del alcance '
          'del prototipo'],
         ['RoHS', 'Componentes y soldadura sin plomo']],
        [3300, 5537], size=17),
     CAP('Tabla 5.11. Normas aplicables y alcance dentro del prototipo.')])

# ───────────── 5.10 ─────────────
add([H1('5.10 Plan de verificación'),
     KT(['ID', 'Procedimiento', 'Criterio de aceptación', 'Verifica'],
        [['PU-HW-01', 'Puesta en marcha: tensiones de VSYS, 3V3_D y 3V3_MIC; rizado en el VDD del micrófono con el '
          'Wi-Fi transmitiendo (osciloscopio con promediado y ancho de banda limitado)', 'Tensiones ±3 %; rizado '
          '≤ 1 mVpp (el criterio funcional es EN-09)', 'D5.5 · RD-03'],
         ['PU-HW-02', 'Consumo por modo con amperímetro de registro', '±20 % del presupuesto, o presupuesto '
          'actualizado', 'D5.1, D5.2 · RD-08'],
         ['PU-HW-03', 'Corriente de batería con el equipo apagado; apagado por firmware', '≤ 100 µA (esperado '
          '≈ 12,6 µA); apagado real al liberar POWER_HOLD', 'D5.4 · RD-12'],
         ['PU-HW-04', 'Lectura de batería frente a multímetro entre 3,0 y 4,2 V; disparo del corte', 'Error ≤ 30 mV; '
          'corte a 3,50 ± 0,05 V con carga', 'D5.1 · CU-02 · RD-12'],
         ['PU-HW-05', 'Carga con fuentes por defecto, de 1,5 A y de 3 A, con el equipo apagado y encendido', 'Modo '
          'correcto sin el ESP32; carga ≤ 4 h con fuente ≥ 1,5 A', 'D5.3 · RD-08'],
         ['PU-HW-06', 'Carga y medición simultáneas a 35 °C de ambiente', 'Superficies accesibles ≤ 45 °C; NTC '
          'operativa; tiempo de carga registrado', 'D5.3, D5.7'],
         ['PU-HW-07', 'Integridad de BCLK, WS y SD en el extremo del vástago; desconexión del vástago', 'Sin '
          'sobrepicos que crucen umbrales; 0 errores en 1 h; desconexión detectada', 'D5.5'],
         ['PU-HW-08', 'Inserción invertida de la celda (con fuente limitada en corriente)', 'Sin daño ni consumo '
          'apreciable', 'D5.4'],
         ['PU-HW-09', 'Descarga electrostática informal en conectores, pulsadores y vástago; teléfono móvil a 10 cm',
          'Sin daño; sin reinicio; efecto en el piso ≤ 1 dB', 'D5.7 · EMC'],
         ['EN-02 / EN-09', 'Piso de ruido en recinto aislado; con Wi-Fi activo e inactivo y con USB conectado',
          'Ver anteproyecto', 'RD-03'],
         ['EN-07 / EN-12 / EN-13', 'Autonomía y carga; almacenamiento; caída', 'Ver anteproyecto', 'RD-08, RD-12, RD-13']],
        [1250, 3550, 2600, 1437], size=16),
     CAP('Tabla 5.12. Pruebas de hardware y ensayos del anteproyecto relacionados.')])

# ───────────── 5.11 ─────────────
add([H1('5.11 Conclusiones y decisiones'),
     KT(['ID', 'Decisión', 'Justificación', 'Verificación'],
        [['D5.1', 'LDO 3,3 V (≥ 600 mA); corte del firmware con VSYS ≤ 3,50 V', 'Sin rizado PFM ni emisión; 94 % de '
          'carga utilizable; buck-boost solo +8 %', 'PU-HW-02, PU-HW-04'],
         ['D5.2', 'Celda 18650 de 3000 mAh protegida, en portapila', '9,0 h en el peor caso al fin de vida; '
          'reemplazable', 'EN-07'],
         ['D5.3', 'BQ24074: ISET 0,8 A, ILIM 1,5 A, modo por comparador de CC, NTC en TS', 'Carga en 3,6 h sin depender '
          'del ESP32; ventana de temperatura', 'PU-HW-05, PU-HW-06'],
         ['D5.4', 'Conmutador con enclavamiento (POWER_HOLD); protección de polaridad; divisor sobre BAT',
          'Apagado comandable (12,6 µA); celda reemplazable segura', 'PU-HW-03, PU-HW-08'],
         ['D5.5', 'Riel dedicado al micrófono; placa satélite con cable apantallado, filtros RF y malla en ambos '
          'extremos', 'Rizado ≈ 75 µVpp frente a 15 mVpp admisibles', 'PU-HW-01, PU-HW-07, EN-09'],
         ['D5.6', 'Pines sin arranque, PSRAM ni ADC2; estados definidos con el ESP32 apagado o en reinicio',
          'Arranque fiable; sin realimentación', 'Inspección'],
         ['D5.7', 'PCB de 4 capas; LDO en SOT-89/DFN; antena opuesta al micrófono; TVS', 'EMC, radio y térmica',
          'PU-HW-06, PU-HW-09'],
         ['D5.8', 'Gabinete PETG, vástago desmontable de ≈ 100 mm, fijación para caída', '33,6 mm y 248 g; RD-13',
          'EN-05, EN-13']],
        [700, 3600, 2800, 1737], size=16),
     CAP('Tabla 5.13. Decisiones de diseño del capítulo y su verificación.'),
     H2('Pendientes'),
     B('Medir los consumos reales del ESP32-S3 en modo punto de acceso (PU-HW-02): son el principal riesgo para el '
       'margen de RD-08.'),
     B('Confirmar en las hojas de datos la condición de la PSR del ICS-43434, la caída del LDO elegido y las '
       'resistencias de EN1/EN2, ISET, ILIM y TS del BQ24074; elegir el comparador.'),
     B('Capturar el esquemático y diseñar el PCB en KiCad (E4); decidir entre la placa satélite propia y un módulo '
       'comercial con el ICS-43434.'),
     H2('Historial de revisión'),
     KT(['Versión', 'Cambios'],
        [['0.1', 'Borrador inicial.'],
         ['0.2', 'Revisión con tres revisores independientes (técnico de hardware, trazabilidad y evaluador '
          'académico): apagado comandable por enclavamiento; selección de corriente de carga por comparador de CC con '
          'el equipo apagado; ISET frente a ILIM; salida del cargador a 4,4 V con USB y su efecto térmico; balance '
          'térmico del gabinete; NTC y protección de polaridad; consumo del ESP32-S3 más conservador y celda de '
          '3000 mAh; resistencia serie completa y corte a 3,50 V con criterio corregido; divisor sobre BAT; estados '
          'de los pines con el ESP32 apagado; diagrama de hardware por bloques; FMEA; masa y apilado; pull-down de SD, '
          'filtros RF y malla; normativa ampliada; pruebas PU-HW-08 y PU-HW-09. Decisiones propagadas al '
          'anteproyecto, al anexo de Ingeniería de Software v0.4 y al Capítulo 4. Registro: '
          'revision_egm/registro_cap5_v0.2.md.']],
        [1100, 7737], size=17),
     H1('Referencias del capítulo'),
     *[P(r, size=20, align='left') for r in [
         '[1] Espressif Systems. ESP32-S3 Series Datasheet y ESP32-S3 Technical Reference Manual.',
         '[2] Espressif Systems. ESP32-S3-WROOM-1 / WROOM-1U Datasheet y ESP32-S3 Hardware Design Guidelines.',
         '[3] TDK InvenSense. ICS-43434 Multi-Mode Microphone with I2S Digital Output — Data Sheet, rev. 1.2.',
         '[4] Texas Instruments. LP5907 250-mA Ultra-Low-Noise Low-IQ LDO — Data Sheet.',
         '[5] Texas Instruments. BQ2407x 1.5-A USB-Friendly Li-Ion Battery Charger and Power-Path Management IC — '
         'Data Sheet.',
         '[6] TDK InvenSense. Recommendations for Mounting and Connecting InvenSense Bottom-Ported MEMS '
         'Microphones (nota de aplicación).',
         '[7] USB Implementers Forum. Universal Serial Bus Type-C Cable and Connector Specification.',
         '[8] Ott, H. W. Electromagnetic Compatibility Engineering. Wiley, 2009.',
         '[9] Texas Instruments. TPS63802 2-A High-Current Buck-Boost Converter — Data Sheet (alternativa evaluada).',
         '[10] IEC 61010-1, IEC 61326-1, IEC 61000-4-2, IEC 62133-2 y Naciones Unidas, Manual de Pruebas y Criterios, '
         'sección 38.3.',
         '[11] Horowitz, P.; Hill, W. The Art of Electronics, 3.ª ed. Cambridge University Press, 2015.',
         '[12] Bogatin, E. Signal and Power Integrity — Simplified, 3.ª ed. Prentice Hall, 2018.']]])

ensamblar(TPL, body, FIGURA, OUT)
print('OK', OUT)
