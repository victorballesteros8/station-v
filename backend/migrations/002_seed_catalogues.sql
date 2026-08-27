-- STATION V
-- Migration 002: methodology subindicator catalogue
-- Source: Metodologia matematica OSINT Geopolitica V1.1

BEGIN;

INSERT INTO subindicators (id, dimension_id, code, name, weight, description)
VALUES
(1,1,'protests_mobilization','Protestas y movilización social',0.2000,'Protestas y movilización social.'),
(2,1,'public_order_disturbance','Disturbios / alteración del orden público',0.2000,'Disturbios y alteración del orden público.'),
(3,1,'political_violence','Violencia política',0.1500,'Violencia política.'),
(4,1,'terrorism_internal_insurgency','Terrorismo / insurgencia interna',0.1500,'Terrorismo e insurgencia interna.'),
(5,1,'institutional_crisis','Crisis institucional',0.1500,'Crisis institucional.'),
(6,1,'intergroup_violence','Violencia entre grupos',0.1000,'Violencia entre grupos.'),
(7,1,'strikes_social_disruption','Huelgas / disrupción social',0.0500,'Huelgas y disrupción social.'),
(8,2,'active_armed_conflicts','Conflictos armados activos',0.2500,'Conflictos armados activos.'),
(9,2,'armed_clashes','Enfrentamientos / violencia armada',0.2000,'Enfrentamientos y violencia armada.'),
(10,2,'attacks_on_civilians','Ataques contra población',0.1500,'Ataques contra población.'),
(11,2,'terrorism','Terrorismo',0.1000,'Terrorismo.'),
(12,2,'insurgency_irregular_warfare','Insurgencia / guerra irregular',0.1000,'Insurgencia y guerra irregular.'),
(13,2,'human_impact_casualties','Impacto humano / víctimas',0.1000,'Impacto humano y víctimas.'),
(14,2,'geographic_extent','Extensión geográfica',0.0500,'Extensión geográfica.'),
(15,2,'conflict_persistence','Persistencia del conflicto',0.0500,'Persistencia del conflicto.'),
(16,3,'border_incidents','Incidentes fronterizos',0.2000,'Incidentes fronterizos.'),
(17,3,'territorial_disputes','Disputas territoriales',0.1500,'Disputas territoriales.'),
(18,3,'diplomatic_crises','Crisis diplomáticas',0.1500,'Crisis diplomáticas.'),
(19,3,'threats_official_rhetoric','Amenazas / retórica oficial',0.1000,'Amenazas y retórica oficial.'),
(20,3,'sanctions','Sanciones',0.1000,'Sanciones.'),
(21,3,'foreign_intervention_involvement','Intervención / implicación extranjera',0.1500,'Intervención o implicación extranjera.'),
(22,3,'alliances_bloc_relations','Relaciones con aliados y bloques',0.1000,'Relaciones con aliados y bloques.'),
(23,3,'international_isolation_deterioration','Aislamiento / deterioro internacional',0.0500,'Aislamiento y deterioro internacional.'),
(24,4,'mobilization','Movilización',0.2000,'Movilización militar.'),
(25,4,'troop_deployments_movements','Despliegues / movimientos de tropas',0.2000,'Despliegues y movimientos de tropas.'),
(26,4,'border_military_activity','Actividad militar fronteriza',0.1500,'Actividad militar fronteriza.'),
(27,4,'air_activity','Actividad aérea',0.1000,'Actividad aérea.'),
(28,4,'naval_activity','Actividad naval',0.1000,'Actividad naval.'),
(29,4,'anomalous_military_exercises','Ejercicios militares anómalos',0.1000,'Ejercicios militares anómalos.'),
(30,4,'weapons_employment','Empleo de armamento',0.1000,'Empleo de armamento.'),
(31,4,'military_preparation_posture','Preparación / postura militar',0.0500,'Preparación y postura militar.'),
(32,5,'economic_situation','Situación económica',0.2000,'Situación económica.'),
(33,5,'humanitarian_crisis','Crisis humanitaria',0.1500,'Crisis humanitaria.'),
(34,5,'food_security','Seguridad alimentaria',0.1000,'Seguridad alimentaria.'),
(35,5,'energy','Energía',0.1000,'Energía.'),
(36,5,'population_displacement','Desplazamientos de población',0.1000,'Desplazamientos de población.'),
(37,5,'essential_services','Servicios esenciales',0.1000,'Servicios esenciales.'),
(38,5,'social_pressure','Presión social',0.1000,'Presión social.'),
(39,5,'institutional_capacity','Capacidad institucional',0.1000,'Capacidad institucional.'),
(40,5,'disasters_environmental_vulnerability','Desastres / vulnerabilidad ambiental',0.0500,'Desastres y vulnerabilidad ambiental.')
ON CONFLICT (id) DO NOTHING;

DO $$
DECLARE
    total_weight NUMERIC(6,4);
BEGIN
    FOR total_weight IN
        SELECT COALESCE(SUM(weight),0)
        FROM subindicators
        WHERE active = TRUE
        GROUP BY dimension_id
    LOOP
        IF total_weight <> 1.0000 THEN
            RAISE EXCEPTION 'Invalid subindicator weight total: %', total_weight;
        END IF;
    END LOOP;
END;
$$;

COMMIT;
