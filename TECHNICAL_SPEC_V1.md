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
- impacto material cuando exista;
- países afectados;
- actores;
- timeline;
- evidencias;
- fuentes.

La visualización deberá distinguir entre información factual y valoración analítica.

## 10. Situación

La pantalla Situación será un dashboard resumido de *situational awareness*.

### Elementos V1

- Global Risk;
- países con mayor Country Risk;
- mayor deterioro 24 h;
- mayor mejora 24 h;
- eventos más relevantes.

El dashboard deberá priorizar legibilidad móvil y evitar información excesiva.

La información se calculará en backend.

## 11. Search

La búsqueda V1 permitirá localizar:

- países;
- acontecimientos.

No se implementará búsqueda full-text avanzada en V1.

## 12. Countries

El catálogo de países utilizará ISO 3166-1 alpha-2 y alpha-3 cuando exista código oficial.

La geometría se gestionará mediante PostGIS.

La V1 utilizará 196 entidades analíticas, incluyendo Palestina, Kosovo y Taiwán.

## 13. Eventos

### 13.1 Naturaleza

Un EVENT representa un acontecimiento del mundo real suficientemente estructurado para ser mostrado y/o producir impactos.

No equivale a una noticia.

### 13.2 Campos conceptuales

```text
Event
---------
event_id
category
subtype
title
summary
analyst_summary
location
location_precision
region
place
time_start
time_end
time_precision
status
severity
Escalation Score
Confidence
countries
actors
version
```

### 13.3 Categorías

Las categorías V1 serán:

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

### 13.4 Severidad

```text
info
low
medium
high
critical
```

La severidad representa impacto/riesgo del acontecimiento.

### 13.5 Escalation Score

El Escalation Score será un valor 0–10.

Se utilizará únicamente para acontecimientos High/Critical.

Representará potencial de ampliación/escalada, no gravedad absoluta.

### 13.6 Estados

```text
emerging
active
stable
decreasing
finished
```

### 13.7 Versionado

Los cambios relevantes del evento generarán nuevas versiones.

Las versiones mantendrán un histórico.

## 14. Evidence

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
confirmation
context
analysis
```

Una Evidence no implica automáticamente que el contenido sea verdadero.

La Evidence representa la existencia de una fuente o material que sustenta una afirmación.

## 15. Claims

```text
Claim
---------
claim_id
evidence_id
claim_type
statement
assertion_status
confidence
```

Estados:

```text
confirmed
reported
claimed
disputed
inferred
```

Un CLAIM expresa una afirmación derivada de una Evidence.

## 16. Source Registry

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

### Tiers de fuente

```text
T0
T1
T2
T3
T4
```

La arquitectura debe permitir registrar múltiples fuentes para un mismo evento.

## 17. Confidence

Confidence representará la confianza en la información disponible.

Valores de usuario:

```text
low
medium
high
```

Confidence no equivale a severidad.

No existirá un único número de Confidence visible al usuario en V1.

## 18. Trend

Trend representará evolución reciente.

Para V1:

```text
Trend 24 h = Country Risk actual − Country Risk de referencia 24 h antes
```

Trend no se incluirá como componente adicional del Country Risk.

## 19. Country Risk

Country Risk será un índice 0–100.

Se calculará mediante cinco dimensiones:

```text
Internal Instability       25 %
Conflict & Violence        25 %
International Tension      20 %
Military Activity          15 %
Pressure / Stress          15 %
```

### Fórmula

```text
Country Risk =
0.25 × Internal Instability +
0.25 × Conflict & Violence +
0.20 × International Tension +
0.15 × Military Activity +
0.15 × Pressure / Stress
```

No se añadirá ninguna constante adicional.

El resultado estará limitado a 0–100.

### 19.1 Niveles de Country Risk

```text
0–19   Bajo
20–39  Elevado
40–59  Alto
60–79  Muy alto
80–100 Crítico
```

Los niveles de Country Risk son independientes de la severidad de los eventos.

### 19.2 Actualización

Country Risk podrá recalcularse cuando:

- aparezca nueva Evidence relevante;
- cambie un EVENT relevante;
- cambie un Risk Impact;
- se ejecute una actualización programada.

Cada cálculo generará un snapshot histórico.

## 20. Dimensiones

### 20.1 Internal Instability

Subindicadores V1:

```text
Protestas y movilización social
Disturbios / alteración del orden público
Violencia política
Terrorismo / insurgencia interna
Crisis institucional
Violencia entre grupos
Huelgas / disrupción social
```

### 20.2 Conflict & Violence

```text
Conflictos armados activos
Enfrentamientos / violencia armada
Ataques contra población
Terrorismo
Insurgencia / guerra irregular
Impacto humano / víctimas
Extensión geográfica
Persistencia del conflicto
```

### 20.3 International Tension

```text
Incidentes fronterizos
Disputas territoriales
Crisis diplomáticas
Amenazas / retórica oficial
Sanciones
Intervención / implicación extranjera
Relaciones con aliados y bloques
Aislamiento / deterioro internacional
```

### 20.4 Military Activity

```text
Movilización
Despliegues / movimientos de tropas
Actividad militar fronteriza
Actividad aérea
Actividad naval
Ejercicios militares anómalos
Empleo de armamento
Preparación / postura militar
```

### 20.5 Pressure / Stress

```text
Situación económica
Crisis humanitaria
Seguridad alimentaria
Energía
Desplazamientos de población
Servicios esenciales
Presión social
Capacidad institucional
Desastres / vulnerabilidad ambiental
```

Cada dimensión será una combinación ponderada de sus subindicadores.

Los pesos exactos quedan definidos en el catálogo metodológico de V1.1.

## 21. Risk Impact

Cada EVENT podrá producir uno o varios Risk Impact.

```text
Risk Impact
-----------
event_id
country_id
subindicator_id
base_impact
relevance
temporal_weight
repetition_weight
effective_impact
```

### Fórmula conceptual

```text
Effective Impact =
Base Impact × Relevance × Temporal Weight × Repetition Weight
```

Los valores estarán limitados a los rangos establecidos en la base de datos.

### Relevancia

Relevance representará la relación entre el acontecimiento y el subindicador.

Un mismo EVENT podrá afectar a varios subindicadores con distinta Relevance.

### Temporal Weight

El impacto disminuirá con el tiempo.

La V1 utilizará una función temporal definida en el motor de scoring.

### Repetition Weight

La repetición de acontecimientos similares no generará crecimiento lineal infinito.

Se utilizará una función de saturación.

## 22. Matriz semántica

Cada categoría/subtipo podrá afectar a distintos subindicadores.

La asignación se realizará mediante una matriz semántica.

Ejemplo:

```text
EVENT
│
├── CATEGORY
│
├── SUBTYPE
│
└── LOCATION
        │
        ▼
Semantic Matrix
        │
        ├── Subindicator A
        ├── Subindicator B
        └── Subindicator C
```

La matriz semántica no generará por sí misma el valor final de Country Risk.

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

La presión Tier 1 se calculará mediante:

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

### 23.4 Country Risk medio Tier 1

```text
A = mean(T1)
```

donde se utilizarán los Country Risk de los países Tier 1 disponibles.

Este componente representa el nivel medio de riesgo existente dentro del núcleo sistémico.

### 23.5 Amplitud del deterioro Tier 1

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
- una representación de relaciones causales exhaustivas del sistema internacional.

El indicador utilizará los Country Risk como información de entrada, pero incorporará la importancia sistémica estructural de cada país mediante su clasificación por Tier.

### 23.10 Cobertura y estado de disponibilidad

El Global Risk podrá calcularse aunque no exista información de Country Risk para todos los países del universo STATION V.

La ausencia de un snapshot válido no se interpretará como Country Risk = 0. Los países sin información válida quedarán excluidos del cálculo, de acuerdo con las reglas definidas para cada Tier.

Para evaluar la representatividad del indicador se calcularán dos métricas:

```text
Cobertura global =
países con Country Risk válido / total de países del universo STATION V
```

```text
Cobertura sistémica =
países Tier 1 y Tier 2 con Country Risk válido /
total de países Tier 1 y Tier 2
```

La cobertura no modificará matemáticamente el valor del Global Risk.
Se utilizará exclusivamente como indicador de disponibilidad y representatividad de los datos.

El estado de cobertura se clasificará de la siguiente forma:

```text
INSUFICIENTE
Cobertura global < 25 %
o
Cobertura sistémica < 50 %
```

```text
PROVISIONAL

Cobertura global >= 25 %
y
Cobertura sistémica >= 50 %

pero no se cumplen simultáneamente los criterios de estado OPERATIVO.
```

```text
OPERATIVO

Cobertura global >= 60 %
y
Cobertura sistémica >= 80 %
```

Cuando el estado sea INSUFICIENTE o PROVISIONAL, el frontend podrá mostrar un indicador visual asociado al panel de Global Risk para advertir de la limitación de cobertura.

El estado OPERATIVO no requerirá un indicador visual adicional.

La cobertura constituye un metadato de calidad y representatividad del indicador y no debe confundirse con el nivel de riesgo expresado por Global Risk.

### 23.11 Interdependencia

La V1 no incorporará todavía una medida explícita de interdependencia o contagio entre países.

La arquitectura podrá incorporar posteriormente:

```text
Trade Exposure

Energy Exposure

Financial Exposure

Military Alliances

Supply Chain Exposure

Strategic Infrastructure
```

Estas relaciones podrán modificar el impacto sistémico en versiones posteriores.

## 24. Confidence

Confidence:

```text
Confidence =
f(Source Reliability,
Independence,
Corroboration,
Recency)
```

La fórmula exacta podrá evolucionar durante el desarrollo V1.

## 25. Risk Engine

El motor de riesgo será responsabilidad exclusiva del backend.

Se dividirá en módulos lógicos:

```text
Evidence Layer
      ↓
Event Layer
      ↓
Risk Impact Layer
      ↓
Subindicator Layer
      ↓
Dimension Layer
      ↓
Country Risk Layer
      ↓
Global Risk Layer
```

Cada módulo deberá poder probarse individualmente.

## 26. Historical Data

Se conservarán snapshots históricos de Country Risk.

Cada snapshot contendrá:

```text
country_id
timestamp
5 dimensions
Country Risk
Confidence
```

Posteriormente se podrán añadir series temporales más profundas.

## 27. API

La API será REST.

Ejemplos conceptuales:

```text
GET /countries

GET /countries/{id}

GET /events

GET /events/{id}

GET /events/{id}/evidence

GET /search

GET /risk/{country_id}

GET /risk/{country_id}/history
```

El frontend no accederá directamente a PostgreSQL.

## 28. Base de datos

PostgreSQL + PostGIS.

La base deberá soportar:

- relaciones geográficas;
- eventos;
- evidencias;
- claims;
- snapshots;
- histórico;
- consultas temporales;
- búsquedas eficientes.

La integridad referencial será responsabilidad de la base de datos.

## 29. Ingestión OSINT

La ingestión automática queda fuera del primer MVP.

La arquitectura reservará una capa independiente para su futura implementación.

Posteriormente se podrán incorporar fuentes T0–T4.

### 29.1 Principio de coste V1

La implementación OSINT de V1 deberá poder ejecutarse con un coste de licencias y acceso a fuentes de **0 €**.

No se incorporarán como dependencias obligatorias de la ingestión V1 fuentes que requieran:

- suscripción de pago;
- licencia de datos de pago;
- licencia específica para automatización o redistribución;
- acceso empresarial de pago;
- infraestructura externa de pago necesaria para su funcionamiento.

La ausencia de coste no sustituye la evaluación de las condiciones de uso, licencias, límites técnicos y permisos de cada fuente.

### 29.2 Matriz inicial de fuentes OSINT

La primera capa OSINT de STATION V se construirá sobre una combinación de fuentes estructuradas, académicas, institucionales y de descubrimiento.

Fuentes piloto iniciales:

```text
USGS
GDACS
GDELT
```

Su función inicial será deliberadamente diferente:

```text
USGS
Fuente estructurada de evidencia.
Especialización inicial: actividad sísmica y terremotos.

GDACS
Fuente estructurada de alertas y contexto sobre desastres.
Especialización inicial: terremotos, ciclones, inundaciones y otras
emergencias de alcance internacional.

GDELT
Fuente secundaria de descubrimiento y monitorización de información.
No se considerará por sí misma evidencia suficiente para convertir
automáticamente una noticia o mención en un EVENT.
```

Estas tres fuentes se utilizarán inicialmente para validar el circuito de ingestión y tratamiento OSINT:

```text
SOURCE

↓

EVIDENCE

↓

CLAIM

↓

EVENT
```

La incorporación de una fuente al sistema no implica que todos sus datos generen automáticamente acontecimientos. La función de cada fuente deberá quedar registrada y respetar su capacidad de detección, corroboración, contexto y datos cuantitativos.

### 29.3 Fuentes previstas para fases posteriores

Una vez validado el pipeline con las fuentes piloto, podrán incorporarse:

```text
UCDP
ReliefWeb / OCHA
NASA FIRMS
Fuentes oficiales gubernamentales
Organismos internacionales
```

Estas fuentes tendrán funciones complementarias:

```text
UCDP
Datos académicos sobre conflicto armado y violencia organizada.

ReliefWeb / OCHA
Crisis humanitarias, emergencias y contexto operacional.

NASA FIRMS
Observaciones satelitales de actividad térmica e incendios.
Los hotspots no se interpretarán automáticamente como EVENT.

Fuentes oficiales gubernamentales
Evidencia primaria sobre decisiones, declaraciones, alertas,
actividad estatal y acontecimientos oficiales.

Organismos internacionales
Evidencia primaria o institucional sobre crisis, decisiones,
operaciones, alertas y acontecimientos internacionales.
```

### 29.4 Medios de comunicación y fuentes de descubrimiento

Medios internacionales de alta calidad, como Reuters, podrán utilizarse como fuentes de descubrimiento o corroboración cuando exista acceso público y permitido para el uso concreto.

Reuters no será una dependencia obligatoria del pipeline automatizado de V1 ni se almacenará sistemáticamente su contenido salvo que las condiciones de uso aplicables lo permitan.

La arquitectura no dependerá de un único medio de comunicación.

La utilización de una fuente de descubrimiento no implicará que el contenido publicado por dicha fuente pueda copiarse, redistribuirse o almacenarse íntegramente. Se conservarán únicamente los elementos necesarios para la trazabilidad y el funcionamiento del modelo, de acuerdo con las condiciones de uso aplicables.

### 29.5 Criterios de incorporación

Antes de incorporar una nueva fuente al pipeline OSINT se evaluará:

- coste;
- licencia y condiciones de uso;
- método de acceso;
- estabilidad del acceso;
- límites de consulta;
- cobertura geográfica;
- cobertura temporal;
- capacidad de detección;
- capacidad de corroboración;
- calidad de los datos;
- independencia respecto de otras fuentes;
- posibilidad de mantener trazabilidad hacia la fuente original.

La matriz de fuentes será un componente de arquitectura y no una simple lista de URLs.

Cada fuente deberá tener una función definida dentro del modelo `SOURCE → EVIDENCE → CLAIM → EVENT`.

### 29.6 Estrategia de implementación

No se implementarán todas las fuentes simultáneamente.

La primera iteración OSINT se centrará en:

```text
USGS
GDACS
GDELT
```

El objetivo será demostrar que el sistema puede:

1. consultar una fuente;
2. normalizar su información;
3. registrar la fuente y la evidencia;
4. evitar duplicados;
5. asociar países y localizaciones cuando proceda;
6. mantener trazabilidad;
7. diferenciar detección de corroboración;
8. generar o actualizar EVENT de forma controlada.

Una vez validado este circuito, se incorporarán progresivamente las fuentes restantes.

La incorporación de nuevas fuentes no deberá exigir modificar el núcleo conceptual de `SOURCE`, `EVIDENCE`, `CLAIM` y `EVENT`.


## 30. Testing

La V1 deberá incluir tests automatizados para:

- scoring;
- normalización;
- event lifecycle;
- deduplicación;
- API;
- consultas críticas.

Los tests serán parte integral del desarrollo.

## 31. Seguridad

La V1 no requerirá autenticación de usuarios.

Se deberán aplicar:

- validación de inputs;
- parametrización SQL;
- protección frente a XSS;
- control de CORS;
- manejo seguro de errores;
- validación de payloads.

Las claves y credenciales de APIs externas, cuando existan, nunca se almacenarán en el repositorio.

## 32. Rendimiento

La V1 priorizará:

- carga rápida en móvil;
- baja transferencia de datos;
- consultas indexadas;
- paginación;
- consultas geográficas eficientes.

El objetivo es mantener tiempos de respuesta bajos para operaciones habituales.

## 33. Desarrollo incremental

El proyecto se desarrollará por iteraciones.

Cada iteración deberá:

```text
1. definir
2. implementar
3. probar
4. validar
5. documentar
```

No se incorporará complejidad antes de que la capa anterior sea estable.

## 34. Decisiones abiertas

Quedan deliberadamente abiertas para fases posteriores:

- ingestión automática;
- número exacto de fuentes OSINT;
- integración de datos satelitales;
- aviación;
- marítimo;
- interdependencia;
- notificaciones;
- usuarios;
- IA auxiliar;
- modelización histórica avanzada.

Estas decisiones no deberán bloquear la V1 básica.

## 35. Filosofía del sistema

STATION V no pretende conocer todos los acontecimientos del mundo.

Pretende identificar y estructurar aquellos acontecimientos que sean suficientemente relevantes para responder:

> ¿Qué está ocurriendo?
>
> ¿Dónde?
>
> ¿Con qué gravedad?
>
> ¿Puede escalar?
>
> ¿Qué evidencia lo sustenta?
>
> ¿Qué efecto tiene sobre el riesgo del país?

El sistema priorizará:

```text
Calidad

sobre

Cantidad
```

```text
Trazabilidad

sobre

Opacidad
```

```text
Señal

sobre

Ruido
```

---

# FIN DE LA ESPECIFICACIÓN V1
