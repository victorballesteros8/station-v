# STATION V — Risk Subindicator Mapping V1

**Estado:** Matriz operativa V1
**Ámbito:** EVENT → RiskImpact → Subindicator
**Fuente conceptual:** Event Model V1.1 + Metodología matemática V1.1

## 1. Propósito

Esta matriz define, para los subtipos de EVENT actualmente definidos en el Event Model V1.1, qué subindicadores de riesgo pueden recibir un `RiskImpact` y con qué relevancia por defecto.

La matriz no sustituye la evaluación del EVENT. El sistema solo crea un impacto cuando los hechos consolidados del EVENT respaldan la relación indicada.

La unidad de análisis es el acontecimiento subyacente, no el número de noticias o evidencias que lo describen.

## 2. Relevance

| Código | Valor | Uso |
|---|---:|---|
| `direct` | 1.00 | El acontecimiento constituye directamente el fenómeno representado por el subindicador. |
| `indirect` | 0.50 | El acontecimiento produce una consecuencia relevante y demostrada sobre el subindicador. |
| `residual` | 0.25 | Existe una consecuencia secundaria, demostrada y materialmente relevante, pero no constituye el efecto principal. |

`No relevante` = 0.00 y no se crea `RiskImpact`.

Una relación marcada como `conditional` solo se activa si el EVENT contiene hechos consolidados que satisfacen la condición. No se infiere por plausibilidad.

## 3. Regla general de Base Impact

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
- `medium`: punto medio redondeado al entero más cercano.
- `high`: límite superior.

La intensidad se evalúa sobre cinco factores: magnitud, extensión, duración/persistencia, consecuencias observables y capacidad de alterar materialmente el estado del subindicador.

No se asigna un valor superior al rango de la severidad del EVENT.

Un mismo EVENT puede recibir distintos `base_impact` sobre distintos subindicadores.

## 4. Matriz operativa

### 4.1 conflict_violence

| Subtype | Subindicador | Relevance | Condición |
|---|---|---:|---|
| `armed_clash` | `armed_clashes` | 1.00 | Siempre que el enfrentamiento esté consolidado como hecho. |
| `armed_clash` | `human_impact_casualties` | 0.50 | Solo si existen víctimas/heridos consolidados. |
| `armed_clash` | `geographic_extent` | 0.50 | Solo si el hecho demuestra extensión relevante más allá del punto inicial. |
| `armed_clash` | `conflict_persistence` | 0.50 | Solo si forma parte de violencia persistente o de una secuencia ya documentada. |
| `armed_clash` | `active_armed_conflicts` | 0.50 | Solo si el enfrentamiento forma parte de un conflicto armado activo. |
| `armed_clash` | `border_incidents` | 0.50 | Solo si el enfrentamiento ocurre entre fuerzas/actores a través de una frontera o zona fronteriza. |
| `bombing` | `armed_clashes` | 0.50 | Cuando el bombardeo sea una acción de violencia armada. |
| `bombing` | `attacks_on_civilians` | 0.50 | Si población civil es objetivo o resulta afectada de forma consolidada. |
| `bombing` | `human_impact_casualties` | 0.50 | Si existen víctimas/heridos consolidados. |
| `bombing` | `weapons_employment` | 0.50 | Si el empleo de armamento constituye actividad militar relevante. |
| `bombing` | `geographic_extent` | 0.25 | Solo cuando exista extensión material demostrada. |
| `attack` | `attacks_on_civilians` | 1.00 | Si el ataque afecta a población civil. |
| `attack` | `armed_clashes` | 0.50 | Si existe violencia armada organizada. |
| `attack` | `human_impact_casualties` | 0.50 | Si existen víctimas/heridos consolidados. |
| `attack` | `terrorism` | 0.50 | Solo cuando el EVENT esté clasificado además como terrorismo conforme a sus hechos/atribución. |

### 4.2 protests_unrest

| Subtype | Subindicador | Relevance | Condición |
|---|---|---:|---|
| `protest` | `protests_mobilization` | 1.00 | Siempre que exista una movilización/protesta consolidada. |
| `protest` | `social_pressure` | 0.50 | Si la protesta refleja o genera presión social relevante y demostrada. |
| `protest` | `public_order_disturbance` | 0.50 | Solo si existen alteraciones del orden público, violencia o disrupciones relevantes. |
| `protest` | `strikes_social_disruption` | 0.50 | Solo si la protesta implica huelga o disrupción social/servicios material. |
| `riot` | `public_order_disturbance` | 1.00 | Siempre que el disturbio generalizado esté consolidado. |
| `riot` | `political_violence` | 0.50 | Si existe violencia política identificable. |
| `riot` | `intergroup_violence` | 0.50 | Si la violencia se produce entre grupos identificables. |
| `riot` | `human_impact_casualties` | 0.50 | Si existen víctimas/heridos consolidados. |
| `riot` | `strikes_social_disruption` | 0.25 | Solo si existe disrupción social/servicios material además del disturbio. |
| `strike` | `strikes_social_disruption` | 1.00 | Siempre que exista una huelga consolidada. |
| `strike` | `protests_mobilization` | 0.50 | Si la huelga forma parte de una movilización/protesta social más amplia. |
| `strike` | `social_pressure` | 0.50 | Si existe presión social relevante y demostrada. |
| `strike` | `essential_services` | 0.50 | Si la huelga produce interrupción material de servicios esenciales. |
| `strike` | `institutional_capacity` | 0.25 | Solo si existe evidencia de deterioro material de la capacidad institucional. |

### 4.3 military_activity

| Subtype | Subindicador | Relevance | Condición |
|---|---|---:|---|
| `deployment` | `troop_deployments_movements` | 1.00 | Siempre que exista despliegue/movimiento militar consolidado. |
| `deployment` | `military_preparation_posture` | 0.50 | Si el despliegue modifica de forma relevante la postura militar. |
| `deployment` | `border_military_activity` | 0.50 | Si ocurre en zona fronteriza o próxima a ella. |
| `deployment` | `mobilization` | 0.25 | Solo si el despliegue forma parte de una movilización más amplia. |
| `mobilization` | `mobilization` | 1.00 | Siempre que exista movilización militar consolidada. |
| `mobilization` | `troop_deployments_movements` | 0.50 | Si la movilización implica movimientos/despliegues observables. |
| `mobilization` | `military_preparation_posture` | 0.50 | Si altera de forma relevante la postura militar. |
| `mobilization` | `border_military_activity` | 0.50 | Si la movilización está vinculada a una zona fronteriza. |
| `exercise` | `anomalous_military_exercises` | 1.00 | Si el ejercicio es anómalo respecto al patrón normal y está suficientemente corroborado. |
| `exercise` | `military_preparation_posture` | 0.50 | Si modifica materialmente la preparación/postura militar. |
| `exercise` | `troop_deployments_movements` | 0.25 | Solo si implica movimientos/despliegues relevantes fuera de la actividad normal del ejercicio. |
| `exercise` | `border_military_activity` | 0.25 | Solo si el ejercicio se desarrolla en contexto fronterizo relevante. |

### 4.4 border_tension

| Subtype | Subindicador | Relevance | Condición |
|---|---|---:|---|
| `incursion` | `border_incidents` | 1.00 | Siempre que exista una incursión fronteriza consolidada. |
| `incursion` | `territorial_disputes` | 0.50 | Si la incursión está vinculada a una disputa territorial identificada. |
| `incursion` | `border_military_activity` | 0.50 | Si participan fuerzas militares o existe actividad militar fronteriza. |
| `incursion` | `foreign_intervention_involvement` | 0.25 | Solo si existe implicación de un tercer Estado consolidada. |
| `border_clash` | `armed_clashes` | 1.00 | Si existe enfrentamiento armado consolidado. |
| `border_clash` | `border_incidents` | 1.00 | Siempre que el hecho sea un incidente fronterizo. |
| `border_clash` | `border_military_activity` | 1.00 | Si participan fuerzas militares o existe actividad militar fronteriza. |
| `border_clash` | `human_impact_casualties` | 0.50 | Si existen víctimas/heridos consolidados. |
| `border_clash` | `conflict_persistence` | 0.25 | Si forma parte de una secuencia persistente de enfrentamientos. |
| `territorial_incident` | `territorial_disputes` | 1.00 | Cuando el incidente esté vinculado a una disputa territorial. |
| `territorial_incident` | `border_incidents` | 1.00 | Si constituye un incidente fronterizo. |
| `territorial_incident` | `threats_official_rhetoric` | 0.25 | Si existe retórica oficial de amenaza asociada y consolidada. |
| `territorial_incident` | `diplomatic_crises` | 0.25 | Solo si genera una crisis diplomática material y demostrada. |

### 4.5 political_crisis

| Subtype | Subindicador | Relevance | Condición |
|---|---|---:|---|
| `coup_attempt` | `institutional_crisis` | 1.00 | Siempre que exista intento de golpe consolidado. |
| `coup_attempt` | `political_violence` | 0.50 | Si existe violencia o coerción política consolidada. |
| `coup_attempt` | `mobilization` | 0.50 | Si existe movilización militar como parte del intento. |
| `coup_attempt` | `military_preparation_posture` | 0.50 | Si las fuerzas armadas adoptan una postura extraordinaria vinculada al intento. |
| `coup_attempt` | `institutional_capacity` | 0.50 | Si existe deterioro material de la capacidad institucional. |
| `institutional_crisis` | `institutional_crisis` | 1.00 | Siempre que exista una crisis institucional consolidada. |
| `institutional_crisis` | `institutional_capacity` | 0.50 | Si la crisis afecta materialmente al funcionamiento estatal. |
| `institutional_crisis` | `social_pressure` | 0.25 | Si genera presión social demostrada. |
| `institutional_crisis` | `political_violence` | 0.25 | Solo si existe violencia política consolidada. |
| `election_violence` | `political_violence` | 1.00 | Siempre que exista violencia vinculada al proceso electoral. |
| `election_violence` | `institutional_crisis` | 0.50 | Si la violencia altera materialmente el proceso o funcionamiento institucional. |
| `election_violence` | `public_order_disturbance` | 0.50 | Si produce alteración relevante del orden público. |
| `election_violence` | `intergroup_violence` | 0.50 | Si la violencia se produce entre grupos políticos/sociales identificables. |

### 4.6 disaster

| Subtype | Subindicador | Relevance | Condición |
|---|---|---:|---|
| `earthquake` | `disasters_environmental_vulnerability` | 1.00 | Siempre que el terremoto esté confirmado. |
| `earthquake` | `human_impact_casualties` | 0.50 | Si existen víctimas/heridos consolidados. |
| `earthquake` | `essential_services` | 0.50 | Si hay interrupción material de servicios esenciales. |
| `earthquake` | `humanitarian_crisis` | 0.50 | Si las consecuencias alcanzan una situación humanitaria relevante y demostrada. |
| `earthquake` | `population_displacement` | 0.50 | Si existen desplazamientos consolidados. |
| `earthquake` | `institutional_capacity` | 0.25 | Si la respuesta/capacidad estatal resulta materialmente afectada. |
| `flood` | `disasters_environmental_vulnerability` | 1.00 | Siempre que la inundación esté confirmada. |
| `flood` | `human_impact_casualties` | 0.50 | Si existen víctimas/heridos consolidados. |
| `flood` | `essential_services` | 0.50 | Si hay interrupción material de servicios esenciales. |
| `flood` | `humanitarian_crisis` | 0.50 | Si existe consecuencia humanitaria relevante y demostrada. |
| `flood` | `population_displacement` | 0.50 | Si existen desplazamientos consolidados. |
| `wildfire` | `disasters_environmental_vulnerability` | 1.00 | Siempre que el incendio forestal esté confirmado. |
| `wildfire` | `human_impact_casualties` | 0.50 | Si existen víctimas/heridos consolidados. |
| `wildfire` | `population_displacement` | 0.50 | Si existen evacuaciones/desplazamientos consolidados. |
| `wildfire` | `essential_services` | 0.25 | Si existe interrupción material de servicios esenciales. |

### 4.7 critical_infrastructure

| Subtype | Subindicador | Relevance | Condición |
|---|---|---:|---|
| `blackout` | `essential_services` | 1.00 | Siempre que exista interrupción relevante del suministro eléctrico/servicios. |
| `blackout` | `energy` | 1.00 | Si la interrupción afecta materialmente al sistema energético. |
| `blackout` | `institutional_capacity` | 0.25 | Si afecta de forma material a la capacidad de funcionamiento estatal. |
| `blackout` | `economic_situation` | 0.25 | Solo si existe impacto económico material demostrado. |
| `infrastructure_attack` | `essential_services` | 0.50 | Si el ataque interrumpe servicios esenciales. |
| `infrastructure_attack` | `energy` | 0.50 | Si afecta infraestructura energética. |
| `infrastructure_attack` | `economic_situation` | 0.25 | Si existe daño económico material demostrado. |
| `infrastructure_attack` | `political_violence` | 0.25 | Solo si el ataque constituye violencia política consolidada. |
| `service_disruption` | `essential_services` | 1.00 | Siempre que la disrupción afecte a un servicio esencial. |
| `service_disruption` | `economic_situation` | 0.50 | Si existe impacto económico material demostrado. |
| `service_disruption` | `institutional_capacity` | 0.25 | Si afecta materialmente al funcionamiento institucional. |
| `service_disruption` | `social_pressure` | 0.25 | Si produce presión social relevante y demostrada. |

### 4.8 security_terrorism

| Subtype | Subindicador | Relevance | Condición |
|---|---|---:|---|
| `terrorist_attack` | `terrorism` | 1.00 | Siempre que el acontecimiento esté clasificado como ataque terrorista con base suficiente. |
| `terrorist_attack` | `terrorism_internal_insurgency` | 0.50 | Si forma parte de una campaña terrorista/insurgente interna. |
| `terrorist_attack` | `attacks_on_civilians` | 1.00 | Si la población civil es objetivo o resulta afectada. |
| `terrorist_attack` | `human_impact_casualties` | 0.50 | Si existen víctimas/heridos consolidados. |
| `terrorist_attack` | `public_order_disturbance` | 0.25 | Solo si produce alteración relevante del orden público. |
| `kidnapping` | `terrorism` | 0.25 | Solo si el secuestro forma parte de actividad terrorista. |
| `kidnapping` | `insurgency_irregular_warfare` | 0.25 | Solo si forma parte de una campaña insurgente/guerra irregular. |
| `kidnapping` | `human_impact_casualties` | 0.25 | Si existen daños físicos consolidados; no por el mero hecho del secuestro. |
| `kidnapping` | `political_violence` | 0.50 | Si existe motivación/violencia política consolidada. |
| `insurgency` | `insurgency_irregular_warfare` | 1.00 | Siempre que exista insurgencia consolidada. |
| `insurgency` | `terrorism_internal_insurgency` | 1.00 | Si la insurgencia constituye actividad interna organizada. |
| `insurgency` | `armed_clashes` | 0.50 | Si existe enfrentamiento armado. |
| `insurgency` | `human_impact_casualties` | 0.50 | Si existen víctimas/heridos consolidados. |
| `insurgency` | `conflict_persistence` | 0.50 | Si existe persistencia demostrada de la campaña insurgente. |
| `insurgency` | `geographic_extent` | 0.25 | Si la actividad se extiende materialmente a varias áreas. |

## 5. Reglas de exclusión

1. No se genera `RiskImpact` únicamente porque un subtipo tenga una relación plausible con un subindicador.
2. No se genera impacto sobre un subindicador de consecuencia sin un hecho consolidado que lo sustente.
3. La misma Evidence no genera impactos adicionales por aparecer en varias fuentes.
4. Un EVENT no recibe un impacto por el número de artículos que lo describen.
5. `duplicate_of` no genera un nuevo impacto independiente.
6. Una actualización del mismo EVENT no se considera automáticamente una nueva ocurrencia.
7. Un país indirectamente afectado no recibe Country Risk automáticamente; debe existir evidencia suficiente de una consecuencia relevante.
8. `base_impact = 0` implica ausencia de impacto y no debe producir un RiskImpact operativo.

## 6. Repetición y series

La matriz no decide por sí sola la repetición. Los multiplicadores `1.00 / 0.60 / 0.35 / 0.20 / 0.10` se aplican a acontecimientos equivalentes o altamente correlacionados, no a artículos ni a actualizaciones del timeline.

Las relaciones `same_series`, `escalates`, `part_of` y `duplicate_of` deberán utilizarse posteriormente para construir la lógica de agrupación/correlación. La detección automática completa de correlación queda fuera de esta matriz.

## 7. Ejemplo canónico

`border_tension / border_clash`, severidad `high`:

```text
armed_clashes              relevance 1.00
border_incidents           relevance 1.00
border_military_activity   relevance 1.00
human_impact_casualties    relevance 0.50  [solo con víctimas]
conflict_persistence       relevance 0.25  [solo si existe persistencia]
```

La intensidad concreta de cada impacto se evalúa independientemente dentro del rango `6–10` de una severidad `high`.

## 8. Estado y mantenimiento

Esta matriz debe considerarse parte de la configuración metodológica de V1 para el tramo EVENT → RiskImpact. Cualquier nuevo subtype deberá añadir su entrada antes de utilizarse para scoring automático.

Si una implementación práctica demuestra que un subtype no puede mapearse de forma coherente a los subindicadores existentes, se detendrá el desarrollo del scoring y se actualizará primero esta especificación y, cuando corresponda, el Event Model.
