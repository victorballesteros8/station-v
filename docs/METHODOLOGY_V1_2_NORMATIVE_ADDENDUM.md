# STATION V — Metodología matemática V1.2

## Addendum normativo

**Estado:** Normativa operativa V1.2
**Ámbito:** Risk Impact → Subindicator → Dimension → Country Risk

Este documento formaliza las reglas de V1.2 que deben prevalecer sobre cualquier implementación anterior de V1.1 cuando exista discrepancia.

## 1. Saturación de la presión de eventos

La presión de eventos se calcula mediante:

```text
P = 100 × (1 - exp(-Σ I_effective / K))
```

con:

```text
K = 3.0
```

`Σ I_effective` es la suma de los impactos efectivos válidos. La suma continúa siendo el acumulador intermedio; la presión final es la función saturada.

La saturación se aplica después de calcular:

```text
I_effective = I_base × R × W_t × W_r
```

La presión queda limitada al intervalo 0–100.

## 2. Repetición y correlación

La reducción por repetición solo se aplica entre EVENT distintos que formen una secuencia sustancialmente correlacionada.

### 2.1 Duplicados

Un EVENT relacionado mediante `duplicate_of` no genera una nueva contribución de riesgo. Se conserva para trazabilidad.

### 2.2 Relaciones válidas

Pueden activar una secuencia de repetición:

- `same_series`
- `escalates`
- `continuation_of`
- `part_of`, cuando proceda y exista una relación material con el mismo fenómeno

No activan por sí solas una reducción:

- `related_to`
- `preceded_by`
- `followed_by`
- `caused_by`

### 2.3 Condiciones acumulativas

Para considerar un EVENT como repetición deben cumplirse simultáneamente:

1. representa un acontecimiento distinto;
2. afecta al mismo país analizado;
3. existe una relación válida de correlación;
4. genera impacto sobre el mismo subindicador;
5. se encuentra dentro de la ventana de contexto de 7 días.

La secuencia se ordena por el momento de ocurrencia del acontecimiento, no por publicación de noticias o evidencias.

### 2.4 Multiplicadores

```text
1.º  → 1.00
2.º  → 0.60
3.º  → 0.35
4.º  → 0.20
5.º+ → 0.10
```

Si no existe evidencia suficiente para establecer correlación, se utiliza `W_r = 1.00`.

No se permite inferir correlación mediante similitud textual, proximidad geográfica o coincidencia temporal por sí solas.

La reducción se aplica a nivel de `RiskImpact`: un mismo EVENT puede recibir multiplicadores diferentes para distintos países o subindicadores.

Una escalada mantiene su evaluación propia de severidad e intensidad. El descuento por repetición no sustituye esa evaluación.

Los acontecimientos cualitativamente distintos e independientes pueden acumularse sin reducción específica por repetición.

## 3. Orden normativo completo

Para cada `RiskImpact` válido:

```text
1. Determinar I_base dentro del rango permitido por severity.
2. Determinar R (relevance).
3. Calcular W_t (half-life = 48 h).
4. Determinar W_r según la regla de repetición.
5. Calcular I_effective.
6. Sumar los I_effective válidos.
7. Aplicar saturación con K = 3.0.
8. Utilizar la presión resultante para actualizar el subindicador.
9. Agregar subindicadores a dimensiones y dimensiones a Country Risk.
```

## 4. Compatibilidad con V1.1

Estas reglas no modifican:

- las cinco dimensiones;
- los pesos de dimensiones y subindicadores;
- los rangos de Base Impact por severity;
- los valores de Relevance;
- la semivida temporal de 48 horas;
- la ventana de contexto de 7 días;
- la separación entre Trend y Confidence y el Country Risk.

Su finalidad es resolver dos ambigüedades de implementación de V1.1: la fórmula normativa de saturación y la aplicación de los multiplicadores de repetición.
