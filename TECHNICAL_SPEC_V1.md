# STATION V

## Technical Specification — V1

**Producto:** STATION V  
**Subtítulo:** Inteligencia geopolítica de código abierto  
**Versión:** V1  
**Estado:** Especificación técnica inicial para desarrollo

---

## 1. Objetivo

Esta especificación define la arquitectura técnica mínima necesaria para implementar la V1 funcional de STATION V.

La V1 será una aplicación web responsive de *situational awareness* geopolítico basada en información OSINT estructurada, optimizada prioritariamente para dispositivos móviles.

Su objetivo es permitir al usuario:

- identificar rápidamente dónde están ocurriendo acontecimientos relevantes;
- consultar qué está ocurriendo;
- conocer qué países presentan mayor Country Risk;
- identificar cambios recientes;
- identificar acontecimientos con mayor potencial de escalada;
- consultar las evidencias y fuentes que sustentan las evaluaciones.

STATION V no será un agregador masivo de noticias. La arquitectura debe transformar fuentes y evidencias en acontecimientos estructurados y, posteriormente, en indicadores de riesgo.

## 2. Alcance de la V1

### Incluido

- Aplicación web responsive, optimizada para móvil.
- Mapa mundial interactivo.
- Zoom y desplazamiento libre del mapa.
- Visualización geográfica de acontecimientos Alta/Crítica.
- Ocho categorías de acontecimientos.
- Panel de evento.
- Panel de país.
- Country Risk.
- Cinco dimensiones de riesgo.
- Trend 24 h.
- Confidence.
- Pantalla Situación.
- Búsqueda de países y acontecimientos.
- Evidencias y fuentes asociadas.
- Motor de scoring V1.1.
- Histórico de Country Risk.
- API REST.
- Base de datos relacional.
- Datos de prueba (*seed data*).

### No incluido en el MVP

- Watchlist.
- Notificaciones push.
- Sistema de usuarios.
- Login.
- Suscripciones.
- Regiones como unidad de análisis.
- Comparador avanzado.
- IA/LLM visible para el usuario.
- Integración de aviación.
- Integración marítima.
- Integración satelital.
- Automatización completa de ingestión OSINT.
- Análisis histórico avanzado.
- Predicciones.

La arquitectura deberá permitir incorporar estas capacidades posteriormente sin rediseñar el núcleo.

## 3. Principios técnicos

### 3.1 Separación de conceptos

No se mezclarán:

- fuente;
- evidencia;
- claim;
- acontecimiento;
- severidad;
- impacto;
- subindicador;
- dimensión;
- Country Risk;
- Escalation Score;
- Trend;
- Confidence.

### 3.2 Trazabilidad

Todo Country Risk deberá poder rastrearse hacia:

```text
Country Risk

    ↓

Dimension

    ↓

Subindicator

    ↓

Risk Impact

    ↓

Event

    ↓

Claim

    ↓

Evidence

    ↓

Source
```

### 3.3 Una noticia no es un evento

Varias fuentes pueden describir un mismo acontecimiento. La aplicación deberá representar el hecho subyacente como un único EVENT, manteniendo las distintas evidencias.

### 3.4 No falsa precisión

La precisión geográfica y temporal almacenada nunca deberá superar la precisión disponible en las evidencias.

### 3.5 Frontend sin lógica de scoring

El frontend mostrará resultados calculados por el backend. Las fórmulas y reglas de scoring estarán centralizadas en el backend.

## 4. Arquitectura general

```text
                         STATION V

                             │

              ┌──────────────┴──────────────┐

              │                             │

          FRONTEND                       BACKEND

              │                             │

       Aplicación web                  API REST

              │                        Domain Logic

       Interactive Map                  Risk Engine

       Situation Dashboard              Event Logic

       Search                           Evidence Logic

       Country Panel                         │

       Event Panel                           ▼

              │                         PostgreSQL

              │                          + PostGIS

              │

              └──────── HTTPS / JSON ──────┘
```

La arquitectura lógica de datos será:

```text
SOURCE

   ↓

EVIDENCE

   ↓

CLAIM

   ↓

EVENT

   ↓

RISK IMPACT

   ↓

SUBINDICATOR

   ↓

DIMENSION

   ↓

COUNTRY RISK
```

Las áreas principales de la aplicación son vistas diferentes del mismo modelo de datos. Country Panel y Event Panel son componentes de detalle superpuestos y no constituyen áreas de navegación principales independientes.

## 5. Stack tecnológico

Estas son decisiones técnicas del proyecto, no elementos establecidos por los documentos metodológicos.

### Frontend

- React
- Vite
- TypeScript

El frontend V1 se implementará inicialmente como una aplicación web responsive, diseñada para su uso prioritario en dispositivos móviles.

La arquitectura deberá permitir valorar posteriormente una evolución hacia una aplicación nativa si las necesidades del producto lo justifican.

### Backend

- Python
- FastAPI
- Pydantic

### Base de datos

- PostgreSQL
- PostGIS

### Desarrollo

- Git
- GitHub
- Docker
- Docker Compose

### Tests

- pytest para backend
- tests de TypeScript/React para frontend

El stack podrá modificarse posteriormente si la experiencia durante el desarrollo demuestra que existe una alternativa claramente superior, pero no se cambiará durante la construcción del MVP salvo necesidad justificada.

## 6. Aplicación

La V1 se implementará como una aplicación web responsive, optimizada prioritariamente para dispositivos móviles.

La aplicación tendrá tres áreas principales y tres pestañas de navegación en V1:

```text
🌍 MAPA

📊 SITUACIÓN

🔎 BUSCAR
```

**MAPA** será la entrada principal de la V1.

**SITUACIÓN** será un dashboard único de indicadores y cambios geopolíticos.

**BUSCAR** permitirá localizar y explorar países y acontecimientos.

No existirán pantallas independientes de países o acontecimientos en V1. Los detalles se mostrarán mediante paneles superpuestos.

La navegación deberá permitir incorporar nuevas áreas funcionales en futuras versiones sin modificar el núcleo conceptual de la aplicación.

## 7. Mapa

### 7.1 Naturaleza

El mapa será:

- interactivo;
- navegable;
- ampliable;
- desplazable;
- vectorial;
- preparado para múltiples niveles de zoom.

No será una imagen estática.

### 7.2 Estética funcional

El mapa tendrá:

- fondo homogéneo;
- fronteras internacionales;
- geometrías de países;
- elementos geográficos mínimos necesarios.

No se coloreará el mundo según Country Risk en V1.

Los acontecimientos aparecerán como marcadores.

### 7.3 Eventos visibles

El mapa mostrará inicialmente únicamente acontecimientos de severidad Alta o Crítica que hayan superado el umbral de corroboración operativo.

El color de los marcadores se determinará por Escalation Score, no por severidad:

```text
0–3       baja       verde

>3–6      moderada   amarillo

>6–8      alta       naranja

>8–10     crítica    rojo
```

### 7.4 Categorías

```text
conflict_violence

protests_unrest

military_activity

border_tension

political_crisis

disaster

critical_infrastructure

security_terrorism
```

Cada categoría tendrá icono, nombre legible y clave interna.

### 7.5 Clustering

El mapa deberá soportar agrupación visual de eventos cuando el nivel de zoom provoque solapamiento.

El clustering es una característica de presentación y no modifica ni agrupa los EVENT en la base de datos.

### 7.6 Carga geográfica

El frontend no descargará todos los datos completos de los eventos. La API devolverá inicialmente únicamente los eventos relevantes para la zona visible del mapa.

La consulta podrá utilizar *bounding box* y zoom. El detalle completo se solicitará al seleccionar un evento.

## 8. Panel de país

El panel aparecerá al seleccionar un país.

Contendrá:

### Identificación

- bandera;
- nombre;
- código ISO.

### Country Risk

- score 0–100;
- nivel;
- Trend 24 h;
- Confidence.

### Dimensiones

- Inestabilidad interna;
- Conflicto y violencia;
- Tensión internacional;
- Actividad militar;
- Presión / estrés.

### Eventos relevantes

Lista resumida de acontecimientos asociados al país.

No se implementará todavía una pantalla independiente de análisis de país.

## 9. Panel de evento

El panel mostrará:

- categoría;
- título;
- ubicación;
- severidad;
- Escalation Score cuando corresponda;
- estado;
- Confidence;
- última actualización;
- resumen factual;
- impacto humano cuando exista;
- países afectados;
- impactos sobre subindicadores;
- acceso a evidencias y fuentes.

La complejidad interna del EVENT no se trasladará íntegramente a la interfaz móvil.

## 10. Situación

La pantalla Situación será un dashboard único.

Contendrá inicialmente cinco paneles:

### 10.1 Riesgo global

Mostrará un indicador agregado del nivel de riesgo sistémico internacional.

La pregunta que deberá representar será:

> ¿Está aumentando o disminuyendo la tensión/riesgo del sistema internacional en conjunto?

El Riesgo Global no será una media simple de los Country Risk de todos los países.

Su cálculo tendrá en cuenta la importancia sistémica estructural de los países y la concentración del riesgo entre los principales actores del sistema internacional.

El indicador se expresará en una escala 0–100.

Niveles iniciales:

```text
0–19      Bajo
20–39     Elevado
40–59     Alto
60–79     Muy alto
80–100    Crítico
```

Estos niveles son categorías interpretativas del índice y no representan probabilidades.

El Riesgo Global no representará una probabilidad de guerra, conflicto o guerra mundial.

### 10.2 Mayor Country Risk

Ranking de países por Country Risk descendente.

### 10.3 Mayor deterioro · 24 h

Países con mayor Trend positivo.

### 10.4 Mayor mejora · 24 h

Países con mayor Trend negativo.

### 10.5 Eventos más relevantes

Se mostrarán como máximo los 10 acontecimientos más relevantes con Severidad Alta o Crítica.

La ordenación se realizará jerárquicamente:

1. Severidad del acontecimiento, priorizando Crítica sobre Alta.
2. Escalation Score descendente dentro de cada nivel de severidad.

Por tanto, un acontecimiento Crítico con un Escalation Score inferior aparecerá antes que un acontecimiento Alto con un Escalation Score superior.

Ejemplo:

```text
Crítica — 7.6
Crítica — 6.8
Alta — 9.2
Alta — 8.5
```

Los acontecimientos con Severidad inferior a Alta no aparecerán en este panel.

No se incluirá todavía un ranking regional.

Podrán incorporarse paneles adicionales en futuras iteraciones sin modificar la arquitectura conceptual del dashboard.

## 11. Búsqueda

La pestaña principal se denominará **BUSCAR**.

La búsqueda permitirá inicialmente:

```text
País

Acontecimiento
```

La arquitectura se preparará para incorporar regiones posteriormente.

Endpoint:

```text
GET /api/v1/search?q={query}
```

Los resultados estarán agrupados por tipo. La selección abrirá el correspondiente CountryPanel o EventPanel.

La exploración y filtrado de acontecimientos se integrará en esta área y no constituirá una cuarta pestaña independiente en V1.

## 12. Modelo de datos

### 12.1 Country

```text
Country
---------

id

iso2

iso3

name

geometry

created_at

updated_at
```

La geometría se almacenará mediante PostGIS.

### 12.2 Event

```text
Event
---------

event_id

event_version

category

subtype

title

summary

analyst_summary

country_id

region

place

latitude

longitude

location_precision

time_start

time_end

time_precision

status

severity

escalation_score

confidence

first_detected_at

last_evidence_at

created_at

updated_at

duplicate_of

current_version_id
```

El EVENT será versionable. Cada modificación estructural relevante del acontecimiento generará una nueva versión conservando el estado anterior.

La versión vigente estará identificada mediante `current_version_id`. Las versiones históricas no se sobrescribirán.

Los duplicados conservarán su relación mediante `duplicate_of` y no se eliminarán silenciosamente.

### 12.3 Event Timeline

```text
EventTimeline
---------

id

event_id

timestamp

update_type

description

event_version_id

created_at
```

`event_timeline` registrará la evolución temporal de un EVENT.

Tipos iniciales de actualización:

```text
initial_detection

general_update

status_change

occurrence
```

`initial_detection`

Registra la detección o creación inicial del EVENT.

`general_update`

Registra una actualización relevante que no implique necesariamente un cambio de estado o una nueva ocurrencia independiente.

`status_change`

Registra cambios relevantes en el estado operativo del EVENT.

`occurrence`

Registra una nueva ocurrencia relacionada con el mismo acontecimiento o incidente.

Una `occurrence` no crea automáticamente un EVENT nuevo. Se mantiene dentro del EVENT existente siempre que exista continuidad suficiente para considerar que forma parte del mismo acontecimiento.

Cuando una actualización modifique información estructural del EVENT, deberá generarse una nueva versión. La actualización del timeline conservará la referencia a `event_version_id` cuando corresponda.

El timeline y el versionado tienen funciones diferentes:

`event_versions` conserva el estado estructurado del EVENT en cada versión;

`event_timeline` conserva la secuencia temporal de actualizaciones relevantes.

La información del timeline deberá mantener trazabilidad hacia el EVENT y, cuando corresponda, hacia la versión del evento que originó la actualización.

## 13. Países afectados

Se utilizará una relación muchos-a-muchos:

```text
event_countries

----------------

event_id

country_id

relationship_type
```

Valores iniciales:

```text
directly_affected

indirectly_affected
```

Las relaciones indirectas no generarán automáticamente impacto sobre Country Risk.

## 14. Source

El Source Registry seguirá los campos establecidos en el documento de fuentes.

```text
Source
---------

source_id

name

tier

source_class

source_type

geographic_scope

coverage

reliability

roles

detection_capability

corroboration_capability

expertise

independence_group

access_method

status
```

## 15. Evidence

```text
Evidence
---------

evidence_id

event_id

source_id

published_at

retrieved_at

title

url

author

language

content_type

evidence_type

source_role

relationship_to_event

independence_group

evidence_quality

first_seen_at

last_seen_at

content_hash
```

Tipos iniciales:

```text
report

statement

observation

dataset

measurement
```

Roles:

```text
detection

corroboration

primary_confirmation

context

quantitative_data
```

## 16. Claims

```text
Claim
---------

claim_id

evidence_id

claim_type

statement

assertion_status

confidence

created_at

updated_at
```

Tipos iniciales:

```text
event_occurrence

casualty

location

time

actor

attribution

damage

military_activity

political_statement

consequence

status
```

Estados:

```text
confirmed

reported

claimed

disputed

inferred
```

Un claim no confirmado no se convertirá automáticamente en un hecho del EVENT.

## 17. Event ↔ Evidence

No se almacenarán URLs como única prueba de un acontecimiento.

La relación será:

```text
SOURCE

   ↓

EVIDENCE

   ↓

CLAIM

   ↓

EVENT
```

Se podrán conservar evidencias principales, contradictorias, de actualización y de sustitución de información anterior.

## 18. Risk Impact

Los acontecimientos no modificarán directamente una dimensión ni Country Risk.

La relación será:

```text
Event

  ↓

RiskImpact

  ↓

Subindicator

  ↓

Dimension

  ↓

Country Risk
```

Modelo mínimo:

```text
RiskImpact
---------

id

event_id

country_id

subindicator_id

base_impact

relevance

temporal_weight

repetition_weight

effective_impact

created_at
```

El impacto efectivo seguirá:

```text
I_effective = I_base × R × W_t × W_r
```

## 19. Subindicadores y dimensiones

La base de datos tendrá entidades normalizadas para `Dimension` y `Subindicator`.

Las cinco dimensiones oficiales son:

```text
internal_instability

conflict_violence

international_tension

military_activity

pressure_stress
```

Pesos:

```text
25%

25%

20%

15%

15%
```

Los subindicadores se conservarán individualmente para garantizar trazabilidad y permitir futuras recalibraciones.

### Importancia sistémica por Tier

Los países dispondrán de una clasificación estructural de importancia sistémica independiente de su Country Risk actual.

La clasificación inicial será:

```text
Tier 1
Potencias sistémicas globales.

Tier 2
Actores con capacidad significativa de transmisión internacional o regional.

Tier 3
Actores cuya importancia sistémica es principalmente regional o limitada.
```

La clasificación no dependerá de acontecimientos concretos, conflictos específicos ni del Country Risk actual.

La importancia sistémica se determinará a partir de capacidades estructurales como, entre otras:

- peso económico;
- capacidad militar;
- capacidades estratégicas y nucleares;
- población;
- posición geográfica;
- recursos;
- energía;
- comercio y conectividad;
- capacidad tecnológica e industrial;
- influencia diplomática;
- pertenencia a alianzas e instituciones;
- capacidad de transmisión internacional.

Tier 2 podrá distinguir internamente entre T2-A, T2-B y T2-Strategic cuando resulte necesario para la clasificación, sin que estas subcategorías impliquen fórmulas diferentes de Country Risk.

La clasificación de Tier será un atributo estructural del país y no se modificará como consecuencia de cambios temporales en su Country Risk.

## 20. Risk Snapshot

Se almacenarán evaluaciones históricas.

```text
RiskSnapshot
---------

id

country_id

timestamp

internal_instability

conflict_violence

international_tension

military_activity

pressure_stress

country_risk

confidence
```

Esto permitirá reconstruir la evolución temporal del país.

### Unicidad temporal de los snapshots

Cada combinación de `country_id`, `subindicator_id` y `timestamp`

deberá identificar un único `risk_subindicator_snapshot`.

La base de datos deberá impedir la existencia de múltiples

`risk_subindicator_snapshots` para el mismo país, subindicador e instante

de cálculo.

Del mismo modo, cada combinación de `country_id` y `timestamp` deberá

identificar un único `risk_snapshot`.

La base de datos deberá impedir la existencia de múltiples

`risk_snapshots` para el mismo país e instante de cálculo.

Los índices existentes podrán mantenerse para optimizar las consultas,

pero la unicidad deberá estar garantizada mediante una restricción o

índice único.

## 21. Motor de scoring

El motor implementará las reglas oficiales de V1.1.

### Ventana temporal

La ventana de cálculo de impactos de eventos será de **7 días (168 horas)**.

Los eventos con una antigüedad superior a 7 días tendrán un peso temporal de 0 para el cálculo del impacto efectivo.

### Decaimiento

Se utilizará una semivida de 48 horas:

```text
W_t = 2^(-t/48)
```

donde `t` representa la antigüedad del evento en horas.

Valores de referencia:

```text
0 h       → 1.0000

48 h      → 0.5000

96 h      → 0.2500

168 h     → 0.0884

>168 h    → 0
```

Los eventos futuros respecto al momento de referencia tendrán peso temporal 1.0.

### Repetición

```text
1.º   1.00

2.º   0.60

3.º   0.35

4.º   0.20

5.º+  0.10
```

### Impacto efectivo

```text
I_effective = I_base × R × W_t × W_r
```

Los valores de entrada se limitarán a sus rangos válidos antes de realizar el cálculo.

### Presión acumulada

La presión de eventos se calculará mediante una función de saturación:

```text
P = 100 × (1 - exp(-Σ I_effective / K))
```

con:

```text
K = 3.0
```

La presión resultante estará limitada al intervalo 0–100.

### Estado del subindicador

```text
S_t = 0.65 × S_(t-1) + 0.35 × P
```

donde:

- `S_(t-1)` es el estado anterior del subindicador;
- `P` es la presión actual de eventos.

### Country Risk

```text
CRS = 0.25 I
    + 0.25 C
    + 0.20 T
    + 0.15 M
    + 0.15 P
```

Todos los scores se expresarán en el intervalo 0–100.

### 21.3 Recalculación y acumulación

El motor de scoring deberá ser determinista respecto al estado de los datos de entrada.

La ejecución repetida del motor sobre un mismo conjunto de eventos, evidencias y ocurrencias no deberá incrementar artificialmente el riesgo.

Un mismo `RiskImpact` no podrá incorporarse repetidamente al estado de un subindicador únicamente por ejecutar de nuevo el proceso de cálculo.

La evaluación del riesgo deberá poder reconstruirse a partir de los impactos válidos en el instante de cálculo, sin depender del número de veces que se haya ejecutado previamente el motor.

Se distinguirán los siguientes casos:

- una nueva detección de un EVENT podrá generar un `RiskImpact`;
- una nueva `occurrence` podrá generar una nueva contribución al subindicador cuando corresponda;
- una nueva evidencia podrá modificar la evaluación del EVENT o de su impacto cuando aporte información relevante;
- un `general_update` no generará automáticamente un nuevo impacto;
- un `status_change` no generará automáticamente un nuevo impacto;
- una nueva ejecución del motor sin cambios relevantes en los datos de entrada no generará una nueva contribución del mismo `RiskImpact`.

El `event_timeline` conservará la secuencia temporal de actualizaciones del EVENT, pero sus entradas no deberán interpretarse automáticamente como nuevos impactos de riesgo.

Los `risk_subindicator_snapshots` conservarán las evaluaciones históricas del subindicador. La existencia de un snapshot anterior no deberá utilizarse por sí misma como justificación para volver a aplicar un `RiskImpact` ya contabilizado.

La lógica de acumulación deberá mantener trazabilidad entre los impactos considerados, los subindicadores afectados y el snapshot resultante.

## 22. Trend

Trend será independiente del Country Risk.

```text
Trend_24h = CRS_t - CRS_(t-24h)
```

Trend no se incluirá como componente adicional del Country Risk.

## 23. Global Risk

Global Risk será un indicador agregado de presión/riesgo sistémico internacional.

Su objetivo será responder a la pregunta:

> ¿Está aumentando o disminuyendo la tensión/riesgo del sistema internacional en conjunto?

Global Risk no será una media simple de Country Risk.

El modelo V1 tendrá en cuenta la importancia sistémica estructural de los países y la distribución del riesgo entre Tier 1, Tier 2 y Tier 3.

### 23.1 Fórmula general

El Global Risk se calculará mediante:

```text
GR = 0.65 × T1 + 0.25 × T2 + 0.10 × T3
```

donde:

```text
T1 = presión de los países Tier 1

T2 = presión de los países Tier 2

T3 = presión de los países Tier 3
```

El resultado final estará limitado al intervalo 0–100.

### 23.2 Presión Tier 1

La presión de Tier 1 combinará intensidad, riesgo medio y amplitud del deterioro dentro del grupo:

```text
T1 = 0.50 × I + 0.30 × A + 0.20 × B
```

donde:

```text
I = intensidad del riesgo Tier 1

A = Country Risk medio de Tier 1

B = amplitud del deterioro de Tier 1
```

### 23.3 Intensidad Tier 1

La intensidad Tier 1 se calculará mediante:

```text
I = 0.60 × max(T1) + 0.40 × mean(Top4 T1)
```

`max(T1)` representa el Country Risk más elevado entre los países Tier 1.

`mean(Top4 T1)` representa la media de los cuatro Country Risk más elevados entre los países Tier 1.

Esta combinación permite que una situación extrema de una potencia sistémica tenga un efecto significativo sin ignorar el deterioro simultáneo de varias potencias.

### 23.4 Riesgo medio Tier 1

El componente `A` será:

```text
A = mean(T1)
```

donde se utilizarán los Country Risk de los países Tier 1 disponibles.

Este componente representa el nivel medio de riesgo existente dentro del núcleo sistémico.

### 23.5 Amplitud del deterioro Tier 1

El componente `B` representará la proporción de países Tier 1 cuyo Country Risk sea igual o superior a 50:

```text
B = 100 × N(Country Risk ≥ 50) / N(Tier 1)
```

Esto permitirá diferenciar entre una situación de riesgo concentrada en una única potencia y una situación de deterioro generalizado del núcleo sistémico.

### 23.6 Presión Tier 2

La presión Tier 2 se calculará utilizando los ocho países Tier 2 con mayor Country Risk:

```text
T2 = mean(Top8 T2)
```

La clasificación interna de Tier 2 podrá distinguir entre T2-A, T2-B y T2-Strategic, pero estas categorías no utilizarán fórmulas diferentes en el cálculo del Global Risk V1.

### 23.7 Presión Tier 3

La presión Tier 3 se calculará utilizando los diez países Tier 3 con mayor Country Risk:

```text
T3 = mean(Top10 T3)
```

La contribución de Tier 3 será deliberadamente limitada para evitar que un elevado número de crisis regionales de países con menor importancia sistémica domine el indicador.

### 23.8 Interpretación

Global Risk deberá reflejar la diferencia entre:

- una perturbación extrema pero localizada en un único actor sistémico;
- un deterioro simultáneo de varias potencias sistémicas;
- una crisis amplia entre actores Tier 2;
- una situación de riesgo generalizado en los principales actores del sistema internacional.

Un elevado número de países Tier 3 en situación de riesgo no deberá producir por sí mismo un Global Risk elevado si los principales actores Tier 1 y Tier 2 permanecen estables.

### 23.9 Naturaleza del indicador

Global Risk será un índice sintético de presión/riesgo sistémico internacional.

No será:

- una probabilidad;
- una predicción;
- una estimación de probabilidad de guerra mundial;
- una suma de acontecimientos;
- una media simple de Country Risk;
- un sustituto del Country Risk.

El indicador utilizará los Country Risk como información de entrada, pero incorporará la importancia sistémica estructural de cada país mediante su clasificación por Tier.

### 23.10 Interdependencia

La V1 no incorporará todavía una medida explícita de interdependencia o contagio entre países.

La fórmula V1 medirá:

```text
Country Risk
      ↓
Importancia sistémica
      ↓
Concentración y amplitud
      ↓
Global Risk
```

Los mecanismos de transmisión económica, energética, militar, logística u otras redes de interdependencia podrán incorporarse en versiones posteriores sin modificar el núcleo conceptual del indicador.

## 24. Confidence

Confidence:

```text
High

Medium

Low
```

Será independiente del score y no actuará como multiplicador matemático.

La confianza dependerá de factores relacionados con calidad de fuentes, independencia, corroboración, fuentes primarias, consistencia, antigüedad y contradicciones.

## 25. API

La API será REST.

Los endpoints funcionales V1 se estructurarán bajo el prefijo:

```text
/api/v1
```

Durante la fase actual de desarrollo existen algunos endpoints heredados bajo `/api`. Estos podrán mantenerse temporalmente por compatibilidad durante la construcción del MVP, pero los nuevos endpoints funcionales deberán utilizar `/api/v1`.

### Países

```http
GET /api/v1/countries/{country_id}
```

### Eventos

```http
GET /api/v1/events

GET /api/v1/events/{event_id}
```

### Mapa

```http
GET /api/v1/map/events
```

Parámetros:

```text
min_lat

max_lat

min_lon

max_lon

zoom
```

### Riesgo

```http
POST /api/v1/risk/recalculate/{country_id}
```

### Situación

```http
GET /api/v1/situation
```

Respuesta lógica:

```text
top_risk

deterioration_24h

improvement_24h

relevant_events
```

### Búsqueda

```http
GET /api/v1/search?q={query}
```

Los resultados podrán incluir países y acontecimientos.

## 26. Estructura del frontend

La implementación actual utiliza React, Vite y TypeScript.

Estructura base:

```text
frontend/

│

├── public/

│

├── src/

│   ├── api/

│   │   ├── country.ts

│   │   ├── events.ts

│   │   ├── search.ts

│   │   └── situation.ts

│   │

│   ├── components/

│   │   └── CountryIdentity.tsx

│   │

│   ├── App.tsx

│   ├── MapView.tsx

│   ├── Situation.tsx

│   ├── Search.tsx

│   ├── CountryPanel.tsx

│   ├── EventDetailPanel.tsx

│   │

│   ├── App.css

│   ├── MapView.css

│   ├── Situation.css

│   ├── Search.css

│   └── index.css

│

└── package.json
```

Las tres áreas principales de navegación son:

```text
MAPA

SITUACIÓN

BUSCAR
```

`CountryPanel` y `EventDetailPanel` son componentes de detalle superpuestos y no áreas principales de navegación.

## 27. Estructura del backend

La implementación actual utiliza una estructura modular sencilla:

```text
backend/

│

├── app/

│   ├── api/

│   │   ├── countries.py

│   │   ├── country.py

│   │   ├── events.py

│   │   ├── risk.py

│   │   ├── search.py

│   │   └── situation.py

│   │

│   ├── models/

│   ├── schemas/

│   │   └── events.py

│   │

│   ├── scoring/

│   │   ├── risk_engine.py

│   │   └── risk_service.py

│   │

│   ├── db.py

│   └── main.py

│
├── migrations/

└── scripts/
```

La lógica de scoring estará centralizada en `scoring/`.

La lógica de acceso a datos y exposición HTTP permanecerá separada de las fórmulas matemáticas del motor de riesgo.

La estructura podrá evolucionar hacia módulos más especializados cuando aumente la complejidad del sistema.

## 28. Seed Data

Antes de conectar fuentes reales se utilizará un dataset controlado de desarrollo.

El dataset se ampliará progresivamente hasta cubrir:

```text
10–20 países

20–30 acontecimientos

varias evidencias por acontecimiento

claims asociados

impactos sobre subindicadores

snapshots de Country Risk

actualizaciones de eventos mediante event_timeline
```

Durante las primeras fases se utilizará un subconjunto reducido para validar la arquitectura, el scoring, la API y la interfaz.

El seed dataset no representará información OSINT real destinada a producción.

Los datos sintéticos deberán identificarse como datos de desarrollo y no deberán interpretarse como evaluaciones geopolíticas reales.

## 29. Ingestión OSINT

La ingestión automática queda fuera del primer MVP.

La arquitectura reservará una capa independiente para su futura implementación.

Posteriormente se podrán incorporar fuentes T0–T4.

## 30. Docker

Desarrollo local:

```text
docker-compose

│

└── db

    └── postgis
```

El frontend se ejecutará inicialmente mediante Vite y el backend mediante FastAPI durante el desarrollo local.

## 31. Testing

El MVP contará con tests automatizados para las principales capas del sistema.

### Scoring

- decaimiento temporal;
- ventana temporal de 7 días;
- repetición;
- relevancia;
- impacto efectivo;
- presión de eventos;
- agregación de subindicadores;
- dimensiones;
- Country Risk;
- Trend;
- Global Risk.

### Datos

- relaciones Event/Country;
- Event Timeline;
- Evidence/Claim;
- duplicados;
- versionado.

### API

- respuestas correctas;
- estructura de respuestas;
- búsqueda;
- errores;
- recursos inexistentes.

### Frontend

- navegación entre las tres áreas principales;
- selección de país;
- selección de evento;
- apertura/cierre de paneles;
- búsqueda.

Los tests del backend se ejecutarán mediante `pytest`.

La lógica matemática del motor de riesgo deberá mantenerse cubierta por tests independientes de la base de datos.

## 32. Estado actual de implementación

La V1 se encuentra en una fase de MVP técnico funcional.

Actualmente están implementados:

- PostgreSQL + PostGIS;
- catálogo de países;
- modelo de eventos;
- relaciones Event/Country;
- Risk Impact;
- snapshots de subindicadores;
- snapshots de Country Risk;
- motor de scoring V1.1;
- API de países;
- API de eventos;
- API de Country Risk;
- API de Situación;
- API de búsqueda;
- interfaz de mapa;
- panel de país;
- panel de evento;
- pantalla Situación;
- búsqueda;
- tests automatizados del motor de riesgo, servicio de riesgo y API.

El dataset de desarrollo continúa siendo sintético y reducido.

La tabla `event_timeline` está implementada y se utiliza funcionalmente para registrar la evolución temporal de los acontecimientos.

El sistema mantiene separación entre timeline y versionado: el timeline registra la secuencia temporal de actualizaciones y `event_versions` conserva los estados estructurados del EVENT.

La ingestión OSINT real todavía no forma parte del sistema operativo del MVP.

## 33. Milestones

### M0 — Repository

Crear la estructura inicial del repositorio y documentación base.

### M1 — Database

Implementar PostgreSQL/PostGIS y las entidades principales.

### M2 — Scoring

Implementar metodología V1.1 con tests matemáticos.

### M3 — API

Implementar los endpoints principales.

### M4 — Web shell

Crear navegación, tres pestañas y componentes base con React, Vite y TypeScript.

### M5 — Interactive Map

Implementar mapa, zoom, desplazamiento, países, marcadores, categorías, clustering y selección.

### M6 — Panels

Implementar CountryPanel y EventPanel.

### M7 — Situation

Implementar los cuatro paneles.

### M8 — Search

Implementar búsqueda de países y eventos.

### M9 — End-to-end MVP

Validar el circuito completo:

```text
EVENT

↓

RISK

↓

API

↓

MAP

↓

PANEL

↓

SITUATION

↓

SEARCH
```

## 34. Criterio de finalización del MVP

La V1 técnica será funcional cuando un usuario pueda:

1. abrir STATION V;
2. navegar por un mapa mundial interactivo;
3. hacer zoom y desplazarse;
4. identificar acontecimientos Alta/Crítica por categoría;
5. seleccionar un acontecimiento;
6. consultar su panel;
7. consultar sus países afectados;
8. seleccionar un país;
9. consultar su Country Risk;
10. consultar sus cinco dimensiones;
11. consultar Trend y Confidence;
12. abrir Situación;
13. consultar los rankings;
14. consultar deterioros y mejoras;
15. consultar acontecimientos ordenados por Escalation Score;
16. buscar un país;
17. buscar un acontecimiento;
18. llegar desde el score hasta las evidencias que lo sustentan.

## 35. Límites metodológicos

Durante la implementación no se permitirá:

- convertir una noticia en EVENT automáticamente;
- usar número de artículos como proxy de riesgo;
- sumar impactos directamente al Country Risk;
- utilizar Confidence como multiplicador;
- utilizar Trend dentro del Country Risk;
- calcular Escalation para eventos inferiores a Alta;
- mostrar como confirmado un claim disputado;
- inventar precisión geográfica;
- eliminar silenciosamente duplicados;
- sobrescribir evidencias originales.

## 36. Principio de extensibilidad

La V1 deberá ser pequeña, pero el núcleo de datos no deberá ser desechable.

La arquitectura deberá poder incorporar posteriormente aviación, marítimo, satélite, infraestructura, energía, OSINT social, nuevas fuentes, nuevos subindicadores, nuevas categorías y nuevas señales OSINT.

## 37. Regla final de desarrollo

> No añadir funcionalidades porque sean técnicamente interesantes si no son necesarias para el MVP.

La prioridad será:

```text
Rigor

↓

Coherencia

↓

Trazabilidad

↓

Funcionamiento

↓

Velocidad

↓

Ampliación
```

La V1 no pretende demostrar cuántas fuentes puede ingerir STATION V, sino demostrar que el modelo completo funciona de extremo a extremo.

## 38. Decisión técnica pendiente: motor de mapa

La especificación funcional exige un mapa vectorial interactivo con zoom, desplazamiento, clustering y geometrías de países.

La tecnología concreta del motor de mapas queda pendiente de decisión antes de implementar M5. Deberá evaluarse su compatibilidad con React, rendimiento, mapas vectoriales y gestión de tiles.
