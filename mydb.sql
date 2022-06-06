SET
  @OLD_UNIQUE_CHECKS = @ @UNIQUE_CHECKS,
  UNIQUE_CHECKS = 0;
SET
  @OLD_FOREIGN_KEY_CHECKS = @ @FOREIGN_KEY_CHECKS,
  FOREIGN_KEY_CHECKS = 0;
SET
  @OLD_SQL_MODE = @ @SQL_MODE,
  SQL_MODE = 'TRADITIONAL,ALLOW_INVALID_DATES';
-- ----------------------------------------------------- -- Schema mydb -- -----------------------------------------------------
  -- ----------------------------------------------------- -- Schema mydb -- -----------------------------------------------------
  DROP DATABASE IF EXISTS `mydb`;
CREATE SCHEMA IF NOT EXISTS `mydb` DEFAULT CHARACTER SET utf8;
USE `mydb`;
-- ----------------------------------------------------- -- Table `mydb`.`user` -- -----------------------------------------------------
  CREATE TABLE IF NOT EXISTS `mydb`.`user` (
    `id` INT AUTO_INCREMENT NOT NULL,
    `username` VARCHAR(45) NOT NULL,
    `email` VARCHAR(45) NOT NULL,
    `pseudo` VARCHAR(45) NULL,
    `password` VARCHAR(45) NOT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE INDEX `email_UNIQUE` (`email` ASC),
    UNIQUE INDEX `username_UNIQUE` (`username` ASC)
  ) ENGINE = InnoDB;
-- ----------------------------------------------------- -- Table `mydb`.`video` -- -----------------------------------------------------
  CREATE TABLE IF NOT EXISTS `mydb`.`video` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `name` VARCHAR(255) NOT NULL,
    `duration` INT NULL,
    `user_id` INT NOT NULL,
    `source` VARCHAR(255) NOT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `view` INT NOT NULL,
    `enabled` TINYINT(1) NOT NULL,
    `source_resolution` INT NOT NULL,
    PRIMARY KEY (`id`),
    INDEX `fk_video_user_idx` (`user_id` ASC),
    CONSTRAINT `fk_video_user` FOREIGN KEY (`user_id`) REFERENCES `mydb`.`user` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION
  ) ENGINE = InnoDB;
-- ----------------------------------------------------- -- Table `mydb`.`format` -- -----------------------------------------------------
  CREATE TABLE IF NOT EXISTS `mydb`.`format` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `resolution` VARCHAR(255) NOT NULL,
    PRIMARY KEY (`id`),
    UNIQUE INDEX `resolution_unique` (`resolution` ASC)
  ) ENGINE = InnoDB;
-- ----------------------------------------------------- -- Table `mydb`.`video_format` -- -----------------------------------------------------
  CREATE TABLE IF NOT EXISTS `mydb`.`video_format` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `source` VARCHAR(255) NOT NULL,
    `resolution` INT NOT NULL,
    `video_id` INT NOT NULL,
    `format_id` INT NOT NULL,
    PRIMARY KEY (`id`),
    INDEX `fk_video_format_video1_idx` (`video_id` ASC),
    INDEX `fk_video_format_format1_idx` (`format_id` ASC),
    CONSTRAINT `fk_video_format_video1` FOREIGN KEY (`video_id`) REFERENCES `mydb`.`video` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION,
    CONSTRAINT `fk_video_format_format1` FOREIGN KEY (`format_id`) REFERENCES `mydb`.`format` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION
  ) ENGINE = InnoDB;
-- ----------------------------------------------------- -- Table `mydb`.`token` -- -----------------------------------------------------
  CREATE TABLE IF NOT EXISTS `mydb`.`token` (
    `id` INT AUTO_INCREMENT NOT NULL,
    `code` VARCHAR(255) NOT NULL,
    `expired_at` DATETIME NOT NULL,
    `user_id` INT NOT NULL,
    PRIMARY KEY (`id`),
    INDEX `fk_token_user1_idx` (`user_id` ASC),
    UNIQUE INDEX `code_UNIQUE` (`code` ASC),
    CONSTRAINT `fk_token_user1` FOREIGN KEY (`user_id`) REFERENCES `mydb`.`user` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION
  ) ENGINE = InnoDB;
-- ----------------------------------------------------- -- Table `mydb`.`comment` -- -----------------------------------------------------
  CREATE TABLE IF NOT EXISTS `mydb`.`comment` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `body` LONGTEXT NULL,
    `user_id` INT NOT NULL,
    `video_id` INT NOT NULL,
    PRIMARY KEY (`id`),
    INDEX `fk_comment_user1_idx` (`user_id` ASC),
    INDEX `fk_comment_video1_idx` (`video_id` ASC),
    CONSTRAINT `fk_comment_user1` FOREIGN KEY (`user_id`) REFERENCES `mydb`.`user` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION,
    CONSTRAINT `fk_comment_video1` FOREIGN KEY (`video_id`) REFERENCES `mydb`.`video` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION
  ) ENGINE = InnoDB;
  
  INSERT INTO `mydb`.`format` (`id`, `resolution`) VALUES (1, '144');
  INSERT INTO `mydb`.`format` (`id`, `resolution`) VALUES (2, '240');
  INSERT INTO `mydb`.`format` (`id`, `resolution`) VALUES (3, '360');
  INSERT INTO `mydb`.`format` (`id`, `resolution`) VALUES (4, '480');
  INSERT INTO `mydb`.`format` (`id`, `resolution`) VALUES (5, '720');
  INSERT INTO `mydb`.`format` (`id`, `resolution`) VALUES (6, '1080');

SET
  SQL_MODE = @OLD_SQL_MODE;
SET
  FOREIGN_KEY_CHECKS = @OLD_FOREIGN_KEY_CHECKS;
SET
  UNIQUE_CHECKS = @OLD_UNIQUE_CHECKS;