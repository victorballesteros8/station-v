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

Endpoint de detalle de evento:

```text
https://www.gdacs.org/gdacsapi/api/events/geteventdata
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

## 5. Discovery y Refresh V1

La ingesta GDACS separará dos operaciones independientes: **Discovery** y **Refresh**.

La frecuencia de consulta de GDACS es independiente de la frecuencia de cálculo de Country Risk.

### 5.1 Discovery

`geteventlist/SEARCH` se utilizará para descubrir eventos recientes y detectar nuevos `eventid`.

Las consultas de Discovery utilizarán ventanas temporales operativas acotadas. No se dependerá de consultas históricas de gran amplitud como mecanismo ordinario de actualización.

Cuando se detecte un `eventid` nuevo, el sistema podrá obtener sus datos completos mediante `geteventdata` antes de persistir la evidencia normalizada.

### 5.2 Refresh

`geteventdata` se utilizará para refrescar EVENTs GDACS ya conocidos y detectar modificaciones o nuevos episodios.

El refresco no dependerá de `iscurrent`, porque este campo no es suficiente para determinar si un EVENT puede seguir recibiendo modificaciones. Tampoco se utilizará `istemporary` como criterio único de finalización del seguimiento.

La política concreta de frecuencia y selección de EVENTs a refrescar deberá limitar consultas innecesarias y evitar ventanas históricas de gran tamaño.

Un EVENT conocido podrá seguir recibiendo modificaciones aunque su `fromdate` sea anterior a la ventana utilizada para Discovery. Por tanto, la ventana de Discovery no constituye por sí misma una política de actualización de EVENTs conocidos.

La frecuencia de Refresh y la ventana metodológica de Country Risk son conceptos independientes y no deberán mezclarse.

### 5.3 Comportamiento ante limitaciones de la API

Las consultas de Discovery deberán mantenerse acotadas y la implementación deberá tolerar latencias elevadas, respuestas vacías, errores HTTP, timeouts y respuestas malformadas sin generar duplicados ni dejar datos parcialmente inconsistentes.

La estrategia de Refresh deberá ser selectiva y no depender de una única consulta histórica de gran amplitud.

### 5.4 Fallo durante Refresh

Si un `geteventdata` utilizado para refrescar un EVENT conocido falla:

- se conservará la EVIDENCE existente;
- no se sobrescribirán datos válidos con valores incompletos;
- no se creará una nueva EVIDENCE únicamente por el fallo de consulta;
- el EVENT seguirá disponible para futuros intentos de Refresh;
- el fallo de un EVENT no deberá impedir continuar con el procesamiento de los demás EVENTs seleccionados.

La actualización deberá ser idempotente y cada operación completada correctamente deberá dejar el estado persistido de forma consistente.

Un fallo temporal de la API no se interpretará como desaparición, finalización o invalidación del EVENT.

## 6. Consulta inicial

La integración utilizará consultas de búsqueda sobre un intervalo temporal acotado.

La API de GDACS permite filtrar, entre otros parámetros, por tipo de evento, fecha inicial, fecha final y nivel de alerta.

El sistema deberá evitar consultas excesivamente amplias.

La respuesta deberá tratarse como una colección de eventos externos que debe ser normalizada antes de persistirse.

## 7. Identificación externa

Los eventos GDACS disponen de identificadores propios y deben distinguirse tres conceptos:

```text
eventid
episodeid
sourceid
```

`eventid` identifica el acontecimiento GDACS y se utilizará como identificador externo del EVENT.

`episodeid` identifica una evaluación o episodio concreto de GDACS y se conservará como identificador externo de la EVIDENCE.

`sourceid` identifica la fuente sísmica original declarada por GDACS, por ejemplo un identificador NEIC/USGS, y se conservará como dato estructurado.

La regla de identidad V1 es:

```text
mismo eventid + mismo episodeid
→ misma EVIDENCE, actualizable
```

```text
mismo eventid + nuevo episodeid
→ nueva EVIDENCE, mismo EVENT
```

Nunca se creará un EVENT nuevo únicamente porque GDACS genere un nuevo episodio.

No se utilizarán identificadores generados localmente como sustituto de los identificadores oficiales de GDACS.

V1 no realizará asociación heurística entre GDACS y otras fuentes mediante coordenadas, magnitud, hora, título u otros atributos aproximados.

`sourceid` podrá utilizarse para una relación determinista con otra fuente únicamente cuando exista una coincidencia exacta y la evidencia correspondiente esté disponible.

## 8. Episodios y trazabilidad histórica

Un EVENT GDACS puede contener uno o varios episodios.

Cada episodio representa una evaluación concreta y deberá conservarse independientemente para mantener la trazabilidad histórica.

Por ejemplo, un mismo `eventid` puede disponer de:

```text
EVENT 1557236
│
├── episode 1724205 → Orange
│
└── episode 1724218 → Red
```

En este caso siguen existiendo un único EVENT y dos unidades de EVIDENCE asociadas a episodios distintos.

`datemodified` representa la fecha de modificación declarada por GDACS para el registro consultado. No se utilizará `datemodified` por sí solo para inferir el orden relativo entre episodios, ya que distintos episodios pueden compartir el mismo valor.

`fromdate` y `todate` representan el intervalo temporal del fenómeno y no deben confundirse con `datemodified`.

## 9. Datos conservados

La integración conservará en `evidence.structured_data` los datos relevantes proporcionados por GDACS.

### 9.1 Datos principales

Como mínimo, cuando estén disponibles:

```text
eventid
episodeid
eventtype
alertlevel
alertscore
episodealertlevel
episodealertscore
name
description
country
iso3
latitude
longitude
magnitude
depth
fromdate
todate
datemodified
source
sourceid
affectedcountries
```

Los nombres y descripciones de GDACS se conservarán como información de la fuente. La presentación visible en español de STATION V se resolverá en la capa de presentación y no modificará innecesariamente el contenido original de la EVIDENCE.

### 9.2 Datos estructurados de contexto

Podrán conservarse en `structured_data`, sin incorporarse automáticamente al modelo matemático de Country Risk:

- información adicional de `severitydata`;
- `earthquakedetails`;
- `rapidpop`;
- `shakepop`;
- `additionalinfos`;
- otros atributos de contexto relevantes proporcionados directamente por GDACS.

La conservación de estos datos no implica que formen parte de la fórmula de Risk V1.

### 9.3 Recursos secundarios

`images`, `documents`, `shakemap`, `impacts` y URLs de recursos asociados no se convertirán en columnas específicas del modelo común de EVIDENCE.

Cuando sea necesario conservar su referencia, se hará mediante datos estructurados sin convertirlos automáticamente en variables analíticas de V1.

La información `episodes` se utilizará para descubrir referencias a episodios cuando resulte necesario, pero no se tratará como una nueva entidad del modelo común distinta de EVIDENCE.

## 10. Geometría

GDACS proporciona información geoespacial adicional mediante GeoJSON.

La geometría se considerará información contextual de la evidencia.

No se interpretará automáticamente una geometría de impacto como prueba de que toda el área representada haya sufrido daños.

La geometría deberá conservar su procedencia y significado original.

## 11. Países afectados

Cuando esté disponible, `affectedcountries` será la referencia principal de GDACS para construir las relaciones geográficas del EVENT.

El campo `country` se conservará como contexto original proporcionado por GDACS, pero no sustituirá a la lista de países afectados.

La presencia de un país en `affectedcountries` no implica por sí sola una categoría de impacto analítico distinta de la definida por STATION V.

La clasificación de la relación geográfica y la asignación posterior de Risk Impact deberán seguir el modelo de relaciones de EVENT de STATION V.

## 12. Severidad y datos sísmicos

La magnitud y profundidad describen el fenómeno físico y se conservarán separadas de la evaluación de alerta de GDACS.

`alertlevel` y `alertscore` representan la evaluación de GDACS del EVENT, mientras que `episodealertlevel` y `episodealertscore` representan la evaluación del episodio concreto.

GDACS puede proporcionar la magnitud mediante `severitydata.severity` y también mediante `earthquakedetails.magnitude`. Cuando ambos estén disponibles, se conservarán sus valores de fuente y se utilizará la normalización definida por STATION V sin tratar ambos campos como dos señales independientes del mismo fenómeno.

Los datos de GDACS no se convertirán automáticamente en nuevas variables matemáticas de Country Risk fuera de las reglas de severidad y Risk Impact ya definidas por STATION V.

## 13. Nivel de alerta y resolución de severidad V1.2

GDACS utiliza niveles de alerta, incluyendo:

```text
green
orange
red
```

STATION V conservará el nivel original de GDACS.

Para terremotos, el nivel de alerta se utilizará junto con la magnitud para resolver la `severity` del EVENT.

La referencia mínima por nivel de alerta será:

| Nivel GDACS | Severidad mínima |
|---|---|
| `green` | `info` |
| `orange` | `medium` |
| `red` | `high` |

También se aplican las referencias de magnitud:

| Magnitud | Severidad mínima |
|---|---|
| M < 5,0 | `info` |
| M 5,0–5,9 | `low` |
| M 6,0–6,9 | `medium` |
| M 7,0–7,9 | `high` |
| M ≥ 8,0 | `critical` |

La severidad resultante será la mayor respaldada por las señales objetivas disponibles. No se sumarán puntos entre señales ni se utilizará una media entre criterios.

En V1.2, las señales específicas adicionales de impacto se interpretarán de la siguiente manera cuando estén disponibles y tengan significado aplicable al registro:

- `MMI < VII`: no eleva;
- `MMI VII`: eleva un nivel;
- `MMI VIII`: eleva dos niveles;
- `MMI IX o superior`: eleva dos niveles;
- indicador explícito de tsunami: eleva un nivel;
- otros campos objetivos solo podrán elevar si se define expresamente una regla antes de su implementación.

Las elevaciones nunca podrán reducir la referencia mínima ya establecida por magnitud o por alerta GDACS.

Las severidades USGS y GDACS no se promediarán. Cada fuente evalúa su propia evidencia. Una fuente independiente puede aportar evidencia para actualizar la severidad del mismo EVENT mediante una nueva versión, conservando la trazabilidad de la evaluación anterior.

Esta regla es específica de la ingestión sísmica GDACS y no constituye una regla genérica para todas las categorías de desastre.

## 14. EVIDENCE

Cada registro GDACS aceptado por el ingestor constituirá una unidad de:

```text
EVIDENCE
```

La evidencia representará que GDACS ha registrado o proporcionado información sobre este evento.

El `source_id` deberá apuntar al registro `GDACS` de la tabla `sources`.

La persistencia deberá ser idempotente respecto de `source_id + external_id + external_episode_id`.

## 15. CLAIM

La primera implementación generará un CLAIM asociado a cada EVIDENCE GDACS.

El CLAIM describirá de forma controlada el hecho que la fuente permite afirmar.

El nivel de confianza y el `assertion_status` deberán reflejar la naturaleza de la fuente.

No se utilizará el CLAIM para convertir automáticamente una alerta GDACS en un acontecimiento STATION V confirmado.

## 16. EVENT

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

Cuando un EVENT ya existente reciba nueva evidencia independiente de GDACS que sustente una severidad superior, la actualización deberá realizarse mediante el mecanismo de versionado del EVENT y no creando un segundo EVENT para el mismo acontecimiento.

## 17. Relación con USGS

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

La coincidencia entre un registro USGS y uno GDACS no se establecerá únicamente por el título del evento ni mediante matching aproximado.

En V1 no se establecerá una relación GDACS ↔ USGS cuando no exista una coincidencia determinista disponible.

## 18. Deduplicación y actualización

La deduplicación se realizará mediante los identificadores externos de GDACS.

El sistema deberá ser idempotente:

```text
misma EVIDENCE GDACS
+
mismo eventid
+
mismo episodeid
        ↓
no crear una segunda EVIDENCE
```

Cuando GDACS proporcione un nuevo episodio:

```text
mismo eventid
+
nuevo episodeid
        ↓
nueva EVIDENCE
+
same EVENT
```

La actualización de información de un episodio ya conocido deberá actualizar la evidencia correspondiente en lugar de generar duplicados.

Los episodios anteriores no deberán eliminarse por el hecho de que GDACS proporcione otro episodio para el mismo EVENT.

## 19. Trazabilidad

Cada EVIDENCE GDACS deberá conservar, cuando esté disponible:

- URL original;
- identificador externo;
- `episodeid`;
- `sourceid`;
- tipo de evento;
- timestamp del fenómeno;
- timestamp de recuperación;
- `datemodified`;
- datos estructurados relevantes;
- fuente original.

La trazabilidad deberá permitir reconstruir de qué registro GDACS procede cada EVIDENCE y qué evaluación concreta representa.

## 20. Límites y comportamiento

La API de búsqueda de GDACS permite consultas personalizadas y devuelve datos geoespaciales.

Las consultas deberán realizarse con intervalos temporales controlados y respetando los límites técnicos de la API.

La implementación deberá tolerar:

- respuesta vacía;
- campos opcionales ausentes;
- cambios de estado de alerta;
- nuevos episodios;
- actualización de registros existentes;
- errores HTTP;
- respuestas malformadas;
- timeouts;
- interrupciones temporales del servicio.

Los errores de la fuente no deberán provocar corrupción parcial de la base de datos.

## 21. Política de interpretación

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

## 22. Alcance inicial

La primera implementación deberá demostrar:

1. conexión con la API;
2. Discovery mediante `geteventlist/SEARCH`;
3. Refresh mediante `geteventdata`;
4. normalización;
5. identificación externa;
6. persistencia de SOURCE;
7. persistencia de EVIDENCE;
8. persistencia de CLAIM;
9. deduplicación;
10. actualización de registros existentes;
11. creación de nueva EVIDENCE para nuevos episodios;
12. resolución de nuevos episodios sobre el mismo EVENT;
13. persistencia de países afectados;
14. asignación correcta de Risk Impacts;
15. trazabilidad;
16. comportamiento correcto ante respuestas vacías, errores y timeouts.

No se implementará todavía:

- correlación automática USGS ↔ GDACS mediante matching heurístico;
- incorporación de ciclones;
- incorporación de inundaciones;
- scoring de riesgo basado directamente en GDACS fuera de las reglas ya definidas;
- interpretación automática de zonas afectadas más allá de las relaciones definidas por STATION V.

## 23. Fuentes oficiales

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
