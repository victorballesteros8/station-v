# STATION V — Risk Subindicator Mapping V1

**Estado:** Matriz operativa V1 — consolidada
**Ámbito:** EVENT → RiskImpact → Subindicator
**Fuente conceptual:** Event Model V1.1 + Metodología matemática V1.1

## 1. Propósito

Esta matriz define las relaciones operativas permitidas entre los 24 subtipos actualmente definidos en el Event Model V1.1 y los subindicadores de riesgo.

La matriz no sustituye la evaluación del EVENT. Solo se crea un `RiskImpact` cuando los hechos consolidados del EVENT respaldan la relación indicada.

La unidad de análisis es el acontecimiento subyacente, no el número de noticias o evidencias que lo describen.

El Event Model V1.1 fija ocho categorías y los siguientes subtipos iniciales: `armed_clash`, `bombing`, `attack`; `protest`, `riot`, `strike`; `deployment`, `mobilization`, `exercise`; `incursion`, `border_clash`, `territorial_incident`; `coup_attempt`, `institutional_crisis`, `election_violence`; `earthquake`, `flood`, `wildfire`; `blackout`, `infrastructure_attack`, `service_disruption`; `terrorist_attack`, `kidnapping`, `insurgency`.

La matriz es conservadora: una relación no incluida significa que el subtipo no genera por sí mismo ese impacto. Podrá existir impacto mediante otro EVENT o mediante una futura fuente de estado/base del subindicador.

## 2. Relevance

| Código | Valor | Uso |
|---|---:|---|
| `direct` | 1.00 | El acontecimiento constituye directamente el fenómeno representado por el subindicador. |
| `indirect` | 0.50 | El acontecimiento produce una consecuencia relevante y demostrada sobre el subindicador. |
| `residual` | 0.25 | Existe una consecuencia secundaria, demostrada y materialmente relevante. |

`No relevante` = 0.00 y no se crea `RiskImpact`.

Una relación condicional solo se activa si el EVENT contiene hechos consolidados que satisfacen la condición. No se infiere por plausibilidad.

## 3. Base Impact

La severidad determina el rango permitido de `base_impact`:

| Severity | Rango |
|---|---:|
| `info` | 0 |
| `low` | 1–2 |
| `medium` | 3–5 |
| `high` | 6–10 |
| `critical` | 11–20 |

La intensidad del impacto concreto sobre cada subindicador determina la posición dentro del rango:

- `low`: límite inferior.
- `medium`: punto medio redondeado.
- `high`: límite superior.

La intensidad se valora sobre cinco factores: magnitud, extensión, duración/persistencia, consecuencias observables y capacidad de alterar materialmente el estado del subindicador.

No se asigna un valor superior al rango permitido por la severidad del EVENT. Un mismo EVENT puede recibir valores distintos sobre subindicadores distintos.

## 4. Matriz operativa

### 4.1 `conflict_violence`

| Subtype | Subindicador | Relevance | Condición |
|---|---|---:|---|
| `armed_clash` | `armed_clashes` | 1.00 | Enfrentamiento armado consolidado. |
| `armed_clash` | `active_armed_conflicts` | 0.50 | Si forma parte de un conflicto armado activo. |
| `armed_clash` | `human_impact_casualties` | 0.50 | Si existen víctimas/heridos consolidados. |
| `armed_clash` | `geographic_extent` | 0.50 | Si existe extensión material demostrada. |
| `armed_clash` | `conflict_persistence` | 0.50 | Si forma parte de violencia persistente o de una secuencia documentada. |
| `armed_clash` | `border_incidents` | 0.50 | Si ocurre entre actores a través de una frontera o zona fronteriza. |
| `bombing` | `armed_clashes` | 0.50 | Si constituye violencia armada. |
| `bombing` | `attacks_on_civilians` | 0.50 | Si población civil es objetivo o resulta afectada de forma consolidada. |
| `bombing` | `human_impact_casualties` | 0.50 | Si existen víctimas/heridos consolidados. |
| `bombing` | `geographic_extent` | 0.25 | Si existe extensión material demostrada. |
| `bombing` | `weapons_employment` | 0.50 | Si el empleo de armamento constituye actividad militar relevante. |
| `attack` | `attacks_on_civilians` | 1.00 | Si el ataque afecta a población civil. |
| `attack` | `armed_clashes` | 0.50 | Si existe violencia armada organizada. |
| `attack` | `human_impact_casualties` | 0.50 | Si existen víctimas/heridos consolidados. |
| `attack` | `terrorism` | 0.50 | Solo si el EVENT está además clasificado como terrorismo conforme a hechos consolidados. |

### 4.2 `protests_unrest`

| Subtype | Subindicador | Relevance | Condición |
|---|---|---:|---|
| `protest` | `protests_mobilization` | 1.00 | Movilización/protesta consolidada. |
| `protest` | `social_pressure` | 0.50 | Si refleja o genera presión social relevante y demostrada. |
| `protest` | `public_order_disturbance` | 0.50 | Si existen alteraciones del orden público, violencia o disrupciones relevantes. |
| `protest` | `strikes_social_disruption` | 0.50 | Si implica huelga o disrupción social/servicios material. |
| `riot` | `public_order_disturbance` | 1.00 | Disturbio generalizado consolidado. |
| `riot` | `political_violence` | 0.50 | Si existe violencia política identificable. |
| `riot` | `intergroup_violence` | 0.50 | Si la violencia se produce entre grupos identificables. |
| `riot` | `human_impact_casualties` | 0.50 | Si existen víctimas/heridos consolidados. |
| `riot` | `strikes_social_disruption` | 0.25 | Si existe disrupción social/servicios material además del disturbio. |
| `strike` | `strikes_social_disruption` | 1.00 | Huelga consolidada. |
| `strike` | `protests_mobilization` | 0.50 | Si forma parte de una movilización/protesta más amplia. |
| `strike` | `social_pressure` | 0.50 | Si existe presión social relevante y demostrada. |
| `strike` | `essential_services` | 0.50 | Si produce interrupción material de servicios esenciales. |
| `strike` | `institutional_capacity` | 0.25 | Si existe deterioro material de la capacidad institucional. |

### 4.3 `military_activity`

| Subtype | Subindicador | Relevance | Condición |
|---|---|---:|---|
| `deployment` | `troop_deployments_movements` | 1.00 | Despliegue/movimiento militar consolidado. |
| `deployment` | `military_preparation_posture` | 0.50 | Si modifica de forma relevante la postura militar. |
| `deployment` | `border_military_activity` | 0.50 | Si ocurre en zona fronteriza o próxima a ella. |
| `deployment` | `mobilization` | 0.25 | Si forma parte de una movilización más amplia. |
| `mobilization` | `mobilization` | 1.00 | Movilización militar consolidada. |
| `mobilization` | `troop_deployments_movements` | 0.50 | Si implica movimientos/despliegues observables. |
| `mobilization` | `military_preparation_posture` | 0.50 | Si altera de forma relevante la postura militar. |
| `mobilization` | `border_military_activity` | 0.50 | Si está vinculada a una zona fronteriza. |
| `exercise` | `anomalous_military_exercises` | 1.00 | Ejercicio anómalo respecto al patrón normal y suficientemente corroborado. |
| `exercise` | `military_preparation_posture` | 0.50 | Si modifica materialmente preparación/postura. |
| `exercise` | `troop_deployments_movements` | 0.25 | Si implica movimientos/despliegues relevantes fuera de la actividad normal. |
| `exercise` | `border_military_activity` | 0.25 | Si se desarrolla en contexto fronterizo relevante. |

### 4.4 `border_tension`

| Subtype | Subindicador | Relevance | Condición |
|---|---|---:|---|
| `incursion` | `border_incidents` | 1.00 | Incursión fronteriza consolidada. |
| `incursion` | `territorial_disputes` | 0.50 | Si está vinculada a una disputa territorial identificada. |
| `incursion` | `border_military_activity` | 0.50 | Si participan fuerzas militares o existe actividad militar fronteriza. |
| `incursion` | `foreign_intervention_involvement` | 0.25 | Si existe implicación consolidada de un tercer Estado. |
| `border_clash` | `armed_clashes` | 1.00 | Enfrentamiento armado consolidado. |
| `border_clash` | `border_incidents` | 1.00 | Incidente fronterizo consolidado. |
| `border_clash` | `border_military_activity` | 1.00 | Si participan fuerzas militares o existe actividad militar fronteriza. |
| `border_clash` | `human_impact_casualties` | 0.50 | Si existen víctimas/heridos consolidados. |
| `border_clash` | `conflict_persistence` | 0.25 | Si forma parte de una secuencia persistente. |
| `territorial_incident` | `territorial_disputes` | 1.00 | Incidente vinculado a disputa territorial. |
| `territorial_incident` | `border_incidents` | 1.00 | Si constituye un incidente fronterizo. |
| `territorial_incident` | `threats_official_rhetoric` | 0.25 | Si existe retórica oficial de amenaza asociada y consolidada. |
| `territorial_incident` | `diplomatic_crises` | 0.25 | Solo si genera una crisis diplomática material y demostrada. |

### 4.5 `political_crisis`

| Subtype | Subindicador | Relevance | Condición |
|---|---|---:|---|
| `coup_attempt` | `institutional_crisis` | 1.00 | Intento de golpe consolidado. |
| `coup_attempt` | `political_violence` | 0.50 | Si existe violencia/coerción política consolidada. |
| `coup_attempt` | `mobilization` | 0.50 | Si existe movilización militar como parte del intento. |
| `coup_attempt` | `military_preparation_posture` | 0.50 | Si las fuerzas armadas adoptan postura extraordinaria vinculada al intento. |
| `coup_attempt` | `institutional_capacity` | 0.50 | Si existe deterioro material de la capacidad institucional. |
| `institutional_crisis` | `institutional_crisis` | 1.00 | Crisis institucional consolidada. |
| `institutional_crisis` | `institutional_capacity` | 0.50 | Si afecta materialmente al funcionamiento estatal. |
| `institutional_crisis` | `social_pressure` | 0.25 | Si genera presión social demostrada. |
| `institutional_crisis` | `political_violence` | 0.25 | Solo si existe violencia política consolidada. |
| `election_violence` | `political_violence` | 1.00 | Violencia vinculada al proceso electoral. |
| `election_violence` | `institutional_crisis` | 0.50 | Si altera materialmente el proceso o funcionamiento institucional. |
| `election_violence` | `public_order_disturbance` | 0.50 | Si produce alteración relevante del orden público. |
| `election_violence` | `intergroup_violence` | 0.50 | Si se produce entre grupos políticos/sociales identificables. |

### 4.6 `disaster`

| Subtype | Subindicador | Relevance | Condición |
|---|---|---:|---|
| `earthquake` | `disasters_environmental_vulnerability` | 1.00 | Terremoto confirmado. |
| `earthquake` | `human_impact_casualties` | 0.50 | Si existen víctimas/heridos consolidados. |
| `earthquake` | `essential_services` | 0.50 | Si hay interrupción material de servicios esenciales. |
| `earthquake` | `humanitarian_crisis` | 0.50 | Si las consecuencias alcanzan una situación humanitaria relevante y demostrada. |
| `earthquake` | `population_displacement` | 0.50 | Si existen desplazamientos consolidados. |
| `earthquake` | `institutional_capacity` | 0.25 | Si la capacidad de respuesta estatal resulta materialmente afectada. |
| `flood` | `disasters_environmental_vulnerability` | 1.00 | Inundación confirmada. |
| `flood` | `human_impact_casualties` | 0.50 | Si existen víctimas/heridos consolidados. |
| `flood` | `essential_services` | 0.50 | Si hay interrupción material de servicios esenciales. |
| `flood` | `humanitarian_crisis` | 0.50 | Si existe consecuencia humanitaria relevante y demostrada. |
| `flood` | `population_displacement` | 0.50 | Si existen desplazamientos consolidados. |
| `wildfire` | `disasters_environmental_vulnerability` | 1.00 | Incendio forestal confirmado. |
| `wildfire` | `human_impact_casualties` | 0.50 | Si existen víctimas/heridos consolidados. |
| `wildfire` | `population_displacement` | 0.50 | Si existen evacuaciones/desplazamientos consolidados. |
| `wildfire` | `essential_services` | 0.25 | Si existe interrupción material de servicios esenciales. |

### 4.7 `critical_infrastructure`

| Subtype | Subindicador | Relevance | Condición |
|---|---|---:|---|
| `blackout` | `essential_services` | 1.00 | Interrupción relevante del suministro eléctrico/servicios. |
| `blackout` | `energy` | 1.00 | Interrupción material del sistema energético. |
| `blackout` | `institutional_capacity` | 0.25 | Si afecta materialmente a la capacidad estatal. |
| `blackout` | `economic_situation` | 0.25 | Solo con impacto económico material demostrado. |
| `infrastructure_attack` | `essential_services` | 0.50 | Si el ataque interrumpe servicios esenciales. |
| `infrastructure_attack` | `energy` | 0.50 | Si afecta infraestructura energética. |
| `infrastructure_attack` | `economic_situation` | 0.25 | Solo con daño económico material demostrado. |
| `infrastructure_attack` | `political_violence` | 0.25 | Solo si existe violencia política consolidada asociada. |
| `service_disruption` | `essential_services` | 1.00 | Disrupción material de un servicio esencial. |
| `service_disruption` | `institutional_capacity` | 0.50 | Si afecta materialmente a la capacidad institucional. |
| `service_disruption` | `economic_situation` | 0.25 | Solo con impacto económico material demostrado. |
| `service_disruption` | `energy` | 0.50 | Si el servicio afectado pertenece al sistema energético. |

### 4.8 `security_terrorism`

| Subtype | Subindicador | Relevance | Condición |
|---|---|---:|---|
| `terrorist_attack` | `terrorism` | 1.00 | Ataque terrorista consolidado. |
| `terrorist_attack` | `terrorism_internal_insurgency` | 1.00 | Si afecta al entorno interno del país. |
| `terrorist_attack` | `attacks_on_civilians` | 0.50 | Si población civil es objetivo o resulta afectada. |
| `terrorist_attack` | `human_impact_casualties` | 0.50 | Si existen víctimas/heridos consolidados. |
| `terrorist_attack` | `public_order_disturbance` | 0.25 | Si produce una alteración material del orden público. |
| `terrorist_attack` | `political_violence` | 0.25 | Si existe componente de violencia política consolidado. |
| `kidnapping` | `terrorism` | 0.50 | Solo si el secuestro está vinculado de forma consolidada a terrorismo. |
| `kidnapping` | `terrorism_internal_insurgency` | 0.50 | Solo si existe vínculo consolidado con terrorismo/insurgencia interna. |
| `kidnapping` | `political_violence` | 0.25 | Solo si existe coerción/violencia política consolidada. |
| `kidnapping` | `human_impact_casualties` | 0.25 | Solo si existen víctimas/heridos consolidados. |
| `insurgency` | `insurgency_irregular_warfare` | 1.00 | Actividad insurgente consolidada. |
| `insurgency` | `terrorism_internal_insurgency` | 1.00 | Si afecta al entorno interno del país. |
| `insurgency` | `active_armed_conflicts` | 0.50 | Si forma parte de un conflicto armado activo. |
| `insurgency` | `armed_clashes` | 0.50 | Si existen enfrentamientos armados consolidados. |
| `insurgency` | `political_violence` | 0.50 | Si existe violencia política consolidada. |
| `insurgency` | `human_impact_casualties` | 0.50 | Si existen víctimas/heridos consolidados. |
| `insurgency` | `geographic_extent` | 0.50 | Si existe extensión territorial material demostrada. |
| `insurgency` | `conflict_persistence` | 0.50 | Si existe persistencia o continuidad documentada. |

## 5. Subindicadores sin activación directa por los 24 subtipos actuales

La existencia de 40 subindicadores no implica que los 40 deban ser activados por todos los eventos ni que todos tengan que disponer de un subtipo propio en V1.

Con los 24 subtipos actuales, los siguientes subindicadores **no tienen un disparador directo estable** y solo pueden recibir impacto mediante relaciones condicionales de otros eventos o, preferentemente, mediante futuras fuentes de estado/base del subindicador:

- `sanctions`
- `alliances_bloc_relations`
- `international_isolation_deterioration`
- `food_security`

Además, `diplomatic_crises` y `threats_official_rhetoric` solo están cubiertos condicionalmente por `territorial_incident`; esto no equivale a disponer todavía de subtipos específicos de crisis diplomática o amenazas.

Esto **no debe solucionarse inventando mappings** para forzar cobertura 40/40. Si V1 necesita esos factores como señales dinámicas de eventos, habrá que ampliar formalmente el Event Model con nuevos subtipos o incorporar una capa de estado/base de subindicadores.

## 6. Reglas de aplicación

1. El subtype es un selector de relaciones posibles, no una orden automática de crear impactos.
2. Las condiciones se evalúan sobre `canonical_event_data`, `human_impact`, `material_impact`, países afectados y evidencias consolidadas.
3. No se crean impactos por rumores, claims disputados o consecuencias meramente plausibles.
4. Un EVENT puede generar varios `RiskImpact` sobre subindicadores distintos cuando exista relación causal/analítica clara.
5. No se debe duplicar el mismo impacto por varias noticias que describan el mismo EVENT.
6. Los países indirectamente afectados no reciben automáticamente el impacto; debe existir evidencia suficiente de una consecuencia relevante en ese país.
7. `base_impact` se asigna por intensidad del impacto concreto y siempre dentro del rango permitido por la severidad del EVENT.
8. `relevance`, `temporal_weight` y `repetition_weight` se aplican después para obtener `effective_impact`.
9. La repetición se refiere a acontecimientos equivalentes o altamente correlacionados, no a actualizaciones o artículos del mismo EVENT.
10. La matriz no calcula dimensiones ni Country Risk directamente.

## 7. Relación con el scoring

La cadena operativa es:

```text
SOURCE
  ↓
EVIDENCE
  ↓
CLAIM
  ↓
EVENT
  ↓
RiskImpact
  ↓
SUBINDICATOR
  ↓
DIMENSION
  ↓
COUNTRY RISK
```

El impacto efectivo sigue:

```text
I_effective = I_base × R × W_t × W_r
```

La ventana temporal V1 es de 7 días y la semivida es de 48 horas. Los acontecimientos equivalentes o altamente correlacionados utilizan los multiplicadores de repetición definidos en la metodología matemática V1.1.

## 8. Estado y pendientes

Esta matriz consolida el **mapping EVENT → subindicador** para los 24 subtipos actuales. No resuelve por sí sola:

- detección automática de duplicados;
- detección automática de eventos de la misma serie;
- cálculo automático de intensidad `low/medium/high`;
- atribución de actores;
- incorporación de señales de estado/base no derivadas de EVENT;
- nuevos subtipos de sanciones, diplomacia, amenazas, alianzas, aislamiento u otros factores.

Esos puntos requieren reglas adicionales en el Event Model o en la metodología antes de automatizarlos.
