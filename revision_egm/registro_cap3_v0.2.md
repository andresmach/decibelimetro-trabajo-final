# Registro de revisión EGM — Capítulo 3 (DSP), v0.1 → v0.2

Método: Elephant–Goldfish. El elefante (redactor con contexto completo) produjo la v0.1.
Tres peces dorados (revisores sin contexto previo) la revisaron por separado:
T = técnico DSP/acústica · R = trazabilidad · A = evaluador académico.
Decisión final de cada cambio: autor humano (pendiente de aprobación).

## Aceptados e incorporados en v0.2

| # | Origen | Hallazgo | Cambio |
|---|--------|----------|--------|
| 1 | T, R | Error de índice en el costo (antialias asignado a la banda de 8 kHz a 96 kHz) | Script corregido: 3,32 M mult/s (N=4), 2,85 M (N=3), +17 %; CPU ≈ 14 % |
| 2 | T, A | Causa raíz incompleta; 125 Hz mal descrita | ω₀ ausente en todas las bandas (a₁ = −(1+a₂)); inestabilidad en float32 en 1 y 8 kHz; 125 Hz con polos complejos y 1,4 octavas de ancho |
| 3 | T | La verificación usaba solo 17 puntos | Verificación densa: 289 tonos por banda contra la máscara interpolada; márgenes de banda de paso y de rechazo por separado |
| 4 | T, A | Definición de atenuación relativa / margen trivial en f_m | Referencia a la banda de 1 kHz en 1 kHz; error de ganancia entre bandas informado |
| 5 | T | Alcance frente a ISO 8253-1 | Acotado a conducción aérea con auriculares; ósea y campo libre fuera de alcance |
| 6 | A | Faltaba teoría | Ecuaciones (1)–(7): bilineal con predistorsión, SOS, DF2T, L_eq, K, σ, piso de ruido |
| 7 | A | Faltaban polos y ceros | Figura 3.2 (prototipo frente a propuesto) |
| 8 | A | Faltaban alternativas | Tabla 3.4: FIR, FFT, IIR directo, IIR multitasa |
| 9 | A | Descarte de 0,5 s sin justificar | Transitorio medido: 60 ms en 125 Hz |
| 10 | A | Faltaba el ruido de redondeo | DF2T simulada en float32: −181 dBFS |
| 11 | A | Faltaba la incertidumbre del L_eq | Ecuación (6) y Tabla 3.8 |
| 12 | A | Tensión entre RD-03 y RD-05 | Declarada; se resuelve con D3.8 y se propone revisar RD-03 |
| 13 | R | Regla del piso de ruido contradictoria | D3.8: sin corrección / corregida / "< L_det" = cumple |
| 14 | R | Calibración: 10 s frente a 5 s de CU-01 | Unificado en 5 s |
| 15 | R | Tabla de pruebas incompleta | Columna "Verifica"; se agregan EN-04, EN-05 y EN-09; EN-03 y EN-06 completos |
| 16 | A, R | Refresco 12→11 bloques | Valor único: 11 bloques ≈ 235 ms |
| 17 | A | Sin justificación del paso de 51,2 a 48 kHz | Agregada en 3.5 |
| 18 | T | Micrófono supuesto plano | D3.7: corrección C_b por banda desde el inicio |
| 19 | T | 0,16 dB no reproducible | Reemplazado por 0,135 dB, ahora calculado por analisis_complementario.m |
| 20 | T | "Exactamente 0 dB" y "centrada" | Redacción corregida |
| 21 | T | N=3 con más sobremuestreo | Mencionado como alternativa |
| 22 | T | Ancho efectivo sin método ni límite | Integral en log f; tolerancia pendiente de la norma |
| 23 | R | Memoria y radio del antialias | ≈ 9 kB en total; antialias \|p\| = 0,907 |
| 24 | A | Citas, siglas y redacción | Citas [n] en el texto, tabla de siglas, glosas corregidas |
| 25 | A | Tablas partidas; leyenda confusa | Tablas que no se parten; leyenda aclarada; texto del diagrama más grande |
| 26 | A | Figuras 3.5 y 3.6 redundantes | Se reemplaza la figura extremo a extremo por la de atenuación relativa con la máscara; se explican los picos cerca de 24 kHz |

## Hallazgo del elefante durante la integración

- Al analizar el contra-caso que pidió A (125 Hz a 48 kHz en float32), el diseño directo resultó viable: 0,006 dB de error de coeficientes y −178 dBFS de redondeo. La v0.1 sobrestimaba la necesidad de la multitasa por precisión. **La justificación se reformuló**: mitad de costo (6,7 → 3,3 M mult/s), robustez y extensibilidad.

## No incorporados (o diferidos)

| Origen | Hallazgo | Motivo |
|--------|----------|--------|
| A | Usar el editor de ecuaciones de Word | El generador es XML plano; las ecuaciones están numeradas en texto. Se convertirán a OMML en la versión final si el formato lo exige |
| A | Llevar la elección del micrófono al capítulo de hardware | Se mantiene D3.2 porque la justifica el análisis de ruido por banda; se indica que es una decisión compartida |
| T | Confirmar si ISO 8253-1 exige clase 1 y el valor de 8 kHz | Requiere la norma: queda en Pendientes |

## Cambios necesarios en OTROS documentos (pendientes de aprobación del autor)

1. Anteproyecto, Métodos › PDS: "Butterworth 6.º orden / Python-SciPy" → orden 8 (N=4) / GNU Octave + signal.
2. Anteproyecto, Material: agregar GNU Octave; micrófono ICS-43434 (INMP441 solo como referencia); encapsulado LGA (adaptador o reflow).
3. Anteproyecto, Limitaciones: margen en 500 Hz → 7,5 dB con ICS-43434; riesgo 1/f.
4. Anteproyecto, Datos históricos: banda de 1 kHz de < 10 a 1117 Hz; ω₀ ausente; inestabilidad en float32.
5. Anteproyecto: pruebas unitarias DSP en MCU (PU-DSP-02..04) además de las del host.
6. Anexo IS: CU-02 4b y CU-03 1a → regla D3.8; nueva HU/CU "Medir piso de ruido propio" (RD-03, EN-02); CU-05 marca las bandas corregidas; columna PU-DSP en la matriz de trazabilidad; HU-13 → Octave en CI.
7. ERS (E1): f_s = 48 kHz, bloques de 1024, C_b por banda; revisar RD-03 frente a RD-05; posible RD-02 → clase 1.
