# Registro de revisión EGM — Capítulo 4 (RTOS), v0.1 → v0.2

Revisores sin contexto previo: T = técnico de tiempo real / ESP-IDF (verificó en el código fuente de ESP-IDF 5.4) ·
R = trazabilidad · A = evaluador académico (nota tentativa de la v0.1: "bueno").
Los hallazgos críticos de T se confirmaron leyendo el código fuente antes de incorporarlos.

## Aceptados e incorporados

| # | Origen | Hallazgo | Cambio |
|---|---|---|---|
| 1 | T | La cola del driver tiene `desc_num − 1` entradas (i2s_common.c:328) | Q = (N−1)·512; 160 ms útiles; S_máx ≈ 154 ms; simulación rehecha (8 desc.: 1536 muestras perdidas) |
| 2 | T | lwIP y httpd sin afinidad; esp_timer en CPU0; IPC1 con prioridad 24; ISR del GDMA en el núcleo que inicializa | Afinidad explícita (Tabla 4.14); canal creado desde T_DSP; interferencias corregidas |
| 3 | T, A | RTA sin bloqueo SMP ni fluctuación | Ec. (2) con B y J; detenciones por flash fuera del RTA |
| 4 | T | Fuentes de flash no controladas (NVS del Wi-Fi, lectura de particiones web) | Tabla 4.12: Wi-Fi en RAM, web embebida; volcado de memoria como excepción |
| 5 | T, A | El driver toma un candado APB_FREQ_MAX; T_DSP bloqueada en REPOSO con el TWDT | Canal deshabilitado en REPOSO; espera con plazo de 500 ms; pseudocódigo; aporte a RD-08 matizado |
| 6 | T | H4.3 sobrestimado; faltaba la escritura en NVS desde task_dsp | H4.3 en severidad media con todas las líneas; nuevo H4.4; H4.8 incluye g_cal_factor |
| 7 | T, A, R | Métrica de la simulación del pool ambigua y no monótona | Métrica "procesados alterados": 84–99 %; definición explícita |
| 8 | A | Faltaba el análisis del núcleo 0 | Tabla 4.9 con costos supuestos explícitos |
| 9 | A | Se confundían WCET, estimación y máximo observado; los 10 ciclos por multiplicación no estaban justificados | Terminología corregida; justificación de la cota |
| 10 | A | Plazo efectivo y recuperación | Ec. (3): t_r = S·U/(1−U) |
| 11 | A | Faltaban secuencia, pseudocódigo, alternativas y EDF | Figura 4.2, ciclo de T_DSP, Tabla 4.4, párrafo sobre EDF |
| 12 | A | Latencia de 281 ms frente a RD-06 | Aclarado: RD-06 fija el período, no la latencia |
| 13 | R | Espera de 3 s y descarte de 0,5 s contradictorios | PREPARAR/INICIAR: sin reinicio de filtros en MIDIENDO; descarte solo en CALIBRAR/PISO |
| 14 | R | q_cmd de 16 B insuficiente | 48 B |
| 15 | R | PU-RT-04 citaba EN-09 | RD-07 · CU-04 · EN-06 |
| 16 | R | Decisiones sin prueba | PU-RT-07 (energía), 08 (acumulador), 09 (TWDT); columna "Verificación" |
| 17 | R | Umbral de alarma frente a criterio de aceptación | Explicado (10,7 ms en campo frente a 6,2 ms en laboratorio) |
| 18 | T | Falta ESP_TASK_WDT_TIMEOUT_S; la suspensión automática no figura como experimental; % de SRAM | Corregidos |
| 19 | A | Siglas, anglicismos, tablas sin número, [7] sin citar, jerga del historial | Corregidos |

## No incorporados o diferidos

| Origen | Hallazgo | Motivo |
|---|---|---|
| A | Ecuaciones con editor de fórmulas | Mismo criterio que en el Cap. 3 (OMML en la versión final) |
| A | Figuras en página apaisada | Se amplió el ancho a 17 cm; se evaluará en la versión final |
| T | Medir B, costos de ISR y ráfagas Wi-Fi | Requiere el hardware: PU-RT-02 y PU-RT-04 |

## Cambios necesarios en otros documentos (pendientes de aprobación del autor)

1. **Anteproyecto**, Métodos › Firmware embebido: reemplazar "captura en el núcleo 0, DSP en el núcleo 1, búferes ping-pong" por "captura y DSP en una tarea del núcleo 1 sobre el anillo DMA de i2s_std; aplicación y Wi-Fi en el núcleo 0; colas con mensajes por valor; medición con contador de ciclos".
2. **Anteproyecto**, tareas: agregar la tarea 3.8 "Pruebas de concurrencia y robustez" (≈ 12 h, mar–abr) o ampliar la 3.2; E3 debe mencionar la medición de C en la placa (PU-RT-02).
3. **Anexo IS**, máquina de estados (v0.3): estado ESPERA (3 s) entre REPOSO y MIDIENDO; rechazo de escrituras en flash/OTA en MIDIENDO, CALIBRANDO y MIDIENDO_PISO; ACTUALIZANDO → imagen corrupta → REPOSO; falla fatal/TWDT → INICIO; autotransición "desborde DMA" en MIDIENDO (sesión "con pérdidas").
4. **Anexo IS**, CU-02: alternativo 7b (microSD con error, sesión retenida); postcondición con la marca "con pérdidas"; CU-05: la marca en el informe; CU-07/CU-08: descarga del volcado de memoria.
5. **Anexo IS**, matriz: columna de pruebas con PU-RT (RD-07 → PU-RT-02/03/04; RD-08 → PU-RT-07; RD-09 → PU-RT-06; RD-11 → PU-RT-05); nota "PU definidas en los Cap. 3 y 4".
