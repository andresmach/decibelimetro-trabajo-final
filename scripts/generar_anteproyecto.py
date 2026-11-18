#!/usr/bin/env python3
"""Completa ModeloAnteproyecto(1).docx con el contenido del anteproyecto.

Uso:  python3 -I generar_anteproyecto.py <plantilla.docx> <figura.png> <salida.docx>

El contenido vive en este archivo (secciones CONTENIDO_*), para poder
re-generar el documento cada vez que se pulan los textos.
"""
import re
import sys
import zipfile
from xml.sax.saxutils import escape

TPL, IMG, OUT = sys.argv[1], sys.argv[2], sys.argv[3]

sys.path.insert(0, __import__('os').path.dirname(__file__))
from docx_xml import *  # noqa: E402,F401,F403

# ───────────────────────── CONTENIDO: portada ─────────────────────────
TITULO = ('Analizador autónomo de ruido ambiente por bandas de octava para la '
          'verificación de cabinas audiométricas según ISO 8253-1')
AUTOR = 'Andrés Machtey'
DIRECTOR = 'Esp. Víctor Valotto (Profesor Titular, FIUNER)'
FECHA = 'Noviembre de 2026, Oro Verde, Paraná, Entre Ríos.'

# ───────────────────────── CONTENIDO: secciones ─────────────────────────
S = {}

S['Resumen'] = [
    P('La validez de una audiometría tonal depende de que el ruido ambiente dentro de la cabina no '
      'enmascare los tonos de prueba de menor intensidad. La norma **ISO 8253-1** fija, para cada banda '
      'de octava, el nivel máximo de presión sonora admisible; sin embargo, en la mayoría de los servicios '
      'de fonoaudiología esta condición no se verifica de forma rutinaria, porque un sonómetro con filtros '
      'de octava tiene un costo elevado y su uso exige formación técnica.'),
    P('Este proyecto propone diseñar, implementar y validar un **instrumento embebido autónomo y '
      'portátil**, basado en un microcontrolador ESP32-S3 con FreeRTOS y un micrófono MEMS digital (I2S), '
      'que mida el nivel continuo equivalente (Leq) en las siete bandas de octava audiométricas '
      '(125 Hz a 8 kHz), compare cada banda con los límites de la norma y emita un veredicto '
      '**APTA / NO APTA** en el lugar. El equipo funcionará a batería, con pantalla y botones propios, '
      'registrará cada sesión en una tarjeta microSD y publicará los datos por Wi-Fi a un panel web desde '
      'el que se obtiene el historial y el informe imprimible.'),
    P('El trabajo parte de un prototipo desarrollado en el curso de Procesamiento Digital de Señales '
      '(ESP32 + INMP441 conectado a una PC). Su análisis permitió identificar fallas de diseño, como filtros '
      'de octava fuera de especificación, dependencia de una PC y un margen de ruido propio insuficiente, '
      'que el presente proyecto corrige aplicando técnicas propias de la especialización: arquitectura de '
      'firmware en capas sobre RTOS, procesamiento multitasa de tiempo real, diseño de hardware de bajo '
      'ruido y bajo consumo, ingeniería de requisitos y verificación sistemática mediante ensayos.'),
]

S['Objetivo General'] = [
    P('Diseñar, implementar y validar un instrumento embebido autónomo y portátil que mida el nivel de '
      'presión sonora continuo equivalente por bandas de octava (125 Hz – 8 kHz) y verifique en el lugar '
      'el cumplimiento de los niveles máximos de ruido ambiente establecidos por la norma ISO 8253-1 para '
      'cabinas audiométricas, registrando y documentando cada medición.'),
]

S['Objetivos particulares'] = [
    B('Relevar las necesidades de los usuarios y especificar los requisitos del sistema, modelándolos '
      'mediante casos de uso e historias de usuario con trazabilidad hacia los ensayos.'),
    B('Diseñar un banco de filtros de octava IIR conforme a la norma IEC 61260-1 (clase 2 como mínimo, con '
      'objetivo de diseño clase 1), validado por simulación numérica antes de su implementación en el '
      'microcontrolador.'),
    B('Reestructurar el firmware sobre FreeRTOS en una arquitectura por capas: captura I2S/DMA sin pérdida '
      '(API i2s_std), procesamiento DSP en tiempo real, cálculo de Leq y máquina de estados de la aplicación.'),
    B('Diseñar el hardware del instrumento: alimentación por batería con regulación de bajo ruido, interfaz '
      'local (pantalla, botones e indicadores), almacenamiento en microSD, circuito impreso y gabinete.'),
    B('Implementar un servidor web embebido con comunicación WebSocket por Wi-Fi e integrarlo con el '
      'software de gestión existente (historial e informe PDF).'),
    B('Implementar un procedimiento de calibración con calibrador acústico (94 dB SPL a 1 kHz) con '
      'persistencia del factor de calibración y control de su vigencia.'),
    B('Caracterizar el instrumento: respuesta de los filtros, ruido propio, linealidad, exactitud, '
      'desempeño de tiempo real y autonomía, comparándolo con un sonómetro de referencia.'),
    B('Documentar el desarrollo y elaborar los manuales de usuario y técnico.'),
]

S['Alcances y limitaciones'] = [
    H2('Alcances'),
    B('Prototipo funcional (TRL 5–6) de un instrumento portátil autónomo, validado en laboratorio y en al '
      'menos una cabina audiométrica en condiciones reales de uso.'),
    B('Medición simultánea de las 7 bandas de octava audiométricas (125 Hz a 8 kHz) con tiempo de '
      'integración configurable y veredicto según la tabla de límites de ISO 8253-1.'),
    B('Firmware completo (captura, DSP, aplicación, interfaz local, servidor web, almacenamiento, '
      'calibración y actualización OTA) y diseño de hardware propio (esquemático, PCB y gabinete).'),
    B('Adaptación del software de gestión existente (servidor Python, panel web e informe PDF) a la nueva '
      'conexión inalámbrica.'),
    H2('Limitaciones'),
    B('El instrumento **no será homologado** ni certificado metrológicamente (por ejemplo, ante el INTI). La '
      'conformidad con IEC 61260-1 / IEC 61672-1 clase 2 es un objetivo de diseño verificado con ensayos '
      'propios, no una certificación.'),
    B('El ruido propio del micrófono limita el nivel mínimo medible. Con el ICS-43434 elegido, el margen '
      'estimado frente al límite más exigente de la norma (500 Hz) es de 7,5 dB (el INMP441 del prototipo '
      'daba 3,5 dB). La estimación supone ruido blanco y el componente 1/f puede reducir el margen en las '
      'bandas graves; se confirmará con el ensayo EN-02 y, si no alcanza, se evaluará una cápsula analógica de '
      'bajo ruido con conversor I2S.'),
    B('El alcance se limita a la verificación de cabinas para **conducción aérea con auriculares**. Los '
      'límites para conducción ósea y campo libre son inferiores al piso de ruido de los micrófonos MEMS.'),
    B('La exactitud absoluta depende de contar con un calibrador acústico y un sonómetro de referencia. Su '
      'acceso deberá gestionarse a través de la Facultad o de un laboratorio externo.'),
    B('Quedan fuera del alcance: el análisis en tercios de octava, el monitoreo continuo de 24 h, la '
      'integración con sistemas de información hospitalarios y la fabricación en serie.'),
    B('El sistema no almacena datos de pacientes: solo registra datos de la cabina, del equipo y del '
      'operador.'),
]

S['Métodos y Técnicas'] = [
    H2('Gestión e ingeniería de requisitos'),
    P('Se adoptará un ciclo de vida **iterativo e incremental** (Scrum adaptado a un desarrollador, con '
      'iteraciones de dos semanas). La verificación seguirá un **modelo en V**: cada requisito tendrá un '
      'ensayo asociado. Los requisitos se modelarán con UML (diagramas de casos de uso, de secuencia y de '
      'estados) en Enterprise Architect y se complementarán con historias de usuario con criterios de '
      'aceptación. Una matriz de trazabilidad vinculará requisitos, casos de uso, historias y ensayos.'),
    H2('Procesamiento digital de señales'),
    B('Diseño de filtros pasabanda Butterworth de 8.º orden por banda (prototipo de orden 4, implementado '
      'como 4 secciones biquad en cascada), calculados con GNU Octave (paquete signal) y verificados '
      'automáticamente contra las máscaras de atenuación de IEC 61260-1. El orden 6 no cumple la máscara '
      '(ver Capítulo 3).'),
    B('Esquema **multitasa** a 48 kHz: las bandas graves se procesan tras diezmado sucesivo por 2, con un '
      'filtro antialias elíptico entre etapas. Reduce el costo computacional a la mitad y mantiene todas las '
      'bandas con el mismo condicionamiento numérico.'),
    B('Los coeficientes se exportan automáticamente a un archivo de cabecera C (octave_coeffs.h): el '
      'firmware no contiene coeficientes escritos a mano.'),
    B('Implementación en punto flotante de 32 bits (forma directa II transpuesta) con la biblioteca '
      'ESP-DSP optimizada para el núcleo Xtensa LX7, e integración del cuadrado de la señal para obtener '
      'el Leq por banda.'),
    B('Validación cruzada: los mismos vectores de prueba (tonos, barridos y ruido rosa) se procesan en '
      'GNU Octave y en el firmware, comparando los resultados banda por banda.'),
    H2('Firmware embebido'),
    B('ESP-IDF v5.x sobre FreeRTOS con afinidad explícita de todas las tareas: captura y DSP en una única '
      'tarea del núcleo 1 que lee el anillo DMA del driver i2s_std; aplicación, interfaz, almacenamiento y '
      'Wi-Fi en el núcleo 0. Cada recurso tiene un solo dueño y las tareas se comunican con colas de mensajes '
      'por valor, sin búferes compartidos ni mutex en el camino de tiempo real (ver Capítulo 4).'),
    B('Análisis de tiempo de respuesta con prioridades fijas y dimensionamiento del anillo DMA para absorber '
      'detenciones; ninguna escritura en flash durante la medición.'),
    B('Arquitectura en capas (HAL / controladores, servicios DSP, lógica de aplicación, comunicaciones) y '
      'máquina de estados explícita de la aplicación.'),
    B('Medición de tiempos de ejecución con el contador de ciclos de la CPU, de uso de CPU y de margen de '
      'pila; contador de desbordes del anillo DMA; perro guardián de tareas y volcado de memoria ante fallas.'),
    B('Servidor HTTP y WebSocket embebido, sistema de archivos FAT en microSD, NVS para calibración y '
      'configuración, y actualización OTA con particiones duales.'),
    B('Pruebas unitarias de los módulos DSP en el host (framework Unity) y en el microcontrolador, con '
      'vectores de referencia generados en Octave, y pruebas de integración en la placa mediante un modo de '
      'prueba que inyecta señales sintéticas.'),
    H2('Hardware'),
    B('Captura del esquemático y diseño del PCB en KiCad; alimentación a batería Li-ion con cargador USB-C y '
      'regulador LDO de bajo ruido dedicado al micrófono; separación de planos y rutas de las fuentes de '
      'ruido digital (Wi-Fi, conmutación).'),
    B('Gabinete diseñado en CAD e impreso en 3D, con el micrófono separado del cuerpo para reducir '
      'reflexiones.'),
    H2('Verificación y gestión de configuración'),
    B('Ensayos eléctricos y acústicos con calibrador, generador de señales y sonómetro de referencia, más '
      'un ensayo de campo en una cabina audiométrica real.'),
    B('Control de versiones con Git/GitHub, compilación automatizada (GitHub Actions) y registro de '
      'incidencias.'),
]

S['Material y Equipo'] = [
    T(['Categoría', 'Ítem', 'Disponibilidad'],
      [['Desarrollo', 'Placa ESP32-S3-DevKitC-1 (N16R8) y ESP32 DevKit v1 del prototipo previo', 'Propio / a adquirir'],
       ['Sensores', 'Micrófono MEMS I2S ICS-43434 para el instrumento (encapsulado LGA: placa adaptadora o montaje por refusión); INMP441 del prototipo como referencia comparativa', 'Propio / a adquirir'],
       ['Interfaz', 'Pantalla TFT 2,4–2,8" (SPI), pulsadores, LED bicolor, módulo microSD', 'A adquirir'],
       ['Energía', 'Celda Li-ion 18650 o LiPo ≈ 2000 mAh, cargador con protección, LDO de bajo ruido', 'A adquirir'],
       ['Fabricación', 'PCB prototipo (5 unidades), filamento PETG para el gabinete', 'A adquirir'],
       ['Instrumental', 'Osciloscopio, analizador lógico, multímetro, fuente de laboratorio', 'Propio / laboratorio FIUNER'],
       ['Acústica', 'Calibrador acústico 94 dB SPL @ 1 kHz (IEC 60942)', 'A gestionar (FIUNER / externo)'],
       ['Acústica', 'Sonómetro de referencia clase 1 con filtros de octava', 'A gestionar (FIUNER / externo)'],
       ['Ensayo de campo', 'Acceso a una cabina audiométrica en uso', 'A gestionar (servicio de fonoaudiología)'],
       ['Software', 'ESP-IDF v5.x, GNU Octave + paquete signal, gnuplot, Python 3 (FastAPI), KiCad, FreeCAD, Enterprise Architect, Git', 'Libre / licencia académica'],
       ['Equipo de trabajo', 'PC con Linux, parlante y placa de audio para generar tonos de prueba', 'Propio']],
      [1700, 5100, 2038]),
]

# ── Tabla de requerimientos (celda derecha) ──
R = {}
R['Uso previsto del producto:'] = [
    P('Verificar, antes de una sesión de audiometría tonal o de forma periódica, que el ruido ambiente '
      'dentro de una cabina o sala audiométrica no supere los niveles máximos por banda de octava de la '
      'norma ISO 8253-1, y registrar y documentar el resultado.', size=20),
    P('Es un instrumento de medición auxiliar: no diagnostica, no entra en contacto con pacientes y no '
      'almacena datos de pacientes.', size=20),
]
R['Perfil del usuario previsto.'] = [
    B('**Primario:** licenciado/a en Fonoaudiología o técnico/a en audiometría, sin formación específica en '
      'acústica; necesita un veredicto claro y un registro que pueda adjuntar.', size=20),
    B('**Secundario:** personal técnico o de ingeniería clínica, a cargo de la calibración, la '
      'configuración y el mantenimiento.', size=20),
]
R['Requisitos de desempeño HW, SW o FW (incluyendo uso normal, almacenamiento, manipulación y mantenimiento)'] = [
    P('**Convención:** RD-xx = requisito de desempeño, numerado para su trazabilidad hacia casos de uso, '
      'decisiones de diseño y ensayos (EN-xx). Entre corchetes se indica dónde se implementa: [HW] hardware '
      '(componentes electrónicos, alimentación, gabinete); [FW] firmware (programa que corre en el '
      'microcontrolador ESP32-S3); [SW] software que corre fuera del equipo (panel web en el navegador y '
      'servidor de gestión). Ver "Siglas y abreviaturas" al final.', size=18, italic=True),
    P('**Uso normal**', size=20, after=40, keep_next=True),
    B('**RD-01** [HW+FW] Medición simultánea del Leq en 7 bandas de octava (125 a 8000 Hz).', size=20),
    B('**RD-02** [FW] Filtros de octava dentro de las máscaras de IEC 61260-1 clase 2.', size=20),
    B('**RD-03** [HW] Ruido propio por banda al menos 5 dB por debajo del límite ISO correspondiente.', size=20),
    B('**RD-04** [HW+FW] Rango hasta ≥ 100 dB SPL sin saturación; linealidad ±1,0 dB.', size=20),
    B('**RD-05** [FW] Exactitud a 1 kHz tras calibración: ±0,5 dB respecto del calibrador.', size=20),
    B('**RD-06** [FW+SW] Integración configurable de 10 a 120 s (30 s por defecto); actualización de la indicación, en pantalla y en el panel web, cada ≤ 250 ms.', size=20),
    B('**RD-07** [FW] Tiempo real sin pérdida de bloques (0 desbordes en 8 h) y uso de CPU del núcleo DSP ≤ 70 %.', size=20),
    B('**RD-08** [HW] Autonomía ≥ 8 h con Wi-Fi activo; carga completa ≤ 4 h por USB-C.', size=20),
    P('**Almacenamiento**', size=20, after=40, before=60, keep_next=True),
    B('**RD-09** [HW+FW] Registro de ≥ 1000 sesiones en microSD, sin corrupción ante un corte de energía.', size=20),
    B('**RD-12** [HW+FW] Guardado entre −10 y 50 °C y de 10 a 90 % de humedad relativa sin condensación, sin '
      'pérdida de la calibración, la configuración ni los registros, que se conservan sin alimentación '
      '(memoria no volátil y microSD). Consumo con el equipo apagado ≤ 100 µA, de modo que la batería '
      'conserve ≥ 50 % de carga tras 3 meses guardado.', size=20),
    P('**Manipulación**', size=20, after=40, before=60, keep_next=True),
    B('**RD-13** [HW] Resiste una caída de 1 m sobre piso duro dentro de su estuche y sigue funcionando, con '
      'la calibración dentro de ±0,5 dB. El micrófono tiene una protección (pantalla antiviento o tapa) y los '
      'conectores USB-C y microSD quedan protegidos del polvo durante el transporte.', size=20),
    P('**Mantenimiento**', size=20, after=40, before=60, keep_next=True),
    B('**RD-10** [FW] Factor de calibración persistente con fecha; aviso de vencimiento a los 12 meses.', size=20),
    B('**RD-11** [FW] Actualización de firmware OTA con reversión automática ante falla.', size=20),
    B('Verificación con calibrador antes de cada jornada; transporte en estuche; batería reemplazable.', size=20),
]
R['Interfaz con el usuario:'] = [
    B('**Local:** pantalla color con barras por banda frente al límite, veredicto APTA / NO APTA, estado de '
      'la batería y de la calibración; 3 pulsadores (medir, calibrar, menú) y un LED bicolor visible desde '
      'fuera de la cabina.', size=20),
    B('**Remota:** el equipo genera su propio punto de acceso Wi-Fi (no requiere internet) con un panel web en '
      'tiempo real, historial de sesiones, descarga CSV e informe PDF.', size=20),
    B('Idioma español; las acciones que borran datos o cambian la calibración piden confirmación.', size=20),
]
R['Características físicas:'] = [
    P('Equipo de mano, de aproximadamente 160 × 80 × 35 mm y ≤ 350 g. Micrófono en el extremo superior, '
      'separado del cuerpo; rosca de 1/4" para trípode; conector USB-C; ranura microSD accesible. Gabinete '
      'prototipo impreso en 3D (PETG).', size=20),
]
R['Límites y tolerancias:'] = [
    B('Los límites de ISO 8253-1:2010 se guardan como una tabla configurable (conducción aérea por defecto; '
      'las demás condiciones de la norma se pueden seleccionar). Los valores del prototipo previo (35 / 25 / '
      '21 / 26 / 34 / 37 / 43 dB SPL) **se revisarán contra el texto de la norma**.', size=20),
    B('Filtros: tolerancias de IEC 61260-1 clase 2.', size=20),
    B('Diferencia frente al sonómetro de referencia: ±1,5 dB entre 250 Hz y 4 kHz y ±2,0 dB en 125 Hz y 8 kHz.', size=20),
]
R['Requisitos relacionados al ambiente:'] = [
    P('Uso en interiores: 10 a 35 °C, humedad relativa de 25 a 80 % sin condensación. Almacenamiento: −10 a '
      '50 °C. Estabilización térmica de 5 min antes de medir. Debe convivir con equipamiento clínico sin '
      'interferencias apreciables (inmunidad básica) y sin que su propio Wi-Fi degrade la medición.', size=20),
]
R['Vida útil prevista:'] = [
    P('5 años, con verificación metrológica anual. La batería es reemplazable (≈ 300 a 500 ciclos) y el '
      'firmware se puede actualizar en campo durante toda la vida útil.', size=20),
]
R['Datos históricos (Eventos adversos/quejas/fallas de diseños previos, etc) - Documentación de diseños previos:'] = [
    P('Prototipo del curso de Procesamiento Digital de Señales (UNER, 2026): ESP32 + INMP441, FreeRTOS, '
      'enlace UART/USB con un servidor Python (FastAPI, SQLite, PDF). Repositorios: '
      'github.com/andresmach/decibilimetro-iso8253 y github.com/andresmach/decibel-iso (PWA para celular). '
      'El análisis de este diseño mostró las siguientes fallas:', size=20),
    B('Los coeficientes biquad no dependen de la frecuencia central (equivalen a ω₀ = 0): las bandas de '
      '250 Hz a 8 kHz se comportan como pasabajos (por ejemplo, la de 1 kHz deja pasar de menos de 10 Hz a '
      '1117 Hz) y la de 125 Hz mide 1,4 octavas. Además, redondeados a float32, los filtros de 1 kHz y 8 kHz '
      'quedan inestables. Las mediciones por banda no son válidas.', size=20),
    B('Un único biquad de 2.º orden no alcanza la selectividad de IEC 61260-1; además, se citaba IEC 61672 '
      'para los filtros, cuando la norma que corresponde es IEC 61260-1.', size=20),
    B('El ruido propio del INMP441 (≈ 33 dBA) deja un margen escaso frente al límite de 21 dB SPL en 500 Hz.', size=20),
    B('El sistema dependía de una PC y de un puente físico D17→RX0; la API I2S estaba obsoleta; el buffer '
      'circular podía sobrescribirse durante el procesamiento.', size=20),
    B('Un diseño anterior con micrófono analógico KY-037 fue descartado por su ruido y su respuesta en '
      'frecuencia no documentada. La PWA para celular es solo indicativa (control automático de ganancia y '
      'respuesta del micrófono desconocida).', size=20),
]
R['Costos:'] = [
    P('Prototipo, materiales estimados (USD, valores de referencia sin impuestos de importación):', size=20),
    B('ESP32-S3-DevKitC 12 · micrófonos MEMS (×2) 16 · pantalla TFT 10 · microSD + tarjeta 7', size=20),
    B('batería + cargador/protección 11 · LDO de bajo ruido y pasivos 8 · pulsadores/LED/conectores 5', size=20),
    B('PCB (5 u.) 20 · gabinete 3D 10 → **total ≈ USD 100 por prototipo**', size=20),
    P('Calibrador y sonómetro de referencia: préstamo a gestionar (su compra superaría USD 1000). Esfuerzo de '
      'ingeniería estimado: __HORAS__ h.', size=20),
]
R['Requisitos normativos (seguridad eléctrica, compatibilidad electromagnética, normas sanitarias, etc)'] = [
    B('**ISO 8253-1:2010**: niveles máximos de ruido ambiente en audiometría (requisito funcional central).', size=20),
    B('**IEC 61260-1:2014**: filtros de banda de octava (clase 2 como objetivo de diseño).', size=20),
    B('**IEC 61672-1:2013**: sonómetros (referencia para Leq y ponderaciones); **IEC 60942**: calibradores acústicos.', size=20),
    B('**IEC 61010-1**: seguridad eléctrica de equipos de medición; **IEC 61326-1**: compatibilidad '
      'electromagnética de equipos de medición (no es un producto médico, por lo que no aplica IEC 60601).', size=20),
    B('**IEC 62133-2**: seguridad de las baterías de litio; módulo Wi-Fi precertificado (verificar homologación ENACOM).', size=20),
]
R['Otros requisitos esenciales para el diseño:'] = [
    B('Arquitectura de firmware modular y testeable; estilo de codificación según BARR-C / guía MISRA-C.', size=20),
    B('Trazabilidad entre requisitos, casos de uso, historias de usuario y ensayos (documento anexo de '
      'Ingeniería de Software).', size=20),
    B('Wi-Fi protegido con WPA2 y contraseña configurable; sin datos de pacientes.', size=20),
    B('Código abierto (licencia MIT) y documentación reproducible.', size=20),
]

S['Entregables principales del proyecto (con fecha)'] = [
    T(['N.º', 'Entregable', 'Fecha'],
      [['E1', 'Especificación de requisitos (ERS), modelo de casos de uso e historias de usuario, plan de ensayos', '15/01/2027'],
       ['E2', 'Informe de diseño del banco de filtros y scripts de verificación contra IEC 61260-1', '26/02/2027'],
       ['E3', 'Firmware v0.5: captura y DSP validados en placa de desarrollo, con pruebas unitarias y medición del tiempo de ejecución en la placa', '31/03/2027'],
       ['E4', 'Esquemático, PCB, lista de materiales y gabinete del prototipo', '30/04/2027'],
       ['E5', 'Prototipo integrado v1.0 (hardware, firmware, interfaz local y web)', '11/06/2027'],
       ['E6', 'Informe de ensayos y verificación de requisitos (incluye el ensayo en cabina real)', '09/07/2027'],
       ['E7', 'Informe final, manuales de usuario y técnico, y repositorio publicado', '30/07/2027']],
      [700, 6538, 1600], center_cols=(0, 2)),
]

S['Ensayos (propuestos para verificación de requerimientos)'] = [
    T(['ID', 'Req.', 'Procedimiento', 'Criterio de aceptación'],
      [['EN-01', 'RD-02', 'Barrido senoidal digital inyectado en el modo de prueba y, luego, barrido eléctrico; respuesta de cada filtro', 'Dentro de las máscaras de IEC 61260-1 clase 2'],
       ['EN-02', 'RD-03', 'Micrófono en un acoplador sellado / recinto aislado; Leq de 60 s por banda', '≥ 5 dB por debajo del límite ISO en cada banda'],
       ['EN-03', 'RD-05, RD-10', 'Calibración con calibrador de 94 dB / 1 kHz; 10 repeticiones retirando y recolocando el calibrador', 'Lectura 94,0 ± 0,5 dB; desvío estándar ≤ 0,2 dB'],
       ['EN-04', 'RD-04', 'Tonos en escalones de 5 dB, de 30 a 100 dB SPL, comparados con el sonómetro de referencia', 'Error de linealidad ≤ ±1,0 dB'],
       ['EN-05', 'RD-01', 'Medición simultánea con el sonómetro de referencia en una sala y en una cabina real (ruido rosa y ambiente)', '±1,5 dB (250 Hz – 4 kHz); ±2 dB (125 Hz y 8 kHz)'],
       ['EN-06', 'RD-06, RD-07', 'Funcionamiento continuo de 8 h con registro de desbordes, uso de CPU, pila y latencia', '0 desbordes; CPU ≤ 70 %; actualización ≤ 250 ms'],
       ['EN-07', 'RD-08', 'Descarga completa con Wi-Fi activo y medición continua; luego, carga completa', 'Autonomía ≥ 8 h; carga ≤ 4 h'],
       ['EN-08', 'RD-09', '1000 sesiones sintéticas y 50 cortes de energía aleatorios durante la escritura', 'Sin pérdida de sesiones cerradas ni corrupción de archivos'],
       ['EN-09', 'Ambiente', 'Piso de ruido con Wi-Fi activo frente a inactivo; funcionamiento a 10 y 35 °C (según disponibilidad)', 'Diferencia ≤ 1 dB; deriva ≤ 0,5 dB'],
       ['EN-10', 'RD-11', 'OTA válida, OTA con imagen corrupta y corte durante la actualización', 'El equipo arranca siempre en una imagen válida'],
       ['EN-11', 'Interfaz', 'Prueba de usabilidad con 3 o más fonoaudiólogos/as: calibrar, medir y obtener el informe sin asistencia', 'Tarea completa en < 5 min; SUS ≥ 70'],
       ['EN-12', 'RD-12', 'Equipo apagado 72 h a −10 °C y 72 h a 50 °C (cámara climática, según disponibilidad); medición del consumo apagado', 'Calibración, configuración y registros intactos; consumo ≤ 100 µA'],
       ['EN-13', 'RD-13', 'Caídas de 1 m sobre piso duro dentro del estuche (6 caras); luego, verificación funcional y con calibrador', 'Funciona; lectura 94,0 ± 0,5 dB']],
      [800, 1100, 4100, 2838], size=17, center_cols=(0, 1)),
]

TAREAS = [
    # (id, nombre, horas, meses activos [0=Dic-26 … 7=Jul-27])
    ('1', '##Requisitos y modelado', None, None),
    ('1.1', 'Relevamiento con usuarios (fonoaudiólogos/as)', 8, [0]),
    ('1.2', 'Especificación de requisitos (ERS)', 12, [0, 1]),
    ('1.3', 'Casos de uso, historias de usuario y trazabilidad', 12, [0, 1]),
    ('1.4', 'Plan de ensayos', 8, [1]),
    ('2', '##Procesamiento digital de señales', None, None),
    ('2.1', 'Estudio de ISO 8253-1, IEC 61260-1 e IEC 61672-1', 12, [0]),
    ('2.2', 'Diseño y simulación del banco de filtros multitasa', 24, [1, 2]),
    ('2.3', 'Implementación embebida (ESP-DSP)', 24, [2, 3]),
    ('2.4', 'Pruebas unitarias (host y MCU) y validación cruzada con Octave', 20, [2, 3]),
    ('3', '##Firmware', None, None),
    ('3.1', 'Arquitectura en capas y migración a i2s_std', 24, [2]),
    ('3.2', 'Tareas RTOS, buffers, Leq y máquina de estados', 32, [3]),
    ('3.3', 'Calibración y persistencia (NVS)', 12, [3, 4]),
    ('3.4', 'Registro en microSD', 16, [4]),
    ('3.5', 'Interfaz local (pantalla, botones, LED)', 24, [4, 5]),
    ('3.6', 'Wi-Fi, servidor web y WebSocket', 24, [5]),
    ('3.7', 'Actualización OTA', 8, [6]),
    ('3.8', 'Pruebas de concurrencia y robustez (FSM, fallas inyectadas)', 12, [3, 4]),
    ('4', '##Hardware', None, None),
    ('4.1', 'Selección de componentes y montaje del micrófono ICS-43434', 16, [1, 2]),
    ('4.2', 'Diseño de la alimentación a batería', 16, [3]),
    ('4.3', 'Esquemático', 20, [3, 4]),
    ('4.4', 'Diseño del PCB', 20, [4]),
    ('4.5', 'Fabricación y armado', 10, [5]),
    ('4.6', 'Gabinete', 8, [5, 6]),
    ('5', '##Software de gestión', None, None),
    ('5.1', 'Adaptación del servidor, historial e informe PDF', 30, [6]),
    ('6', '##Ensayos', None, None),
    ('6.1', 'Ensayos eléctricos, de filtros y de ruido propio', 30, [6]),
    ('6.2', 'Ensayos de tiempo real, autonomía, almacenamiento y caída', 20, [5, 6]),
    ('6.3', 'Comparación con referencia, cabina real y usabilidad', 20, [6, 7]),
    ('7', '##Documentación', None, None),
    ('7.1', 'Manual de usuario', 12, [7]),
    ('7.2', 'Manual técnico', 16, [6, 7]),
    ('7.3', 'Informe final', 32, [7]),
]
TOTAL_H = sum(t[2] for t in TAREAS if t[2])
R['Costos:'] = [x.replace('__HORAS__', str(TOTAL_H)) for x in R['Costos:']]

S['Desglose del trabajo en tareas'] = [
    T(['ID', 'Tarea', 'Horas'],
      [[t[0], t[1], '' if t[2] is None else str(t[2])] if t[2] else
       [('##' + t[0], 'EDEDED'), (t[1], 'EDEDED'),
        ('##' + str(sum(x[2] for x in TAREAS if x[2] and x[0].startswith(t[0] + '.'))), 'EDEDED')]
       for t in TAREAS] + [[('', 'D9E2F3'), ('##Total', 'D9E2F3'), ('##' + str(TOTAL_H), 'D9E2F3')]],
      [800, 6838, 1200], center_cols=(0, 2)),
]

MESES = ['Dic', 'Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul']
GANTT_ROWS = []
for t in TAREAS:
    if t[2] is None:
        GANTT_ROWS.append([('##' + t[0] + ' ' + t[1].lstrip('#'), 'EDEDED')] + [('', 'EDEDED')] * 8)
    else:
        GANTT_ROWS.append([t[0] + ' ' + t[1]] + [('', '4472C4') if m in t[3] else '' for m in range(8)])
HITOS = {'E1': 1, 'E2': 2, 'E3': 3, 'E4': 4, 'E5': 6, 'E6': 7, 'E7': 7}
hito_row = [('##Entregables', 'FFF2CC')]
for m in range(8):
    hs = [k for k, v in HITOS.items() if v == m]
    hito_row.append(('##' + ' '.join(hs), 'FFF2CC'))
GANTT_ROWS.append(hito_row)

S['Diagrama de Gantt'] = [
    P('Período: diciembre de 2026 a julio de 2027 (meses 2026–2027). Las celdas sombreadas indican la '
      'ejecución de cada tarea; la última fila ubica los entregables.', size=20),
    T(['Tarea'] + MESES, GANTT_ROWS, [4838] + [500] * 8, size=15, center_cols=tuple(range(1, 9))),
]

S['Referencias'] = [B(r, size=20) for r in [
    'ISO 8253-1:2010. Acoustics — Audiometric test methods — Part 1: Pure-tone air and bone conduction audiometry. International Organization for Standardization.',
    'IEC 61260-1:2014. Electroacoustics — Octave-band and fractional-octave-band filters — Part 1: Specifications. International Electrotechnical Commission.',
    'IEC 61672-1:2013. Electroacoustics — Sound level meters — Part 1: Specifications. International Electrotechnical Commission.',
    'IEC 60942:2017. Electroacoustics — Sound calibrators. International Electrotechnical Commission.',
    'IEC 61010-1:2010 / IEC 61326-1:2020. Seguridad eléctrica y compatibilidad electromagnética de equipos de medida, control y laboratorio.',
    'Espressif Systems. ESP-IDF Programming Guide (v5.x) y ESP32-S3 Technical Reference Manual.',
    'Espressif Systems. ESP-DSP Library — Documentation.',
    'TDK InvenSense. ICS-43434 Multi-Mode Microphone with I2S Digital Output — Datasheet. InvenSense. INMP441 — Datasheet.',
    'Barry, R. Mastering the FreeRTOS Real Time Kernel — A Hands-On Tutorial Guide. Real Time Engineers Ltd.',
    'Smith, S. W. The Scientist and Engineer\'s Guide to Digital Signal Processing. California Technical Publishing, 1997.',
    'Oppenheim, A. V.; Schafer, R. W. Tratamiento de señales en tiempo discreto, 3.ª ed. Pearson, 2011.',
    'Sommerville, I. Ingeniería de Software, 9.ª ed. Pearson, 2011.',
    'Cohn, M. User Stories Applied: For Agile Software Development. Addison-Wesley, 2004.',
    'Machtey, A. Decibelímetro de bandas de octava ISO 8253-1 — firmware y servidor. github.com/andresmach/decibilimetro-iso8253, 2026.',
    'GNU Octave y paquete signal 1.4.5 (diseño y verificación de filtros).',
]]
SIGLAS = [
    ('RD-xx', 'Requisito de desempeño (numerado)'), ('EN-xx', 'Ensayo de verificación'),
    ('E1…E7', 'Entregables del proyecto'), ('CU / HU', 'Caso de uso / historia de usuario'),
    ('HW', 'Hardware: electrónica, alimentación y gabinete'),
    ('FW', 'Firmware: programa del microcontrolador'),
    ('SW', 'Software fuera del equipo: panel web y servidor'),
    ('ERS', 'Especificación de requisitos de software'),
    ('DSP', 'Procesamiento digital de señales'), ('IIR', 'Filtro de respuesta al impulso infinita'),
    ('Leq', 'Nivel continuo equivalente de presión sonora'),
    ('dB SPL', 'Nivel de presión sonora (ref. 20 µPa)'), ('dBA', 'Nivel con ponderación A'),
    ('MEMS', 'Sistema microelectromecánico (micrófono)'), ('I2S', 'Bus serie de audio digital'),
    ('DMA', 'Acceso directo a memoria'), ('RTOS', 'Sistema operativo de tiempo real (FreeRTOS)'),
    ('NVS', 'Memoria no volátil del ESP32'), ('OTA', 'Actualización de firmware inalámbrica'),
    ('PCB', 'Circuito impreso'), ('TFT', 'Pantalla de cristal líquido color'),
    ('LDO', 'Regulador lineal de baja caída'), ('LGA', 'Encapsulado de contactos planos'),
    ('PWA', 'Aplicación web progresiva (celular)'), ('TRL', 'Nivel de madurez tecnológica'),
]
S['Referencias'] += [
    P('Siglas y abreviaturas', size=24, bold=True, before=240, after=80, keep_next=True, align='left'),
    T(['Sigla', 'Significado', 'Sigla', 'Significado'],
      [[a, b, c, d] for (a, b), (c, d) in zip(SIGLAS[0::2], SIGLAS[1::2] + [('', '')])],
      [1100, 3319, 1100, 3319], size=17),
]

# ───────────────────────── ensamblado ─────────────────────────
z = zipfile.ZipFile(TPL)
files = {n: z.read(n) for n in z.namelist()}
doc = files['word/document.xml'].decode('utf-8')

PARA = re.compile(r'<w:p[ >].*?</w:p>', re.S)


def text_of(p):
    return ''.join(re.findall(r'<w:t[^>]*>(.*?)</w:t>', p))


def find_para(label, start=0):
    for m in PARA.finditer(doc, start):
        if text_of(m.group(0)).strip() == label:
            return m
    raise KeyError(label)


# Portada
m = find_para('Título')
newp = m.group(0).replace('<w:t>Título</w:t>', f'<w:t>{escape(TITULO)}</w:t>')
newp = newp.replace('<w:sz w:val="40"/><w:szCs w:val="40"/>', '<w:sz w:val="32"/><w:szCs w:val="32"/>')
doc = doc[:m.start()] + newp + doc[m.end():]

# Imagen de portada en lugar de "Foto ilustrativa"
CX = 5400000
from PIL import Image  # noqa: E402
w, h = Image.open(IMG).size
CY = int(CX * h / w)
m = find_para('Foto ilustrativa')
img_p = (f'<w:p><w:pPr><w:pStyle w:val="Normal"/><w:spacing w:before="120" w:after="120"/><w:jc w:val="center"/></w:pPr>'
         f'{IMG_RUN("rIdDiag1", CX, CY, 101, "diagrama_bloques.png")}</w:p>')
doc = doc[:m.start()] + img_p + doc[m.end():]

for label, value in (('Autor:', AUTOR), ('Director:', DIRECTOR)):
    m = find_para(label)
    newp = m.group(0).replace('<w:t xml:space="preserve"> </w:t>', f'<w:t xml:space="preserve"> {escape(value)}</w:t>', 1)
    doc = doc[:m.start()] + newp + doc[m.end():]

m = find_para('Fecha, Oro Verde, Paraná, Entre Ríos.')
doc = doc[:m.start()] + m.group(0).replace('Fecha, Oro Verde, Paraná, Entre Ríos.', escape(FECHA)) + doc[m.end():]

# Quitar párrafos vacíos de relleno entre Director y Fecha (para que la portada entre en una página)
md = find_para('Director:' + ' ' + DIRECTOR)
mf = find_para(FECHA)
between = doc[md.end():mf.start()]
empties = PARA.findall(between)
keep = 2
between_new = ''.join(empties[:keep])
doc = doc[:md.end()] + between_new + doc[mf.start():]

# Secciones del cuerpo: reemplazar el párrafo vacío siguiente al título (o insertar)
for label, content in S.items():
    m = find_para(label)
    nxt = PARA.match(doc, m.end())
    body = ''.join(content)
    if nxt and not text_of(nxt.group(0)).strip() and '<w:drawing' not in nxt.group(0):
        doc = doc[:nxt.start()] + body + doc[nxt.end():]
    else:
        doc = doc[:m.end()] + body + doc[m.end():]

# Tabla de requerimientos: celda derecha de cada fila
for label, content in R.items():
    m = find_para(label)
    tc_end = doc.index('</w:tc>', m.end()) + len('</w:tc>')
    tc2_start = doc.index('<w:tc>', tc_end)
    tc2_end = doc.index('</w:tc>', tc2_start)
    seg = doc[tc2_start:tc2_end]
    pm = PARA.search(seg)
    seg_new = seg[:pm.start()] + ''.join(content) + seg[pm.end():]
    doc = doc[:tc2_start] + seg_new + doc[tc2_end:]

# Quitar párrafos vacíos sobrantes antes de "Referencias"
m = find_para('Referencias')
prev = doc.rfind('</w:tbl>', 0, m.start())
gap = doc[prev:m.start()]
doc = doc[:prev] + '</w:tbl>' + P('', after=60) + doc[m.start():]

# Saltos de página antes de los títulos largos
for label in ('Requerimientos', 'Diagrama de Gantt'):
    m = find_para(label)
    doc = doc[:m.start()] + '<w:p><w:r><w:br w:type="page"/></w:r></w:p>' + doc[m.start():]

# Títulos de la plantilla: mantener con el párrafo siguiente
for label in list(S) + ['Requerimientos']:
    m = find_para(label)
    doc = doc[:m.start()] + m.group(0).replace('<w:pStyle w:val="Normal"/>', '<w:pStyle w:val="Normal"/><w:keepNext/>', 1) + doc[m.end():]

files['word/document.xml'] = doc.encode('utf-8')

# Relación e imagen
rels = files['word/_rels/document.xml.rels'].decode()
rels = rels.replace('</Relationships>',
                    '<Relationship Id="rIdDiag1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/diagrama_bloques.png"/></Relationships>')
files['word/_rels/document.xml.rels'] = rels.encode()
files['word/media/diagrama_bloques.png'] = open(IMG, 'rb').read()
ct = files['[Content_Types].xml'].decode()
if 'Extension="png"' not in ct:
    ct = ct.replace('<Default ', '<Default Extension="png" ContentType="image/png"/><Default ', 1)
files['[Content_Types].xml'] = ct.encode()

with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED) as zo:
    for n, data in files.items():
        zo.writestr(n, data)
print('OK', OUT, 'horas totales:', TOTAL_H)
