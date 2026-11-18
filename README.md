# Analizador autónomo de ruido ambiente por bandas de octava (ISO 8253-1)

Trabajo final de la **Especialización en Sistemas Embebidos — FI-UNER**.
Autor: Andrés Machtey · Director propuesto: Esp. Víctor Valotto (FIUNER).

El trabajo se organiza en capítulos; cada uno analiza el mismo proyecto desde el enfoque de una materia de la
carrera. Cada capítulo se revisa con el método **Elephant–Goldfish** (un redactor con todo el contexto y tres
revisores independientes sin contexto previo); los registros de cada revisión están en `revision_egm/`.

## Contenido

| Carpeta / archivo | Contenido |
|---|---|
| `Anteproyecto_Decibelimetro_Octavas_Machtey.docx` | Anteproyecto sobre la plantilla de la carrera |
| `ingenieria_software/` | Anexo de Ingeniería de Software (casos de uso, historias de usuario, FSM, trazabilidad) y modelos PlantUML |
| `capitulos/` | Cap. 3 DSP · Cap. 4 Sistemas operativos de tiempo real · Cap. 5 Diseño de hardware |
| `dsp/` | Diseño y verificación del banco de filtros (GNU Octave + paquete signal), coeficientes `octave_coeffs.h` |
| `rtos/` | Análisis temporal y simulaciones del firmware (Python) |
| `hw/` | Potencia, autonomía, carga, rizado, térmica y masa (Python) |
| `figuras/` | Figuras (SVG fuente y PNG) |
| `scripts/` | Generadores de los documentos `.docx` y de los diagramas |
| `revision_egm/` | Borradores revisados (PDF/TXT) y registros de cada ronda de revisión |
| `plantilla/` | Plantilla del anteproyecto de la carrera |

## Cómo regenerar

Requisitos: Python 3 con Pillow, GNU Octave con el paquete `signal`, gnuplot, ImageMagick y LibreOffice (para
convertir a PDF). Desde la raíz del repositorio:

```bash
# Cálculos y figuras
(cd dsp && octave --no-gui octave/diseno_banco.m && octave --no-gui octave/analisis_complementario.m && gnuplot octave/graficos.gp)
(cd rtos && python3 -I analisis_temporal.py && gnuplot graficos_rt.gp)
(cd hw && python3 -I analisis_potencia.py && gnuplot graficos_hw.gp)

# Documentos
T=plantilla/ModeloAnteproyecto.docx
python3 -I scripts/generar_anteproyecto.py $T figuras/diagrama_bloques.png Anteproyecto_Decibelimetro_Octavas_Machtey.docx
python3 -I scripts/generar_ing_software.py $T figuras/casos_de_uso.png ingenieria_software/Ingenieria_Software_Casos_de_Uso_HU.docx
python3 -I scripts/generar_cap3_dsp.py $T figuras capitulos/Cap3_DSP_Banco_Octavas.docx
python3 -I scripts/generar_cap4_rtos.py $T figuras capitulos/Cap4_RTOS_Firmware.docx
python3 -I scripts/generar_cap5_hw.py $T figuras capitulos/Cap5_Hardware.docx
```

Los documentos se editan en los scripts, no en los `.docx`.

## Estado

| Documento | Versión |
|---|---|
| Anteproyecto | alineado con los Cap. 3, 4 y 5 |
| Anexo de Ingeniería de Software | 0.4 |
| Cap. 3 — DSP | 0.2 |
| Cap. 4 — Tiempo real | 0.2.1 |
| Cap. 5 — Hardware | 0.2 |

## Aviso

Los límites de IEC 61260-1 e ISO 8253-1 usados en los cálculos son **valores de trabajo** pendientes de
verificar contra las normas, que no se incluyen en el repositorio por derechos de autor. Los consumos de
hardware son supuestos hasta su medición.

Repositorios relacionados: [decibilimetro-iso8253](https://github.com/andresmach/decibilimetro-iso8253) (prototipo
del curso de DSP) y [decibel-iso](https://github.com/andresmach/decibel-iso) (PWA para celular).
