# STATION V — Risk Scoring Rules V1.2

**Estado:** Regla normativa V1.2 para implementación
**Ámbito:** RiskImpact → presión de eventos → Subindicator
**Complementa:** Metodología matemática OSINT Geopolítica V1.2 y Event Model V1.1

## 1. Saturación de presión

La presión de eventos se calcula a partir de la suma de impactos efectivos válidos:

```text
P = 100 × (1 - exp(-Σ I_effective / K))
```

con:

```text
K = 3.0
```

La suma de `I_effective` es el acumulador intermedio; `P` es la presión final y queda limitada al intervalo 0–100.

Cada impacto efectivo se calcula como:

```text
I_effective = I_base × R × W_t × W_r
```

La saturación se aplica después de calcular los impactos individuales.

## 2. Principio de repetición

La repetición reduce la contribución de acontecimientos distintos pero equivalentes o altamente correlacionados. No se utiliza el número de noticias, evidencias ni actualizaciones de un mismo EVENT como medida de repetición.

La unidad de análisis es:

```text
país + subindicador + acontecimiento subyacente
```

## 3. Duplicados

Un EVENT relacionado mediante `duplicate_of` con otro EVENT no constituye un acontecimiento adicional para el scoring.

El duplicado se conserva para trazabilidad, pero no genera una segunda contribución de riesgo.

## 4. Relaciones válidas para repetición

Las relaciones siguientes pueden activar la consideración de repetición:

- `same_series`;
- `escalates` o equivalente `escalation_of`;
- `continuation_of`;
- `part_of`, únicamente cuando exista pertenencia material a la misma secuencia/ fenómeno.

Las relaciones siguientes **no activan por sí solas** un descuento de repetición:

- `related_to`;
- `preceded_by`;
- `followed_by`;
- `caused_by`.

Una relación semántica general no es suficiente para declarar dos acontecimientos como repetidos.

## 5. Condiciones para formar una secuencia

Un EVENT solo se considera parte de una secuencia de repetición para un `RiskImpact` concreto cuando:

1. representa un acontecimiento distinto y no un duplicado;
2. afecta al mismo país para el `RiskImpact` evaluado;
3. afecta al mismo subindicador;
4. existe una relación válida de repetición entre los acontecimientos;
5. el acontecimiento anterior se encuentra dentro de la ventana de contexto de 7 días;
6. la relación representa una secuencia o correlación material del fenómeno y no únicamente una relación contextual.

Si cualquiera de estas condiciones no se cumple, el multiplicador de repetición es `1.00`.

## 6. Multiplicadores

Los acontecimientos de una secuencia se ordenan por el momento en que ocurrieron, no por el momento en que fueron publicados o ingeridos.

| Posición | `W_r` |
|---:|---:|
| 1.º | 1.00 |
| 2.º | 0.60 |
| 3.º | 0.35 |
| 4.º | 0.20 |
| 5.º y posteriores | 0.10 |

Estos multiplicadores se aplican al `RiskImpact` correspondiente, no globalmente a todo el EVENT.

## 7. Acontecimientos independientes

Los acontecimientos cualitativamente distintos e independientes no reciben descuento por repetición aunque ocurran en el mismo país y dentro de la misma ventana temporal.

Por ejemplo, una protesta, un terremoto y un incidente fronterizo no constituyen automáticamente una secuencia de repetición.

Cada uno puede contribuir con `W_r = 1.00` en los subindicadores que correspondan.

## 8. Escaladas

Una escalada o continuación puede formar parte de la misma secuencia y recibir el multiplicador correspondiente a su posición. Esto no limita la severidad ni el `I_base` que corresponda al nuevo acontecimiento.

Por tanto, un acontecimiento posterior más grave puede aportar un impacto superior aunque reciba un `W_r` inferior.

## 9. Incertidumbre

Cuando no exista evidencia suficiente para determinar que dos acontecimientos son equivalentes o altamente correlacionados, no se aplicará descuento.

```text
correlación no demostrada → W_r = 1.00
```

Se prioriza evitar la reducción artificial de riesgo frente a inferir correlaciones no demostradas.

## 10. Secuencia completa de cálculo

```text
EVENT
  ↓
RiskImpact
  ↓
comprobar duplicate_of
  ↓
identificar país + subindicador
  ↓
buscar acontecimientos correlacionados en 7 días
  ↓
ordenar cronológicamente
  ↓
asignar W_r
  ↓
I_effective = I_base × R × W_t × W_r
  ↓
Σ I_effective
  ↓
P = 100 × (1 - exp(-Σ I_effective / 3.0))
  ↓
Subindicator
```

## 11. Restricción de implementación V1.2

No se implementará todavía una detección automática de correlación basada únicamente en similitud textual, proximidad geográfica o coincidencia temporal.

La implementación deberá utilizar relaciones de EVENT suficientemente consolidadas. Una futura versión podrá incorporar reglas automáticas adicionales cuando hayan sido definidas y validadas metodológicamente.
