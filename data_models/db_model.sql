CREATE DATABASE monitoring_events;
USE monitoring_events;
DROP TABLE IF EXISTS client_metrics;

CREATE TABLE `client_metrics` (
  `id`                INT          NOT NULL AUTO_INCREMENT,
  `ip`                VARCHAR(600) NOT NULL,
  `metrics`           TEXT(60000),
  `metrics_timestamp` TIMESTAMP    NOT NULL,
  `update_time`       TIMESTAMP             DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`, `ip`, `metrics_timestamp`)
);

COMMIT;