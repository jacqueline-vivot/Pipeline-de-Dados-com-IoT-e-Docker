CREATE OR REPLACE VIEW avg_temp_por_dispositivo AS
SELECT device_id, location, COUNT(*) AS leituras,
       AVG(temperature) AS avg_temp
FROM temperature_readings GROUP BY device_id, location;

CREATE OR REPLACE VIEW leituras_por_hora AS
SELECT CAST(EXTRACT(HOUR FROM observed_at) AS INTEGER) AS hora,
       location, COUNT(*) AS contagem
FROM temperature_readings GROUP BY EXTRACT(HOUR FROM observed_at), location;

CREATE OR REPLACE VIEW temp_max_min_por_dia AS
SELECT CAST(observed_at AS DATE) AS data, location,
       MAX(temperature) AS temp_max, MIN(temperature) AS temp_min,
       AVG(temperature) AS temp_media
FROM temperature_readings GROUP BY CAST(observed_at AS DATE), location;
