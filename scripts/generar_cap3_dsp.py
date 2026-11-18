#!/usr/bin/env python3
"""Capítulo 3 — Procesamiento Digital de Señales: banco de filtros de octava (v0.2).

Uso (desde anteproyecto/):
  python3 -I scripts/generar_cap3_dsp.py "../ModeloAnteproyecto(1).docx" figuras capitulos/Cap3_DSP_Banco_Octavas.docx

Cifras: dsp/resultados/resumen.txt (diseno_banco.m) y dsp/resultados/complementario.txt
(analisis_complementario.m).
"""
import os
import re
import sys
import zipfile

sys.path.insert(0, os.path.dirname(__file__))
from docx_xml import P, B, H2, T, IMG_RUN  # noqa: E402
from PIL import Image  # noqa: E402

TPL, FIG, OUT = sys.argv[1], sys.argv[2], sys.argv[3]


def H1(text):
    return P(text, size=28, bold=True, before=240, after=120, keep_next=True, align='left')


def PB():
    return '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'


def CAP(text):
    return P(text, size=18, italic=True, align='center', after=200)


def _runs_of(p_xml):
    return p_xml[p_xml.index('<w:r>'):-len('</w:p>')]


def EQ(text, num):
    """Ecuación centrada con su número alineado a la derecha."""
    return ('<w:p><w:pPr><w:keepNext/><w:tabs><w:tab w:val="center" w:pos="4419"/>'
            '<w:tab w:val="right" w:pos="8838"/></w:tabs><w:spacing w:before="80" w:after="120"/></w:pPr>'
            '<w:r><w:tab/></w:r>' + _runs_of(P(text, size=22, italic=True)) +
            '<w:r><w:tab/></w:r>' + _runs_of(P(f'({num})', size=22)) + '</w:p>')


def KT(*a, **k):
    k.setdefault('keep', True)
    return T(*a, **k)


IMAGES = []  # (rid, archivo)


def FIGURA(archivo, ancho_cm, leyenda):
    rid = f'rIdC3F{len(IMAGES) + 1}'
    IMAGES.append((rid, archivo))
    w, h = Image.open(os.path.join(FIG, archivo)).size
    cx = int(ancho_cm * 360000)
    cy = int(cx * h / w)
    return [f'<w:p><w:pPr><w:keepNext/><w:jc w:val="center"/></w:pPr>'
            f'{IMG_RUN(rid, cx, cy, 300 + len(IMAGES), archivo)}</w:p>', CAP(leyenda)]


body = []
add = body.extend

# ───────────── Portada ─────────────
add([P('', after=600),
     P('Capítulo 3', size=40, bold=True, align='center', color='1E5E9F', after=120),
     P('Procesamiento Digital de Señales', size=36, bold=True, align='center', color='1E5E9F', after=200),
     P('Diseño y verificación del banco de filtros de octava y del cálculo de niveles', size=28,
       bold=True, align='center', after=400),
     P('Analizador autónomo de ruido ambiente por bandas de octava para la verificación de cabinas '
       'audiométricas según ISO 8253-1', size=24, align='center', after=1200),
     P('**Autor:** Andrés Machtey', size=24, align='left', after=100),
     P('**Director propuesto:** Esp. Víctor Valotto (FIUNER)', size=24, align='left', after=100),
     P('**Versión:** 0.2 (revisada con el método Elephant–Goldfish) · Noviembre de 2026',
       size=24, align='left', after=100),
     P('**Material reproducible:** dsp/octave/diseno_banco.m, dsp/octave/analisis_complementario.m, '
       'dsp/octave/graficos.gp y dsp/resultados/', size=20, align='left', after=100),
     PB()])

# ───────────── Siglas ─────────────
add([H1('Siglas y convenciones'),
     KT(['Sigla', 'Significado', 'Sigla', 'Significado'],
        [['ADC', 'Conversor analógico-digital', 'L_eq', 'Nivel continuo equivalente de presión sonora'],
         ['dBFS', 'Decibeles respecto del fondo de escala digital', 'MEMS', 'Sistema microelectromecánico (micrófono)'],
         ['dBA', 'Nivel con ponderación frecuencial A', 'SOS', 'Sección de segundo orden (biquad)'],
         ['DF2T', 'Forma directa II transpuesta', 'I2S', 'Bus serie de audio digital (Inter-IC Sound)'],
         ['EIN', 'Ruido equivalente de entrada del micrófono', 'NVS', 'Memoria no volátil del ESP32'],
         ['FIR / IIR', 'Respuesta al impulso finita / infinita', 'f_m, f_s', 'Frecuencia media de banda / de muestreo'],
         ['FFT', 'Transformada rápida de Fourier', 'G', 'Razón de octava en base diez, 10^(3/10)']],
        [900, 3519, 900, 3518], size=17),
     P('Los identificadores remiten a los demás documentos del proyecto: **RD-xx**, requisitos de desempeño del '
       'anteproyecto; **EN-xx**, ensayos del anteproyecto; **E1…E7**, entregables; **CU-xx / HU-xx**, casos de uso '
       'e historias de usuario del anexo de Ingeniería de Software; **PU-DSP-xx**, pruebas unitarias definidas en '
       'este capítulo; **D3.x**, decisiones de diseño de este capítulo. "Extremo a extremo" designa la '
       'simulación de la cadena completa, desde la muestra de 48 kHz hasta la salida de cada banda.', size=20)])

# ───────────── 3.1 ─────────────
add([H1('3.1 Enfoque del capítulo'),
     P('Este capítulo analiza el proyecto desde la materia **Procesamiento Digital de Señales**. Su objeto '
       'es la cadena que transforma las muestras del micrófono en siete niveles de presión sonora por banda '
       'de octava: el diseño de los filtros, la arquitectura multitasa, la verificación numérica contra la '
       'norma IEC 61260-1 [1], el cálculo del nivel equivalente y el límite que impone el ruido propio del '
       'micrófono. Parte del análisis crítico del prototipo construido en el curso de DSP y termina con '
       'decisiones de diseño justificadas y con los coeficientes listos para el firmware.'),
     P('El diseño es reproducible: los scripts de GNU Octave [8] calculan los filtros, simulan la cadena '
       'completa, miden los márgenes contra la máscara y generan el archivo **octave_coeffs.h** que compila el '
       'firmware. Las cifras de este capítulo salen de su salida (resultados/resumen.txt y '
       'resultados/complementario.txt).'),
     H2('Requisitos que condicionan el procesamiento'),
     KT(['Requisito', 'Enunciado (anteproyecto)', 'Consecuencia para el DSP'],
        [['RD-01', 'Leq simultáneo en 7 bandas de octava, 125 Hz a 8 kHz',
          'Siete filtros en paralelo sobre el mismo flujo; frecuencias medias normalizadas'],
         ['RD-02', 'Filtros dentro de las máscaras de IEC 61260-1 clase 2',
          'Orden y tipo de filtro; se diseña con objetivo clase 1 para tener margen'],
         ['RD-03', 'Ruido propio por banda ≥ 5 dB bajo el límite ISO',
          'Límite de detección por banda y regla de veredicto (sección 3.8)'],
         ['RD-04', 'Hasta ≥ 100 dB SPL sin saturar; linealidad ±1 dB',
          'Escala digital del micrófono; aritmética de punto flotante'],
         ['RD-05', 'Exactitud ±0,5 dB a 1 kHz tras calibración',
          'Error de ganancia entre bandas acotado; constante de calibración'],
         ['RD-06', 'Integración 10 a 120 s; refresco ≤ 250 ms',
          'Integración lineal por bloques; acumuladores sin pérdida de precisión'],
         ['RD-07', 'Tiempo real sin pérdidas; CPU del núcleo DSP ≤ 70 %',
          'Costo computacional acotado; multitasa; biblioteca ESP-DSP'],
         ['RD-10', 'Factor de calibración persistente con fecha',
          'La constante K de la ecuación (5) se guarda en NVS']],
        [1100, 3700, 4037], size=18)])

# ───────────── 3.2 ─────────────
add([H1('3.2 Análisis crítico del prototipo previo'),
     P('El prototipo del curso usaba un único biquad pasabanda por banda a f_s = 51 200 Hz, con '
       'coeficientes precalculados (biquad_filters.c). La Figura 3.1 muestra su respuesta real, calculada a '
       'partir de esos coeficientes. Entre 250 Hz y 8 kHz **ningún filtro es pasabanda**: todos se comportan '
       'como pasabajos con la frecuencia de corte cerca de la frecuencia central. La banda de 125 Hz sí es '
       'pasabanda (polos complejos en 122 Hz), pero su ancho a −3 dB va de 87 a 230 Hz, es decir, '
       '1,4 octavas.'),
     *FIGURA('cap3_prototipo_previo.png', 15.5,
             'Figura 3.1. Respuesta de los biquads del prototipo previo (coeficientes de biquad_filters.c).'),
     KT(['Banda', 'Polos: |p| (ángulo → Hz)', 'Ganancia en f_c', 'Bordes −3 dB', '|p| máx. en float32'],
        [['125 Hz', '0,9913 (±122 Hz)', '−0,26 dB', '87 – 230 Hz', '1 − 8,7·10⁻³'],
         ['250 Hz', '0,9969 / 0,9682 (reales)', '−2,03 dB', '22 – 309 Hz', '1 − 3,1·10⁻³'],
         ['500 Hz', '0,9985 / 0,9334 (reales)', '−2,35 dB', '12 – 584 Hz', '1 − 1,5·10⁻³'],
         ['1 kHz', '1,0000 / 0,8710 (reales)', '−2,54 dB', '< 10 – 1117 Hz', ('1 + 4,6·10⁻⁷ (inestable)', 'F8D7DA')],
         ['2 kHz', '1,0000 / 0,7693 (reales)', '−2,77 dB', '< 10 – 2103 Hz', ('1 (sobre el círculo)', 'F8D7DA')],
         ['4 kHz', '1,0000 / 0,6254 (reales)', '−3,39 dB', '< 10 – 3682 Hz', '1 − 1,6·10⁻⁷'],
         ['8 kHz', '1,0000 / 0,4514 (reales)', '−4,77 dB', '< 10 – 5867 Hz', ('1 + 5,4·10⁻⁸ (inestable)', 'F8D7DA')]],
        [1000, 2500, 1500, 1700, 2137], size=17, center_cols=(0, 1, 2, 3, 4)),
     CAP('Tabla 3.1. Polos y bordes de la respuesta de los filtros previos, y radio de polos con los '
         'coeficientes redondeados a float32, tal como los ejecutaba el ESP32.'),
     P('**Causa raíz.** El comentario del código describe la fórmula clásica del pasabanda de 2.º orden [9]: '
       'α = sen ω₀ / (2Q), b₀ = α / (1 + α), b₂ = −b₀, a₁ = −2 cos ω₀ / (1 + α), a₂ = (1 − α) / (1 + α). Los '
       'coeficientes cargados cumplen 1 − a₂ = 2b₀, coherente con un valor de α, pero también '
       '**a₁ = −(1 + a₂)**, que solo se obtiene con cos ω₀ = 1, es decir, con ω₀ = 0. **La frecuencia central '
       'no interviene en ninguno de los coeficientes**: el resultado es un "pasabanda centrado en 0 Hz", con un '
       'polo en z = 1 que se cancela con el cero en z = 1 y deja un pasabajos de primer orden (Figura 3.2). En '
       '125 a 500 Hz la diferencia es solo de redondeo, lo que explica que esas bandas se aparten menos.'),
     P('El defecto no es solo de respuesta. Al redondear a float32, los polos de las bandas de 1 kHz y 8 kHz '
       'quedan **fuera del círculo unitario**: esos filtros eran inestables tal como se ejecutaban. La '
       'cancelación con el cero en z = 1 disimula el problema hasta que el estado interno se desborda.'),
     *FIGURA('cap3_polos_ceros.png', 15.5,
             'Figura 3.2. Polos y ceros de la banda de 1 kHz: biquad previo (polo en z = 1 cancelado por un '
             'cero) y filtro propuesto (8 polos complejos con |p| ≤ 0,90; ceros cuádruples en z = ±1).'),
     P('**Limitaciones de fondo, aun con los coeficientes correctos:**'),
     B('Un pasabanda de 2.º orden con Q = √2 cae 6 dB por octava fuera de banda. A una octava de f_m '
       'atenúa unos 7 dB, cuando la norma exige alrededor de 17 dB. **No puede cumplir IEC 61260-1** en '
       'ninguna clase.'),
     B('La norma citada en el prototipo para los filtros era IEC 61672-1 [10], que trata los sonómetros; la '
       'norma específica de filtros de octava es **IEC 61260-1** [1].'),
     P('**Lecciones aprendidas:** (1) los coeficientes deben generarse con una herramienta y no transcribirse '
       'a mano; (2) la respuesta de cada filtro, y su estabilidad con los coeficientes realmente cargados, '
       'debe verificarse automáticamente; (3) toda decisión de diseño debe quedar vinculada a un resultado '
       'reproducible.')])

# ───────────── 3.3 ─────────────
add([H1('3.3 Marco normativo de los filtros'),
     H2('Frecuencias medias y bordes de banda'),
     P('IEC 61260-1:2014 [1] define las bandas con razón de octava en base diez, G = 10^(3/10) ≈ 1,99526. Las '
       'frecuencias medias exactas son f_m = 1000 · G^k Hz y los bordes de banda f₁ = f_m · G^(−1/2) y '
       'f₂ = f_m · G^(1/2). Los valores nominales (125, 250 … 8000 Hz) sirven solo como rótulos: el diseño '
       'usa siempre los exactos.'),
     KT(['k', 'Nominal', 'f_m exacta [Hz]', 'f₁ [Hz]', 'f₂ [Hz]', 'Ancho [Hz]'],
        [['−3', '125', '125,89', '89,13', '177,83', '88,7'],
         ['−2', '250', '251,19', '177,83', '354,81', '177,0'],
         ['−1', '500', '501,19', '354,81', '707,95', '353,1'],
         ['0', '1000', '1000,00', '707,95', '1412,54', '704,6'],
         ['1', '2000', '1995,26', '1412,54', '2818,38', '1405,8'],
         ['2', '4000', '3981,07', '2818,38', '5623,41', '2805,0'],
         ['3', '8000', '7943,28', '5623,41', '11220,18', '5596,8']],
        [700, 1200, 1700, 1700, 1700, 1500], size=18, center_cols=(0, 1, 2, 3, 4, 5)),
     CAP('Tabla 3.2. Bandas de octava en base diez (IEC 61260-1).'),
     H2('Atenuación relativa y máscara'),
     P('La norma expresa los requisitos como **atenuación relativa**: la atenuación del filtro a la frecuencia f '
       'menos la **atenuación de referencia**, que es la de la banda de referencia (1 kHz) a la frecuencia de '
       'referencia (1 kHz). Con esa definición, el límite en Ω = f / f_m = 1 acota la diferencia de ganancia '
       'entre cada banda y la de referencia. Los límites a ambos lados acotan la forma: en la banda de paso, el '
       'límite máximo limita la caída; fuera de ella, el límite mínimo exige rechazo.'),
     KT(['Ω (potencia de G)', 'Clase 1 mín. [dB]', 'Clase 1 máx. [dB]', 'Clase 2 mín. [dB]', 'Clase 2 máx. [dB]'],
        [['G^0', '−0,4', '+0,4', '−0,6', '+0,6'],
         ['G^(±1/8)', '−0,4', '+0,6', '−0,6', '+0,8'],
         ['G^(±1/4)', '−0,4', '+0,8', '−0,6', '+1,1'],
         ['G^(±3/8)', '−0,4', '+1,4', '−0,6', '+1,9'],
         ['G^(±1/2) (bordes)', '+1,2', '+5,3', '+0,4', '+5,8'],
         ['G^(±1)', '+17,5', '+∞', '+16,5', '+∞'],
         ['G^(±2)', '+42,5', '+∞', '+41,5', '+∞'],
         ['G^(±3)', '+62,0', '+∞', '+55,0', '+∞'],
         ['G^(±4)', '+75,0', '+∞', '+60,0', '+∞']],
        [2237, 1650, 1650, 1650, 1650], size=18, center_cols=(0, 1, 2, 3, 4)),
     CAP('Tabla 3.3. Máscara de trabajo usada en la verificación. Entre puntos de quiebre se interpola '
         'linealmente en el exponente de G. ATENCIÓN: valores pendientes de contrastar con la Tabla 1 de '
         'IEC 61260-1:2014.'),
     P('**Advertencia metodológica.** El texto completo de IEC 61260-1:2014 es de acceso pago y no se pudo '
       'consultar. Los límites de la Tabla 3.3 son **valores de trabajo**, y también lo es la regla de '
       'interpolación entre puntos de quiebre. La verificación está automatizada para que esto no sea un '
       'riesgo: la máscara es un archivo (resultados/mascara.csv) y, al reemplazarla por los valores oficiales, '
       'el script recalcula todos los márgenes. Conseguir la norma, en la biblioteca de la FIUNER o en IRAM, es '
       'una tarea del entregable E2. Lo mismo vale para la tolerancia del ancho de banda efectivo '
       '(sección 3.6).')])

# ───────────── 3.4 ─────────────
add([H1('3.4 Diseño del filtro de banda'),
     H2('Alternativas de implementación'),
     P('Antes de elegir el filtro se compararon cuatro formas de obtener niveles por banda de octava:'),
     KT(['Criterio', 'Banco FIR', 'FFT / Welch (suma de bins)', 'IIR a 48 kHz', 'IIR multitasa (elegido)'],
        [['Cumplimiento de la máscara', 'Sí, con miles de coeficientes en 125 Hz',
          'Depende de la ventana; la forma de banda no es la de IEC 61260', 'Sí', 'Sí'],
         ['Costo [M mult/s]', '> 50 (sin multitasa)', '≈ 1–2', '6,7', '3,3'],
         ['Memoria', 'Alta (líneas de retardo largas)', 'Media (bloques de 4096 o más)', 'Muy baja', 'Baja (≈ 9 kB)'],
         ['Latencia y transitorio', 'Retardo fijo de decenas de ms en 125 Hz', 'Un bloque (85 ms o más)',
          'Corto', 'Corto (60 ms en 125 Hz)'],
         ['Fase', 'Lineal', '—', 'No lineal', 'No lineal'],
         ['Observación', 'La fase lineal no aporta nada a una medición de energía',
          'Resolución fija en Hz; bandas bajas con pocos bins', 'Polos más cerca de z = 1',
          'Práctica habitual en analizadores [4]']],
        [1600, 1800, 1850, 1600, 1987], size=16),
     CAP('Tabla 3.4. Comparación cualitativa de alternativas. Los costos FIR y FFT son órdenes de magnitud '
         'estimados; los costos IIR salen del script.'),
     P('La medición busca energía por banda, así que la fase lineal del FIR no aporta beneficios y su costo es '
       'prohibitivo en las bandas bajas. La FFT es barata, pero su forma de banda depende de la ventana y no '
       'reproduce naturalmente la máscara normativa. Por eso se eligió un **banco IIR**.'),
     H2('Tipo de aproximación'),
     P('Se eligió la aproximación **Butterworth** [3] porque su banda de paso es máximamente plana, lo que '
       'cuida el margen más estrecho de la máscara, el que está alrededor de f_m. Además, su atenuación en '
       'los bordes es de 3,01 dB, dentro del intervalo admitido (1,2 a 5,3 dB en clase 1), y su retardo de grupo '
       'es más suave que el de Chebyshev o el elíptico, lo que acorta los transitorios. Chebyshev o elíptico '
       'darían más rechazo con el mismo orden, a costa de ondulación en la banda de paso.'),
     H2('Del prototipo analógico al filtro digital'),
     P('El prototipo pasabajos analógico de orden N se transforma en pasabanda y luego en digital mediante la '
       '**transformación bilineal**. Para que los bordes digitales caigan exactamente en f₁ y f₂, se '
       '**predistorsionan** antes de la transformación [3]:'),
     EQ('s = (2 / T_s) · (1 − z⁻¹) / (1 + z⁻¹)          Ω_a = (2 / T_s) · tan(π f / f_s)', 1),
     P('Así se obtiene un pasabanda de orden 2N. Se implementa como **N secciones de segundo orden en cascada** '
       '(función zp2sos), cada una con transferencia:'),
     EQ('H_i(z) = (b₀ᵢ + b₁ᵢ z⁻¹ + b₂ᵢ z⁻²) / (1 + a₁ᵢ z⁻¹ + a₂ᵢ z⁻²),     H(z) = Π H_i(z)', 2),
     P('Cada sección se calcula en **forma directa II transpuesta**, la estructura de ESP-DSP [7], que necesita '
       'dos variables de estado por sección:'),
     EQ('y[n] = b₀ x[n] + w₁[n−1];   w₁[n] = b₁ x[n] − a₁ y[n] + w₂[n−1];   w₂[n] = b₂ x[n] − a₂ y[n]', 3),
     P('La cascada de secciones evita la sensibilidad extrema a la cuantización que tendría la forma directa de '
       'orden 8.'),
     H2('Elección del orden'),
     P('Se compararon los prototipos N = 3 (pasabanda de orden 6) y N = 4 (orden 8). La Tabla 3.5 muestra la '
       'atenuación de la banda de 1 kHz en los puntos de quiebre del lado inferior. Ese lado es el más exigente, '
       'porque la transformación bilineal comprime el eje de frecuencias cerca de Nyquist y agrega atenuación '
       'del lado superior.'),
     KT(['Punto', 'Límite clase 1', 'Límite clase 2', 'N = 3', 'N = 4'],
        [['f_m / G', '17,5', '16,5', '18,2', '24,2'],
         ['f_m / G²', '42,5', '41,5', ('41,2 ✗', 'F8D7DA'), '55,0'],
         ['f_m / G³', '62,0', '55,0', ('60,3 ✗ c1', 'FCE8D4'), '80,5'],
         ['f_m / G⁴', '75,0', '60,0', '78,6', '104,8'],
         ['##Margen mínimo clase 1', '', '', ('−1,66 dB', 'F8D7DA'), ('+0,40 dB', 'D4EDDA')],
         ['##Margen mínimo clase 2', '', '', ('−0,27 dB', 'F8D7DA'), ('+0,60 dB', 'D4EDDA')],
         ['##SOS totales (bandas + antialias)', '', '', '39', '46'],
         ['##Multiplicaciones por segundo', '', '', '2,85 M', '3,32 M']],
        [2837, 1500, 1500, 1500, 1500], size=18, center_cols=(1, 2, 3, 4)),
     CAP('Tabla 3.5. Atenuación relativa [dB] de la banda de 1 kHz, calculada analíticamente a su tasa de '
         '6 kHz, y márgenes contra la máscara de trabajo en los puntos de quiebre.'),
     P('**Decisión D3.1: prototipo Butterworth de orden N = 4 (pasabanda de orden 8, 4 SOS por banda).** Con '
       'N = 3 el banco no cumple la máscara de trabajo ni siquiera en clase 2: le faltan 0,27 dB en f_m / G². '
       'Con N = 4 la cumple en clase 1 en todo el eje de frecuencias (sección 3.6), con un costo 17 % mayor '
       '(3,32 frente a 2,85 millones de multiplicaciones por segundo), que es irrelevante para el ESP32-S3. El '
       'fallo de N = 3 depende de la relación f_m / f_s ≈ 1/6: en analógico, N = 3 da unos 43,5 dB en '
       'f_m / G². Si los valores oficiales resultaran más laxos, o si se aumentara el sobremuestreo, N = 3 '
       'podría reconsiderarse. La decisión queda vinculada al resultado del script.'),
     *FIGURA('cap3_mascara_1k.png', 15.5,
             'Figura 3.3. Banda de 1 kHz con N = 3 y N = 4 frente a la máscara de trabajo clase 1 (curvas de '
             'ganancia relativa: el límite superior corresponde a la atenuación mínima).'),
     *FIGURA('cap3_mascara_1k_detalle.png', 15.5,
             'Figura 3.4. Detalle de la banda de paso: ambos órdenes respetan los límites cerca de f_m.')])

# ───────────── 3.5 ─────────────
add([H1('3.5 Arquitectura multitasa'),
     P('**Frecuencia de muestreo.** El prototipo muestreaba a 51,2 kHz para que las bandas de un analizador '
       'FFT cayeran en múltiplos exactos. El diseño propuesto usa **48 kHz**: es una tasa estándar del I2S del '
       'ESP32-S3 y del micrófono, cubre la banda de 8 kHz con holgura (f₂ = 11,2 kHz) y se divide por 2 seis '
       'veces de forma exacta, hasta llegar a 750 Hz.'),
     P('Diseñar las siete bandas directamente a 48 kHz es posible. El análisis complementario muestra que la '
       'banda de 125 Hz, con polos a 1,5·10⁻³ del círculo unitario, mantiene en float32 un error de '
       'coeficientes de 0,006 dB y un ruido de redondeo de −178 dBFS. Aun así, se adopta la **descomposición '
       'por octavas** [4] por dos razones:'),
     B('**Costo:** reduce el cálculo a la mitad, de 6,7 a 3,3 millones de multiplicaciones por segundo, '
       'antialias incluidos.'),
     B('**Robustez:** todas las bandas trabajan con la misma relación f_m / f_s ≈ 1/6 y el radio máximo de '
       'polos baja de 0,9985 a 0,90. El diseño queda lejos de la zona sensible y es extensible, por ejemplo a '
       'bandas de tercio de octava o a 63 Hz, sin cambiar la arquitectura.'),
     P('La banda más alta se filtra a 48 kHz. Para cada octava inferior, la señal se filtra con un pasabajos '
       'antialias y se diezma por 2 (Figura 3.5).'),
     *FIGURA('cap3_multitasa.png', 16.5,
             'Figura 3.5. Arquitectura multitasa: un filtro de banda por tasa y una etapa antialias + ↓2 entre tasas.'),
     KT(['Banda', '8 kHz', '4 kHz', '2 kHz', '1 kHz', '500 Hz', '250 Hz', '125 Hz'],
        [['f_s de la banda', '48 kHz', '24 kHz', '12 kHz', '6 kHz', '3 kHz', '1,5 kHz', '750 Hz'],
         ['f₂ / (f_s/2)', '0,468', '0,469', '0,470', '0,471', '0,472', '0,473', '0,474'],
         ['|p| máximo', '0,899', '0,899', '0,898', '0,898', '0,898', '0,898', '0,897']],
        [1700] + [1019] * 7, size=17, center_cols=tuple(range(1, 8))),
     CAP('Tabla 3.6. Tasa de procesamiento y condicionamiento de cada banda (N = 4).'),
     H2('Filtro antialias'),
     P('Antes de cada diezmado se usa un **pasabajos elíptico de orden 6 (3 SOS)**, igual en todas las '
       'etapas porque está normalizado a la tasa de entrada. Sus características:'),
     B('**Banda de paso:** hasta 0,118 · f_entrada, que cubre el borde superior de todas las bandas inferiores, '
       'con 0,01 dB de ondulación.'),
     B('**Banda de rechazo:** desde 0,382 · f_entrada, con 80 dB. Es la región que, al diezmar, se plegaría '
       'sobre la banda de paso de la octava siguiente.'),
     B('**Polos:** radio máximo de 0,907.'),
     P('La ondulación se fijó en 0,01 dB porque se acumula a lo largo de las seis etapas. Con 0,05 dB, el error '
       'de ganancia de la banda de 125 Hz respecto de la de 1 kHz llega a +0,135 dB; con 0,01 dB queda en '
       '+0,028 dB.'),
     P('Los filtros IIR no permiten calcular solo las muestras que sobreviven al diezmado, así que cada etapa '
       'antialias corre a su tasa de entrada. Los antialias suman 1,42 millones de multiplicaciones por segundo '
       'de los 3,32 totales. Una implementación polifásica con filtros pasatodo de media banda los reduciría a '
       'la mitad, pero no hace falta.')])

# ───────────── 3.6 ─────────────
add([H1('3.6 Verificación numérica'),
     P('La verificación tiene dos niveles. El **analítico** evalúa la respuesta en frecuencia de cada banda a '
       'su propia tasa (Figura 3.6). El **extremo a extremo** inyecta tonos de 4 s a 48 kHz, los hace pasar '
       'por toda la cadena (antialias, diezmados y filtro de banda), mide la potencia de salida descartando el '
       'transitorio y calcula la atenuación relativa respecto de la banda de 1 kHz en 1 kHz. Para cada banda se '
       'usan **289 tonos**, entre f_m / G^4,5 y f_m · G^4,5 en pasos de G^(1/32), y cada uno se compara con '
       'la máscara interpolada. Este segundo nivel incluye lo que el análisis por bandas no ve: la ondulación '
       'acumulada de los antialias y el plegado espectral.'),
     *FIGURA('cap3_banco_n4.png', 15.5,
             'Figura 3.6. Respuesta analítica del banco propuesto (N = 4).'),
     *FIGURA('cap3_e2e_relativa.png', 16.5,
             'Figura 3.7. Atenuación relativa extremo a extremo de las 7 bandas superpuestas, en frecuencia '
             'normalizada. Los picos de −80 dB hacia la derecha son tonos cercanos a 24 kHz que el antialias '
             'atenúa 80 dB antes de plegarse; quedan por debajo de la máscara.'),
     KT(['Banda', '125', '250', '500', '1k', '2k', '4k', '8k'],
        [['Error de ganancia en f_m [dB]', '+0,028', '+0,017', '+0,008', '0,000', '−0,003', '−0,005', '−0,005'],
         ['Margen en banda de paso, clase 1 [dB]', '0,37', '0,38', '0,39', '0,40', '0,40', '0,39', '0,39'],
         ['Margen fuera de banda, clase 1 [dB]', '1,94', '1,93', '1,92', '1,91', '1,91', '1,91', '1,90'],
         ['Margen fuera de banda, clase 2 [dB]', '2,75', '2,74', '2,73', '2,72', '2,72', '2,72', '2,71']],
        [2900] + [848] * 7, size=17, center_cols=tuple(range(1, 8))),
     CAP('Tabla 3.7. Resultados de la verificación densa extremo a extremo (N = 4).'),
     P('**Lectura de los márgenes.** En la banda de paso el margen está limitado por el límite de ±0,4 dB en '
       'f_m, que en esta arquitectura mide el error de ganancia entre bandas (como máximo 0,028 dB). Por eso el '
       'margen en banda de paso queda disponible casi entero para otros errores, como la respuesta del micrófono '
       'o la calibración. Fuera de banda, el punto más exigente está justo después del borde inferior '
       '(Ω ≈ G^(−0,53)), en la zona donde la máscara se interpola. El margen allí, de 1,9 dB, depende de la regla '
       'de interpolación supuesta y debe recalcularse con la norma oficial. En los puntos de quiebre '
       'propiamente dichos el margen es de al menos 6,7 dB.'),
     H2('Otros indicadores'),
     B('**Ancho de banda efectivo:** se calcula como la integral de |H|² en escala logarítmica de frecuencia, '
       'normalizada por el ancho nominal log₁₀ G. La desviación es de +0,078 dB (con N = 3, de +0,135 dB). Con '
       'ruido rosa, el error de nivel debido a la forma del filtro queda por debajo de una décima de decibel. La '
       'tolerancia normativa de este indicador debe tomarse de la norma.'),
     B('**Plegado espectral:** ningún tono fuera de G^(±4,2) produce una salida mayor que −80,6 dB en ninguna '
       'banda. El margen es justo respecto de los 80 dB del antialias, pero la máscara exige mucho menos en '
       'esa zona.'),
     B('**Cuantización de coeficientes:** al pasar los coeficientes a float32, la respuesta cambia como máximo '
       '2·10⁻⁶ dB en la zona útil (> −40 dB).'),
     B('**Ganancia en f_m y bordes:** el error de ganancia es menor que 0,03 dB (Tabla 3.7) y la atenuación '
       'en los bordes es de 3,01 dB. Con la bilineal el máximo de la respuesta no cae exactamente en f_m, pero '
       'en un Butterworth la diferencia es despreciable.'),
     H2('Ruido de redondeo en float32'),
     P('Para evaluar la aritmética real se simuló la forma DF2T en precisión simple, como la ejecuta '
       'dsps_biquad_f32, con un caso exigente: un tono fuerte fuera de banda (−13 dBFS a 7,9 kHz) y ruido '
       'blanco a −100 dBFS. El nivel de la banda de 125 Hz, de −124,7 dBFS, coincide con la referencia en doble '
       'precisión con una diferencia de 0,0003 dB, y el error de redondeo queda en −181 dBFS. Si el fondo de '
       'escala del micrófono corresponde a unos 120 dB SPL, los niveles más bajos que interesan (≈ 7 dB SPL '
       'por banda) están cerca de −113 dBFS, y el redondeo queda más de 60 dB por debajo.')])

# ───────────── 3.7 ─────────────
add([H1('3.7 Del filtro al nivel de presión sonora'),
     H2('Nivel equivalente por banda'),
     P('Para cada banda b, la salida del filtro y_b[n], en unidades de fondo de escala, se eleva al cuadrado y '
       'se acumula durante el tiempo de integración T, que contiene N_b = T · f_s,b muestras:'),
     EQ('L_eq,b = 10 · log₁₀( (1 / N_b) · Σ y_b²[n] ) + K + C_b    [dB SPL]', 4),
     P('K es la constante de calibración y C_b la corrección de respuesta del micrófono en la banda b, que se '
       'trata más abajo. La integración es **lineal**, un promedio energético simple como corresponde al L_eq; '
       'no se usan las ponderaciones temporales exponenciales "rápida" y "lenta" de los sonómetros [10].'),
     H2('Calibración'),
     P('Con el calibrador acústico de 94 dB SPL a 1 kHz acoplado, se reinician los filtros, se descartan 0,5 s '
       'y se mide el cuadrado medio de la banda de 1 kHz durante **5 s**, el mismo tiempo que fija el caso de '
       'uso CU-01:'),
     EQ('K = 94 − 10 · log₁₀( media de y_1k² ) − C_1k', 5),
     P('Se usa la salida de la banda de 1 kHz y no la señal de banda ancha para que el ruido ambiente fuera de '
       'la banda no sesgue la calibración. Como el error de ganancia entre bandas es menor que 0,03 dB, la misma '
       'K vale para las siete. K se guarda en NVS con su fecha (RD-10).'),
     P('**Respuesta del micrófono (D3.7).** Los micrófonos MEMS tienen caída en baja frecuencia y realce en '
       'alta, del orden de algunos decibeles hacia 8 kHz [5]. Una única constante a 1 kHz no compensa esa forma. '
       'Por eso las correcciones C_b por banda se incluyen desde el inicio: primero se toman de la curva típica '
       'de la hoja de datos y después se ajustan con el ensayo de comparación EN-05.'),
     H2('Integración por bloques, precisión y transitorios'),
     P('El firmware procesa bloques de 1024 muestras de entrada (21,3 ms). Cada banda acumula la suma de '
       'cuadrados del bloque en float32 y la vuelca en un acumulador de **doble precisión** por sesión: en 120 s '
       'la banda de 8 kHz suma 5,8 millones de muestras y en float32 los incrementos se perderían frente al '
       'acumulado. La indicación se refresca cada **11 bloques (≈ 235 ms)**, de modo que cumple RD-06.'),
     P('El tiempo de establecimiento de la cadena, medido con un tono en f_m que se enciende en t = 0 hasta '
       'quedar dentro de ±0,1 dB, es de **60 ms en la banda de 125 Hz** y de menos de 1 ms en la de 8 kHz. Al '
       'iniciar una medición se descartan 0,5 s, ocho veces ese valor. El descarte queda cubierto por la espera '
       'de estabilización de 3 s de CU-02, durante la cual los filtros ya están procesando.'),
     H2('Incertidumbre estadística del nivel'),
     P('Con ruido aleatorio, el L_eq medido en un tiempo finito fluctúa. Para ruido gaussiano en una banda de '
       'ancho B [11]:'),
     EQ('σ(L_eq) ≈ 4,34 / √(B · T)    [dB]', 6),
     KT(['T', '125 Hz', '250 Hz', '500 Hz', '1 kHz', '2 kHz', '4 kHz', '8 kHz'],
        [['5 s', '0,21', '0,15', '0,10', '0,07', '0,05', '0,04', '0,03'],
         ['10 s', '0,15', '0,10', '0,07', '0,05', '0,04', '0,03', '0,02'],
         ['30 s', '0,08', '0,06', '0,04', '0,03', '0,02', '0,02', '0,01']],
        [1100] + [962] * 7, size=17, center_cols=tuple(range(8))),
     CAP('Tabla 3.8. Desvío estándar del L_eq [dB] según el tiempo de integración.'),
     P('El mínimo de 10 s de RD-06 da un desvío de 0,15 dB en la banda más baja, y los 30 s por defecto lo '
       'bajan a 0,08 dB. Ambos son compatibles con la exactitud pedida. El ruido real de una cabina no es '
       'estacionario, así que estos valores son una cota inferior.')])

# ───────────── 3.8 ─────────────
add([H1('3.8 Ruido propio del micrófono y límite de detección'),
     H2('Alcance respecto de ISO 8253-1'),
     P('ISO 8253-1 [2] fija niveles máximos de ruido ambiente según el tipo de audiometría: conducción aérea con '
       'auriculares, conducción ósea o campo libre. Los valores de la tabla del prototipo '
       '(35/25/21/26/34/37/43 dB SPL de 125 Hz a 8 kHz) parecen corresponder a **conducción aérea con '
       'auriculares supraaurales**. Los límites para conducción ósea y campo libre son mucho más bajos, de un '
       'dígito en 1 a 4 kHz, y quedan por debajo del piso de cualquier micrófono MEMS. **El alcance del '
       'instrumento se acota a la verificación para conducción aérea con auriculares.** Los valores exactos, '
       'incluido el de 8 kHz, deben confirmarse con la norma.'),
     H2('Estimación del piso de ruido'),
     P('El ruido equivalente de entrada (EIN) del micrófono sale de su hoja de datos: 94 dB SPL menos la relación '
       'señal/ruido ponderada A. Para el INMP441 es de 33 dBA (SNR 61 dBA) [6] y para el ICS-43434, de 29 dBA (SNR '
       '65 dBA) [5]. Si se supone un ruido de espectro blanco, el nivel por banda se obtiene repartiendo el EIN '
       'según el ancho equivalente de la ponderación A entre 20 Hz y 20 kHz, que es de unos 12 470 Hz:'),
     EQ('L_ruido,b = EIN + 10 · log₁₀( B_b / 12 470 )', 7),
     *FIGURA('cap3_piso_ruido.png', 15.5,
             'Figura 3.8. Piso de ruido estimado por banda frente a los límites de la tabla del prototipo.'),
     KT(['Banda', 'Límite ISO*', 'INMP441: piso / margen', 'ICS-43434: piso / margen', 'Sesgo si L = límite (ICS)'],
        [['125 Hz', '35', '11,5 / 23,5', '7,5 / 27,5', '0,01 dB'],
         ['250 Hz', '25', '14,5 / 10,5', '10,5 / 14,5', '0,15 dB'],
         ['500 Hz', '21', ('17,5 / 3,5 ✗', 'F8D7DA'), '13,5 / 7,5', '0,71 dB'],
         ['1 kHz', '26', '20,5 / 5,5', '16,5 / 9,5', '0,46 dB'],
         ['2 kHz', '34', '23,5 / 10,5', '19,5 / 14,5', '0,15 dB'],
         ['4 kHz', '37', '26,5 / 10,5', '22,5 / 14,5', '0,15 dB'],
         ['8 kHz', '43', '29,5 / 13,5', '25,5 / 17,5', '0,08 dB']],
        [1200, 1300, 2200, 2200, 1937], size=18, center_cols=(0, 1, 2, 3, 4)),
     CAP('Tabla 3.9. Estimación del piso de ruido [dB SPL] y margen frente a RD-03 (≥ 5 dB). '
         '*Valores de la tabla del prototipo, pendientes de verificar contra ISO 8253-1.'),
     P('**Decisión D3.2: micrófono ICS-43434.** Con el INMP441 el margen en 500 Hz es de 3,5 dB y no cumple '
       'RD-03. Una medición justo en el límite tendría un sesgo de +1,6 dB. Con el ICS-43434 el margen mínimo es '
       'de 7,5 dB y el sesgo en el límite queda por debajo de 0,8 dB. El cambio no altera la interfaz I2S ni el '
       'firmware. Es una decisión compartida con el capítulo de hardware, que debe resolver el montaje del '
       'encapsulado LGA.'),
     P('**Tensión entre requisitos.** Un piso de ruido exactamente 5 dB por debajo del límite (el mínimo que '
       'admite RD-03) sesga en +1,2 dB una medición que esté en el límite, más de lo que permite RD-05 '
       '(±0,5 dB). Para que el sesgo no supere 0,5 dB sin corrección, el margen debería ser de al menos 9,1 dB. '
       'La tensión se resuelve con la corrección por ruido propio descrita a continuación; se propone, además, '
       'revisar la redacción de RD-03 en la especificación de requisitos.'),
     H2('Regla de tratamiento y veredicto'),
     P('El firmware guarda en NVS el piso de ruido medido por banda (L_piso,b) con el procedimiento de EN-02. '
       'Con la diferencia Δ = L_medido − L_piso:'),
     B('**Δ ≥ 10 dB:** se informa L_medido sin corrección; el sesgo es menor que 0,5 dB.'),
     B('**3 dB ≤ Δ < 10 dB:** se resta la energía del piso, L = 10 · log₁₀(10^(L_medido/10) − 10^(L_piso/10)), y '
       'la banda se marca como "corregida" en el registro y en el informe.'),
     B('**Δ < 3 dB:** la banda queda **por debajo del límite de detección** y se informa "< L_det". Como RD-03 '
       'garantiza L_piso ≤ límite ISO − 5 dB, una banda por debajo del límite de detección **cumple** el '
       'requisito de ISO 8253-1: el veredicto es APTA para esa banda.'),
     P('**Supuestos y riesgos.** El ruido de los MEMS no es blanco: el componente 1/f lo hace crecer en baja '
       'frecuencia, así que el piso real en 125 y 250 Hz será mayor que el estimado. El margen en esas bandas es '
       'amplio, pero la estimación debe confirmarse con el ensayo EN-02, con el micrófono en un recinto aislado.')])

# ───────────── 3.9 ─────────────
add([H1('3.9 Implementación en el ESP32-S3'),
     B('**Biblioteca:** ESP-DSP [7] ofrece dsps_biquad_f32, con una variante optimizada para las instrucciones '
       'vectoriales del ESP32-S3. Usa el formato {b₀, b₁, b₂, a₁, a₂} con a₀ = 1 y dos variables de estado '
       'por sección (ecuación 3), el mismo formato que genera octave_coeffs.h.'),
     B('**Memoria:** 46 SOS × (5 coeficientes + 2 estados) × 4 bytes ≈ 1,3 kB. A eso se suman los búferes '
       'intermedios de cada tasa, 1024 + 512 + … + 16 muestras en float32 ≈ 8 kB. En total, unos 9 kB: caben '
       'holgadamente en la SRAM interna.'),
     B('**Cómputo:** 3,32 millones de multiplicaciones por segundo. Aun suponiendo 10 ciclos por '
       'multiplicación-acumulación, con lazos, cargas y la conversión de 24 bits a float, son unos 33 millones de '
       'ciclos por segundo: alrededor del 14 % de un núcleo a 240 MHz. Es una cota conservadora frente al 70 % de '
       'RD-07, y se medirá en el ensayo EN-06.'),
     B('**Generación automática:** el firmware no contiene coeficientes escritos a mano; incluye '
       'octave_coeffs.h, generado por diseno_banco.m. Así se elimina la causa raíz del error del prototipo.'),
     B('**Modo de prueba:** un comando de servicio reemplaza las muestras del I2S por un barrido senoidal '
       'generado internamente, lo que permite ejecutar EN-01 en el equipo real.')])

# ───────────── 3.10 ─────────────
add([H1('3.10 Plan de verificación del procesamiento'),
     KT(['ID', 'Tipo', 'Procedimiento', 'Criterio de aceptación', 'Verifica'],
        [['PU-DSP-01', 'Unitaria (PC, integración continua)',
          'diseno_banco.m con la máscara oficial de IEC 61260-1',
          'Margen ≥ 0 dB en todas las bandas (clase 2 obligatoria; objetivo clase 1)', 'RD-02 · HU-13'],
         ['PU-DSP-02', 'Unitaria (MCU)', 'Vectores de referencia: la salida del firmware para 10 señales de '
          'prueba se compara con la de Octave', 'Error de nivel ≤ 0,01 dB por banda', 'RD-01, RD-07'],
         ['PU-DSP-03', 'Unitaria (MCU)', 'Tono de amplitud conocida en f_m de cada banda; L_eq de 10 s',
          'L_eq teórico ± 0,05 dB', 'RD-05'],
         ['PU-DSP-04', 'Unitaria (MCU)', 'Señal de fondo de escala y silencio digital',
          'Sin desbordes ni NaN; nivel mínimo representable < 0 dB SPL', 'RD-04'],
         ['EN-01', 'Integración', 'Barrido senoidal en modo de prueba y, luego, barrido eléctrico',
          'Dentro de la máscara', 'RD-02'],
         ['EN-02', 'Sistema', 'Micrófono en recinto aislado; L_eq de 60 s por banda',
          'Piso ≥ 5 dB bajo el límite ISO; se guarda en NVS', 'RD-03'],
         ['EN-03', 'Sistema', 'Calibración con 94 dB / 1 kHz; 10 repeticiones',
          '94,0 ± 0,5 dB; desvío estándar ≤ 0,2 dB', 'RD-05, RD-10'],
         ['EN-04', 'Sistema', 'Tonos de 30 a 100 dB SPL en escalones de 5 dB frente al sonómetro de referencia',
          'Linealidad ±1,0 dB', 'RD-04'],
         ['EN-05', 'Sistema', 'Comparación con el sonómetro de referencia (ruido rosa y cabina real)',
          '±1,5 dB (250 Hz – 4 kHz); ±2 dB (125 Hz y 8 kHz); ajusta C_b', 'RD-01'],
         ['EN-06', 'Sistema', 'Funcionamiento de 8 h con registro de CPU, desbordes y latencia',
          'CPU ≤ 70 %; 0 desbordes; refresco ≤ 250 ms', 'RD-06, RD-07'],
         ['EN-09', 'Sistema', 'Piso de ruido con Wi-Fi activo frente a inactivo',
          'Diferencia ≤ 1 dB', 'Ambiente']],
        [1150, 1350, 2700, 2500, 1137], size=16),
     CAP('Tabla 3.10. Pruebas unitarias nuevas (PU-DSP) y ensayos del anteproyecto que verifican este capítulo.')])

# ───────────── 3.11 ─────────────
add([H1('3.11 Conclusiones y decisiones'),
     KT(['ID', 'Decisión', 'Justificación'],
        [['D3.1', 'Butterworth, prototipo N = 4 (orden 8, 4 SOS por banda)',
          'Cumple la máscara de trabajo clase 1 extremo a extremo; N = 3 no cumple ni clase 2'],
         ['D3.2', 'Micrófono ICS-43434 en lugar de INMP441', 'Margen de ruido ≥ 7,5 dB en todas las bandas (RD-03)'],
         ['D3.3', 'f_s = 48 kHz y arquitectura multitasa con diezmado por 2',
          'Mitad de costo que a 48 kHz directo; polos con |p| ≤ 0,90; extensible'],
         ['D3.4', 'Antialias elíptico de orden 6, ondulación 0,01 dB, rechazo de 80 dB',
          'Error entre bandas ≤ 0,03 dB tras 6 etapas; plegado < −80 dB'],
         ['D3.5', 'L_eq lineal; calibración de 5 s en la banda de 1 kHz; acumulador de doble precisión',
          'Coherente con ISO 8253-1; inmune al ruido fuera de banda; sin pérdida numérica'],
         ['D3.6', 'Coeficientes generados por script y verificados automáticamente',
          'Elimina la causa raíz del error del prototipo'],
         ['D3.7', 'Corrección de respuesta del micrófono por banda (C_b)',
          'La respuesta MEMS no es plana; se ajusta con EN-05'],
         ['D3.8', 'Regla de piso de ruido: sin corrección / corregida / < L_det (cumple)',
          'Resuelve la tensión entre RD-03 y RD-05; veredicto lógicamente consistente']],
        [800, 3900, 4137], size=18),
     H2('Pendientes'),
     B('Obtener IEC 61260-1:2014 y reemplazar la máscara de trabajo y la regla de interpolación por las '
       'oficiales, incluida la tolerancia del ancho de banda efectivo.'),
     B('Verificar los límites de ruido ambiente de ISO 8253-1:2010, en particular el de 8 kHz, y confirmar si la '
       'norma exige instrumental clase 1. En ese caso RD-02 debería pasar a clase 1, que el diseño ya alcanza.'),
     B('Confirmar con el ensayo EN-02 el piso de ruido real del ICS-43434, incluido el componente 1/f.'),
     B('Revisar la redacción de RD-03 a la luz de la tensión con RD-05 (sección 3.8).'),
     H2('Historial de revisión'),
     KT(['Versión', 'Cambios'],
        [['0.1', 'Borrador inicial (elefante: redactor con el contexto completo del proyecto).'],
         ['0.2', 'Revisión con el método Elephant–Goldfish [12]: tres revisores sin contexto previo (técnico DSP, '
          'trazabilidad y evaluador académico). Cambios principales: corrección del cálculo de costo; causa raíz '
          'completa con inestabilidad en float32; definición de atenuación relativa; verificación densa contra la '
          'máscara; reformulación de la justificación de la multitasa; ecuaciones, polos y ceros, alternativas FIR '
          'y FFT; transitorio, redondeo e incertidumbre del L_eq; alcance frente a ISO 8253-1; regla de veredicto; '
          'citas y siglas. Decisiones propagadas al anteproyecto y al anexo de Ingeniería de Software. '
          'El registro completo está en revision_egm/registro_cap3_v0.2.md.']],
        [1100, 7737], size=17),
     H1('Referencias del capítulo'),
     *[P(r, size=20, align='left') for r in [
         '[1] IEC 61260-1:2014. Electroacoustics — Octave-band and fractional-octave-band filters — Part 1: '
         'Specifications.',
         '[2] ISO 8253-1:2010. Acoustics — Audiometric test methods — Part 1: Pure-tone air and bone '
         'conduction audiometry.',
         '[3] Oppenheim, A. V.; Schafer, R. W. Discrete-Time Signal Processing, 3.ª ed. Pearson, 2010.',
         '[4] Crochiere, R. E.; Rabiner, L. R. Multirate Digital Signal Processing. Prentice Hall, 1983.',
         '[5] TDK InvenSense. ICS-43434 Multi-Mode Microphone with I2S Digital Output — Data Sheet.',
         '[6] TDK InvenSense. INMP441 Omnidirectional Microphone with I2S Digital Output — Data Sheet.',
         '[7] Espressif Systems. ESP-DSP Library — API Reference (dsps_biquad_f32).',
         '[8] GNU Octave y paquete signal 1.4.5: butter, ellip, zp2sos, sosfilt.',
         '[9] Bristow-Johnson, R. Cookbook formulae for audio EQ biquad filter coefficients (W3C Audio EQ '
         'Cookbook).',
         '[10] IEC 61672-1:2013. Electroacoustics — Sound level meters — Part 1: Specifications.',
         '[11] Bendat, J. S.; Piersol, A. G. Random Data: Analysis and Measurement Procedures, 4.ª ed. '
         'Wiley, 2010.',
         '[12] Google Open Source. Introducing the Elephant Goldfish Model plugin. Octubre de 2026.']]])

# ───────────── Ensamblado sobre la plantilla ─────────────
z = zipfile.ZipFile(TPL)
files = {n: z.read(n) for n in z.namelist()}
doc = files['word/document.xml'].decode('utf-8')
b0 = doc.index('<w:body>') + len('<w:body>')
paras = list(re.finditer(r'<w:p[ >].*?</w:p>', doc[b0:], re.S))
header = ''.join(m.group(0) for m in paras[:3])
sect = re.search(r'<w:sectPr>.*?</w:sectPr>', doc, re.S).group(0)
doc = doc[:b0] + header + ''.join(body) + sect + '</w:body></w:document>'
files['word/document.xml'] = doc.encode('utf-8')

rels = files['word/_rels/document.xml.rels'].decode()
extra = ''.join(f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/'
                f'relationships/image" Target="media/{fn}"/>' for rid, fn in IMAGES)
files['word/_rels/document.xml.rels'] = rels.replace('</Relationships>', extra + '</Relationships>').encode()
for _, fn in IMAGES:
    files[f'word/media/{fn}'] = open(os.path.join(FIG, fn), 'rb').read()
ct = files['[Content_Types].xml'].decode()
if 'Extension="png"' not in ct:
    ct = ct.replace('<Default ', '<Default Extension="png" ContentType="image/png"/><Default ', 1)
files['[Content_Types].xml'] = ct.encode()

with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED) as zo:
    for n, data in files.items():
        zo.writestr(n, data)
print('OK', OUT)
