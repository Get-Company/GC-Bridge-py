-- Adminer 4.8.1 MySQL 8.0.31 dump

SET NAMES utf8;
SET time_zone = '+00:00';
SET foreign_key_checks = 0;
SET sql_mode = 'NO_AUTO_VALUE_ON_ZERO';

SET NAMES utf8mb4;

DROP DATABASE IF EXISTS `gc-bridge_db`;
CREATE DATABASE `gc-bridge_db` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `gc-bridge_db`;

DROP TABLE IF EXISTS `alembic_version`;
CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL,
  PRIMARY KEY (`version_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

DROP TABLE IF EXISTS `bridge_category_entity`;
CREATE TABLE `bridge_category_entity` (
  `id` int NOT NULL AUTO_INCREMENT,
  `erp_nr` int NOT NULL,
  `api_id` char(36) NOT NULL,
  `erp_nr_parent` int DEFAULT NULL,
  `api_idparent` char(36) DEFAULT NULL,
  `title` varchar(255) DEFAULT NULL,
  `image` varchar(255) DEFAULT NULL,
  `description` text,
  `erp_ltz_aend` datetime DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=216 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

DROP TABLE IF EXISTS `bridge_category_translation_entity`;
CREATE TABLE `bridge_category_translation_entity` (
  `id` int NOT NULL AUTO_INCREMENT,
  `language_iso` varchar(5) NOT NULL,
  `title` varchar(255) DEFAULT NULL,
  `image` varchar(255) DEFAULT NULL,
  `description` text,
  `erp_ltz_aend` datetime DEFAULT NULL,
  `category_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_bridge_category_translation_entity_category_id_bridge_e190` (`category_id`),
  CONSTRAINT `fk_bridge_category_translation_entity_category_id_bridge_e190` FOREIGN KEY (`category_id`) REFERENCES `bridge_category_entity` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


DROP TABLE IF EXISTS `bridge_customer_address_entity`;
CREATE TABLE `bridge_customer_address_entity` (
  `id` int NOT NULL AUTO_INCREMENT,
  `api_id` char(36) NOT NULL,
  `erp_nr` int NOT NULL,
  `na1` varchar(255) NOT NULL,
  `na2` varchar(255) NOT NULL,
  `na3` varchar(255) DEFAULT NULL,
  `str` varchar(255) DEFAULT NULL,
  `plz` char(12) DEFAULT NULL,
  `city` varchar(255) DEFAULT NULL,
  `land` int DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `company` varchar(255) DEFAULT NULL,
  `erp_ltz_aend` datetime DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `customer_id` int DEFAULT NULL,
  `erp_ansnr` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_bridge_customer_address_entity_customer_id_bridge_cus_9403` (`customer_id`),
  CONSTRAINT `fk_bridge_customer_address_entity_customer_id_bridge_cus_9403` FOREIGN KEY (`customer_id`) REFERENCES `bridge_customer_entity` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


DROP TABLE IF EXISTS `bridge_customer_contact_entity`;
CREATE TABLE `bridge_customer_contact_entity` (
  `id` int NOT NULL AUTO_INCREMENT,
  `api_id` char(36) NOT NULL,
  `erp_nr` int NOT NULL,
  `first_name` varchar(255) DEFAULT NULL,
  `last_name` varchar(255) DEFAULT NULL,
  `title` varchar(255) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `erp_ltz_aend` datetime DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `address_id` int DEFAULT NULL,
  `erp_ansnr` int NOT NULL,
  `erp_aspnr` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_bridge_customer_contact_entity_address_id_bridge_cust_84b9` (`address_id`),
  CONSTRAINT `fk_bridge_customer_contact_entity_address_id_bridge_cust_84b9` FOREIGN KEY (`address_id`) REFERENCES `bridge_customer_address_entity` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


DROP TABLE IF EXISTS `bridge_customer_entity`;
CREATE TABLE `bridge_customer_entity` (
  `id` int NOT NULL AUTO_INCREMENT,
  `api_id` char(36) NOT NULL,
  `erp_nr` int NOT NULL,
  `erp_ltz_aend` datetime DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


DROP TABLE IF EXISTS `bridge_product_category_entity`;
CREATE TABLE `bridge_product_category_entity` (
  `product_id` int NOT NULL,
  `category_id` int NOT NULL,
  PRIMARY KEY (`product_id`,`category_id`),
  KEY `fk_bridge_product_category_entity_category_id_bridge_cat_32b5` (`category_id`),
  CONSTRAINT `fk_bridge_product_category_entity_category_id_bridge_cat_32b5` FOREIGN KEY (`category_id`) REFERENCES `bridge_category_entity` (`id`),
  CONSTRAINT `fk_bridge_product_category_entity_product_id_bridge_prod_f296` FOREIGN KEY (`product_id`) REFERENCES `bridge_product_entity` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

DROP TABLE IF EXISTS `bridge_product_entity`;
CREATE TABLE `bridge_product_entity` (
  `id` int NOT NULL AUTO_INCREMENT,
  `erp_nr` varchar(255) DEFAULT NULL,
  `api_id` char(36) NOT NULL,
  `name` varchar(255) DEFAULT NULL,
  `image` json DEFAULT NULL,
  `description` text,
  `price` float DEFAULT NULL,
  `price_rebate_amount` int DEFAULT NULL,
  `price_rebate` float DEFAULT NULL,
  `stock` int NOT NULL,
  `factor` int DEFAULT NULL,
  `min_purchase` int DEFAULT NULL,
  `purchase_unit` int DEFAULT NULL,
  `unit` varchar(255) DEFAULT NULL,
  `erp_ltz_aend` datetime DEFAULT NULL,
  `wshopkz` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `tax_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_bridge_product_entity_tax_id_bridge_tax_entity` (`tax_id`),
  CONSTRAINT `fk_bridge_product_entity_tax_id_bridge_tax_entity` FOREIGN KEY (`tax_id`) REFERENCES `bridge_tax_entity` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=453 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

DROP TABLE IF EXISTS `bridge_product_translation_entity`;
CREATE TABLE `bridge_product_translation_entity` (
  `id` int NOT NULL AUTO_INCREMENT,
  `language_iso` varchar(5) NOT NULL,
  `name` varchar(255) DEFAULT NULL,
  `image` varchar(255) DEFAULT NULL,
  `description` text,
  `erp_ltz_aend` datetime DEFAULT NULL,
  `product_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_bridge_product_translation_entity_product_id_bridge_p_40c6` (`product_id`),
  CONSTRAINT `fk_bridge_product_translation_entity_product_id_bridge_p_40c6` FOREIGN KEY (`product_id`) REFERENCES `bridge_product_entity` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


DROP TABLE IF EXISTS `bridge_synchronize_entity`;
CREATE TABLE `bridge_synchronize_entity` (
  `id` int NOT NULL AUTO_INCREMENT,
  `dataset_category_sync_date` datetime DEFAULT NULL,
  `dataset_product_sync_date` datetime DEFAULT NULL,
  `dataset_address_sync_date` datetime DEFAULT NULL,
  `dataset_tax_sync_date` datetime DEFAULT NULL,
  `sw6_category_sync_date` datetime DEFAULT NULL,
  `sw6_product_sync_date` datetime DEFAULT NULL,
  `sw6_address_sync_date` datetime DEFAULT NULL,
  `loop_continue` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_bridge_synchronize_entity_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

DROP TABLE IF EXISTS `bridge_tax_entity`;
CREATE TABLE `bridge_tax_entity` (
  `id` int NOT NULL AUTO_INCREMENT,
  `steuer_schluessel` int DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  `satz` float DEFAULT NULL,
  `api_id` char(36) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=35 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

DROP TABLE IF EXISTS `mappei_classei_product_entity`;
CREATE TABLE `mappei_classei_product_entity` (
  `product_id` int DEFAULT NULL,
  `mappei_id` int DEFAULT NULL,
  KEY `fk_mappei_classei_product_entity_product_id_bridge_produ_e6b9` (`product_id`),
  KEY `fk_mappei_classei_product_entity_mappei_id_mappei_product_entity` (`mappei_id`),
  CONSTRAINT `fk_mappei_classei_product_entity_mappei_id_mappei_product_entity` FOREIGN KEY (`mappei_id`) REFERENCES `mappei_product_entity` (`id`),
  CONSTRAINT `fk_mappei_classei_product_entity_product_id_bridge_produ_e6b9` FOREIGN KEY (`product_id`) REFERENCES `bridge_product_entity` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


DROP TABLE IF EXISTS `mappei_price_entity`;
CREATE TABLE `mappei_price_entity` (
  `id` int NOT NULL AUTO_INCREMENT,
  `price_high` float DEFAULT NULL,
  `price_low` float DEFAULT NULL,
  `price_quantity` int DEFAULT NULL,
  `land` varchar(255) DEFAULT NULL,
  `last_mod` datetime DEFAULT NULL,
  `product_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_mappei_price_entity_product_id_mappei_product_entity` (`product_id`),
  CONSTRAINT `fk_mappei_price_entity_product_id_mappei_product_entity` FOREIGN KEY (`product_id`) REFERENCES `mappei_product_entity` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


DROP TABLE IF EXISTS `mappei_product_entity`;
CREATE TABLE `mappei_product_entity` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nr` varchar(255) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `image` varchar(255) DEFAULT NULL,
  `description` char(1) DEFAULT NULL,
  `release_date` datetime DEFAULT NULL,
  `last_mod` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


-- 2022-11-18 06:49:08
