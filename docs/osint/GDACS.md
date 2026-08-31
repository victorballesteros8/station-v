# GDACS — Fuente OSINT

## 1. Función en STATION V

GDACS (Global Disaster Alert and Coordination System) se utilizará como fuente institucional estructurada de detección y contexto sobre desastres de aparición súbita.

En STATION V tendrá inicialmente una función de:

- detección;
- alerta;
- contextualización;
- corroboración secundaria.

GDACS no se considerará automáticamente evidencia primaria del fenómeno físico observado.

## 2. Coste

La utilización de los datos y APIs de GDACS es gratuita.

La integración V1 no dependerá de suscripciones de pago, licencias de datos de pago, acceso empresarial ni infraestructura externa de pago.

El coste previsto para la integración es:

```text
0 €
```

La gratuidad no elimina la obligación de respetar las condiciones de uso y atribución de GDACS.

La atribución requerida por GDACS es:

```text
Global Disaster Alert and Coordination System, GDACS
```

## 3. Método de acceso

La fuente principal será la Web API de GDACS.

Endpoint de búsqueda:

```text
https://www.gdacs.org/gdacsapi/api/events/geteventlist/SEARCH
```

La API permite obtener información de eventos en formato GeoJSON.

La integración no utilizará scraping de páginas HTML.

Los feeds XML/RSS de GDACS podrán utilizarse posteriormente como mecanismo alternativo o complementario, pero no serán la interfaz principal de V1.

## 4. Primera implementación V1

La primera integración de GDACS se limitará inicialmente a:

```text
eventtype = EQ
```

Es decir, terremotos.

No se implementarán simultáneamente ciclones, inundaciones, incendios u otros tipos de desastre.

Una vez validado el pipeline de terremotos, se podrán incorporar nuevos tipos de evento sin modificar el núcleo conceptual:

```text
SOURCE
EVIDENCE
CLAIM
EVENT
```

## 5. Consulta inicial

La integración utilizará consultas de búsqueda sobre un intervalo temporal acotado.

La API de GDACS permite filtrar, entre otros parámetros, por tipo de evento, fecha inicial, fecha final y nivel de alerta.

El sistema deberá evitar consultas excesivamente amplias.

La respuesta deberá tratarse como una colección de eventos externos que debe ser normalizada antes de persistirse.

## 6. Identificación externa

Los eventos GDACS disponen de identificadores propios.

Para la integración inicial se conservarán:

```text
eventid
episodeid
eventtype
```

El identificador externo utilizado para la deduplicación de EVIDENCE será estable y deberá permitir distinguir correctamente un evento GDACS de otro.

La identificación deberá conservar también `episodeid` cuando sea necesario para mantener la trazabilidad de una determinada alerta o episodio.

No se utilizarán identificadores generados localmente como sustituto de los identificadores oficiales de GDACS.

## 7. Datos conservados

La integración conservará en `evidence.structured_data` los datos relevantes proporcionados por GDACS.

Como mínimo, cuando estén disponibles:

```text
eventid
episodeid
eventtype
alertlevel
eventname
country
latitude
longitude
magnitude
depth
event_time
update_time
```

También podrán conservarse otros campos cuantitativos o descriptivos relevantes proporcionados directamente por GDACS.

No se copiará innecesariamente contenido textual completo de las páginas HTML de GDACS.

## 8. Geometría

GDACS proporciona información geoespacial adicional mediante GeoJSON.

La geometría se considerará información contextual de la evidencia.

No se interpretará automáticamente una geometría de impacto como prueba de que toda el área representada haya sufrido daños.

La geometría deberá conservar su procedencia y significado original.

## 9. Nivel de alerta

GDACS utiliza niveles de alerta, incluyendo:

```text
green
orange
red
```

STATION V conservará el nivel original de GDACS.

No se realizará una conversión automática de:

```text
green → riesgo bajo
orange → riesgo alto
red → riesgo crítico
```

porque el nivel GDACS representa una evaluación específica de la alerta de desastre y no es equivalente al `Country Risk` ni al `Global Risk` de STATION V.

## 10. EVIDENCE

Cada registro GDACS aceptado por el ingestor constituirá una unidad de:

```text
EVIDENCE
```

La evidencia representará que GDACS ha registrado o proporcionado información sobre este evento.

El `source_id` deberá apuntar al registro `GDACS` de la tabla `sources`.

## 11. CLAIM

La primera implementación generará un CLAIM asociado a cada EVIDENCE GDACS.

El CLAIM describirá de forma controlada el hecho que la fuente permite afirmar.

El nivel de confianza y el `assertion_status` deberán reflejar la naturaleza de la fuente.

No se utilizará el CLAIM para convertir automáticamente una alerta GDACS en un acontecimiento STATION V confirmado.

## 12. EVENT

La existencia de EVIDENCE + CLAIM de GDACS no implica automáticamente un EVENT.

La creación o actualización de un EVENT requerirá posteriormente reglas específicas de clasificación, corroboración y evaluación.

En particular:

```text
SOURCE
  ↓
EVIDENCE
  ↓
CLAIM
```

es un proceso distinto de:

```text
CLAIM
  ↓
EVENT
```

## 13. Relación con USGS

USGS y GDACS pueden describir un mismo terremoto desde perspectivas diferentes.

```text
USGS
→ observación sísmica
→ magnitud
→ profundidad
→ coordenadas

GDACS
→ alerta de desastre
→ evaluación de impacto potencial
→ nivel de alerta
→ contexto geoespacial
```

Cuando exista correspondencia entre ambos registros, la arquitectura deberá permitir posteriormente relacionar las evidencias sin fusionarlas incorrectamente.

La coincidencia entre un registro USGS y uno GDACS no se establecerá únicamente por el título del evento.

## 14. Deduplicación

La deduplicación se realizará mediante los identificadores externos de GDACS.

El sistema deberá ser idempotente:

```text
misma EVIDENCE GDACS
        ↓
no crear una segunda EVIDENCE
```

y:

```text
misma EVIDENCE
+
mismo claim_type
        ↓
no crear un segundo CLAIM
```

La actualización de información de un evento GDACS existente deberá actualizar la evidencia correspondiente en lugar de generar duplicados.

## 15. Trazabilidad

Cada EVIDENCE GDACS deberá conservar, cuando esté disponible:

- URL original;
- identificador externo;
- tipo de evento;
- timestamp de publicación o evento;
- timestamp de recuperación;
- datos estructurados relevantes;
- fuente original.

La trazabilidad deberá permitir reconstruir de qué registro GDACS procede cada EVIDENCE.

## 16. Actualizaciones

GDACS mantiene feeds que se actualizan periódicamente.

La integración deberá asumir que los registros existentes pueden cambiar.

Por ello:

```text
external_id
```

identifica el registro lógico de la fuente, mientras que los campos estructurados pueden actualizarse con nueva información.

La ingestión repetida no deberá generar duplicados.

## 17. Límites y comportamiento

La API de búsqueda de GDACS permite consultas personalizadas y devuelve datos geoespaciales.

Las consultas deberán realizarse con intervalos temporales controlados y respetando los límites técnicos de la API.

La implementación deberá tolerar:

- respuesta vacía;
- campos opcionales ausentes;
- cambios de estado de alerta;
- actualización de registros;
- errores HTTP;
- respuestas malformadas;
- interrupciones temporales del servicio.

Los errores de la fuente no deberán provocar corrupción parcial de la base de datos.

## 18. Política de interpretación

GDACS es una fuente institucional de alerta y coordinación.

Por tanto:

```text
GDACS alerta
≠
evento confirmado por STATION V
```

y:

```text
GDACS orange/red
≠
Country Risk orange/red
```

Los niveles propios de GDACS se conservarán como atributos de la fuente.

La transformación posterior a indicadores internos de STATION V será una capa separada.

## 19. Alcance inicial

La primera implementación deberá demostrar:

1. conexión con la API;
2. descarga de eventos EQ;
3. normalización;
4. identificación externa;
5. persistencia de SOURCE;
6. persistencia de EVIDENCE;
7. persistencia de CLAIM;
8. deduplicación;
9. actualización de registros existentes;
10. trazabilidad;
11. comportamiento correcto ante respuestas vacías o errores.

No se implementará todavía:

- correlación automática USGS ↔ GDACS;
- creación automática de EVENT;
- incorporación de ciclones;
- incorporación de inundaciones;
- scoring de riesgo basado directamente en GDACS;
- interpretación automática de zonas afectadas.

## 20. Fuentes oficiales

Documentación API:

https://www.gdacs.org/Documents/2025/GDACS_API_quickstart_v1.pdf

Referencia de feeds:

https://data.gdacs.org/feed_reference.aspx

Swagger/API:

https://www.gdacs.org/gdacsapi/swagger/index.html

Recursos de eventos:

https://www.gdacs.org/resources.aspx

Condiciones de uso:

https://www.gdacs.org/documents/2025/GDACS_Terms_of_use_Mar_25.pdf
