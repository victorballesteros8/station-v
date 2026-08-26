# STATION V

## Technical Specification — V1

**Producto:** STATION V  
**Subtítulo:** Inteligencia geopolítica de código abierto  
**Versión:** V1  
**Estado:** Especificación técnica inicial para desarrollo

---

## 1. Objetivo

Esta especificación define la arquitectura técnica mínima necesaria para implementar la V1 funcional de STATION V.

La V1 será una aplicación móvil de *situational awareness* geopolítico basada en información OSINT estructurada.

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

- Aplicación móvil.
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
       Aplicación móvil                  API REST
              │                             │
       Interactive Map                 Domain Logic
       Situation                       Risk Engine
       Search                          Event Logic
       Country Panel                   Evidence Logic
       Event Panel                         │
              │                            ▼
              │                       PostgreSQL
              │                        + PostGIS
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

## 5. Stack tecnológico

Estas son decisiones técnicas del proyecto, no elementos establecidos por los documentos metodológicos.

### Frontend

- React Native
- Expo
- TypeScript

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
- tests de TypeScript/React Native para frontend

El stack podrá modificarse posteriormente si la experiencia durante el desarrollo demuestra que existe una alternativa claramente superior, pero no se cambiará durante la construcción del MVP salvo necesidad justificada.

## 6. Aplicación móvil

La aplicación tendrá tres áreas principales:

```text
🌍 MAPA
📊 SITUACIÓN
🔎 BUSCAR
```

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

Cada categoría tendrá icono, representación cromática, nombre legible y clave interna.

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

Contendrá cuatro paneles:

### 10.1 Mayor Country Risk

Ranking de países por Country Risk descendente.

### 10.2 Mayor deterioro · 24 h

Países con mayor Trend positivo.

### 10.3 Mayor mejora · 24 h

Países con mayor Trend negativo.

### 10.4 Eventos más relevantes

Eventos Alta/Crítica ordenados por Escalation Score descendente.

No se incluirá todavía un ranking regional.

## 11. Búsqueda

La búsqueda permitirá:

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
```

El EVENT deberá ser versionable y los duplicados conservarán su relación mediante `duplicate_of`.

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

## 21. Motor de scoring

El motor implementará las reglas oficiales de V1.1.

### Ventana temporal

7 días.

### Decaimiento

Semivida de 48 horas:

```text
W_t = 2^(-t/48)
```

### Repetición

```text
1.º  1.00
2.º  0.60
3.º  0.35
4.º  0.20
5.º+ 0.10
```

### Presión acumulada

```text
P = Σ I_effective
```

### Estado del subindicador

```text
S_t = 0.65 × S_(t-1) + 0.35 × S_events
```

### Country Risk

```text
CRS = 0.25 I + 0.25 C + 0.20 T + 0.15 M + 0.15 P
```

## 22. Trend

Trend será independiente del Country Risk.

```text
Trend_24h = CRS_t - CRS_(t-24h)
```

Trend no se incluirá como componente adicional del Country Risk.

## 23. Confidence

Confidence:

```text
High
Medium
Low
```

Será independiente del score y no actuará como multiplicador matemático.

La confianza dependerá de factores relacionados con calidad de fuentes, independencia, corroboración, fuentes primarias, consistencia, antigüedad y contradicciones.

## 24. API

La API será REST y versionada.

Prefijo:

```text
/api/v1
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

### País

```http
GET /api/v1/countries/{country_id}
```

### Evento

```http
GET /api/v1/events/{event_id}
```

### Situación

```http
GET /api/v1/situation
```

Respuesta lógica:

```text
top_country_risk
top_deterioration
top_improvement
top_events
```

### Búsqueda

```http
GET /api/v1/search?q=
```

## 25. Estructura del frontend

```text
frontend/
│
├── app/
│
├── screens/
│   ├── MapScreen
│   ├── SituationScreen
│   └── SearchScreen
│
├── panels/
│   ├── CountryPanel
│   └── EventPanel
│
├── map/
│   ├── MapView
│   ├── EventMarker
│   └── EventCluster
│
├── components/
├── services/
│   └── api/
├── types/
└── assets/
```

## 26. Estructura del backend

```text
backend/
│
├── app/
│   ├── api/
│   │   ├── map.py
│   │   ├── countries.py
│   │   ├── events.py
│   │   ├── situation.py
│   │   └── search.py
│   │
│   ├── models/
│   ├── schemas/
│   ├── services/
│   │   ├── events/
│   │   ├── evidence/
│   │   └── risk/
│   │
│   ├── scoring/
│   │   ├── impacts.py
│   │   ├── temporal.py
│   │   ├── repetition.py
│   │   ├── dimensions.py
│   │   └── country_risk.py
│   │
│   └── database/
│
└── tests/
```

## 27. Seed Data

Antes de conectar fuentes reales se utilizará un dataset controlado.

Objetivo inicial:

```text
10–20 países
20–30 acontecimientos
varias evidencias por acontecimiento
claims asociados
impactos sobre subindicadores
snapshots de Country Risk
```

El seed dataset no representará información OSINT real destinada a producción.

## 28. Ingestión OSINT

La ingestión automática queda fuera del primer MVP.

La arquitectura reservará una capa independiente:

```text
ingestion/
├── sources/
├── normalizers/
├── evidence/
├── corroboration/
└── event_matching/
```

Posteriormente se podrán incorporar fuentes T0–T4.

## 29. Docker

Desarrollo local:

```text
docker-compose
│
├── postgres
│   └── postgis
│
└── backend
```

El frontend se ejecutará inicialmente mediante Expo.

## 30. Testing

El MVP deberá contar con tests para:

### Scoring

- decaimiento temporal;
- repetición;
- relevancia;
- agregación de subindicadores;
- dimensiones;
- Country Risk;
- Trend.

### Datos

- relaciones Event/Country;
- Evidence/Claim;
- duplicados;
- versionado.

### API

- respuestas correctas;
- filtros;
- errores.

### Frontend

- navegación;
- selección de país;
- selección de evento;
- apertura/cierre de paneles;
- búsqueda.

## 31. Milestones

### M0 — Repository

Crear la estructura inicial del repositorio y documentación base.

### M1 — Database

Implementar PostgreSQL/PostGIS y las entidades principales.

### M2 — Scoring

Implementar metodología V1.1 con tests matemáticos.

### M3 — API

Implementar los endpoints principales.

### M4 — Mobile shell

Crear navegación, tres pestañas y componentes base.

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

## 32. Criterio de finalización del MVP

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

## 33. Límites metodológicos

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

## 34. Principio de extensibilidad

La V1 deberá ser pequeña, pero el núcleo de datos no deberá ser desechable.

La arquitectura deberá poder incorporar posteriormente aviación, marítimo, satélite, infraestructura, energía, OSINT social, nuevas fuentes, nuevos subindicadores, nuevas categorías y nuevas señales OSINT.

## 35. Regla final de desarrollo

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

## 36. Decisión técnica pendiente: motor de mapa

La especificación funcional exige un mapa vectorial interactivo con zoom, desplazamiento, clustering y geometrías de países.

La tecnología concreta del motor de mapas queda pendiente de decisión antes de implementar M5. Deberá evaluarse su compatibilidad con React Native/Expo, rendimiento, mapas vectoriales y gestión de tiles.
