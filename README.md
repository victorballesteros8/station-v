# STATION V

*Inteligencia geopolítica de código abierto*

STATION V es una aplicación OSINT de *situational awareness* geopolítico basada en acontecimientos, evidencias y evaluación estructurada del riesgo país.

## Estado

**MVP en desarrollo — V1**

## Objetivo

La primera versión busca ofrecer una visión rápida y trazable de la situación geopolítica mediante:

- un mapa mundial interactivo;
- acontecimientos geopolíticos estructurados;
- Country Risk y sus cinco dimensiones;
- evolución del riesgo a 24 horas;
- acontecimientos ordenados por potencial de escalada;
- búsqueda de países y acontecimientos;
- trazabilidad hacia evidencias y fuentes.

## Documentación

- [`TECHNICAL_SPEC_V1.md`](TECHNICAL_SPEC_V1.md) — especificación técnica de la V1.
- `docs/` — documentación de arquitectura, metodología y API.

## Estructura inicial

```text
station-v/
├── README.md
├── TECHNICAL_SPEC_V1.md
├── LICENSE
├── .gitignore
├── docs/
├── frontend/
├── backend/
└── data/
```

## Principio de desarrollo

La V1 prioriza rigor, coherencia, trazabilidad y funcionamiento antes que amplitud de funcionalidades.

La metodología y el modelo de datos deberán mantenerse separados de las decisiones de presentación de la aplicación.
