# Registro de revisión EGM — Capítulo 6 (Comunicaciones), v0.1 → v0.2

Revisores sin contexto previo: T = técnico de comunicaciones (verificó contra el código de ESP-IDF 5.4 y del
prototipo) · R = trazabilidad · A = evaluador académico (nota tentativa de la v0.1: "muy bueno").

## Aceptados e incorporados

| # | Origen | Hallazgo | Cambio |
|---|---|---|---|
| 1 | T, R | La única tarea de esp_http_server quedaba bloqueada por OTA, CSV e historial (y con ellos la publicación) | Nueva tarea T_XFER (prio 4, 8 kB) con httpd_req_async_handler_begin; una transferencia a la vez (503 si ocupada) |
| 2 | T | httpd_queue_work puede fallar (buzón UDP de 6) y la bandera quedaba trabada | La función de trabajo baja la bandera; ante error, T_APP la baja y reintenta; nunca la variante bloqueante |
| 3 | T | 7 sockets + 3 internos = 10 = LWIP_MAX_SOCKETS; sin lugar para el DNS | CONFIG_LWIP_MAX_SOCKETS = 16 |
| 4 | T | La recuperación de fábrica no volvía a factory | CONFIG_BOOTLOADER_OTA_DATA_ERASE; tiempo total de ≈ 6 s con los dos pulsadores; esquema aditivo de cal para la imagen factory |
| 5 | T | Riesgo del desafío subestimado: token en claro, AP falso con WPA3, degradación en transición, K equivale a contraseña | Riesgo medio con cualquier modo; token asociado a IP; opción "solo WPA3" (transition_disable); bloqueo global y persistente |
| 6 | T, R | Cálculo de cierre ignoraba TCP_SNDQUEUELOWAT y los 2 send() por trama; envío parcial desincroniza | MSG_DONTWAIT por send_override; cierre ante envío parcial o > 2 s sin escribir (≈ 2,9 s midiendo, 6 s en reposo); ping, AP_STADISCONNECTED y close_fn; criterio de PU-COM-03 ajustado |
| 7 | T | lru_purge cerraba paneles que solo reciben | lru_purge_enable = false; respuestas HTTP cierran la conexión |
| 8 | T, A | Origin contradice "cualquier nombre"; revinculación de DNS | 302 a 192.168.4.1; solo Host y Origin 192.168.4.1; ws_pre_handshake_cb; DNS privado e iOS en PU-COM-06 |
| 9 | T | esp_random sin radio no es aleatorio verdadero | Claves de fábrica generadas con la radio encendida y guardadas en cal |
| 10 | T | Escrituras de NVS durante MIDIENDO (contador, bloqueo) | Diferidas a REPOSO (D4.3) |
| 11 | T | Firma: clave tomada de la imagen en ejecución; custodia; plazo de 60 s propio | Factory firmada; custodia sin rotación; temporizador propio |
| 12 | T, A | DTIM no rige el unicast | Intervalo de escucha (supuesto ≤ 3 balizas): peor caso 458 ms; criterio ≤ 300 ms p99 con pantalla encendida |
| 13 | T | Inactividad de 30 s podía expulsar celulares | 60 s y prueba con pantalla apagada |
| 14 | T, R | 2,9 % del binario no venía del script; faltaban DIFS/backoff y ACK TCP | Script corregido: JSON 3,7 %, binario 3,2 % |
| 15 | T | Memoria sin cJSON, ventana OTA, SAE, T_XFER | 144 kB; "memoria dinámica acotada" para cJSON |
| 16 | T | 16 handlers justos; /sesiones/{id} | 24 y httpd_uri_match_wildcard |
| 17 | T | Hora: celular adelantado bloquea correcciones | Ventana de plausibilidad y corrección con token |
| 18 | R | q_net lleno perdía acks hasta reconectar | "hola" inmediato a todos |
| 19 | R | cmd no entra en q_evt de 32 B | q_evt de 64 B (cambio al Cap. 4) |
| 20 | R | Roles de calibrar y piso | Roles por operación en la Tabla 6.7 |
| 21 | R | Sin pruebas para historial, informe, CSV, 5.º cliente, RD-08 | PU-COM-12; quinta pestaña en PU-COM-03; EN-07 con 4 clientes |
| 22 | R | ≈ 7 mA de TX no estaban en los 145 mA del Cap. 5 | Sumados: peor caso ≈ 8,7 h (cambio al Cap. 5) |
| 23 | R | GPIO13 sí figura libre (reservado a táctil SPI); realimentación del RTC; cambio de celda | Texto corregido; RTC con respaldo que deshabilita I2C; hora perdida al cambiar la celda |
| 24 | R | Transiciones de OTA por tiempo y autodiagnóstico fallido | Abandono a los 30 s → REPOSO; reversión, no ERROR (cambio al anexo) |
| 25 | R | Cifras menores (tramas por cliente, suma de memoria, DHCP, > 50 %, tasa de inst, RD-09, D6.3, H6.9, hueco 0x15000) | Corregidas |
| 26 | A, R | Bibliografía casi sin citar; siglas faltantes | Citas en cada uso; siglas ampliadas; [15] ENACOM y [16] Dragonblood |
| 27 | A | Sin normativa de radio | Subsección "Marco regulatorio" (módulo certificado, código de país AR, ENACOM) |
| 28 | A | Sin máquina de estados del protocolo | Tabla 6.9 (estados, plazos y errores) |
| 29 | A | Modelo de capas implícito | Tabla 6.4 (decisiones por capa e integridad) |
| 30 | A | Alternativas solo cualitativas | Tabla 6.3 con consumo, alcance, latencia y dependencias |
| 31 | A | Figura 6.1 mezclaba dos gráficos; letra chica; rótulo de sección | Figuras 6.1 y 6.3 separadas; letras más grandes; rótulo 6.11 |
| 32 | A | H6.6 fuera de alcance; tono "límite honesto" | H6.6 acotado al campo transmitido (Baja); "Limitaciones del esquema" |

## No incorporados o diferidos

| Origen | Hallazgo | Motivo |
|---|---|---|
| A | Mover la configuración de ESP-IDF a un anexo | Es la evidencia verificable de las decisiones; se mantiene en tablas compactas |
| T | PAKE (SRP/SPAKE2) o HTTPS | Documentado como mejora de producción |
| T | Vincular el token al WebSocket | Las operaciones de técnico van por HTTP con token asociado a IP; suficiente para el prototipo |

## Cambios necesarios en OTROS documentos (pendientes de aprobación del autor)

1. **Anteproyecto**
   - Otros requisitos: "WPA2/WPA3 con PMF y contraseña aleatoria por equipo".
   - Interfaz remota: informe HTML imprimible en el equipo (PDF en el servidor).
   - Métodos/firmware: particiones factory + ota_0/ota_1 firmadas, RTC y sincronización de hora.
   - Material y costos: RTC con cristal (≈ USD 2); celulares de prueba (2 Android, 1 iOS); analizador de Wi-Fi.
   - EN-06: latencia ≤ 300 ms en el 99 %. EN-07 y EN-09: con 4 clientes recibiendo. EN-10: calibración conservada.
   - Tareas 3.6 (24 h) y 3.7 (8 h): revisar por el alcance nuevo (seguridad, protocolo, OTA firmada).
2. **Anexo IS**
   - Actor "Servidor de gestión": consulta incremental; CU-02 pasos 7/7a sin "envío".
   - CU-04 2b: 4 asociaciones y cierre 1013 a la quinta conexión.
   - CU-07: PIN de 6 dígitos, contraseña, canal y potencia.
   - FSM: ACTUALIZANDO con tiempo de espera → REPOSO; arranque con verificación pendiente → reversión.
   - Trazabilidad: PU-COM en RD-06, 07, 09, 10, 11, Interfaz; fila Seguridad (PU-COM-07).
3. **Cap. 4**
   - Tabla 4.5: T_NET = tarea de esp_http_server activada por httpd_queue_work; nueva T_XFER (núcleo 0, prio 4, 8 kB); T_STOR atiende q_lect; T_MON dueña del I2C/RTC.
   - Tabla 4.6: q_net (8 × 64 B), q_lect, StreamBuffer de 4 kB; aviso de mbx a T_NET con bandera; q_evt de 64 B.
   - Tabla 4.9: T_XFER en el RTA (prio 4, fondo).
   - Tabla 4.14: HTTPD_WS_SUPPORT, WS_PRE_HANDSHAKE_CB, LWIP_MAX_SOCKETS = 16, APP_ROLLBACK, SECURE_SIGNED_APPS, FACTORY_RESET, tabla de particiones propia.
4. **Cap. 5**
   - Tabla 5.7: GPIO13 SDA, GPIO21 SCL; reinicio de la pantalla por comando; táctil futuro I2C; MENÚ como pin de recuperación de fábrica.
   - Figura 5.1, Tabla 5.3, BOM y costo: RTC con respaldo desde la celda.
   - Consumo apagado: 12,6 → ≈ 12,65 µA.
   - Tabla 5.4: + ≈ 7 mA de transmisión con 4 clientes; peor caso ≈ 8,7 h.

## Estado

Aprobado por el autor (incluida la incorporación del RTC). Cambios aplicados: anteproyecto (546 h), anexo IS v0.5,
Cap. 4 v0.2.2 (T_XFER en la RTA: R = 133,8 ms; U₀ = 52 %), Cap. 5 v0.2.1 (peor caso 8,7 h; apagado 12,65 µA; BOM ≈ USD 86)
y Cap. 6 v0.2.1.
