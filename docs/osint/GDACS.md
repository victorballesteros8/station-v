# GDACS â€” Fuente OSINT

## 1. FunciÃ³n en STATION V

GDACS (Global Disaster Alert and Coordination System) se utilizarÃ¡ como fuente institucional estructurada de detecciÃ³n y contexto sobre desastres de apariciÃ³n sÃºbita.

En STATION V tendrÃ¡ inicialmente una funciÃ³n de:

- detecciÃ³n;
- alerta;
- contextualizaciÃ³n;
- corroboraciÃ³n secundaria.

GDACS no se considerarÃ¡ automÃ¡ticamente evidencia primaria del fenÃ³meno fÃ­sico observado.

## 2. Coste

La utilizaciÃ³n de los datos y APIs de GDACS es gratuita.

La integraciÃ³n V1 no dependerÃ¡ de suscripciones de pago, licencias de datos de pago, acceso empresarial ni infraestructura externa de pago.

El coste previsto para la integraciÃ³n es:

```text
0 â‚¬
```

La gratuidad no elimina la obligaciÃ³n de respetar las condiciones de uso y atribuciÃ³n de GDACS.

La atribuciÃ³n requerida por GDACS es:

```text
Global Disaster Alert and Coordination System, GDACS
```

## 3. MÃ©todo de acceso

La fuente principal serÃ¡ la Web API de GDACS.

Endpoint de bÃºsqueda:

```text
https://www.gdacs.org/gdacsapi/api/events/geteventlist/SEARCH
```

Endpoint de detalle de evento:

```text
https://www.gdacs.org/gdacsapi/api/events/geteventdata
```

La API permite obtener informaciÃ³n de eventos en formato GeoJSON.

La integraciÃ³n no utilizarÃ¡ scraping de pÃ¡ginas HTML.

Los feeds XML/RSS de GDACS podrÃ¡n utilizarse posteriormente como mecanismo alternativo o complementario, pero no serÃ¡n la interfaz principal de V1.

## 4. Alcance multi-hazard V1

La integraciÃ³n de GDACS en STATION V serÃ¡ multi-hazard.

Los tipos de evento contemplados son:

```text
EQ  â†’ Earthquake
TC  â†’ Tropical Cyclone
FL  â†’ Flood
VO  â†’ Volcano
DR  â†’ Drought
WF  â†’ Wildfire
```
La ingestiÃ³n V1 se centrarÃ¡ en eventos que GDACS clasifique con nivel de alerta:
```
orange
red
```
Los eventos green no se incorporarÃ¡n al flujo ordinario de eventos GDACS de STATION V.

La selecciÃ³n del nivel GDACS no determina directamente la severidad de STATION V. Cada tipo de desastre deberÃ¡ disponer de reglas de severidad especÃ­ficas que traduzcan las seÃ±ales relevantes de GDACS a la escala comÃºn de severidad de STATION V.

El nÃºcleo conceptual de la integraciÃ³n serÃ¡ comÃºn a todos los hazards:
```
SOURCE
EVIDENCE
CLAIM
EVENT
RISK IMPACT
```


La incorporaciÃ³n de nuevos hazards no deberÃ¡ requerir modificar el modelo conceptual comÃºn de STATION V.

La primera implementaciÃ³n validada se ha realizado sobre EQ. Los demÃ¡s hazards se incorporarÃ¡n utilizando el mismo pipeline de integraciÃ³n, pero con normalizaciÃ³n y resoluciÃ³n de severidad especÃ­ficas para cada categorÃ­a.

No se utilizarÃ¡ una Ãºnica fÃ³rmula de severidad para todos los hazards.

La severidad de STATION V serÃ¡ independiente del nivel de alerta original de GDACS, aunque este podrÃ¡ constituir una de las seÃ±ales utilizadas por las reglas especÃ­ficas de cada hazard.


## 5. Discovery y Refresh V1

La ingesta GDACS separarÃ¡ dos operaciones independientes: **Discovery** y **Refresh**.

La frecuencia de consulta de GDACS es independiente de la frecuencia de cÃ¡lculo de Country Risk.

### 5.1 Discovery

`geteventlist/SEARCH` se utilizarÃ¡ para descubrir eventos recientes y detectar nuevos `eventid`.

Las consultas de Discovery utilizarÃ¡n ventanas temporales operativas acotadas. No se dependerÃ¡ de consultas histÃ³ricas de gran amplitud como mecanismo ordinario de actualizaciÃ³n.

Cuando se detecte un `eventid` nuevo, el sistema podrÃ¡ obtener sus datos completos mediante `geteventdata` antes de persistir la evidencia normalizada.

### 5.2 Refresh

`geteventdata` se utilizarÃ¡ para refrescar EVENTs GDACS ya conocidos y detectar modificaciones o nuevos episodios.

El refresco no dependerÃ¡ de `iscurrent`, porque este campo no es suficiente para determinar si un EVENT puede seguir recibiendo modificaciones. Tampoco se utilizarÃ¡ `istemporary` como criterio Ãºnico de finalizaciÃ³n del seguimiento.

La polÃ­tica concreta de frecuencia y selecciÃ³n de EVENTs a refrescar deberÃ¡ limitar consultas innecesarias y evitar ventanas histÃ³ricas de gran tamaÃ±o.

Un EVENT conocido podrÃ¡ seguir recibiendo modificaciones aunque su `fromdate` sea anterior a la ventana utilizada para Discovery. Por tanto, la ventana de Discovery no constituye por sÃ­ misma una polÃ­tica de actualizaciÃ³n de EVENTs conocidos.

La frecuencia de Refresh y la ventana metodolÃ³gica de Country Risk son conceptos independientes y no deberÃ¡n mezclarse.

### 5.3 Comportamiento ante limitaciones de la API

Las consultas de Discovery deberÃ¡n mantenerse acotadas y la implementaciÃ³n deberÃ¡ tolerar latencias elevadas, respuestas vacÃ­as, errores HTTP, timeouts y respuestas malformadas sin generar duplicados ni dejar datos parcialmente inconsistentes.

La estrategia de Refresh deberÃ¡ ser selectiva y no depender de una Ãºnica consulta histÃ³rica de gran amplitud.

### 5.4 Respuesta vacÃ­a de Discovery

Si `geteventlist/SEARCH` devuelve una respuesta JSON vacÃ­a (`{}`) tras una peticiÃ³n HTTP satisfactoria, se tratarÃ¡ como una respuesta sin eventos descubribles para esa consulta.

No se considerarÃ¡ por sÃ­ misma un error de transporte ni provocarÃ¡ la creaciÃ³n, modificaciÃ³n o eliminaciÃ³n de EVIDENCE.

Una respuesta vacÃ­a no implicarÃ¡ que GDACS no disponga de eventos ni que los EVENTs conocidos hayan dejado de actualizarse.

### 5.5 Fallo durante Refresh

Si un `geteventdata` utilizado para refrescar un EVENT conocido falla:

- se conservarÃ¡ la EVIDENCE existente;
- no se sobrescribirÃ¡n datos vÃ¡lidos con valores incompletos;
- no se crearÃ¡ una nueva EVIDENCE Ãºnicamente por el fallo de consulta;
- el EVENT seguirÃ¡ disponible para futuros intentos de Refresh;
- el fallo de un EVENT no deberÃ¡ impedir continuar con el procesamiento de los demÃ¡s EVENTs seleccionados.

La actualizaciÃ³n deberÃ¡ ser idempotente y cada operaciÃ³n completada correctamente deberÃ¡ dejar el estado persistido de forma consistente.

Un fallo temporal de la API no se interpretarÃ¡ como desapariciÃ³n, finalizaciÃ³n o invalidaciÃ³n del EVENT.

### 5.6 Limitaciones de Discovery y separaciÃ³n de Refresh

`geteventlist/SEARCH` se utilizarÃ¡ como mecanismo de Discovery, pero no se considerarÃ¡ una fuente exhaustiva para detectar todas las modificaciones posteriores de EVENTs ya conocidos.

Un EVENT conocido podrÃ¡ recibir modificaciones que no aparezcan en una consulta concreta de Discovery.

Por este motivo:

```text
Discovery
â†’ detectar EVENTs que deben incorporarse o revisarse

Refresh
â†’ consultar directamente geteventdata(eventid)
â†’ obtener el estado completo del EVENT conocido
```
La ausencia de un EVENT en una respuesta de Discovery no deberÃ¡ interpretarse como desapariciÃ³n, finalizaciÃ³n o invalidaciÃ³n del EVENT.

La implementaciÃ³n no deberÃ¡ ampliar indefinidamente las ventanas de Discovery con el Ãºnico objetivo de detectar modificaciones de EVENTs antiguos. El seguimiento de EVENTs conocidos deberÃ¡ resolverse mediante la polÃ­tica de Refresh.

## 6. Consulta inicial

La integraciÃ³n utilizarÃ¡ consultas de bÃºsqueda sobre un intervalo temporal acotado.

La API de GDACS permite filtrar, entre otros parÃ¡metros, por tipo de evento, fecha inicial, fecha final y nivel de alerta.

El sistema deberÃ¡ evitar consultas excesivamente amplias.

La respuesta deberÃ¡ tratarse como una colecciÃ³n de eventos externos que debe ser normalizada antes de persistirse.

## 7. IdentificaciÃ³n externa

Los eventos GDACS disponen de identificadores propios y deben distinguirse tres conceptos:

```text
eventid
episodeid
sourceid
```

`eventid` identifica el acontecimiento GDACS y se utilizarÃ¡ como identificador externo del EVENT.

`episodeid` identifica una evaluaciÃ³n o episodio concreto de GDACS y se conservarÃ¡ como identificador externo de la EVIDENCE.

`sourceid` identifica la fuente sÃ­smica original declarada por GDACS, por ejemplo un identificador NEIC/USGS, y se conservarÃ¡ como dato estructurado.

La regla de identidad V1 es:

```text
mismo eventid + mismo episodeid
â†’ misma EVIDENCE, actualizable
```

```text
mismo eventid + nuevo episodeid
â†’ nueva EVIDENCE, mismo EVENT
```

Nunca se crearÃ¡ un EVENT nuevo Ãºnicamente porque GDACS genere un nuevo episodio.

No se utilizarÃ¡n identificadores generados localmente como sustituto de los identificadores oficiales de GDACS.

V1 no realizarÃ¡ asociaciÃ³n heurÃ­stica entre GDACS y otras fuentes mediante coordenadas, magnitud, hora, tÃ­tulo u otros atributos aproximados.

`sourceid` podrÃ¡ utilizarse para una relaciÃ³n determinista con otra fuente Ãºnicamente cuando exista una coincidencia exacta y la evidencia correspondiente estÃ© disponible.

## 8. Episodios y trazabilidad histÃ³rica

Un EVENT GDACS puede contener uno o varios episodios.

Cada episodio representa una evaluaciÃ³n concreta y deberÃ¡ conservarse independientemente para mantener la trazabilidad histÃ³rica.

Por ejemplo, un mismo `eventid` puede disponer de:

```text
EVENT 1557236
â”‚
â”œâ”€â”€ episode 1724205 â†’ Orange
â”‚
â””â”€â”€ episode 1724218 â†’ Red
```

En este caso siguen existiendo un Ãºnico EVENT y dos unidades de EVIDENCE asociadas a episodios distintos.

`datemodified` representa la fecha de modificaciÃ³n declarada por GDACS para el registro consultado. No se utilizarÃ¡ `datemodified` por sÃ­ solo para inferir el orden relativo entre episodios, ya que distintos episodios pueden compartir el mismo valor.

`fromdate` y `todate` representan el intervalo temporal del fenÃ³meno y no deben confundirse con `datemodified`.

## 9. Datos conservados

La integraciÃ³n conservarÃ¡ en `evidence.structured_data` los datos relevantes proporcionados por GDACS.

### 9.1 Datos principales

Como mÃ­nimo, cuando estÃ©n disponibles:

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

Los nombres y descripciones de GDACS se conservarÃ¡n como informaciÃ³n de la fuente. La presentaciÃ³n visible en espaÃ±ol de STATION V se resolverÃ¡ en la capa de presentaciÃ³n y no modificarÃ¡ innecesariamente el contenido original de la EVIDENCE.

### 9.2 Datos estructurados de contexto

PodrÃ¡n conservarse en `structured_data`, sin incorporarse automÃ¡ticamente al modelo matemÃ¡tico de Country Risk:

- informaciÃ³n adicional de `severitydata`;
- `earthquakedetails`;
- `rapidpop`;
- `shakepop`;
- `additionalinfos`;
- otros atributos de contexto relevantes proporcionados directamente por GDACS.

La conservaciÃ³n de estos datos no implica que formen parte de la fÃ³rmula de Risk V1.

### 9.3 Recursos secundarios

`images`, `documents`, `shakemap`, `impacts` y URLs de recursos asociados no se convertirÃ¡n en columnas especÃ­ficas del modelo comÃºn de EVIDENCE.

Cuando sea necesario conservar su referencia, se harÃ¡ mediante datos estructurados sin convertirlos automÃ¡ticamente en variables analÃ­ticas de V1.

La informaciÃ³n `episodes` se utilizarÃ¡ para descubrir referencias a episodios cuando resulte necesario, pero no se tratarÃ¡ como una nueva entidad del modelo comÃºn distinta de EVIDENCE.

## 10. GeometrÃ­a

GDACS proporciona informaciÃ³n geoespacial adicional mediante GeoJSON.

La geometrÃ­a se considerarÃ¡ informaciÃ³n contextual de la evidencia.

No se interpretarÃ¡ automÃ¡ticamente una geometrÃ­a de impacto como prueba de que toda el Ã¡rea representada haya sufrido daÃ±os.

La geometrÃ­a deberÃ¡ conservar su procedencia y significado original.

## 11. PaÃ­ses afectados

Cuando estÃ© disponible, `affectedcountries` serÃ¡ la referencia principal de GDACS para construir las relaciones geogrÃ¡ficas del EVENT.

El campo `country` se conservarÃ¡ como contexto original proporcionado por GDACS, pero no sustituirÃ¡ a la lista de paÃ­ses afectados.

La presencia de un paÃ­s en `affectedcountries` no implica por sÃ­ sola una categorÃ­a de impacto analÃ­tico distinta de la definida por STATION V.

La clasificaciÃ³n de la relaciÃ³n geogrÃ¡fica y la asignaciÃ³n posterior de Risk Impact deberÃ¡n seguir el modelo de relaciones de EVENT de STATION V.

## 12. Severidad y datos sÃ­smicos

La magnitud y profundidad describen el fenÃ³meno fÃ­sico y se conservarÃ¡n separadas de la evaluaciÃ³n de alerta de GDACS.

`alertlevel` y `alertscore` representan la evaluaciÃ³n de GDACS del EVENT, mientras que `episodealertlevel` y `episodealertscore` representan la evaluaciÃ³n del episodio concreto.

GDACS puede proporcionar la magnitud mediante `severitydata.severity` y tambiÃ©n mediante `earthquakedetails.magnitude`. Cuando ambos estÃ©n disponibles, se conservarÃ¡n sus valores de fuente y se utilizarÃ¡ la normalizaciÃ³n definida por STATION V sin tratar ambos campos como dos seÃ±ales independientes del mismo fenÃ³meno.

Los datos de GDACS no se convertirÃ¡n automÃ¡ticamente en nuevas variables matemÃ¡ticas de Country Risk fuera de las reglas de severidad y Risk Impact ya definidas por STATION V.

## 13. Nivel de alerta y resoluciÃ³n de severidad

GDACS utiliza niveles de alerta, incluyendo:

```text
green
orange
red
```

STATION V conservarÃ¡ siempre el nivel original de GDACS como atributo de la EVIDENCE.

El nivel de alerta GDACS no se transformarÃ¡ mediante una equivalencia genÃ©rica en una severidad de STATION V.

La resoluciÃ³n de severidad deberÃ¡ ser especÃ­fica para cada tipo de desastre:
```
EQ â†’ reglas sÃ­smicas
TC â†’ reglas de ciclones tropicales
FL â†’ reglas de inundaciones
VO â†’ reglas volcÃ¡nicas
DR â†’ reglas de sequÃ­a
WF â†’ reglas de incendios forestales
```
Cada funciÃ³n especÃ­fica deberÃ¡ utilizar las seÃ±ales objetivas disponibles y relevantes para ese hazard.

El resultado deberÃ¡ expresarse en la escala comÃºn de STATION V:
```
info
low
medium
high
critical
```

La severidad resultante serÃ¡ la mayor respaldada por las seÃ±ales objetivas definidas para ese hazard. No se sumarÃ¡n puntos entre seÃ±ales ni se utilizarÃ¡ una media entre criterios salvo que una metodologÃ­a especÃ­fica posterior lo establezca expresamente.

### 13.1Terremotos

Para EQ, la metodologÃ­a actualmente definida utiliza el nivel de alerta GDACS junto con las caracterÃ­sticas sÃ­smicas y las seÃ±ales adicionales objetivas disponibles.

La referencia mÃ­nima por nivel de alerta serÃ¡:

Nivel GDACS	Severidad mÃ­nima
green	info
orange	medium
red	high

TambiÃ©n se aplican las referencias de magnitud:

Magnitud	Severidad mÃ­nima
M < 5,0	info
M 5,0â€“5,9	low
M 6,0â€“6,9	medium
M 7,0â€“7,9	high
M â‰¥ 8,0	critical

En V1.2, las seÃ±ales especÃ­ficas adicionales de impacto se interpretarÃ¡n de la siguiente manera cuando estÃ©n disponibles y tengan significado aplicable al registro:

MMI < VII: no eleva;
MMI VII: eleva un nivel;
MMI VIII: eleva dos niveles;
MMI IX o superior: eleva dos niveles;
indicador explÃ­cito de tsunami: eleva un nivel;
otros campos objetivos solo podrÃ¡n elevar si se define expresamente una regla antes de su implementaciÃ³n.

Las elevaciones nunca podrÃ¡n reducir la referencia mÃ­nima ya establecida por magnitud o por alerta GDACS.

Las severidades USGS y GDACS no se promediarÃ¡n. Cada fuente evalÃºa su propia evidencia. Una fuente independiente puede aportar evidencia para actualizar la severidad del mismo EVENT mediante una nueva versiÃ³n, conservando la trazabilidad de la evaluaciÃ³n anterior.

Esta metodologÃ­a es especÃ­fica de EQ y no constituye una regla genÃ©rica para las demÃ¡s categorÃ­as de desastre.

### 13.2 Otros hazards

Para TC, FL, VO, DR y WF se definirÃ¡n reglas especÃ­ficas de severidad antes de su incorporaciÃ³n efectiva al pipeline.

Estas reglas deberÃ¡n:

conservar el nivel original de alerta GDACS;
identificar las variables objetivas relevantes del hazard;
evitar tratar como equivalentes magnitudes o indicadores fÃ­sicamente distintos;
producir una severidad comÃºn de STATION V;
mantener separada la evaluaciÃ³n de GDACS de la severidad interna de STATION V;
permitir que una alerta orange resulte en low, medium u otra severidad superior cuando las seÃ±ales objetivas lo respalden;
permitir que una alerta red alcance high o critical segÃºn las caracterÃ­sticas objetivas del evento.

No se establecerÃ¡ una tabla genÃ©rica del tipo:

```
GDACS orange â†’ STATION V medium
GDACS red    â†’ STATION V high
```
para todos los hazards.

Las reglas especÃ­ficas de cada hazard deberÃ¡n documentarse antes de implementar su funciÃ³n de severidad correspondiente.

### 13.3 Visibilidad cartogrÃ¡fica

La visibilidad de un evento en el mapa dependerÃ¡ exclusivamente de la severidad de STATION V.

```
info
low
medium
    â†“
no se muestra como EVENT en el mapa

high
critical
    â†“
EVENT visible en el mapa
```
El nivel de alerta original de GDACS no determina directamente la visibilidad cartogrÃ¡fica.

Por tanto:
```
GDACS orange
â†’ puede producir info / low / medium / high / critical

GDACS red
â†’ puede producir high / critical
```
La decisiÃ³n de mostrar el EVENT se realizarÃ¡ despuÃ©s de resolver la severidad propia de STATION V.


## 14. EVIDENCE

Cada registro GDACS aceptado por el ingestor constituirÃ¡ una unidad de:

```text
EVIDENCE
```

La evidencia representarÃ¡ que GDACS ha registrado o proporcionado informaciÃ³n sobre este evento.

El `source_id` deberÃ¡ apuntar al registro `GDACS` de la tabla `sources`.

La persistencia deberÃ¡ ser idempotente respecto de `source_id + external_id + external_episode_id`.

## 15. CLAIM

La primera implementaciÃ³n generarÃ¡ un CLAIM asociado a cada EVIDENCE GDACS.

El CLAIM describirÃ¡ de forma controlada el hecho que la fuente permite afirmar.

El nivel de confianza y el `assertion_status` deberÃ¡n reflejar la naturaleza de la fuente.

No se utilizarÃ¡ el CLAIM para convertir automÃ¡ticamente una alerta GDACS en un acontecimiento STATION V confirmado.

## 16. EVENT

La existencia de EVIDENCE + CLAIM de GDACS no implica automÃ¡ticamente un EVENT.

La creaciÃ³n o actualizaciÃ³n de un EVENT requerirÃ¡ posteriormente reglas especÃ­ficas de clasificaciÃ³n, corroboraciÃ³n y evaluaciÃ³n.

En particular:

```text
SOURCE
  â†“
EVIDENCE
  â†“
CLAIM
```

es un proceso distinto de:

```text
CLAIM
  â†“
EVENT
```

Cuando un EVENT ya existente reciba nueva evidencia independiente de GDACS que sustente una severidad superior, la actualizaciÃ³n deberÃ¡ realizarse mediante el mecanismo de versionado del EVENT y no creando un segundo EVENT para el mismo acontecimiento.

## 17. RelaciÃ³n con USGS

USGS y GDACS pueden describir un mismo terremoto desde perspectivas diferentes.

```text
USGS
â†’ observaciÃ³n sÃ­smica
â†’ magnitud
â†’ profundidad
â†’ coordenadas

GDACS
â†’ alerta de desastre
â†’ evaluaciÃ³n de impacto potencial
â†’ nivel de alerta
â†’ contexto geoespacial
```

Cuando exista correspondencia entre ambos registros, la arquitectura deberÃ¡ permitir posteriormente relacionar las evidencias sin fusionarlas incorrectamente.

La coincidencia entre un registro USGS y uno GDACS no se establecerÃ¡ Ãºnicamente por el tÃ­tulo del evento ni mediante matching aproximado.

En V1 no se establecerÃ¡ una relaciÃ³n GDACS â†” USGS cuando no exista una coincidencia determinista disponible.

## 18. DeduplicaciÃ³n y actualizaciÃ³n

La deduplicaciÃ³n se realizarÃ¡ mediante los identificadores externos de GDACS.

El sistema deberÃ¡ ser idempotente:

```text
misma EVIDENCE GDACS
+
mismo eventid
+
mismo episodeid
        â†“
no crear una segunda EVIDENCE
```

Cuando GDACS proporcione un nuevo episodio:

```text
mismo eventid
+
nuevo episodeid
        â†“
nueva EVIDENCE
+
same EVENT
```

La actualizaciÃ³n de informaciÃ³n de un episodio ya conocido deberÃ¡ actualizar la evidencia correspondiente en lugar de generar duplicados.

Los episodios anteriores no deberÃ¡n eliminarse por el hecho de que GDACS proporcione otro episodio para el mismo EVENT.

## 19. Trazabilidad

Cada EVIDENCE GDACS deberÃ¡ conservar, cuando estÃ© disponible:

- URL original;
- identificador externo;
- `episodeid`;
- `sourceid`;
- tipo de evento;
- timestamp del fenÃ³meno;
- timestamp de recuperaciÃ³n;
- `datemodified`;
- datos estructurados relevantes;
- fuente original.

La trazabilidad deberÃ¡ permitir reconstruir de quÃ© registro GDACS procede cada EVIDENCE y quÃ© evaluaciÃ³n concreta representa.

## 20. LÃ­mites y comportamiento

La API de bÃºsqueda de GDACS permite consultas personalizadas y devuelve datos geoespaciales.

Las consultas deberÃ¡n realizarse con intervalos temporales controlados y respetando los lÃ­mites tÃ©cnicos de la API.

La implementaciÃ³n deberÃ¡ tolerar:

- respuesta vacÃ­a;
- campos opcionales ausentes;
- cambios de estado de alerta;
- nuevos episodios;
- actualizaciÃ³n de registros existentes;
- errores HTTP;
- respuestas malformadas;
- timeouts;
- interrupciones temporales del servicio.

Los errores de la fuente no deberÃ¡n provocar corrupciÃ³n parcial de la base de datos.

## 21. PolÃ­tica de interpretaciÃ³n

GDACS es una fuente institucional de alerta y coordinaciÃ³n.

Por tanto:

```text
GDACS alerta
â‰ 
evento confirmado por STATION V
```

y:

```text
GDACS orange/red
â‰ 
Country Risk orange/red
```

Los niveles propios de GDACS se conservarÃ¡n como atributos de la fuente.

La transformaciÃ³n posterior a indicadores internos de STATION V serÃ¡ una capa separada.


## 22. Alcance inicial

La integraciÃ³n GDACS deberÃ¡ demostrar:

1. conexiÃ³n con la API;
2. Discovery mediante `geteventlist/SEARCH`;
3. Refresh mediante `geteventdata`;
4. normalizaciÃ³n multi-hazard;
5. identificaciÃ³n externa;
6. persistencia de SOURCE;
7. persistencia de EVIDENCE;
8. persistencia de CLAIM;
9. deduplicaciÃ³n;
10. actualizaciÃ³n de registros existentes;
11. creaciÃ³n de nueva EVIDENCE para nuevos episodios;
12. resoluciÃ³n de nuevos episodios sobre el mismo EVENT;
13. persistencia de paÃ­ses afectados;
14. asignaciÃ³n correcta de Risk Impacts;
15. trazabilidad;
16. comportamiento correcto ante respuestas vacÃ­as, errores y timeouts;
17. resoluciÃ³n de severidad especÃ­fica por hazard;
18. separaciÃ³n entre severidad de STATION V y nivel de alerta original de GDACS;
19. visibilidad cartogrÃ¡fica limitada a EVENTs con severidad `high` o `critical`.

Los hazards contemplados por la integraciÃ³n son:

```text
EQ
TC
FL
VO
DR
WF
```
La metodologÃ­a de severidad de EQ estÃ¡ definida y validada inicialmente.

Las metodologÃ­as especÃ­ficas de TC, FL, VO, DR y WF deberÃ¡n definirse antes de activar su procesamiento efectivo.

No se implementarÃ¡:

- correlaciÃ³n automÃ¡tica USGS â†” GDACS mediante matching heurÃ­stico;
- una fÃ³rmula de severidad comÃºn aplicada indistintamente a todos los hazards;
- equivalencia automÃ¡tica entre el nivel GDACS y la severidad de STATION V.

## 23. Fuentes oficiales

DocumentaciÃ³n API:

https://www.gdacs.org/Documents/2025/GDACS_API_quickstart_v1.pdf

Referencia de feeds:

https://data.gdacs.org/feed_reference.aspx

Swagger/API:

https://www.gdacs.org/gdacsapi/swagger/index.html

Recursos de eventos:

https://www.gdacs.org/resources.aspx

Condiciones de uso:

https://www.gdacs.org/documents/2025/GDACS_Terms_of_use_Mar_25.pdf

