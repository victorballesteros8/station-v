# STATION V — USGS

## Estado

🟢 Fuente piloto V1.

## Función

Fuente estructurada de evidencia sísmica para detectar y representar terremotos.

USGS será una de las tres primeras fuentes utilizadas para validar el pipeline OSINT de STATION V.

## Acceso

La integración utilizará los mecanismos públicos de acceso programático proporcionados por USGS, preferentemente GeoJSON/API, evitando scraping.

## Coste

**0 €**.

La gratuidad no sustituye la revisión de las condiciones de uso y límites técnicos aplicables al servicio utilizado.

## Papel dentro de STATION V

USGS proporcionará evidencia estructurada. Un registro recibido de USGS no se considerará automáticamente un EVENT solo por existir.

La arquitectura general será:

`USGS → SOURCE → EVIDENCE → CLAIM → EVENT`

La generación o actualización de EVENT deberá respetar las reglas generales de STATION V y la lógica específica definida para esta fuente.

## Datos de interés

La integración podrá utilizar, cuando estén disponibles:

- identificador externo del terremoto;
- timestamp del evento;
- magnitud;
- latitud;
- longitud;
- profundidad;
- descripción/localización textual (`place`);
- timestamp de actualización;
- nivel de alerta (`alert`);
- significancia (`sig`);
- indicador de tsunami;
- `felt`;
- `mmi`;
- `cdi`;
- URL de la fuente original.

No todos los campos serán obligatorios para considerar válida una evidencia.

## Normalización

Los datos externos se transformarán al modelo interno de STATION V sin aumentar artificialmente la precisión temporal o geográfica disponible.

El identificador externo de USGS deberá conservarse para permitir deduplicación y trazabilidad.

La localización geográfica se conservará mediante las coordenadas proporcionadas por la fuente. La asociación con un país se realizará posteriormente mediante la infraestructura geográfica disponible en STATION V cuando proceda.

## Datos específicos de la fuente

Los datos sísmicos propios de USGS no se añadirán como columnas específicas a la tabla común `EVIDENCE`.

Se conservarán en la estructura flexible de datos estructurados asociada a la evidencia, utilizando el modelo común definido en `docs/osint/SOURCES.md`.

Para USGS, el payload normalizado podrá conservar campos como:

- `external_id`;
- `time`;
- `updated`;
- `magnitude`;
- `place`;
- `latitude`;
- `longitude`;
- `depth`;
- `alert`;
- `significance`;
- `tsunami`;
- `felt`;
- `mmi`;
- `cdi`.

La estructura flexible no sustituirá a los campos comunes de `EVIDENCE` ni a la referencia a la fuente original.

## Clasificación

La magnitud, significancia, alerta y demás campos de USGS son datos de la fuente y no equivalen directamente a `severity`, `Escalation Score` o `Country Risk` de STATION V.

Las reglas de transformación a categorías y severidad deberán definirse antes de activar la generación automática de EVENT para esta fuente.

## Deduplicación

El identificador externo estable proporcionado por USGS será la referencia primaria para evitar la creación de duplicados del mismo registro.

Los cambios posteriores de un mismo registro deberán poder tratarse como actualización de la evidencia en lugar de generar una nueva entidad duplicada.

`external_id` y `content_hash` tendrán funciones diferentes: el primero identifica el registro externo y el segundo permite identificar el contenido de la evidencia.

## Limitaciones

USGS proporciona información sísmica. Un terremoto registrado no implica por sí mismo consecuencias humanas, materiales, políticas o geopolíticas determinadas.

STATION V no inferirá automáticamente impacto humano, daño material o relevancia geopolítica a partir de la magnitud aislada.

La evidencia USGS deberá poder combinarse con otras fuentes cuando sea necesario para aumentar la confianza o determinar el impacto.

## Integridad metodológica

El conector USGS no modificará directamente el motor de Country Risk ni el Global Risk.

La incorporación de evidencia sísmica al scoring deberá producirse únicamente a través de la cadena general de STATION V:

`EVENT → RISK IMPACT → SUBINDICATOR → DIMENSION → COUNTRY RISK`

## Implementación prevista

La primera implementación deberá centrarse en:

1. consultar USGS;
2. normalizar los registros;
3. registrar SOURCE y EVIDENCE;
4. preservar el identificador externo;
5. conservar los datos específicos relevantes mediante la estructura flexible de evidencia;
6. evitar duplicados;
7. mantener la trazabilidad hacia la fuente original;
8. preparar la posterior generación o actualización de CLAIM y EVENT.

No se implementará inicialmente un scheduler automático ni impacto sobre Country Risk.

## Revisión

Documento actualizado para definir el almacenamiento de datos específicos de USGS mediante la estructura flexible común de evidencia.
