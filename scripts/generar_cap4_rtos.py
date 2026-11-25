#!/usr/bin/env python3
"""Capítulo 4 — Sistemas operativos de tiempo real: arquitectura concurrente del firmware (v0.2).

Uso (desde anteproyecto/):
  python3 -I scripts/generar_cap4_rtos.py "../ModeloAnteproyecto(1).docx" figuras capitulos/Cap4_RTOS_Firmware.docx

Cifras: rtos/resultados/resumen_rt.txt (rtos/analisis_temporal.py).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from docx_xml import P, B, H2  # noqa: E402
from cap_common import H1, PB, CAP, EQ, KT, CODE, Figuras, ensamblar  # noqa: E402

TPL, FIG, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
FIGURA = Figuras(FIG, 'C4')
VERSION = '0.2.2 (revisada con el método Elephant–Goldfish; alineada con los Capítulos 5 y 6)'

body = []
add = body.extend

# ───────────── Portada ─────────────
add([P('', after=600),
     P('Capítulo 4', size=40, bold=True, align='center', color='1E5E9F', after=120),
     P('Sistemas Operativos de Tiempo Real', size=36, bold=True, align='center', color='1E5E9F', after=200),
     P('Arquitectura concurrente del firmware, análisis temporal y robustez', size=28,
       bold=True, align='center', after=400),
     P('Analizador autónomo de ruido ambiente por bandas de octava para la verificación de cabinas '
       'audiométricas según ISO 8253-1', size=24, align='center', after=1200),
     P('**Autor:** Andrés Machtey', size=24, align='left', after=100),
     P('**Director propuesto:** Esp. Víctor Valotto (FIUNER)', size=24, align='left', after=100),
     P(f'**Versión:** {VERSION} · Noviembre de 2026', size=24, align='left', after=100),
     P('**Material reproducible:** rtos/analisis_temporal.py, rtos/graficos_rt.gp, rtos/resultados/, '
       'scripts/diagrama_tareas.py y scripts/diagrama_secuencia.py', size=20, align='left', after=100),
     PB()])

# ───────────── Siglas ─────────────
add([H1('Siglas y convenciones'),
     KT(['Sigla', 'Significado', 'Sigla', 'Significado'],
        [['RTOS', 'Sistema operativo de tiempo real (FreeRTOS)', 'ISR', 'Rutina de servicio de interrupción'],
         ['SMP', 'Multiprocesamiento simétrico (dos núcleos)', 'DMA / GDMA', 'Acceso directo a memoria (general)'],
         ['WCET', 'Tiempo de ejecución en el peor caso', 'RTA', 'Análisis de tiempo de respuesta'],
         ['IRAM / DRAM', 'RAM interna de instrucciones / datos', 'PSRAM', 'RAM externa (octal) del módulo'],
         ['TWDT', 'Perro guardián de tareas', 'FSM', 'Máquina de estados finitos'],
         ['NVS', 'Almacenamiento no volátil en flash', 'OTA', 'Actualización de firmware inalámbrica'],
         ['IPC', 'Comunicación entre procesadores (ESP-IDF)', 'PM', 'Gestión de energía (frecuencia y sueño)'],
         ['GPIO', 'Entrada/salida de propósito general', 'SPI / SDMMC', 'Bus serie / controlador de tarjetas SD'],
         ['FAT', 'Sistema de archivos de la microSD', 'WS', 'WebSocket'],
         ['CSV', 'Archivo de valores separados por comas', 'Unity', 'Marco de pruebas unitarias en C']],
        [1300, 3119, 1300, 3118], size=17),
     P('Notación temporal: **T** período, **C** tiempo de ejecución, **B** bloqueo, **J** fluctuación de la '
       'activación, **D** plazo, **R** tiempo de respuesta, **U** utilización. Los identificadores RD, EN, CU, '
       'HU y D3.x remiten al anteproyecto, al anexo de Ingeniería de Software y al Capítulo 3; las pruebas '
       'nuevas son **PU-RT-xx** y las decisiones **D4.x**. En FreeRTOS la prioridad crece con el número (0 = '
       'tarea inactiva). Se usa "búfer" para buffer y "función de aviso" para callback.', size=20)])

# ───────────── 4.1 ─────────────
add([H1('4.1 Enfoque del capítulo'),
     P('Este capítulo analiza el proyecto desde la materia **Sistemas Operativos de Tiempo Real**. El '
       'instrumento tiene un requisito de tiempo real estricto: procesar sin pérdidas un flujo continuo de '
       '48 000 muestras por segundo. Además, convive con actividades sin plazo estricto: la interfaz, la '
       'escritura en la microSD, el servidor web y la supervisión. El objetivo es diseñar una arquitectura '
       'concurrente sobre FreeRTOS [1, 2] que garantice el primer requisito sin que lo afecten los demás, y '
       'demostrarlo con análisis temporal [3–6], simulación y pruebas.'),
     P('El punto de partida es el firmware del prototipo del curso de DSP (repositorio decibilimetro-iso8253, '
       'carpeta firmware/main), que ya usaba FreeRTOS con dos tareas en núcleos distintos. Las afirmaciones '
       'sobre ESP-IDF se verificaron en el código fuente de la versión 5.4.'),
     H2('Requisitos que condicionan la arquitectura'),
     KT(['Requisito', 'Enunciado (anteproyecto)', 'Consecuencia para el RTOS'],
        [['RD-07', 'Tiempo real sin pérdida de bloques (0 desbordes en 8 h); CPU del núcleo DSP ≤ 70 %',
          'Plazo por bloque; aislamiento del núcleo DSP; contador de desbordes'],
         ['RD-06', 'Integración de 10 a 120 s; refresco ≤ 250 ms',
          'Período de publicación de resultados hacia la pantalla y la web'],
         ['RD-08', 'Autonomía ≥ 8 h con Wi-Fi activo', 'Gestión de energía compatible con el I2S'],
         ['RD-09', '≥ 1000 sesiones sin corrupción ante cortes', 'Tarea dueña de la microSD; escrituras atómicas'],
         ['RD-10, RD-11', 'Calibración persistente; OTA con reversión',
          'Escrituras en flash que detienen la caché: deben programarse'],
         ['RD-12', 'Datos conservados sin alimentación', 'NVS y microSD; cierre ordenado ante batería crítica']],
        [1300, 3800, 3737], size=18),
     CAP('Tabla 4.1. Requisitos del anteproyecto que condicionan la arquitectura concurrente.')])

# ───────────── 4.2 ─────────────
add([H1('4.2 Análisis del firmware previo'),
     P('El prototipo creaba dos tareas: **task_i2s** (prioridad 10, núcleo 0), que leía bloques de 1024 '
       'muestras con la API I2S heredada, los convertía a float y los dejaba en un conjunto de 4 búferes, y '
       '**task_dsp** (prioridad 9, núcleo 1), que filtraba, calculaba niveles cada 10 bloques, los enviaba por '
       'UART y además atendía los comandos. Una tercera tarea, uart_rx (prioridad 5, núcleo 0), interpretaba '
       'los comandos JSON. La Tabla 4.2 resume los hallazgos.'),
     KT(['ID', 'Hallazgo', 'Evidencia', 'Consecuencia', 'Sev.'],
        [['H4.1', 'Conjunto de 4 búferes en ronda sin control de propiedad: el productor escribe antes de saber '
          'si el búfer está libre', 'main.c:94-105', 'Bloques alterados sin aviso cuando el DSP se atrasa', 'Alta'],
         ['H4.2', 'Bloques descartados en silencio si la cola está llena; sin contador', 'main.c:105-107',
          'RD-07 no es verificable', 'Alta'],
         ['H4.3', 'Llamadas a la UART dentro de la tarea DSP. Con anillo TX de 1 kB y sin control de flujo '
          'retornan rápido, pero su duración depende del enlace', 'main.c:127, 151, 178, 197, 203, 212; '
          'uart_comm.c:75, 81', 'C del DSP sin cota; riesgo si se habilita el control de flujo (pines '
          'RTS/CTS ya definidos)', 'Media'],
         ['H4.4', 'Escritura en NVS (nvs_set_u32 + nvs_commit) desde task_dsp al calibrar, con la ISR I2S '
          'heredada fuera de IRAM', 'db_calculator.c:59-66; main.c:144', 'Detención de la caché en ambos '
          'núcleos en plena captura', 'Alta'],
         ['H4.5', 'Comandos sondeados al final de cada bloque dentro del DSP', 'main.c:188',
          'Lógica de aplicación mezclada con el camino de tiempo real', 'Media'],
         ['H4.6', 'El parámetro de calibración se guarda en la variable del tiempo de integración (s_avg_sec) '
          'y se usa como nivel de referencia', 'main.c:144, 207', 'Acoplamiento frágil entre comandos', 'Media'],
         ['H4.7', 'El firmware no integra el L_eq de la sesión: publica niveles de 200 ms y delega el promedio '
          'en la PC', 'main.c:170; app_config.h', 'Imposible en un equipo autónomo', 'Alta'],
         ['H4.8', 'Datos compartidos sin sincronización: búfer de transmisión usado por app_main y task_dsp; '
          'g_cal_factor escrito por task_dsp y leído por otras tareas', 'uart_comm.c:16; main.c:293; '
          'db_calculator.c', 'Carreras de ventana corta', 'Baja'],
         ['H4.9', 'Suma de cuadrados en double convertida a float al calcular el nivel', 'main.c:143, 173',
          'Pérdida de precisión en integraciones largas', 'Media'],
         ['H4.10', 'Semáforo creado y nunca usado; logs silenciados; sin medición de tiempos ni perro guardián; '
          'API I2S heredada; tick de 100 Hz', 'main.c:20, 40, 283-286; sdkconfig', 'Sin evidencia temporal ni '
          'diagnóstico', 'Media']],
        [700, 3150, 1800, 2387, 800], size=16),
     CAP('Tabla 4.2. Hallazgos en el firmware del prototipo, vistos desde el diseño concurrente.'),
     H2('La carrera del conjunto de búferes'),
     P('El productor toma el búfer pool[k mod 4], lo llena y recién después intenta encolar su puntero; si la '
       'cola está llena, descarta el bloque pero avanza el índice igual. Nada impide que ese búfer sea el que '
       'el consumidor está procesando o uno que espera en la cola. Se simuló el mecanismo con el período real '
       'del prototipo (20 ms por bloque) y tiempos de procesamiento crecientes. Un bloque procesado se cuenta '
       'como **alterado** si el productor volvió a escribir su búfer (bloque k + 4) antes de que el consumidor '
       'terminara de procesarlo.'),
     KT(['C del consumidor [ms]', '5', '19', '21', '25', '30', '40', '60', '80'],
        [['Bloques procesados (de 400)', '399', '399', '381', '320', '267', '200', '134', '100'],
         ['Procesados alterados', '0 %', '0 %', '84 %', '96 %', '98 %', '98 %', '99 %', '99 %'],
         ['Bloques descartados', '0', '0', '15', '76', '129', '196', '262', '296']],
        [2700] + [767] * 8, size=17, center_cols=tuple(range(1, 9))),
     CAP('Tabla 4.3. Simulación del conjunto de búferes del prototipo (rtos/analisis_temporal.py, sección 5).'),
     P('Mientras el consumidor tarde menos que el período no pasa nada. Apenas lo supera, el atraso crece '
       'hasta que hay 4 bloques pendientes y, desde ese momento, el búfer que se escribe es justamente el que '
       'se está procesando: **entre el 84 % y el 99 % de los bloques procesados quedan alterados**, y el resto '
       'se descarta. Ninguno de los dos efectos se registra (H4.2). El defecto quedaba oculto porque el '
       'procesamiento del prototipo era liviano. Es un caso típico de **recurso compartido sin dueño '
       'explícito**.')])

# ───────────── 4.3 ─────────────
add([H1('4.3 Arquitectura de tareas propuesta'),
     H2('Principios de diseño'),
     B('**Un dueño por recurso.** Las muestras pertenecen a T_DSP; el estado de la aplicación, a T_APP; la '
       'microSD, a T_STOR. Los demás piden servicios por mensajes. Así no hacen falta mutex entre tareas en el '
       'camino de tiempo real y se evitan la inversión de prioridades y los interbloqueos [8].'),
     B('**Camino de tiempo real sin bloqueos.** T_DSP solo se bloquea esperando datos del I2S o un comando, '
       'siempre con un plazo máximo. No hace E/S, no reserva memoria dinámica, no escribe logs y no toma mutex.'),
     B('**Mensajes por valor.** Las colas transportan estructuras pequeñas copiadas, no punteros a memoria '
       'compartida.'),
     B('**Aislamiento por núcleo, explícito.** Todas las tareas se crean con xTaskCreatePinnedToCore. En ESP-IDF '
       'varias tareas del sistema no tienen afinidad por defecto (lwIP, el servidor HTTP), así que se fijan al '
       'núcleo 0 por configuración (Tabla 4.14).'),
     B('**Todo se mide.** Tiempos de ejecución, desbordes, pilas y uso de CPU se registran y se publican.'),
     H2('Alternativas consideradas'),
     KT(['Alternativa', 'Ventajas', 'Desventajas'],
        [['A. Dos tareas con conjunto de búferes compartido (prototipo)', 'Separa captura y cálculo',
          'Carrera H4.1; copia y cambio de contexto extra; propiedad implícita'],
         ['B. Dos tareas con stream buffer o búfer doble con propiedad explícita', 'Corrige la carrera; la '
          'captura no depende del DSP', 'Duplica el almacenamiento intermedio que el anillo DMA ya provee; '
          'una tarea y una copia más'],
         [('C. Una tarea que lee el anillo DMA de i2s_std (elegida)', 'D4EDDA'), 'Sin búfer compartido; una copia; '
          'propiedad clara; menos cambios de contexto', 'El anillo debe dimensionarse para absorber detenciones '
          '(sección 4.6)'],
         ['D. Procesamiento dentro de la función de aviso on_recv (ISR)', 'Latencia mínima',
          'Cálculo de ~3 ms en contexto de interrupción: bloquea otras ISR y complica la depuración']],
        [3000, 2600, 3237], size=16),
     CAP('Tabla 4.4. Alternativas para el camino de captura y procesamiento.'),
     P('**Decisión D4.1: captura y procesamiento en una sola tarea (alternativa C).** Con el driver i2s_std de '
       'ESP-IDF 5 [2], el anillo de descriptores DMA ya es el búfer entre el periférico y el software: T_DSP '
       'llama a i2s_channel_read(), que copia 1024 muestras del anillo a un búfer propio y libera los '
       'descriptores. Se elimina el conjunto de búferes, una copia y un cambio de contexto por bloque.'),
     P('La Figura 4.1 muestra la arquitectura completa y la Tabla 4.5 resume las tareas.'),
     *FIGURA('cap4_tareas.png', 17,
             'Figura 4.1. Arquitectura de tareas propuesta: núcleos, tareas, colas, buzón y periféricos.'),
     KT(['Tarea', 'Núcleo', 'Prio.', 'Activación', 'Período / plazo', 'Pila', 'Función'],
        [['T_DSP', '1', '20', 'Datos del I2S / q_cmd', 'T = D = 21,3 ms', '4 kB', 'Conversión, banco de filtros, Σx², L_eq'],
         ['T_APP', '0', '10', 'q_evt / q_res (plazo 500 ms)', 'Esporádica; D = 50 ms', '4 kB', 'FSM, sesión, regla de piso, veredicto'],
         ['T_UI', '0', '8', 'Notificación', '≈ 235 ms', '6 kB', 'Dibujo de la pantalla'],
         ['T_STOR', '0', '6', 'q_stor / q_lect', 'D = 1 s', '6 kB', 'Archivos de sesión en la microSD (FAT); lecturas para historial y CSV'],
         ['T_NET', '0', '5', 'httpd_queue_work / red', 'D = 235 ms', '6 kB', 'Tarea de esp_http_server: HTTP y WebSocket (Cap. 6)'],
         ['T_XFER', '0', '4', 'Pedido asíncrono de httpd', 'Fondo; D = 1 s por trozo', '8 kB', 'Transferencias largas: OTA, CSV, historial (una a la vez)'],
         ['T_MON', '0', '2', 'Periódica', 'T = 1 s', '3 kB', 'Pilas, CPU; dueña del ADC1 (VBAT), de /CHG, /PGOOD, «fuente ≥ 1,5 A» y del I2C (RTC)'],
         ['Wi-Fi, lwIP, esp_timer', '0', '18–23', 'ESP-IDF', '—', 'IDF', 'Sistema (fijadas al núcleo 0)'],
         ['IPC1', '1', '24', 'ESP-IDF', 'Esporádica', 'IDF', 'Servicios entre núcleos (p. ej. flash)']],
        [1300, 800, 700, 1700, 1500, 650, 2187], size=16, center_cols=(1, 2, 5)),
     CAP('Tabla 4.5. Tareas, núcleo, prioridad y activación. Las pilas son estimaciones iniciales y se ajustan '
         'con la marca de agua medida; los búferes de T_DSP (≈ 9 kB, Capítulo 3) son estáticos y no ocupan pila.'),
     P('**Prioridades.** En el núcleo 1, T_DSP tiene la mayor prioridad de aplicación; solo la superan las '
       'interrupciones, el tick y la tarea IPC1 de ESP-IDF. En el núcleo 0 las prioridades siguen la urgencia: '
       'T_APP coordina y debe responder rápido; T_UI tiene un plazo blando de refresco; T_STOR y T_NET son de '
       'fondo, y T_XFER, por debajo de T_NET, hace que una descarga u OTA no demore la publicación; T_MON, la más baja, sirve además como testigo: si deja de correr, alguna tarea está acaparando '
       'el procesador. Para que la ISR del GDMA quede en el núcleo 1, el canal I2S se crea **desde T_DSP**: '
       'ESP-IDF asigna la interrupción al núcleo que inicializa el canal.'),
     P('**¿Prioridades fijas o EDF?** FreeRTOS planifica por prioridades fijas con desalojo. EDF (plazo más '
       'próximo primero) aprovecha mejor el procesador en conjuntos de tareas cargados [6], pero aquí no '
       'aporta nada: el núcleo 1 tiene una sola tarea con plazo estricto y el núcleo 0 trabaja con plazos '
       'blandos y utilización moderada. Las prioridades fijas son además las que el análisis de la sección 4.5 '
       'sabe acotar y las que el RTOS implementa de forma nativa.')])

# ───────────── 4.4 ─────────────
add([H1('4.4 Comunicación y sincronización'),
     KT(['Objeto', 'Tipo', 'Productor → consumidor', 'Tamaño', 'Política'],
        [['q_cmd', 'Cola', 'T_APP → T_DSP', '4 × 48 B', 'Comandos PREPARAR, INICIAR (con T_int, K y las 7 C_b), '
          'CALIBRAR, PISO, DETENER y REPOSO; T_DSP los aplica en el borde de bloque'],
         ['q_res', 'Cola', 'T_DSP → T_APP', '4 × 96 B', 'Resultado cada 11 bloques: L_eq parcial y acumulado por '
          'banda, bloques, descriptores perdidos y C máximo. Envío sin espera; si se llena, se cuenta'],
         ['q_evt', 'Cola', 'ISR GPIO, T_NET, T_UI, T_STOR, T_MON → T_APP', '16 × 64 B', 'Eventos de pulsadores, comandos '
          'remotos y confirmaciones; desde la ISR con xQueueSendFromISR'],
         ['mbx', 'Cola de longitud 1', 'T_APP → T_UI, T_NET', '1 × 128 B', 'xQueueOverwrite / xQueuePeek: siempre la '
          'última instantánea, sin acumular atraso; aviso a T_UI con xTaskNotifyGive y a T_NET con httpd_queue_work '
          'y una bandera atómica (si falla, se reintenta en el período siguiente)'],
         ['q_net', 'Cola', 'T_APP → T_NET', '8 × 64 B', 'Confirmaciones de comandos (ack/nack) y eventos para los '
          'paneles'],
         ['q_lect, sb_lect', 'Cola y StreamBuffer', 'T_XFER ↔ T_STOR', '4 × 32 B + 4 kB', 'Pedidos de '
          'lectura de archivos y datos devueltos por trozos; T_STOR sigue siendo el único dueño de la microSD'],
         ['q_stor', 'Cola', 'T_APP → T_STOR', '3 × 256 B', 'Registros de sesión; T_STOR confirma con un evento'],
         ['Contadores', 'Enteros atómicos de 32 bits', 'ISR I2S, T_DSP → T_MON', '—', 'Un solo escritor por '
          'contador; lectura sin bloqueo']],
        [1000, 1350, 2050, 1100, 3337], size=16),
     CAP('Tabla 4.6. Objetos de comunicación. Ninguno se comparte por puntero entre tareas.'),
     P('**Notificaciones o colas.** Las notificaciones de tarea de FreeRTOS son el mecanismo más liviano, pero '
       'solo transportan 32 bits y un único receptor. Se usan para "hay una instantánea nueva" en T_UI; T_NET es la '
       'tarea de esp_http_server y se activa con httpd_queue_work (Capítulo 6); '
       'para datos con estructura (comandos, resultados, registros) se usan colas.'),
     H2('Ciclo de T_DSP'),
     P('T_DSP no tiene estados de aplicación: solo modos (reposo, preparar, acumular, calibrar, piso). El '
       'pseudocódigo muestra cómo se cumplen a la vez el bloqueo acotado, el perro guardián y la aplicación '
       'de comandos en el borde de bloque:'),
     CODE(['void t_dsp(void *arg) {',
           '    canal = i2s_crear_canal();          // la ISR del GDMA queda en el núcleo 1',
           '    esp_task_wdt_add(NULL);             // suscripción al perro guardián',
           '    for (;;) {',
           '        esp_task_wdt_reset();',
           '        if (modo == REPOSO) {           // canal deshabilitado: el I2S no genera datos',
           '            if (xQueueReceive(q_cmd, &cmd, pdMS_TO_TICKS(500))) aplicar(&cmd);',
           '            continue;                   // vuelve a reiniciar el perro guardián',
           '        }',
           '        while (xQueueReceive(q_cmd, &cmd, 0)) aplicar(&cmd);   // borde de bloque',
           '        if (i2s_channel_read(canal, buf, sizeof buf, &n, pdMS_TO_TICKS(100)) != ESP_OK) {',
           '            contar_falla_i2s(); continue;',
           '        }',
           '        t0 = esp_cpu_get_cycle_count();',
           '        convertir(buf, x);  banco_filtros(x);  acumular(modo);   // Capítulo 3',
           '        registrar_ciclos(esp_cpu_get_cycle_count() - t0);',
           '        if (++nb == 11) { publicar(q_res);  nb = 0; }           // xQueueSend con plazo 0',
           '    }',
           '}']),
     P('aplicar() traduce los comandos: **PREPARAR** habilita el canal (i2s_channel_enable) y filtra sin '
       'acumular; **INICIAR** recibe la configuración y empieza a acumular sin reiniciar los filtros, que ya '
       'procesaron durante la espera de 3 s de CU-02; **CALIBRAR** y **PISO** habilitan el canal, reinician '
       'filtros y acumuladores y descartan los primeros 0,5 s (Capítulo 3); **DETENER** publica el resultado '
       'final; **REPOSO** deshabilita el canal. La configuración viaja **dentro** de INICIAR: T_DSP nunca lee '
       'la configuración global y no hay datos compartidos que proteger.'),
     P('La Figura 4.2 muestra la secuencia completa de una medición, desde el pulsador hasta el registro.'),
     *FIGURA('cap4_secuencia.png', 16.5,
             'Figura 4.2. Diagrama de secuencia de una medición de cabina (CU-02). La espera de 3 s la temporiza '
             'T_APP; T_DSP solo recibe comandos.'),
     P('**Sin inversión de prioridades.** Como cada recurso tiene un único dueño, en el diseño no hay mutex '
       'entre tareas de distinta prioridad. Si en el futuro hiciera falta uno, se usará un mutex de FreeRTOS, '
       'que implementa herencia de prioridad [8], y nunca un semáforo binario. La pantalla (SPI2) y la microSD '
       '(SDMMC) usan controladores distintos del ESP32-S3, así que tampoco comparten bus. Los únicos bloqueos '
       'que quedan son internos del núcleo del RTOS (sección 4.5).'),
     P('**Precisión de la integración.** T_DSP acumula Σx² por bloque en float y lo vuelca en acumuladores '
       'double por banda (corrige H4.9). La sesión completa, de hasta 120 s, se integra en el firmware '
       '(corrige H4.7).')])

# ───────────── 4.5 ─────────────
add([H1('4.5 Análisis temporal'),
     P('En esta sección los tiempos son **estimaciones con márgenes explícitos**, no mediciones. Ninguna es un '
       'WCET en sentido estricto: el valor que se usará es el **tiempo máximo observado** con la prueba '
       'PU-RT-02, al que se le exigirá estar por debajo de la cota pesimista.'),
     H2('Presupuesto de la tarea DSP'),
     P('El período de T_DSP es el de un bloque de entrada, T = 1024 / 48 000 = 21,33 ms. El costo del banco de '
       'filtros sale del Capítulo 3 (3,32 millones de multiplicaciones por segundo). Una sección de segundo '
       'orden en forma directa II transpuesta necesita 5 multiplicaciones y 4 sumas por muestra; con la unidad '
       'de punto flotante del ESP32-S3, que encadena multiplicación y suma, eso equivale a unos 4 a 6 ciclos por '
       'multiplicación. Se adopta **10 ciclos por multiplicación** como cota conservadora y luego se la duplica:'),
     KT(['Componente', 'Ciclos por bloque', 'Tiempo a 240 MHz'],
        [['Banco de filtros y antialias (70 827 multiplicaciones × 10)', '708 267', '2,95 ms'],
         ['Conversión de 1024 muestras de 24 bits a float', '6 144', '0,03 ms'],
         ['Cuadrado y suma de 2032 muestras de banda', '8 128', '0,03 ms'],
         ['Sobrecarga (lectura I2S, colas, contadores)', '20 000', '0,08 ms'],
         ['##C nominal / C pesimista (× 2)', '##742 539', '##3,09 ms / 6,19 ms']],
        [5000, 1900, 1937], size=18, center_cols=(1, 2)),
     CAP('Tabla 4.7. Presupuesto de ejecución de T_DSP por bloque. El factor 2 cubre fallos de caché y '
         'contención de bus.'),
     EQ('U_DSP = C / T = 3,09 / 21,33 = 14,5 %   (pesimista: 29,0 %)', 1),
     H2('Tiempo de respuesta en el núcleo 1'),
     P('Para T_DSP se aplica el análisis de tiempo de respuesta de prioridades fijas [4, 5], extendido con un '
       'término de bloqueo y la fluctuación de la activación:'),
     EQ('R = C + B + Σ_j ⌈(R + J_j) / T_j⌉ · C_j  +  J_DSP', 2),
     P('Cada término:'),
     B('**Interferencia (j):** en el núcleo 1 solo quedan el tick de FreeRTOS (1 kHz, ≈ 3 µs), la ISR del GDMA '
       '(una por descriptor, cada 10,67 ms, ≈ 5 µs) y la tarea IPC1 (prioridad 24; se supone una activación de '
       '20 µs cada 10 ms). La tarea y la ISR de esp_timer corren en el núcleo 0 por defecto, y el Wi-Fi, '
       'lwIP y el servidor HTTP se fijan al núcleo 0.'),
     B('**Bloqueo B:** en SMP las secciones críticas del núcleo del RTOS usan un candado compartido por ambos '
       'núcleos; una sección crítica larga en el núcleo 0 puede demorar la operación de cola de T_DSP. Se '
       'supone B = 50 µs, a medir.'),
     B('**Fluctuación J_DSP:** T_DSP se activa por datos, no por temporizador. Su activación fluctúa con la '
       'latencia de la ISR del GDMA, de unos pocos microsegundos.'),
     B('**Fuera del análisis:** las detenciones por operaciones de flash, que paralizan ambos núcleos, no se '
       'modelan como interferencia; las absorbe el anillo DMA (sección 4.6).'),
     KT(['Caso', 'C [ms]', 'R [ms]', 'D [ms]', 'Holgura [ms]', 'U total núcleo 1'],
        [['Nominal', '3,09', '3,19', '21,33', '18,15', '15,0 %'],
         ['Pesimista', '6,19', '6,29', '21,33', '15,04', '29,6 %']],
        [1600, 1300, 1300, 1300, 1600, 1737], size=18, center_cols=(1, 2, 3, 4, 5)),
     CAP('Tabla 4.8. Análisis de tiempo de respuesta de T_DSP con interferencia, bloqueo y fluctuación.'),
     P('El plazo se cumple con holgura incluso en el caso pesimista, y la utilización queda muy por debajo del '
       '70 % de RD-07. Con una sola tarea de aplicación en el núcleo, el criterio de utilización de Liu y Layland '
       '[3] es trivial; el análisis exacto de la ecuación (2) es el que aporta información.'),
     P('**Plazo efectivo y recuperación.** D = T es la condición para que el atraso no se acumule en régimen '
       'permanente, pero el anillo DMA permite que un bloque se termine tarde de forma transitoria. Después de '
       'una detención de duración S, T_DSP recupera el atraso en'),
     EQ('t_r = S · U / (1 − U)', 3),
     P('Con U = 0,29 (pesimista), una detención de 100 ms se recupera en 41 ms. La condición de diseño '
       'completa es entonces doble: U < 1 en régimen y un anillo que cubra la peor detención (sección 4.6).'),
     *FIGURA('cap4_cronograma.png', 16.5,
             'Figura 4.3. Cronograma de dos bloques a escala: DMA continuo, ISR por descriptor, T_DSP y actividad '
             'del núcleo 0.'),
     H2('Tiempo de respuesta en el núcleo 0'),
     P('En el núcleo 0 corren las tareas de la aplicación por debajo de las del sistema (Wi-Fi, esp_timer, lwIP), '
       'cuyos costos dependen del tráfico. Para mostrar el método se aplicó la ecuación (2) con **supuestos '
       'explícitos**: ráfagas de la tarea Wi-Fi de 1,5 ms cada 10 ms, lwIP 1 ms cada 10 ms y esp_timer 50 µs '
       'cada 10 ms. La utilización resultante es del 52 %:'),
     KT(['Tarea', 'Prio.', 'C supuesto [ms]', 'R [ms]', 'D [ms]', 'Resultado'],
        [['T_APP', '10', '1', '3,6', '50', 'Cumple'],
         ['T_UI', '8', '40 (dibujo)', '57,3', '234,7', 'Cumple'],
         ['T_STOR', '6', '30 (escritura de sesión)', '97,5', '1000', 'Cumple'],
         ['T_NET', '5', '5 (trama WS)', '106,1', '234,7', 'Cumple'],
         ['T_XFER', '4', '20 (trozo de OTA o CSV)', '133,8', '1000', 'Cumple'],
         ['T_MON', '2', '1', '134,8', '1000', 'Cumple']],
        [1500, 800, 2400, 1300, 1300, 1537], size=18, center_cols=(1, 2, 3, 4, 5)),
     CAP('Tabla 4.9. Análisis del núcleo 0 con costos supuestos. Las cifras se reemplazan por las medidas en '
         'PU-RT-04; lo importante es que el método y los plazos quedan definidos.'),
     H2('Latencias de extremo a extremo'),
     KT(['Trayecto', 'Cota', 'Comentario'],
        [['Intervalo entre resultados publicados', '11 bloques = 234,7 ms', 'RD-06 fija este período: ≤ 250 ms'],
         ['Comando de T_APP hasta que T_DSP lo aplica', '≤ T + C = 27,5 ms (pesimista)', 'Borde de bloque'],
         ['Muestra hasta la pantalla', '≤ 235 + 6,2 + 40 ≈ 281 ms', 'Latencia, no período: RD-06 no la limita'],
         ['Pulsador hasta el cambio de estado', '≤ 20 ms (antirrebote) + R_APP', 'Respuesta inmediata percibida']],
        [3300, 3000, 2537], size=18),
     CAP('Tabla 4.10. Latencias principales. El tiempo de dibujo depende de la biblioteca gráfica y se medirá.')])

# ───────────── 4.6 ─────────────
add([H1('4.6 Anillo DMA, flash y gestión de energía'),
     H2('Dimensionamiento del anillo DMA'),
     P('El anillo DMA absorbe cualquier intervalo en el que T_DSP no pueda ejecutarse. En ESP-IDF 5.4 el driver '
       'crea su cola de mensajes con **N − 1** entradas para N descriptores (i2s_common.c, línea 328): cuando '
       'se llena, la ISR descarta el descriptor más antiguo y llama a la función de aviso on_recv_q_ovf. La '
       'capacidad útil es Q = (N − 1) · 512 muestras, y el anillo no desborda mientras se cumpla:'),
     EQ('Q ≥ f_s · (S + C)    ⇒    S_máx = Q / f_s − C', 4),
     KT(['Descriptores × muestras', 'Q útil', 'Capacidad', 'Memoria', 'S_máx nominal', 'S_máx pesimista'],
        [['4 × 512', '1536', '32,0 ms', '8 kB', '28,9 ms', '25,8 ms'],
         ['8 × 512', '3584', '74,7 ms', '16 kB', '71,6 ms', '68,5 ms'],
         ['12 × 512', '5632', '117,3 ms', '24 kB', '114,2 ms', '111,1 ms'],
         [('16 × 512', 'D4EDDA'), ('7680', 'D4EDDA'), ('160,0 ms', 'D4EDDA'), ('32 kB', 'D4EDDA'),
          ('156,9 ms', 'D4EDDA'), ('153,8 ms', 'D4EDDA')]],
        [2100, 1100, 1300, 1200, 1500, 1637], size=18, center_cols=tuple(range(6))),
     CAP('Tabla 4.11. Detención máxima tolerable según el tamaño del anillo. Con data_bit_width = 32 bits y un '
         'canal, cada descriptor ocupa 512 × 4 = 2048 B, dentro del máximo de 4092 B del GDMA [7]; el ancho debe '
         'fijarse explícitamente en 32 bits.'),
     *FIGURA('cap4_ocupacion_dma.png', 16,
             'Figura 4.4. Simulación de la ocupación del anillo con una detención de 100 ms del núcleo 1: con 8 '
             'descriptores se pierden 1536 muestras; con 16, la ocupación llega al 67 % sin pérdidas. La '
             'simulación da la primera pérdida a partir de 72 ms y de 156 ms, respectivamente.'),
     P('**Decisión D4.2: anillo de 16 descriptores de 512 muestras (160 ms útiles, 32 kB de RAM interna).** '
       'Tolera detenciones de unos 154 ms aun con el C pesimista, con un costo cercano al 6 % de la SRAM interna '
       '(≈ 10 % de la memoria libre típica). Una pérdida se registra como **descriptores perdidos** (512 '
       'muestras cada uno), no como bloques.'),
     H2('Escrituras en flash'),
     P('Mientras se borra o escribe la flash externa, la caché se deshabilita en **ambos núcleos** y solo puede '
       'ejecutarse código en IRAM [2]. Lo mismo ocurre con las lecturas directas de una partición. El borrado de '
       'un sector puede tardar, según la hoja de datos de la memoria, desde decenas hasta cientos de '
       'milisegundos, más que el anillo. ESP-IDF 5.4 ofrece la suspensión automática de operaciones largas, '
       'pero solo para ciertos chips de flash y con advertencias en su documentación; no se usa en esta '
       'versión y queda como mejora a evaluar. La Tabla 4.12 enumera las fuentes de acceso a flash y su '
       'tratamiento.'),
     KT(['Fuente', 'Cuándo ocurre', 'Medida'],
        [['Calibración, piso de ruido, configuración (NVS)', 'Al terminar CU-01, CU-10, CU-07',
          'Solo en REPOSO (D4.3): el valor se guarda al volver al reposo'],
         ['Actualización OTA', 'CU-08', 'Solo en REPOSO y ACTUALIZANDO; la FSM la rechaza durante la medición'],
         ['Configuración del Wi-Fi en NVS', 'Al conectar o cambiar parámetros',
          'esp_wifi_set_storage(WIFI_STORAGE_RAM); datos de calibración PHY leídos solo al arranque'],
         ['Páginas del panel web', 'Cada petición HTTP', 'Recursos embebidos en el binario y servidos desde la '
          'memoria mapeada, sin lecturas de partición'],
         ['Volcado de memoria (core dump)', 'Solo ante una falla fatal', 'Excepción aceptada: el sistema ya está '
          'en falla y se reinicia']],
        [2900, 2300, 3637], size=16),
     CAP('Tabla 4.12. Fuentes de acceso a la flash y su tratamiento.'),
     P('**Decisión D4.3:** ninguna escritura en flash ocurre durante los estados MIDIENDO, CALIBRANDO, '
       'MIDIENDO_PISO ni durante la espera previa a la medición. Además, la ISR del I2S y el manejador del GDMA '
       'se compilan en IRAM (CONFIG_I2S_ISR_IRAM_SAFE; ESP-IDF exige entonces que on_recv_q_ovf también esté en '
       'IRAM), el lazo de filtrado y sus coeficientes se ubican en memoria interna y los búferes de audio nunca '
       'en PSRAM. La microSD usa el controlador SDMMC y no la flash del programa, de modo que escribir en ella no '
       'detiene la caché; aun así, la sesión se escribe al terminar.'),
     H2('Gestión de energía'),
     P('El driver i2s_std toma por sí mismo un candado de energía ESP_PM_APB_FREQ_MAX mientras el canal está '
       'habilitado, de modo que no hay sueño liviano con el I2S en marcha. Por eso T_DSP **deshabilita el '
       'canal en REPOSO** y espera comandos con un plazo de 500 ms, reiniciando el perro guardián (pseudocódigo '
       'de la sección 4.4). Durante la espera, MIDIENDO, CALIBRANDO y MIDIENDO_PISO, T_APP toma además un '
       'candado ESP_PM_CPU_FREQ_MAX, que fija la frecuencia de CPU y también impide el sueño liviano, para que el '
       'tiempo de ejecución de T_DSP no cambie.'),
     P('**Decisión D4.4** (candados de energía durante la medición y frecuencia reducida en REPOSO). Su aporte a '
       'RD-08 es acotado: con el punto de acceso Wi-Fi activo la radio no duerme, así que el ahorro en REPOSO '
       'proviene sobre todo de la frecuencia de CPU y del brillo de la pantalla. La autonomía se verifica con '
       'EN-07. El Capítulo 5 estima 9,0 h en el peor caso al fin de vida de la celda, de modo que apagar el Wi-Fi '
       'tras un tiempo sin clientes queda solo como mitigación si EN-07 muestra menos margen.')])

# ───────────── 4.7 ─────────────
add([H1('4.7 Robustez y supervisión'),
     KT(['Mecanismo', 'Implementación', 'Reacción'],
        [['Desborde del anillo DMA', 'Función de aviso on_recv_q_ovf (en IRAM) → contador atómico de descriptores',
          'La sesión se marca "con pérdidas" y se informa; nunca se descarta en silencio (corrige H4.2)'],
         ['Perro guardián de tareas', 'T_DSP y T_APP suscritas al TWDT; ambas esperan con plazo ≤ 500 ms y lo '
          'reinician en cada ciclo; plazo del TWDT de 2 s', 'Pánico controlado (el sistema registra la falla, '
          'guarda el volcado y se reinicia)'],
         ['Desborde de pila', 'Canario de FreeRTOS y marca de agua periódica en T_MON',
          'Alarma si la reserva baja del 25 %'],
         ['Uso de CPU', 'Estadísticas de ejecución de FreeRTOS; T_MON publica el porcentaje por tarea',
          'Verificación de RD-07 en EN-06'],
         ['Tiempo de ejecución de T_DSP', 'Contador de ciclos al inicio y al fin de cada bloque; máximo e '
          'histograma', 'Publicado en q_res; alarma en funcionamiento si C > T/2 = 10,7 ms'],
         ['Fallas fatales', 'Volcado de memoria en una partición de flash', 'Descarga desde el panel técnico'],
         ['Caída de tensión', 'Detector de caída de tensión (brown-out) y lectura de batería en T_MON',
          'Batería crítica (VSYS ≤ 3,50 V con carga, promedio de 1 s, histéresis de 100 mV; Capítulo 5): T_APP '
          'cierra la sesión y los archivos y libera POWER_HOLD, lo que corta la alimentación (estado APAGADO)'],
         ['Falla de la microSD', 'T_STOR informa el error por evento', 'La sesión queda en RAM y se reintenta; '
          'T_DSP nunca espera a T_STOR']],
        [2000, 3800, 3037], size=16),
     CAP('Tabla 4.13. Mecanismos de supervisión y reacción ante fallas.'),
     P('El umbral de alarma en funcionamiento (C > 10,7 ms, la mitad del período) no coincide con el criterio de '
       'aceptación de PU-RT-02 (C máximo observado ≤ 6,2 ms): el primero detecta una anomalía en campo con '
       'margen para que el anillo la absorba; el segundo valida en laboratorio que el presupuesto estimado se '
       'cumple.'),
     H2('Configuración de FreeRTOS y ESP-IDF'),
     KT(['Opción de configuración', 'Valor', 'Motivo'],
        [['FREERTOS_HZ', '1000', 'Resolución de 1 ms (el prototipo usaba 100)'],
         ['ESP_WIFI_TASK_PINNED_TO_CORE_0', 'y', 'Wi-Fi fuera del núcleo de tiempo real'],
         ['LWIP_TCPIP_TASK_AFFINITY_CPU0', 'y', 'lwIP no tiene afinidad por defecto'],
         ['httpd_config_t.core_id', '0', 'El servidor HTTP no tiene afinidad por defecto'],
         ['HTTPD_WS_SUPPORT / HTTPD_WS_PRE_HANDSHAKE_CB_SUPPORT', 'y / y', 'WebSocket y control de Host y Origin '
          'antes del protocolo (Cap. 6)'],
         ['LWIP_MAX_SOCKETS', '16', '4 paneles, servidor, DNS y sockets internos (Cap. 6)'],
         ['BOOTLOADER_APP_ROLLBACK_ENABLE', 'y', 'Reversión si la imagen nueva no se confirma'],
         ['SECURE_SIGNED_APPS_NO_SECURE_BOOT', 'y', 'Solo se aceptan actualizaciones firmadas'],
         ['BOOTLOADER_FACTORY_RESET / BOOTLOADER_OTA_DATA_ERASE', 'y / y', 'Recuperación de fábrica con el '
          'pulsador MENÚ; vuelve a la imagen factory'],
         ['PARTITION_TABLE_CUSTOM', 'y', 'nvs, otadata, cal, factory, ota_0, ota_1 y coredump (Tabla 6.13)'],
         ['I2S_ISR_IRAM_SAFE', 'y', 'DMA operativo durante operaciones de flash'],
         ['FREERTOS_CHECK_STACKOVERFLOW_CANARY', 'y', 'Detección de desbordes de pila'],
         ['FREERTOS_GENERATE_RUN_TIME_STATS', 'y', 'Uso de CPU por tarea'],
         ['ESP_TASK_WDT_PANIC / ESP_TASK_WDT_TIMEOUT_S', 'y / 2', 'Una tarea colgada reinicia el equipo (valor '
          'por defecto: 5 s)'],
         ['ESP_COREDUMP_ENABLE_TO_FLASH', 'y', 'Diagnóstico posterior a fallas'],
         ['PM_ENABLE', 'y', 'Frecuencia reducida en REPOSO (con candados durante la medición)']],
        [4200, 1100, 3537], size=16),
     CAP('Tabla 4.14. Opciones de configuración relevantes (prefijo CONFIG_ omitido; nombres verificados en '
         'ESP-IDF 5.4).')])

# ───────────── 4.8 ─────────────
add([H1('4.8 Plan de verificación'),
     KT(['ID', 'Procedimiento', 'Criterio de aceptación', 'Verifica'],
        [['PU-RT-01', 'Pruebas unitarias de la FSM de T_APP en el host (Unity), con la tabla de transiciones del '
          'anexo (v0.3), incluidos los rechazos de escritura en flash', '100 % de las transiciones cubiertas',
          'D4.3 · CU-01, CU-02, CU-07, CU-08, CU-10'],
         ['PU-RT-02', 'Tiempo de ejecución de T_DSP con contador de ciclos en 10⁵ bloques, con y sin Wi-Fi activo',
          'C máx. observado ≤ 6,2 ms; R ≤ D', 'RD-07 · D4.6'],
         ['PU-RT-03', 'Inyección de una espera activa en T_DSP de 100 ms y de 200 ms', '100 ms: 0 desbordes; '
          '200 ms: desborde contado y sesión marcada', 'RD-07 · D4.2, D4.8'],
         ['PU-RT-04', 'Carga de comunicaciones durante una medición: 4 clientes WebSocket, descarga de CSV y '
          'conexiones Wi-Fi repetidas; medición de los tiempos del núcleo 0', '0 desbordes; C de T_DSP sin cambio '
          'significativo; plazos de la Tabla 4.9', 'RD-07 · CU-04 · EN-06'],
         ['PU-RT-05', 'Pedido de escritura en NVS u OTA durante MIDIENDO', 'Rechazado por la FSM; sin desbordes',
          'RD-11 · D4.3'],
         ['PU-RT-06', 'Retiro de la microSD durante la escritura de una sesión', 'Sin bloqueo de T_DSP ni de T_APP; '
          'sesión retenida y reescrita', 'RD-09'],
         ['PU-RT-07', 'Registro de los candados de energía (esp_pm_dump_locks) y de la frecuencia de CPU durante '
          'una medición', 'Sin cambios de frecuencia ni sueño en MIDIENDO; sueño liviano en REPOSO sin Wi-Fi',
          'RD-08 · D4.4'],
         ['PU-RT-08', 'Tono de amplitud conocida durante 120 s; nivel del firmware frente a referencia en doble '
          'precisión', 'Diferencia ≤ 0,01 dB', 'D4.7 · RD-05'],
         ['PU-RT-09', 'Tarea de prueba que deja de reiniciar el perro guardián', 'Reinicio en ≤ 2 s y volcado de '
          'memoria disponible', 'D4.8'],
         ['EN-06', 'Funcionamiento continuo de 8 h con registro de desbordes, CPU, pilas y latencia',
          '0 desbordes; CPU ≤ 70 %; refresco ≤ 250 ms', 'RD-06, RD-07'],
         ['EN-08 / EN-10', 'Cortes de energía durante la escritura; OTA válida y corrupta', 'Ver anteproyecto',
          'RD-09, RD-11']],
        [1150, 3700, 2400, 1587], size=16),
     CAP('Tabla 4.15. Pruebas de este capítulo y ensayos del anteproyecto relacionados. D4.1 y D4.5 se '
         'verifican por inspección de código (ningún búfer compartido, ningún mutex en T_DSP).')])

# ───────────── 4.9 ─────────────
add([H1('4.9 Conclusiones y decisiones'),
     KT(['ID', 'Decisión', 'Justificación', 'Verificación'],
        [['D4.1', 'Captura y DSP en una sola tarea (T_DSP) sobre el anillo DMA de i2s_std',
          'Elimina el conjunto de búferes y su carrera (H4.1)', 'Inspección'],
         ['D4.2', 'Anillo DMA de 16 × 512 muestras (160 ms útiles, 32 kB)',
          'Tolera ≈ 154 ms de detención con C pesimista', 'PU-RT-03'],
         ['D4.3', 'Ningún acceso de escritura a flash durante la medición; Wi-Fi en RAM; web embebida',
          'La flash detiene la caché de ambos núcleos (precedente: H4.4)', 'PU-RT-01, PU-RT-05'],
         ['D4.4', 'Canal I2S deshabilitado en REPOSO; candado CPU_FREQ_MAX durante la medición',
          'Reloj y C estables; ahorro en reposo', 'PU-RT-07, EN-07'],
         ['D4.5', 'Un dueño por recurso y mensajes por valor; sin mutex en el camino de tiempo real',
          'Sin inversión de prioridades ni interbloqueos', 'Inspección'],
         ['D4.6', 'Núcleo 1 dedicado a T_DSP (prioridad 20), con afinidad explícita de todas las tareas',
          'R ≤ 6,3 ms frente a D = 21,3 ms; U ≤ 30 %', 'PU-RT-02, PU-RT-04'],
         ['D4.7', 'L_eq de sesión integrado en el firmware con acumuladores double',
          'Equipo autónomo (H4.7); precisión (H4.9)', 'PU-RT-08'],
         ['D4.8', 'Supervisión: contador de desbordes, TWDT, canario, estadísticas de CPU, volcado de memoria',
          'RD-07 verificable; diagnóstico en campo', 'PU-RT-03, PU-RT-09']],
        [700, 3500, 2900, 1737], size=16),
     CAP('Tabla 4.16. Decisiones de diseño del capítulo y su verificación.'),
     H2('Pendientes'),
     B('Medir en el ESP32-S3 los tiempos reales: C de T_DSP, bloqueo B, costos de las interrupciones, ráfagas del '
       'Wi-Fi y tiempo de dibujo (PU-RT-02, PU-RT-04).'),
     B('Elegir la biblioteca gráfica y verificar que T_UI cumpla su plazo blando.'),
     B('Evaluar la suspensión automática de la flash con el chip concreto del módulo.'),
     H2('Historial de revisión'),
     KT(['Versión', 'Cambios'],
        [['0.1', 'Borrador inicial.'],
         ['0.2', 'Revisión con tres revisores independientes (técnico de tiempo real, trazabilidad y evaluador '
          'académico): capacidad útil del anillo N − 1 verificada en el driver; afinidad explícita de lwIP y del '
          'servidor HTTP; esp_timer fuera del núcleo 1; RTA con bloqueo y fluctuación; análisis del núcleo 0; '
          'recuperación tras detenciones; fuentes de flash (Wi-Fi, web, volcado); candado de energía del propio '
          'driver y T_DSP en REPOSO; nuevo hallazgo H4.4 (NVS desde la tarea DSP); simulación del conjunto de '
          'búferes con métrica corregida; alternativas, EDF, pseudocódigo y diagrama de secuencia; pruebas '
          'PU-RT-07 a 09. Decisiones propagadas al anteproyecto y al anexo de Ingeniería de Software v0.3. '
          'Registro: revision_egm/registro_cap4_v0.2.md.'],
         ['0.2.1', 'Alineación con el Capítulo 5: T_MON dueña de la lectura de batería y de las señales del cargador '
          '(eventos a q_evt); umbral de batería crítica de 3,50 V filtrado; apagado real liberando POWER_HOLD; '
          'margen de autonomía referido al Capítulo 5.'],
         ['0.2.2', 'Alineación con el Capítulo 6: T_NET es la tarea de esp_http_server; nueva T_XFER (prio 4) para '
          'transferencias largas; colas q_net, q_lect y StreamBuffer; q_evt de 64 B; T_MON dueña del I2C del RTC; '
          'opciones de WebSocket, sockets, OTA firmada, reversión y recuperación de fábrica.']],
        [1100, 7737], size=17),
     H1('Referencias del capítulo'),
     *[P(r, size=20, align='left') for r in [
         '[1] Barry, R. Mastering the FreeRTOS Real Time Kernel — A Hands-On Tutorial Guide. Real Time Engineers Ltd.',
         '[2] Espressif Systems. ESP-IDF Programming Guide v5.4: I2S (i2s_std), FreeRTOS (SMP), SPI Flash API '
         '(restricciones de concurrencia y suspensión automática), Task Watchdog Timer, Power Management; y '
         'código fuente de los componentes esp_driver_i2s, esp_system, esp_timer, lwip y esp_http_server.',
         '[3] Liu, C. L.; Layland, J. W. Scheduling algorithms for multiprogramming in a hard-real-time '
         'environment. Journal of the ACM, 20(1), 1973.',
         '[4] Joseph, M.; Pandya, P. Finding response times in a real-time system. The Computer Journal, 29(5), 1986.',
         '[5] Audsley, N.; Burns, A.; Richardson, M.; Tindell, K.; Wellings, A. Applying new scheduling theory to '
         'static priority pre-emptive scheduling. Software Engineering Journal, 8(5), 1993.',
         '[6] Buttazzo, G. Hard Real-Time Computing Systems, 3.ª ed. Springer, 2011.',
         '[7] Espressif Systems. ESP32-S3 Technical Reference Manual (GDMA, I2S, caché) y ESP32-S3 Datasheet.',
         '[8] Sha, L.; Rajkumar, R.; Lehoczky, J. Priority inheritance protocols: an approach to real-time '
         'synchronization. IEEE Transactions on Computers, 39(9), 1990.']]])

ensamblar(TPL, body, FIGURA, OUT)
print('OK', OUT)
