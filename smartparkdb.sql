CREATE SCHEMA IF NOT EXISTS `smartparkdb` DEFAULT CHARACTER SET utf8mb3 ;
USE `smartparkdb` ;

-- -----------------------------------------------------
-- Table `smartparkdb`.`drivers`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `smartparkdb`.`drivers` (
  `driver_id` INT NOT NULL AUTO_INCREMENT,
  `first_name` VARCHAR(80) NULL DEFAULT NULL,
  `last_name` VARCHAR(100) NULL DEFAULT NULL,
  `email` VARCHAR(150) NULL DEFAULT NULL,
  `password` VARCHAR(80) NULL DEFAULT NULL,
  `phone` VARCHAR(15) NULL DEFAULT NULL,
  PRIMARY KEY (`driver_id`));


-- -----------------------------------------------------
-- Table `smartparkdb`.`vehicles`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `smartparkdb`.`vehicles` (
  `vehicle_id` INT NOT NULL AUTO_INCREMENT,
  `registration` VARCHAR(20) NULL DEFAULT NULL,
  `colour` VARCHAR(20) NULL DEFAULT NULL,
  `model` VARCHAR(50) NULL DEFAULT NULL,
  `brand` VARCHAR(50) NULL DEFAULT NULL,
  `driver_id` INT NOT NULL,
  PRIMARY KEY (`vehicle_id`),
  INDEX `fk_vehicles_drivers_idx` (`driver_id` ASC) VISIBLE,
  CONSTRAINT `fk_vehicles_drivers`
    FOREIGN KEY (`driver_id`)
    REFERENCES `smartparkdb`.`drivers` (`driver_id`));

-- -----------------------------------------------------
-- Table `smartparkdb`.`bookings`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `smartparkdb`.`bookings` (
  `booking_id` INT NOT NULL AUTO_INCREMENT,
  `booking_date` VARCHAR(75) NULL DEFAULT NULL,
  `booking_cost` DECIMAL(5,2) NULL DEFAULT NULL,
  `booking_duration` VARCHAR(45) NULL DEFAULT NULL,
  `vehicle_id` INT NOT NULL,
  PRIMARY KEY (`booking_id`),
  INDEX `fk_bookings_vehicles1_idx` (`vehicle_id` ASC) VISIBLE,
  CONSTRAINT `fk_bookings_vehicles1`
    FOREIGN KEY (`vehicle_id`)
    REFERENCES `smartparkdb`.`vehicles` (`vehicle_id`));
