USE `scoring`;
SET foreign_key_checks = 0;

DROP TABLE IF EXISTS `settings`;
CREATE TABLE `settings` ( 
    `id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `skey` VARCHAR(255) NOT NULL,
    `value` VARCHAR(255) NOT NULL);

DROP TABLE IF EXISTS `systems`;
CREATE TABLE `systems` (
    `system` VARCHAR(255) NOT NULL PRIMARY KEY);

DROP TABLE IF EXISTS `team`;
CREATE TABLE `team` (
    `id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(255) NOT NULL UNIQUE,
    `subnet` VARCHAR(15) NOT NULL,
    `netmask` VARCHAR(15) NOT NULL,
    `vapp` VARCHAR(255) NOT NULL UNIQUE);
        
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(255),
    `password` CHAR(60) NOT NULL,
    `team_id` INT,
    `is_admin` BOOL NOT NULL,
    FOREIGN KEY (`team_id`) REFERENCES `team`(`id`)
        ON DELETE CASCADE);
    
DROP TABLE IF EXISTS `service`;
CREATE TABLE `service` (
    `id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `host` INT NOT NULL,
    `port` INT NOT NULL);

DROP TABLE IF EXISTS `service_check`;
CREATE TABLE `service_check` (
    `id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(255) NOT NULL UNIQUE,
    `check_function` VARCHAR(255) NOT NULL,
    `poller` VARCHAR(255) NOT NULL,
    `service_id` INT NOT NULL,
    FOREIGN KEY (`service_id`) REFERENCES `service`(`id`)
        ON DELETE CASCADE);

DROP TABLE IF EXISTS `domain`;
CREATE TABLE `domain` (
    `id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `fqdn` VARCHAR(256) NOT NULL UNIQUE);

DROP TABLE IF EXISTS `check_io`;
CREATE TABLE `check_io` (
    `id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `input` VARCHAR(4095) NOT NULL,
    `expected` VARCHAR(4095) NOT NULL,
    `check_id` INT NOT NULL,
    FOREIGN KEY (`check_id`) REFERENCES `service_check`(`id`)
        ON DELETE CASCADE);

DROP TABLE IF EXISTS `credential`;
CREATE TABLE `credential` (
    `id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(255) NOT NULL,
    `password` VARCHAR(255) NOT NULL,
    `team_id` INT NOT NULL,
    `service_id` INT NOT NULL,
    `domain_id` INT,
    `is_default` BOOL DEFAULT TRUE,
    FOREIGN KEY (`team_id`) REFERENCES `team`(`id`)
       ON DELETE CASCADE,
    FOREIGN KEY (`service_id`) REFERENCES `service`(`id`)
       ON DELETE CASCADE,
    FOREIGN KEY (`domain_id`) REFERENCES `domain`(`id`)
       ON DELETE CASCADE);

DROP TABLE IF EXISTS `cred_input`;
CREATE TABLE `cred_input` (
    `id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `cred_id` INT NOT NULL,
    `check_io_id` INT NOT NULL,
    FOREIGN KEY (`cred_id`) REFERENCES `credential`(`id`)
       ON DELETE CASCADE,
    FOREIGN KEY (`check_io_id`) REFERENCES `check_io`(`id`)
       ON DELETE CASCADE);

DROP TABLE IF EXISTS `result`;
CREATE TABLE `result` (
    `id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `check_id` INT NOT NULL,
    `check_io_id` INT NOT NULL,
    `team_id` INT NOT NULL,
    `time` TIMESTAMP NOT NULL,
    `poll_input` VARCHAR(4095) NOT NULL,
    `poll_result` VARCHAR(4095) NOT NULL,
    `result` BOOL NOT NULL,
    FOREIGN KEY (`check_id`) REFERENCES `service_check`(`id`)
       ON DELETE CASCADE,
    FOREIGN KEY (`check_io_id`) REFERENCES `check_io`(`id`)
       ON DELETE CASCADE,
    FOREIGN KEY (`team_id`) REFERENCES `team`(`id`)
       ON DELETE CASCADE);

DROP TABLE IF EXISTS `pcr`;
CREATE TABLE `pcr` (
    `id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `team_id` INT NOT NULL,
    `service_id` INT,
    `domain_id` INT,
    `submitted` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `completed` TIMESTAMP NULL,
    `status` INT NOT NULL,
    `creds` TEXT NOT NULL,
    `team_comment` VARCHAR(4095) DEFAULT '',
    `admin_comment` VARCHAR(4095) DEFAULT '',
    FOREIGN KEY (`team_id`) REFERENCES `team`(`id`)
       ON DELETE CASCADE,
    FOREIGN KEY (`service_id`) REFERENCES `service`(`id`)
       ON DELETE CASCADE,
    FOREIGN KEY (`domain_id`) REFERENCES `domain`(`id`)
       ON DELETE CASCADE);

DROP TABLE IF EXISTS `default_creds_log`;
CREATE TABLE `default_creds_log` (
    `time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `team_id` INT NOT NULL,
    `perc_default` DOUBLE NOT NULL,
    FOREIGN KEY (`team_id`) REFERENCES `team`(`id`)
        ON DELETE CASCADE);

DROP TABLE IF EXISTS `revert_log`;
CREATE TABLE `revert_log` (
    `time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `team_id` INT NOT NULL,
    `system` VARCHAR(255),
    FOREIGN KEY (`team_id`) REFERENCES `team`(`id`)
        ON DELETE CASCADE);

SET foreign_key_checks = 1;
