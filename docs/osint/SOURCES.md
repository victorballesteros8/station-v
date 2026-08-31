# STATION V — OSINT Sources

Registro central de las fuentes OSINT utilizadas o previstas en STATION V.

Este documento es un índice operativo. La documentación específica de cada fuente se mantiene en su propio archivo dentro de `docs/osint/`.

## Criterio de coste V1

La implementación OSINT V1 deberá poder ejecutarse con un coste de licencias y acceso a fuentes de **0 €**.

La gratuidad no sustituye la revisión de licencias, condiciones de uso, límites técnicos y permisos de cada fuente.

## Fuentes piloto

| Fuente | Estado | Función principal | Coste V1 |
|---|---|---|---:|
| USGS | 🟢 Piloto | Evidencia estructurada de terremotos | 0 € |
| GDACS | 🟢 Piloto | Alertas y contexto de desastres | 0 € |
| GDELT | 🟢 Piloto | Descubrimiento y monitorización de información | 0 € |

## Fuentes previstas

| Fuente | Estado | Función principal | Coste V1 |
|---|---|---|---:|
| UCDP | ⚪ Posterior | Conflicto armado y violencia organizada | 0 € |
| ReliefWeb / OCHA | ⚪ Posterior | Crisis humanitarias y emergencias | 0 € |
| NASA FIRMS | ⚪ Posterior | Observación satelital de actividad térmica e incendios | 0 € |
| Fuentes oficiales gubernamentales | ⚪ Posterior | Evidencia primaria estatal | 0 € |
| Organismos internacionales | ⚪ Posterior | Evidencia institucional internacional | 0 € |

## Fuentes de descubrimiento / corroboración

| Fuente | Estado | Función | Coste V1 |
|---|---|---|---:|
| Reuters | 🟡 Externa | Descubrimiento y/o corroboración cuando exista acceso público y permitido | 0 €* |

`*` Reuters no será una dependencia obligatoria del pipeline automatizado V1. Su uso queda condicionado a las condiciones de acceso y uso aplicables.

## Regla de incorporación

Antes de incorporar una fuente al pipeline OSINT se evaluarán, como mínimo:

- coste;
- licencia y condiciones de uso;
- método de acceso;
- estabilidad del acceso;
- límites de consulta;
- cobertura geográfica y temporal;
- capacidad de detección;
- capacidad de corroboración;
- calidad de los datos;
- independencia respecto de otras fuentes;
- trazabilidad hacia la fuente original.

Cada fuente deberá tener una función definida dentro del modelo:

`SOURCE → EVIDENCE → CLAIM → EVENT`
