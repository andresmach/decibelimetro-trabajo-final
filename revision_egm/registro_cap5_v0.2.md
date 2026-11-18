# Registro de revisión EGM — Capítulo 5 (Hardware), v0.1 → v0.2

Revisores sin contexto previo: T = técnico de hardware (consultó la hoja de datos del BQ24074 y ESP-IDF 5.4) ·
R = trazabilidad · A = evaluador académico (nota tentativa de la v0.1: "aprobado, cerca de bueno").

## Aceptados e incorporados

| # | Origen | Hallazgo | Cambio |
|---|---|---|---|
| 1 | R | El hardware no podía apagarse por firmware (APAGADO del anexo y del Cap. 4); riesgo de descarga profunda | Conmutador con enclavamiento (POWER_HOLD); D5.4 rehecha; PU-HW-03 ampliada |
| 2 | T, A | Con el equipo apagado, EN1/EN2 quedaban indefinidos (USB100 → ~20 h de carga); CC sobre GPIO sin alimentar | Resistencias de modo por defecto (USB500) y comparador de CC con alimentación desde OUT; el ESP32 solo lee su salida |
| 3 | T, R | ILIM limita la corriente de entrada; la de carga la fija ISET | ISET = 0,8 A, ILIM = 1,5 A; Tabla 5.6 con equipo apagado y encendido |
| 4 | T, R, A | Con USB, OUT = 4,4 V: más disipación en el LDO; balance térmico del gabinete ausente | Térmica con USB (246 mW), cargador de 0,9 a 1,7 W, gabinete ≈ +8 °C; PU-HW-06 combinada |
| 5 | T, A | Faltaban la NTC en TS y la protección de polaridad | NTC de 10 kΩ en la celda; P-MOSFET de polaridad; PU-HW-08 |
| 6 | T | El criterio de fracción utilizable estaba mal atribuido (el ESP32 tolera 3,0 V) | Corte por VSYS con carga ≤ 3,50 V (filtrado, con histéresis) → 94 %; buck-boost +8 % |
| 7 | T | Consumo del ESP32 en modo punto de acceso optimista; R_int incompleta | 145/130/170 mA; resistencia serie de 250 mΩ desglosada; sensibilidad; celda de 3000 mAh (D5.2) |
| 8 | T, R | Divisor de batería sin ubicación | Divisor 2 × 1 MΩ sobre BAT; incluido en el consumo apagado |
| 9 | T, R | Corte de 3,60 V con margen nulo y caída del LDO ambigua (0,25 frente a 0,30 V) | Valor único de 0,25 V; nuevo corte; PU-HW-04 con error ≤ 30 mV |
| 10 | A | Faltaban el esquemático conceptual y el FMEA | Figura 5.1 (bloques de hardware) y Tabla 5.9 (FMEA cualitativo) |
| 11 | A, R | Faltaban la masa, el apilado, la humedad y la estabilización | Tabla 5.8 (33,6 mm, 248 g) y texto de D5.8 |
| 12 | T | Cadena del micrófono | Pull-down de 100 kΩ en SD; filtros RF; malla en ambos extremos; 5 conductores + malla |
| 13 | T, R | Inmunidad mal atribuida a EN-09; ESD incompleta; UN 38.3 | PU-HW-09 (ESD informal y teléfono); TVS en CC y pulsadores; normativa ampliada |
| 14 | T | Pines: GPIO33/34 de PSRAM, LED en MISO, sufijo del módulo, pull-ups | Texto y Tabla 5.7 corregidos; N16R8 sin sufijo V; MISO libre |
| 15 | A, R | Referencias cruzadas, siglas (LGA), "medición" ambigua, bibliografía, texto provisorio | Corregidos; Horowitz y Hill, Bogatin |
| 16 | T | USB 2.0 garantiza 100 mA sin enumeración | Declarado como limitación |
| 17 | T | Criterio de PU-HW-01 no discriminaba | ≤ 1 mVpp; el criterio funcional es EN-09 |
| 18 | A | Desacople sin cuantificar; RC de EN | 35 µF calculados → 47 + 10 µF + 100 nF; RC de EN según la guía |

## No incorporados o diferidos

| Origen | Hallazgo | Motivo |
|---|---|---|
| A | BOM con números de parte completos | Corresponde a E4 (esquemático); los candidatos están en la Tabla 5.3 |
| A | Reglas DFM detalladas del fabricante | Se definen al elegir el fabricante en E4 |
| T | Controlador Type-C dedicado | El comparador cubre la necesidad con menos costo; queda como alternativa |

## Cambios necesarios en OTROS documentos (pendientes de aprobación del autor)

1. **Anteproyecto**, Material y Equipo: celda 18650 de 3000 mAh protegida con portapila; módulo WROOM-1 N16R8; BQ24074, LDO 3,3 V, LP5907, comparador; zócalo microSD en la placa; plantilla y aire caliente o módulo con ICS-43434; fuente USB-C ≥ 1,5 A para ensayos.
2. **Anteproyecto**, Costos: conciliar con ≈ USD 84 por prototipo (sin placa de desarrollo).
3. **Anteproyecto**, RD-08: "carga ≤ 4 h con fuente USB-C que anuncie ≥ 1,5 A"; EN-07 con esa fuente.
4. **Anteproyecto**, Características físicas: 160 mm de cuerpo más vástago desmontable de ≈ 100 mm; pulsador de encendido.
5. **Anteproyecto**, ensayos: EN-09 con caso de USB conectado; mención de PU-HW-09 (ESD informal); Gantt: PU-HW en 4.5/6.1.
6. **Anexo IS**: eventos USB conectado/desconectado (modo de carga y tiempo estimado), batería baja y batería crítica (VSYS ≤ 3,50 V con carga, filtrada) → APAGADO por POWER_HOLD; pulsación larga para apagar; medir mientras carga permitido y registrado.
7. **Cap. 4**: T_MON dueña del ADC1 (VBAT) y de /CHG, /PGOOD y "fuente ≥ 1,5 A" (eventos a q_evt); umbral 3,50 V filtrado; apagado liberando POWER_HOLD; D4.4 referida al margen de autonomía del Cap. 5.
