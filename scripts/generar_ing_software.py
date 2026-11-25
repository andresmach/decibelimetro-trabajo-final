#!/usr/bin/env python3
"""Documento de Ingeniería de Software: actores, casos de uso, historias de usuario,
máquina de estados y trazabilidad. Reutiliza el encabezado de la plantilla UNER.

Uso: python3 -I generar_ing_software.py <plantilla.docx> <casos_de_uso.png> <salida.docx>
"""
import os
import re
import sys
import zipfile

sys.path.insert(0, os.path.dirname(__file__))
from docx_xml import P, B, H2, T, IMG_RUN  # noqa: E402

TPL, IMG, OUT = sys.argv[1], sys.argv[2], sys.argv[3]


def H1(text):
    return P(text, size=28, bold=True, before=240, after=120, keep_next=True, align='left')


def PB():
    return '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'


def CAP(text):
    return P(text, size=18, italic=True, align='center', after=200)


body = []
add = body.extend

# ───────────── Portada ─────────────
add([P('', after=600),
      P('Anexo de Ingeniería de Software', size=44, bold=True, align='center', color='1E5E9F', after=200),
      P('Analizador autónomo de ruido ambiente por bandas de octava para la verificación de cabinas '
        'audiométricas según ISO 8253-1', size=28, bold=True, align='center', after=600),
      P('Modelo de casos de uso · Historias de usuario · Máquina de estados · Trazabilidad',
        size=24, align='center', after=1400),
      P('**Autor:** Andrés Machtey', size=26, align='left', after=120),
      P('**Director propuesto:** Esp. Víctor Valotto (FIUNER)', size=26, align='left', after=120),
      P('**Versión:** 0.5 (alineada con los Capítulos 3, 4, 5 y 6) · Noviembre de 2026', size=26, align='left', after=120),
      PB()])

# ───────────── 1. Propósito ─────────────
add([H1('1. Propósito y alcance'),
     P('Este anexo modela el comportamiento esperado del sistema desde el punto de vista de sus usuarios. '
       'Complementa la tabla de requerimientos del anteproyecto (identificadores **RD-xx**) y la vincula '
       'con los ensayos de verificación (**EN-xx**). El modelo sigue la notación UML 2 y la estructura de '
       'especificación de escenarios de Enterprise Architect: precondiciones, flujo principal, flujos '
       'alternativos y postcondiciones.'),
     P('El documento se irá refinando en cada iteración del proyecto; la versión inicial corresponde al '
       'entregable **E1** del plan de trabajo.'),
     P('**Cambios de la versión 0.5:** el servidor de gestión consulta las sesiones en forma incremental en lugar '
       'de recibirlas (CU-02); cuatro clientes y cierre 1013 al quinto (CU-04); PIN de 6 dígitos, contraseña, canal '
       'y potencia del Wi-Fi en CU-07; abandono de la OTA por tiempo y reversión ante verificación pendiente en la '
       'máquina de estados; pruebas PU-COM y fila de seguridad en la matriz de trazabilidad (Capítulo 6).', size=20),
     P('**Cambios de la versión 0.4:** eventos de USB conectado y desconectado (modo de carga y tiempo estimado), '
       'batería baja y batería crítica con apagado real por el enclavamiento POWER_HOLD, pulsación larga para '
       'apagar y medición con USB conectado (Capítulo 5); pruebas PU-HW en la matriz de trazabilidad.', size=20),
     P('**Cambios de la versión 0.3:** estado ESPERA (3 s) entre REPOSO y MIDIENDO; rechazo de escrituras en '
       'flash y OTA durante la medición (decisión D4.3 del Capítulo 4); transiciones por imagen OTA corrupta, '
       'falla fatal y desborde del anillo DMA; marca «con pérdidas» en CU-02 y CU-05; microSD con error en '
       'CU-02; descarga del volcado de memoria en CU-07; pruebas PU-RT en la matriz de trazabilidad.',
       size=20),
     P('**Cambios de la versión 0.2:** nuevo caso de uso CU-10 «Medir piso de ruido propio» y regla de piso de '
       'ruido en CU-02, CU-03 y CU-05 (decisión D3.8 del Capítulo 3); historias HU-14 a HU-16; estado '
       'MIDIENDO_PISO en la máquina de estados; requisitos RD-12 (almacenamiento) y RD-13 (manipulación); '
       'columna de pruebas unitarias PU-DSP en la matriz de trazabilidad. **Convención de abreviaturas:** '
       'RD = requisito de desempeño; CU = caso de uso; HU = historia de usuario; EN = ensayo; PU = prueba '
       'unitaria; D3.x = decisión del Capítulo 3; HW / FW / SW = hardware / firmware / software externo.',
       size=20),
     H1('2. Actores'),
     T(['Actor', 'Tipo', 'Descripción y responsabilidades'],
       [['Fonoaudiólogo/a', 'Humano, primario',
         'Profesional que realiza audiometrías. Verifica la cabina antes de la sesión, calibra en campo, '
         'consulta resultados y obtiene el informe. No necesita formación en acústica.'],
        ['Técnico/a', 'Humano, secundario',
         'Personal técnico o de ingeniería clínica. Hereda todos los casos del fonoaudiólogo/a y además '
         'configura el instrumento (límites, red, tiempos) y actualiza el firmware.'],
        ['Calibrador acústico', 'Dispositivo externo',
         'Fuente de referencia de 94 dB SPL a 1 kHz (IEC 60942) que se acopla al micrófono durante la calibración.'],
        ['Servidor de gestión', 'Sistema externo',
         'Aplicación Python (FastAPI) que, al conectarse al Wi-Fi del equipo, consulta las sesiones nuevas '
         '(GET /api/v1/sesiones con cursor), mantiene el historial central y genera el informe PDF. Es opcional: '
         'el instrumento funciona sin ella.']],
       [2000, 1700, 5138], size=18),
     PB()])

# ───────────── 3. Diagrama ─────────────
from PIL import Image  # noqa: E402
w, h = Image.open(IMG).size
CX = 5600000
CY = int(CX * h / w)
add([H1('3. Diagrama de casos de uso'),
     f'<w:p><w:pPr><w:jc w:val="center"/></w:pPr>{IMG_RUN("rIdUC1", CX, CY, 201, "casos_de_uso.png")}</w:p>',
     CAP('Figura 1. Diagrama de casos de uso del sistema (UML 2). Fuente PlantUML: modelos/casos_de_uso.puml'),
     T(['ID', 'Caso de uso', 'Actor principal', 'Prioridad', 'Requisitos'],
       [['CU-01', 'Calibrar instrumento', 'Fonoaudiólogo/a', 'Must', 'RD-05, RD-10'],
        ['CU-02', 'Medir cabina', 'Fonoaudiólogo/a', 'Must', 'RD-01, RD-06, RD-07'],
        ['CU-03', 'Evaluar conformidad ISO 8253-1', '(incluido)', 'Must', 'RD-01, RD-02'],
        ['CU-04', 'Ver medición en tiempo real', 'Fonoaudiólogo/a', 'Should', 'RD-06'],
        ['CU-05', 'Generar informe de sesión', 'Fonoaudiólogo/a', 'Should', 'RD-09'],
        ['CU-06', 'Consultar historial', 'Fonoaudiólogo/a', 'Should', 'RD-09'],
        ['CU-07', 'Configurar instrumento', 'Técnico/a', 'Must', 'Límites, RD-06'],
        ['CU-08', 'Actualizar firmware (OTA)', 'Técnico/a', 'Could', 'RD-11'],
        ['CU-09', 'Exportar registros', 'Fonoaudiólogo/a', 'Could', 'RD-09'],
        ['CU-10', 'Medir piso de ruido propio', 'Técnico/a', 'Must', 'RD-03']],
       [900, 3200, 1900, 1100, 1738], size=18, center_cols=(0, 3)),
     P('Prioridades según el método MoSCoW (Must / Should / Could / Won\'t).', size=18, italic=True),
     PB()])

# ───────────── 4. Especificación ─────────────
def spec(uid, nombre, d):
    rows = [['##Actores', d['act']], ['##Descripción', d['desc']], ['##Precondiciones', d['pre']],
            ['##Disparador', d['trig']], ['##Flujo principal', d['main']],
            ['##Flujos alternativos y excepciones', d['alt']], ['##Postcondiciones', d['post']],
            ['##Trazabilidad', d['traz']]]
    return [H2(f'{uid} — {nombre}'), T(None, rows, [2200, 6638], size=18)]


add([H1('4. Especificación de casos de uso')])

add(spec('CU-01', 'Calibrar instrumento', dict(
    act='Fonoaudiólogo/a (o Técnico/a); Calibrador acústico',
    desc='Ajusta el factor de sensibilidad del sistema para que la banda de 1 kHz indique el nivel nominal del calibrador.',
    pre='Equipo encendido hace ≥ 5 min (estabilización térmica). Batería > 20 %. Estado REPOSO.',
    trig='El usuario elige «Calibrar» en la pantalla o en el panel web.',
    main='1. El sistema solicita colocar el calibrador y confirma el nivel nominal (94,0 dB por defecto).\n'
         '2. El usuario acopla el calibrador, lo enciende y confirma.\n'
         '3. El sistema pasa a CALIBRANDO, reinicia los filtros, descarta 0,5 s y mide durante 5 s la banda de 1 kHz.\n'
         '4. El sistema verifica la estabilidad de la lectura (desvío ≤ 0,2 dB) y calcula el nuevo factor.\n'
         '5. El sistema muestra la corrección aplicada y pide confirmación.\n'
         '6. El usuario confirma; el sistema guarda el factor con fecha y hora en NVS y vuelve a REPOSO.',
    alt='4a. Lectura inestable o señal ausente: el sistema informa «Calibrador no detectado», no modifica el factor y vuelve a REPOSO.\n'
        '4b. Corrección mayor de ±6 dB: el sistema advierte una posible falla del micrófono y exige la confirmación del Técnico/a.\n'
        '5a. El usuario cancela: se descarta el nuevo factor.',
    post='Factor de calibración vigente y persistente; registro del evento de calibración en la microSD.',
    traz='RD-05, RD-10 · HU-03, HU-04 · D3.5 · PU-DSP-03 · EN-03')))

add(spec('CU-02', 'Medir cabina', dict(
    act='Fonoaudiólogo/a',
    desc='Mide el Leq por banda de octava durante el tiempo de integración configurado y obtiene el veredicto de la cabina.',
    pre='Calibración vigente (≤ 12 meses) y verificación de campo del día realizada. Piso de ruido propio '
        'medido (CU-10). Estado REPOSO.',
    trig='El usuario presiona «Medir» (botón físico o panel web).',
    main='1. El sistema solicita (opcional) el identificador de la cabina y del operador.\n'
         '2. El usuario coloca el equipo en el punto de medición, cierra la cabina y confirma.\n'
         '3. El sistema pasa a ESPERA durante 3 s para que se disipe el ruido de manipulación (los filtros ya '
         'procesan, lo que cubre su transitorio) y luego a MIDIENDO.\n'
         '4. Cada ≤ 250 ms el sistema actualiza en pantalla y por WebSocket los niveles parciales por banda.\n'
         '5. Al cumplirse el tiempo de integración, el sistema ejecuta CU-03 «Evaluar conformidad».\n'
         '6. El sistema muestra el veredicto y las bandas que no cumplen, y enciende el LED (verde o rojo).\n'
         '7. El sistema guarda la sesión en la microSD y la deja disponible para la consulta incremental del '
         'servidor de gestión.',
    alt='1a. Calibración vencida: el sistema avisa y permite medir solo en modo «indicativo», que queda marcado en el informe.\n'
        '1b. Piso de ruido no medido: se usa el piso típico de la hoja de datos y la sesión queda marcada.\n'
        '2a. USB conectado: se permite medir; la sesión queda marcada «medida con USB conectado».\n'
        '4a. El usuario detiene la medición: la sesión se guarda como «interrumpida», sin veredicto.\n'
        '4b. Banda saturada: se marca «saturada»; como el nivel supera cualquier límite de la norma, la banda no cumple.\n'

        '4c. Batería crítica (VSYS ≤ 3,50 V con carga, promediada 1 s): el sistema cierra y guarda la sesión y se apaga liberando el enclavamiento de alimentación.\n'
        '4d. Desborde del anillo DMA: la medición continúa y la sesión se marca «con pérdidas», con la cantidad de muestras perdidas.\n'
        '4e. Pedido de escritura en flash (calibración, configuración u OTA): se rechaza hasta volver a REPOSO.\n'
        '5a. Banda cercana al piso de ruido propio: se aplica la regla de piso (CU-03, paso 1a).\n'
        '7a. El servidor de gestión no se conecta: la sesión queda en la microSD hasta la próxima consulta (sin '
        'pérdida ni duplicados, porque el servidor pide desde su último cursor).\n'
        '7b. microSD ausente o con error: la sesión queda en memoria, se avisa al usuario y se reintenta la escritura.',
    post='Sesión registrada con fecha, cabina, operador, Leq por banda, veredicto, estado de la calibración y, '
         'si corresponde, la marca «con pérdidas».',
    traz='RD-01, RD-03, RD-06, RD-07, RD-09 · HU-01, HU-02, HU-05, HU-06 · D3.5, D3.8, D4.2, D4.3 · '
         'PU-RT-03, PU-RT-06 · EN-05, EN-06')))

add(spec('CU-03', 'Evaluar conformidad ISO 8253-1', dict(
    act='— (caso incluido por CU-02)',
    desc='Compara el Leq de cada banda con la tabla de límites activa.',
    pre='Existen 7 valores de Leq, una tabla de límites seleccionada y el piso de ruido propio por banda (L_piso).',
    trig='Fin del tiempo de integración en CU-02.',
    main='1. Para cada banda, el sistema calcula Δ = Leq − L_piso; si Δ ≥ 10 dB usa el Leq sin corrección.\n'
         '2. Para cada banda, el sistema calcula el margen = límite − Leq.\n'
         '3. Si todos los márgenes son ≥ 0, el veredicto es APTA; si no, NO APTA.\n'
         '4. El sistema identifica la banda de menor margen y la informa.',
    alt='1a. 3 dB ≤ Δ < 10 dB: el sistema resta la energía del piso, evalúa el valor corregido y marca la banda como «corregida».\n'
        '1b. Δ < 3 dB: la banda se informa «< L_det» y **cumple**, porque RD-03 garantiza L_piso ≤ límite − 5 dB.\n'
        '1c. Banda saturada: no cumple.',
    post='Veredicto y márgenes por banda asociados a la sesión.',
    traz='RD-01, RD-02, RD-03 · HU-02 · D3.8 · EN-01, EN-02, EN-05')))

add(spec('CU-04', 'Ver medición en tiempo real', dict(
    act='Fonoaudiólogo/a',
    desc='Permite seguir la medición desde fuera de la cabina con un celular o una PC conectados al Wi-Fi del equipo.',
    pre='Cliente conectado al punto de acceso del instrumento.',
    trig='El usuario abre la dirección del panel en el navegador.',
    main='1. El sistema sirve el panel web y abre un canal WebSocket.\n'
         '2. El sistema envía el estado y los niveles por banda en cada actualización.\n'
         '3. El panel muestra barras por banda frente al límite y el veredicto.',
    alt='2a. Pérdida de conexión: el panel reintenta la conexión de forma automática y la medición en curso no se ve afectada.\n'
        '2b. Ya hay 4 clientes conectados: la quinta conexión WebSocket se cierra con el código 1013 («intente más '
        'tarde») y el panel lo informa.',
    post='Sin cambios de estado en el instrumento.',
    traz='RD-06 · HU-07 · EN-06')))

add(spec('CU-05', 'Generar informe de sesión', dict(
    act='Fonoaudiólogo/a; Servidor de gestión',
    desc='Produce un informe imprimible de una sesión para adjuntarlo al protocolo audiológico.',
    pre='Existe una sesión finalizada.',
    trig='El usuario elige «Informe» al terminar CU-02 o desde CU-06.',
    main='1. El sistema arma el informe con los datos de la cabina, la fecha, el operador, la tabla por banda, '
         'los límites, el veredicto, el estado de la calibración, la marca de cada banda «corregida» o «< L_det» '
         'y, si corresponde, la leyenda «sesión con pérdidas de muestras».\n'
         '2. Si el servidor de gestión está disponible, este genera el PDF; si no, el instrumento sirve una '
         'versión HTML imprimible.\n'
         '3. El usuario descarga o imprime el informe.',
    alt='1a. Sesión medida en modo indicativo: el informe lleva la leyenda «Calibración vencida — no válido para certificar».',
    post='Informe disponible; la sesión queda marcada como «informada».',
    traz='RD-09 · HU-08 · EN-11')))

add(spec('CU-06', 'Consultar historial', dict(
    act='Fonoaudiólogo/a',
    desc='Lista las sesiones anteriores filtradas por cabina y por fechas.',
    pre='Existen sesiones guardadas.',
    trig='El usuario abre «Historial» en el panel web o en el menú local.',
    main='1. El sistema lista las sesiones (fecha, cabina, veredicto).\n'
         '2. El usuario filtra o selecciona una sesión.\n'
         '3. El sistema muestra el detalle por banda.',
    alt='1a. microSD ausente o con error: el sistema informa el problema y muestra solo la última sesión guardada en memoria.',
    post='Sin cambios.',
    traz='RD-09 · HU-09 · EN-08')))

add(spec('CU-07', 'Configurar instrumento', dict(
    act='Técnico/a',
    desc='Ajusta los parámetros: tabla de límites ISO, tiempo de integración, red Wi-Fi (contraseña, canal y '
         'potencia de transmisión), PIN de técnico de 6 dígitos, fecha y hora, '
         'vencimiento de la calibración y correcciones de respuesta del micrófono por banda (C_b). Desde el mismo '
         'menú descarga el diagnóstico: contadores de desbordes, uso de CPU, pilas y el volcado de memoria de la '
         'última falla.',
    pre='Acceso con PIN de técnico de 6 dígitos (desafío y respuesta; el PIN no viaja por la red). Estado REPOSO.',
    trig='El técnico entra a «Configuración».',
    main='1. El sistema solicita el PIN y lo valida.\n'
         '2. El técnico modifica los parámetros.\n'
         '3. El sistema valida los rangos (por ejemplo, integración de 10 a 120 s) y pide confirmación.\n'
         '4. El sistema guarda en NVS y registra el cambio.',
    alt='1a. PIN incorrecto 3 veces: bloqueo por 5 min, global y persistente aunque se reinicie el equipo.\n'
        '2a. Cambio de contraseña o canal del Wi-Fi: se aplica al confirmar y los clientes deben reconectarse.\n3a. Valor fuera de rango: se rechaza indicando el rango válido.',
    post='Configuración nueva vigente y registrada.',
    traz='RD-06, Límites y tolerancias · HU-10 · D3.7, D4.8, D6.5 · PU-RT-09, PU-COM-07 · EN-05, EN-11')))

add(spec('CU-08', 'Actualizar firmware (OTA)', dict(
    act='Técnico/a',
    desc='Carga una nueva imagen de firmware por Wi-Fi.',
    pre='Batería > 50 % o conectada a USB. Estado REPOSO. PIN de técnico.',
    trig='El técnico sube la imagen desde el panel web.',
    main='1. El sistema recibe la imagen y la escribe en la partición OTA inactiva.\n'
         '2. El sistema verifica la integridad y la firma, y marca la partición como de arranque.\n'
         '3. El sistema reinicia y ejecuta un autodiagnóstico (micrófono, microSD, DSP).\n'
         '4. Si el autodiagnóstico es correcto, confirma la imagen nueva.',
    alt='1a. 30 s sin recibir datos: se abandona la actualización y se vuelve a REPOSO.\n'
        '2a. Imagen corrupta o sin firma válida: se descarta y se mantiene la versión actual.\n'
        '3a. Reinicio o corte durante el autodiagnóstico: al arrancar con la imagen pendiente de verificación, '
        'el cargador de arranque revierte a la anterior.\n'
        '4a. Falla el autodiagnóstico o no se confirma en 60 s: reversión automática a la imagen anterior.',
    post='Firmware actualizado o, ante falla, versión anterior intacta. Factor de calibración conservado.',
    traz='RD-11 · HU-11 · D4.3, D6.6 · PU-RT-05, PU-COM-08 · EN-10')))

add(spec('CU-09', 'Exportar registros', dict(
    act='Fonoaudiólogo/a',
    desc='Descarga las sesiones en formato CSV para archivo o análisis.',
    pre='Existen sesiones guardadas.',
    trig='El usuario elige «Exportar» en el panel web.',
    main='1. El usuario selecciona un rango de fechas.\n2. El sistema genera y descarga el CSV.',
    alt='1a. Rango sin datos: el sistema lo informa.',
    post='Archivo CSV descargado; sin cambios en el equipo.',
    traz='RD-09 · HU-12 · EN-08')))

add(spec('CU-10', 'Medir piso de ruido propio', dict(
    act='Técnico/a',
    desc='Mide el ruido propio del instrumento en cada banda y lo guarda como límite de detección para la regla '
         'de piso de ruido de CU-03.',
    pre='PIN de técnico. Micrófono dentro de un recinto aislado o acoplador sellado. Estado REPOSO. '
        'Calibración vigente.',
    trig='El técnico elige «Medir piso de ruido» en el menú de servicio.',
    main='1. El sistema solicita confirmar que el micrófono está aislado y que el Wi-Fi queda en su estado de uso normal.\n'
         '2. El sistema pasa a MIDIENDO_PISO, reinicia los filtros, descarta 0,5 s y mide el Leq de cada banda durante 60 s.\n'
         '3. El sistema compara cada valor con el límite ISO correspondiente y muestra el margen.\n'
         '4. El técnico confirma; el sistema guarda L_piso por banda con fecha en NVS y vuelve a REPOSO.',
    alt='3a. Margen menor que 5 dB en alguna banda: el sistema advierte el incumplimiento de RD-03, guarda el '
        'valor igualmente si el técnico lo confirma y marca el equipo como «fuera de especificación».\n'
        '3b. Lectura mayor que la esperada en varias bandas: el sistema sugiere revisar el aislamiento y repetir.',
    post='Piso de ruido por banda vigente y persistente; evento registrado en la microSD.',
    traz='RD-03 · HU-14 · D3.2, D3.8 · EN-02, EN-09')))
body.append(PB())

# ───────────── 5. Máquina de estados ─────────────
add([H1('5. Máquina de estados del firmware'),
     P('El comportamiento de la capa de aplicación se modela como una máquina de estados finitos. Es la '
       'evolución de la FSM del prototipo previo (IDLE / CALIBRATING / MEASURING), con los estados de '
       'error y de resultado explícitos, el estado de servicio MIDIENDO_PISO y la ESPERA previa a la '
       'medición. Las escrituras en flash solo se aceptan en REPOSO y ACTUALIZANDO (Capítulo 4, D4.3). '
       'Fuente PlantUML: modelos/maquina_estados.puml.'),
     T(['Estado origen', 'Evento / condición', 'Acción', 'Estado destino'],
       [['INICIO', 'Autodiagnóstico correcto', 'Cargar configuración y calibración', 'REPOSO'],
        ['INICIO', 'Falla de micrófono o DSP', 'Mostrar código de error', 'ERROR'],
        ['REPOSO', 'Calibrar', 'Reiniciar filtros, descartar 0,5 s', 'CALIBRANDO'],
        ['CALIBRANDO', 'Lectura estable (5 s) y confirmación', 'Guardar factor en NVS', 'REPOSO'],
        ['CALIBRANDO', 'Lectura inestable / cancelar', 'Descartar', 'REPOSO'],
        ['REPOSO', 'Medir', 'Candado de energía; habilitar canal (PREPARAR); crear sesión', 'ESPERA'],
        ['ESPERA', 'Fin de 3 s', 'INICIAR: acumular sin reiniciar filtros', 'MIDIENDO'],
        ['ESPERA', 'Detener', 'Deshabilitar canal', 'REPOSO'],
        ['MIDIENDO', 'Desborde del anillo DMA', 'Contar muestras perdidas; marcar «con pérdidas»', 'MIDIENDO'],
        ['ESPERA, MIDIENDO, CALIBRANDO, MIDIENDO_PISO', 'Pedido de escritura en flash u OTA', 'Rechazar e informar', '(sin cambio)'],
        ['MIDIENDO', 'Fin del tiempo de integración', 'Evaluar ISO, guardar sesión', 'RESULTADO'],
        ['MIDIENDO', 'Detener', 'Guardar sesión interrumpida', 'REPOSO'],
        ['RESULTADO', 'Aceptar / timeout de 60 s', 'Deshabilitar canal; liberar candado de energía', 'REPOSO'],
        ['Cualquiera', 'Batería crítica (VSYS ≤ 3,50 V con carga, promedio de 1 s)', 'Cerrar sesión y archivos; liberar POWER_HOLD', 'APAGADO'],
        ['REPOSO, RESULTADO', 'Pulsación larga del botón de encendido', 'Cerrar archivos; liberar POWER_HOLD', 'APAGADO'],
        ['Cualquiera', 'Batería baja (≈ 15 %)', 'Aviso en pantalla y en el panel', '(sin cambio)'],
        ['Cualquiera', 'USB conectado / desconectado', 'Informar modo de carga («fuente ≥ 1,5 A» o por defecto) y tiempo estimado', '(sin cambio)'],
        ['REPOSO', 'Medir piso de ruido (técnico)', 'Reiniciar filtros, descartar 0,5 s', 'MIDIENDO_PISO'],
        ['MIDIENDO_PISO', 'Fin de 60 s y confirmación', 'Guardar L_piso por banda en NVS', 'REPOSO'],
        ['MIDIENDO_PISO', 'Cancelar', 'Descartar', 'REPOSO'],
        ['REPOSO', 'OTA iniciada (técnico)', 'Escribir partición inactiva', 'ACTUALIZANDO'],
        ['ACTUALIZANDO', 'Imagen válida', 'Reiniciar', 'INICIO'],
        ['ACTUALIZANDO', 'Imagen corrupta o firma inválida', 'Descartar; conservar la versión actual', 'REPOSO'],
        ['ACTUALIZANDO', '30 s sin datos', 'Abortar la escritura', 'REPOSO'],
        ['INICIO', 'Imagen pendiente de verificación y autodiagnóstico fallido (o sin confirmar en 60 s)', 'Revertir a la imagen anterior; reiniciar', 'INICIO'],
        ['Cualquiera', 'Falla fatal o perro guardián', 'Guardar volcado de memoria; reiniciar', 'INICIO'],
        ['ERROR', 'Reintentar', 'Reiniciar subsistemas', 'INICIO']],
       [2300, 2400, 2638, 1500], size=17),
     PB()])

# ───────────── 6. Historias de usuario ─────────────
HU = [
    ('HU-01', 'Como **fonoaudiólogo/a** quiero **medir la cabina con un solo botón** para verificarla antes de cada sesión sin conocimientos de acústica.',
     'Dado el equipo calibrado y en reposo\nCuando presiono «Medir»\nEntonces la medición termina sola al cumplirse el tiempo configurado y muestra el veredicto.', 'Must', 5, 'CU-02'),
    ('HU-02', 'Como **fonoaudiólogo/a** quiero **ver qué bandas no cumplen y por cuánto** para identificar la fuente de ruido.',
     'Dada una medición NO APTA\nCuando veo el resultado\nEntonces cada banda fuera de límite aparece en rojo con su exceso en dB.', 'Must', 3, 'CU-03'),
    ('HU-03', 'Como **fonoaudiólogo/a** quiero **verificar la calibración con el calibrador al inicio de la jornada** para confiar en la medición.',
     'Dado el calibrador de 94 dB acoplado\nCuando ejecuto «Calibrar»\nEntonces el equipo indica 94,0 ± 0,5 dB y guarda la fecha.', 'Must', 5, 'CU-01'),
    ('HU-04', 'Como **técnico/a** quiero **que el equipo avise si la calibración anual venció** para no emitir informes no válidos.',
     'Dada una calibración de más de 12 meses\nCuando inicio una medición\nEntonces aparece un aviso y el informe queda marcado como «indicativo».', 'Should', 2, 'CU-01, CU-02'),
    ('HU-05', 'Como **fonoaudiólogo/a** quiero **que la medición no se vea afectada por mi manipulación al cerrar la cabina** para obtener un valor representativo.',
     'Dado que presioné «Medir»\nCuando cierro la puerta\nEntonces los primeros 3 s no se integran.', 'Should', 1, 'CU-02'),
    ('HU-06', 'Como **fonoaudiólogo/a** quiero **usar el equipo una jornada completa sin cargarlo** para no depender de un enchufe.',
     'Dada la batería al 100 %\nCuando uso el equipo con Wi-Fi activo\nEntonces funciona ≥ 8 h y avisa al llegar al 15 %.', 'Must', 3, 'CU-02'),
    ('HU-07', 'Como **fonoaudiólogo/a** quiero **seguir la medición desde mi celular fuera de la cabina** para no ingresar y alterar el ruido.',
     'Dado mi celular conectado al Wi-Fi del equipo\nCuando abro el panel\nEntonces veo los niveles actualizados cada ≤ 250 ms.', 'Should', 5, 'CU-04'),
    ('HU-08', 'Como **fonoaudiólogo/a** quiero **obtener un informe imprimible** para adjuntarlo al protocolo audiológico.',
     'Dada una sesión finalizada\nCuando elijo «Informe»\nEntonces obtengo un documento con fecha, cabina, tabla por banda, límites, veredicto y estado de la calibración.', 'Should', 5, 'CU-05'),
    ('HU-09', 'Como **fonoaudiólogo/a** quiero **consultar las mediciones anteriores de una cabina** para ver su evolución.',
     'Dadas sesiones guardadas\nCuando filtro por cabina\nEntonces veo la lista ordenada por fecha con su veredicto.', 'Should', 3, 'CU-06'),
    ('HU-10', 'Como **técnico/a** quiero **seleccionar la tabla de límites y el tiempo de integración** para adaptar el equipo a cada condición de la norma.',
     'Dado el PIN de técnico\nCuando cambio la tabla o el tiempo (10–120 s)\nEntonces el cambio queda guardado y registrado.', 'Must', 3, 'CU-07'),
    ('HU-11', 'Como **técnico/a** quiero **actualizar el firmware sin abrir el equipo** para corregir errores en campo.',
     'Dada una imagen válida\nCuando la cargo por el panel\nEntonces el equipo se actualiza y conserva la calibración; si la imagen falla, vuelve a la versión anterior.', 'Could', 8, 'CU-08'),
    ('HU-12', 'Como **fonoaudiólogo/a** quiero **exportar las sesiones a CSV** para archivarlas.',
     'Dado un rango de fechas con datos\nCuando elijo «Exportar»\nEntonces descargo un CSV con una fila por sesión y una columna por banda.', 'Could', 2, 'CU-09'),
    ('HU-13', 'Como **desarrollador** quiero **pruebas automáticas del banco de filtros** para detectar regresiones en el DSP.',
     'Dado un cambio en el código DSP o en la máscara\nCuando se ejecuta la integración continua (GNU Octave, PU-DSP-01)\nEntonces la respuesta de cada filtro se verifica contra la máscara de IEC 61260-1 y el pipeline falla si el margen es negativo.', 'Must', 5, '— (técnica)'),
    ('HU-14', 'Como **técnico/a** quiero **medir y guardar el ruido propio del equipo por banda** para que las bandas cercanas al piso se informen correctamente.',
     'Dado el micrófono en un recinto aislado\nCuando ejecuto «Medir piso de ruido»\nEntonces el equipo guarda el piso de cada banda y avisa si alguna queda a menos de 5 dB del límite.', 'Must', 3, 'CU-10'),
    ('HU-15', 'Como **fonoaudiólogo/a** quiero **guardar el equipo varios meses sin perder la calibración ni los registros** para usarlo de forma esporádica.',
     'Dado el equipo apagado 3 meses a temperatura ambiente\nCuando lo enciendo\nEntonces conserva calibración, configuración y sesiones, y la batería tiene ≥ 50 %.', 'Should', 3, '— (RD-12)'),
    ('HU-16', 'Como **fonoaudiólogo/a** quiero **trasladar el equipo entre servicios sin que se dañe ni se descalibre** para verificar varias cabinas.',
     'Dado el equipo en su estuche\nCuando sufre una caída de 1 m\nEntonces sigue funcionando y la verificación con el calibrador da 94,0 ± 0,5 dB.', 'Should', 2, '— (RD-13)'),
]
add([H1('6. Historias de usuario'),
     P('Formato «Como ‹rol› quiero ‹objetivo› para ‹beneficio›», con criterios de aceptación en estilo '
       'Dado / Cuando / Entonces. La estimación se expresa en puntos de historia (serie de Fibonacci).'),
     T(['ID', 'Historia', 'Criterios de aceptación', 'Prior.', 'Pts', 'CU'],
       [[a, b, c, d, str(e), f] for a, b, c, d, e, f in HU],
       [750, 2900, 3238, 700, 500, 750], size=16, center_cols=(0, 3, 4, 5)),
     H2('Plan de iteraciones (versión inicial)'),
     T(['Iteración', 'Período', 'Historias', 'Objetivo'],
       [['I-1', 'Feb 2027', 'HU-13', 'Banco de filtros verificado en el host'],
        ['I-2', 'Mar 2027', 'HU-01, HU-02, HU-05', 'Medición y veredicto en la placa de desarrollo'],
        ['I-3', 'Mar–Abr 2027', 'HU-03, HU-04, HU-10, HU-14', 'Calibración, piso de ruido y configuración'],
        ['I-4', 'Abr–May 2027', 'HU-09, HU-12, HU-06', 'Registro, autonomía e interfaz local'],
        ['I-5', 'May 2027', 'HU-07, HU-08', 'Panel web e informe'],
        ['I-6', 'Jun 2027', 'HU-11, HU-15, HU-16', 'OTA, almacenamiento, robustez mecánica y endurecimiento']],
       [1100, 1700, 2400, 3638], size=18, center_cols=(0,)),
     PB()])

# ───────────── 7. Trazabilidad ─────────────
TRZ = [
    ('RD-01', 'CU-02, CU-03', 'HU-01, HU-02', 'PU-DSP-02', 'EN-05'),
    ('RD-02', 'CU-03', 'HU-02, HU-13', 'PU-DSP-01', 'EN-01'),
    ('RD-03', 'CU-02, CU-03, CU-10', 'HU-14', 'PU-HW-01', 'EN-02'),
    ('RD-04', 'CU-02', 'HU-01', 'PU-DSP-04', 'EN-04'),
    ('RD-05', 'CU-01', 'HU-03', 'PU-DSP-03, PU-RT-08', 'EN-03'),
    ('RD-06', 'CU-02, CU-04, CU-07', 'HU-07, HU-10', 'PU-COM-02, PU-COM-03', 'EN-06'),
    ('RD-07', 'CU-02', 'HU-01', 'PU-DSP-02, PU-RT-02, PU-RT-03, PU-RT-04, PU-COM-04', 'EN-06'),
    ('RD-08', 'CU-02', 'HU-06', 'PU-RT-07, PU-HW-02, PU-HW-05', 'EN-07'),
    ('RD-09', 'CU-02, CU-05, CU-06, CU-09', 'HU-08, HU-09, HU-12', 'PU-RT-06, PU-COM-11, PU-COM-12', 'EN-08'),
    ('RD-10', 'CU-01', 'HU-03, HU-04', 'PU-COM-10', 'EN-03'),
    ('RD-11', 'CU-08', 'HU-11', 'PU-RT-01, PU-RT-05, PU-COM-08', 'EN-10'),
    ('RD-12', '— (no funcional)', 'HU-15', 'PU-HW-03, PU-HW-04', 'EN-12'),
    ('RD-13', '— (no funcional)', 'HU-16', '—', 'EN-13'),
    ('Interfaz', 'CU-02, CU-04, CU-05', 'HU-01, HU-07, HU-08', 'PU-COM-05, PU-COM-06', 'EN-11'),
    ('Seguridad', 'CU-07, CU-08', 'HU-10, HU-11', 'PU-COM-07', '—'),
    ('Ambiente', 'CU-02, CU-10', '—', '—', 'EN-09'),
]
add([H1('7. Matriz de trazabilidad'),
     P('Cada requisito de la tabla del anteproyecto se vincula con al menos un caso de uso, una historia y un '
       'ensayo. Esta matriz se mantendrá actualizada en Enterprise Architect mediante relaciones «trace».'),
     T(['Requisito', 'Casos de uso', 'Historias', 'Pruebas unitarias', 'Ensayo'], [list(r) for r in TRZ],
       [1200, 2450, 2100, 2000, 1087], size=17, center_cols=(0, 4)),
     P('RD-12 y RD-13 son requisitos no funcionales (almacenamiento y manipulación): no tienen un caso de uso '
       'propio y se verifican directamente con ensayos. Las pruebas PU-DSP se definen en el Capítulo 3 '
       '(sección 3.10), las PU-RT en el Capítulo 4 (sección 4.8), las PU-HW en el Capítulo 5 (sección 5.10) y las '
       'PU-COM en el Capítulo 6 (sección 6.12). '
       'PU-RT-09 (perro guardián) y PU-HW-06 a PU-HW-09 (térmica, señal, polaridad, descarga electrostática) '
       'verifican decisiones de diseño, no un requisito RD; lo mismo PU-COM-01 y PU-COM-09 (enlace y memoria). La fila '
       '«Seguridad» agrupa las exigencias del Capítulo 6 (D6.5) que el anteproyecto enuncia como «otros requisitos».', size=18, italic=True),
     H1('8. Notas para Enterprise Architect'),
     B('Crear un paquete por vista: «Requisitos» (elementos Requirement RD-xx), «Casos de uso» (diagrama de '
       'la Figura 1), «Comportamiento» (máquina de estados) y «Verificación» (elementos Test EN-xx).'),
     B('Cargar el texto de la sección 4 en la pestaña «Scenarios» de cada caso de uso: flujo básico, '
       'alternativos y excepciones, con los mismos números de paso.'),
     B('Relacionar los requisitos con los casos de uso mediante «realize» o «trace», y los ensayos con los '
       'requisitos mediante «verify», para obtener la matriz de la sección 7 con «Relationship Matrix».'),
     B('Los archivos .puml de la carpeta modelos/ sirven como referencia textual de los diagramas y se '
       'pueden versionar en Git junto con el código.'),
     ])

# ───────────── Ensamblado sobre la plantilla ─────────────
z = zipfile.ZipFile(TPL)
files = {n: z.read(n) for n in z.namelist()}
doc = files['word/document.xml'].decode('utf-8')
b0 = doc.index('<w:body>') + len('<w:body>')
paras = list(re.finditer(r'<w:p[ >].*?</w:p>', doc[b0:], re.S))
header = ''.join(m.group(0) for m in paras[:3])  # logo + Universidad, Facultad, Especialización
sect = re.search(r'<w:sectPr>.*?</w:sectPr>', doc, re.S).group(0)
doc = doc[:b0] + header + ''.join(body) + sect + '</w:body></w:document>'
files['word/document.xml'] = doc.encode('utf-8')

rels = files['word/_rels/document.xml.rels'].decode()
rels = rels.replace('</Relationships>',
                    '<Relationship Id="rIdUC1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/casos_de_uso.png"/></Relationships>')
files['word/_rels/document.xml.rels'] = rels.encode()
files['word/media/casos_de_uso.png'] = open(IMG, 'rb').read()
ct = files['[Content_Types].xml'].decode()
if 'Extension="png"' not in ct:
    ct = ct.replace('<Default ', '<Default Extension="png" ContentType="image/png"/><Default ', 1)
files['[Content_Types].xml'] = ct.encode()

with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED) as zo:
    for n, data in files.items():
        zo.writestr(n, data)
print('OK', OUT)
