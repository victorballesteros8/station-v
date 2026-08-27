-- STATION V
-- Migration 003: V1 country catalogue
-- The country universe is defined by STATION V, not by Natural Earth.
-- ISO 3166-1 alpha-2/alpha-3 are used as identifiers where officially assigned.
-- The UN currently has 193 Member States. Palestine is included as an observer
-- state. Kosovo and Taiwan are included as special analytical entities; XK/XKX
-- for Kosovo is a user-assigned convention, not an official ISO assignment.
-- Natural Earth supplies geometry separately through the importer.

BEGIN;

ALTER TABLE countries
    ADD COLUMN IF NOT EXISTS status VARCHAR(20) NOT NULL DEFAULT 'active';

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'countries_status_valid'
    ) THEN
        ALTER TABLE countries
            ADD CONSTRAINT countries_status_valid
            CHECK (status IN ('active', 'special'));
    END IF;
END $$;

DELETE FROM countries;

INSERT INTO countries (iso2, iso3, name, status) VALUES
('AF','AFG','Afghanistan','active'),('AL','ALB','Albania','active'),('DZ','DZA','Algeria','active'),('AD','AND','Andorra','active'),('AO','AGO','Angola','active'),
('AG','ATG','Antigua and Barbuda','active'),('AR','ARG','Argentina','active'),('AM','ARM','Armenia','active'),('AU','AUS','Australia','active'),('AT','AUT','Austria','active'),
('AZ','AZE','Azerbaijan','active'),('BS','BHS','Bahamas','active'),('BH','BHR','Bahrain','active'),('BD','BGD','Bangladesh','active'),('BB','BRB','Barbados','active'),
('BY','BLR','Belarus','active'),('BE','BEL','Belgium','active'),('BZ','BLZ','Belize','active'),('BJ','BEN','Benin','active'),('BT','BTN','Bhutan','active'),
('BO','BOL','Bolivia','active'),('BA','BIH','Bosnia and Herzegovina','active'),('BW','BWA','Botswana','active'),('BR','BRA','Brazil','active'),('BN','BRN','Brunei','active'),
('BG','BGR','Bulgaria','active'),('BF','BFA','Burkina Faso','active'),('BI','BDI','Burundi','active'),('CV','CPV','Cabo Verde','active'),('KH','KHM','Cambodia','active'),
('CM','CMR','Cameroon','active'),('CA','CAN','Canada','active'),('CF','CAF','Central African Republic','active'),('TD','TCD','Chad','active'),('CL','CHL','Chile','active'),
('CN','CHN','China','active'),('CO','COL','Colombia','active'),('KM','COM','Comoros','active'),('CG','COG','Congo','active'),('CR','CRI','Costa Rica','active'),
('CI','CIV','Côte d''Ivoire','active'),('HR','HRV','Croatia','active'),('CU','CUB','Cuba','active'),('CY','CYP','Cyprus','active'),('CZ','CZE','Czechia','active'),
('KP','PRK','North Korea','active'),('CD','COD','Democratic Republic of the Congo','active'),('DK','DNK','Denmark','active'),('DJ','DJI','Djibouti','active'),('DM','DMA','Dominica','active'),
('DO','DOM','Dominican Republic','active'),('EC','ECU','Ecuador','active'),('EG','EGY','Egypt','active'),('SV','SLV','El Salvador','active'),('GQ','GNQ','Equatorial Guinea','active'),
('ER','ERI','Eritrea','active'),('EE','EST','Estonia','active'),('SZ','SWZ','Eswatini','active'),('ET','ETH','Ethiopia','active'),('FJ','FJI','Fiji','active'),
('FI','FIN','Finland','active'),('FR','FRA','France','active'),('GA','GAB','Gabon','active'),('GM','GMB','Gambia','active'),('GE','GEO','Georgia','active'),
('DE','DEU','Germany','active'),('GH','GHA','Ghana','active'),('GR','GRC','Greece','active'),('GD','GRD','Grenada','active'),('GT','GTM','Guatemala','active'),
('GN','GIN','Guinea','active'),('GW','GNB','Guinea-Bissau','active'),('GY','GUY','Guyana','active'),('HT','HTI','Haiti','active'),('HN','HND','Honduras','active'),
('HU','HUN','Hungary','active'),('IS','ISL','Iceland','active'),('IN','IND','India','active'),('ID','IDN','Indonesia','active'),('IR','IRN','Iran','active'),
('IQ','IRQ','Iraq','active'),('IE','IRL','Ireland','active'),('IL','ISR','Israel','active'),('IT','ITA','Italy','active'),('JM','JAM','Jamaica','active'),
('JP','JPN','Japan','active'),('JO','JOR','Jordan','active'),('KZ','KAZ','Kazakhstan','active'),('KE','KEN','Kenya','active'),('KI','KIR','Kiribati','active'),
('KW','KWT','Kuwait','active'),('KG','KGZ','Kyrgyzstan','active'),('LA','LAO','Laos','active'),('LV','LVA','Latvia','active'),('LB','LBN','Lebanon','active'),
('LS','LSO','Lesotho','active'),('LR','LBR','Liberia','active'),('LY','LBY','Libya','active'),('LI','LIE','Liechtenstein','active'),('LT','LTU','Lithuania','active'),
('LU','LUX','Luxembourg','active'),('MG','MDG','Madagascar','active'),('MW','MWI','Malawi','active'),('MY','MYS','Malaysia','active'),('MV','MDV','Maldives','active'),
('ML','MLI','Mali','active'),('MT','MLT','Malta','active'),('MH','MHL','Marshall Islands','active'),('MR','MRT','Mauritania','active'),('MU','MUS','Mauritius','active'),
('MX','MEX','Mexico','active'),('FM','FSM','Micronesia','active'),('MD','MDA','Moldova','active'),('MC','MCO','Monaco','active'),('MN','MNG','Mongolia','active'),
('ME','MNE','Montenegro','active'),('MA','MAR','Morocco','active'),('MZ','MOZ','Mozambique','active'),('MM','MMR','Myanmar','active'),('NA','NAM','Namibia','active'),
('NR','NRU','Nauru','active'),('NP','NPL','Nepal','active'),('NL','NLD','Netherlands','active'),('NZ','NZL','New Zealand','active'),('NI','NIC','Nicaragua','active'),
('NE','NER','Niger','active'),('NG','NGA','Nigeria','active'),('MK','MKD','North Macedonia','active'),('NO','NOR','Norway','active'),('OM','OMN','Oman','active'),
('PK','PAK','Pakistan','active'),('PW','PLW','Palau','active'),('PA','PAN','Panama','active'),('PG','PNG','Papua New Guinea','active'),('PY','PRY','Paraguay','active'),
('PE','PER','Peru','active'),('PH','PHL','Philippines','active'),('PL','POL','Poland','active'),('PT','PRT','Portugal','active'),('QA','QAT','Qatar','active'),
('RO','ROU','Romania','active'),('RU','RUS','Russia','active'),('RW','RWA','Rwanda','active'),('KN','KNA','Saint Kitts and Nevis','active'),('LC','LCA','Saint Lucia','active'),
('VC','VCT','Saint Vincent and the Grenadines','active'),('WS','WSM','Samoa','active'),('SM','SMR','San Marino','active'),('ST','STP','Sao Tome and Principe','active'),('SA','SAU','Saudi Arabia','active'),
('SN','SEN','Senegal','active'),('RS','SRB','Serbia','active'),('SC','SYC','Seychelles','active'),('SL','SLE','Sierra Leone','active'),('SG','SGP','Singapore','active'),
('SK','SVK','Slovakia','active'),('SI','SVN','Slovenia','active'),('SB','SLB','Solomon Islands','active'),('SO','SOM','Somalia','active'),('ZA','ZAF','South Africa','active'),
('KR','KOR','South Korea','active'),('SS','SSD','South Sudan','active'),('ES','ESP','Spain','active'),('LK','LKA','Sri Lanka','active'),('SD','SDN','Sudan','active'),
('SR','SUR','Suriname','active'),('SE','SWE','Sweden','active'),('CH','CHE','Switzerland','active'),('SY','SYR','Syria','active'),('TJ','TJK','Tajikistan','active'),
('TZ','TZA','Tanzania','active'),('TH','THA','Thailand','active'),('TL','TLS','Timor-Leste','active'),('TG','TGO','Togo','active'),('TO','TON','Tonga','active'),
('TT','TTO','Trinidad and Tobago','active'),('TN','TUN','Tunisia','active'),('TR','TUR','Turkey','active'),('TM','TKM','Turkmenistan','active'),('TV','TUV','Tuvalu','active'),
('UG','UGA','Uganda','active'),('UA','UKR','Ukraine','active'),('AE','ARE','United Arab Emirates','active'),('GB','GBR','United Kingdom','active'),('US','USA','United States','active'),
('UY','URY','Uruguay','active'),('UZ','UZB','Uzbekistan','active'),('VU','VUT','Vanuatu','active'),('VE','VEN','Venezuela','active'),('VN','VNM','Vietnam','active'),
('YE','YEM','Yemen','active'),('ZM','ZMB','Zambia','active'),('ZW','ZWE','Zimbabwe','active'),('PS','PSE','Palestine','active'),('XK','XKX','Kosovo','special'),('TW','TWN','Taiwan','special');

DO $$
DECLARE country_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO country_count FROM countries;
    IF country_count <> 196 THEN
        RAISE EXCEPTION 'Expected 196 STATION V country records, got %', country_count;
    END IF;
END $$;

COMMIT;
