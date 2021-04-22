-- MySQL dump 10.13  Distrib 8.0.23, for Linux (x86_64)
--
-- Host: localhost    Database: innerInformationSystem_System
-- ------------------------------------------------------
-- Server version	8.0.23-0ubuntu0.20.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Current Database: `innerInformationSystem_System`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `innerInformationSystem_System` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `innerInformationSystem_System`;

--
-- Table structure for table `actions`
--

DROP TABLE IF EXISTS `actions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `actions` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'Уникальный идентификатор',
  `name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT 'Имя действия над объектом',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `assignment_permissions_roles`
--

DROP TABLE IF EXISTS `assignment_permissions_roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `assignment_permissions_roles` (
  `permission_id` int NOT NULL,
  `role_id` int NOT NULL,
  PRIMARY KEY (`permission_id`,`role_id`),
  KEY `assignment_permissions_roles_ibfk_2` (`role_id`),
  KEY `assignment_permissions_roles_ibfk_1` (`permission_id`),
  CONSTRAINT `assignment_permissions_roles_ibfk_1` FOREIGN KEY (`permission_id`) REFERENCES `permissions` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `assignment_permissions_roles_ibfk_2` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Связь разрешений и ролей';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `assignment_removed_permissions_users`
--

DROP TABLE IF EXISTS `assignment_removed_permissions_users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `assignment_removed_permissions_users` (
  `user_assignment_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`user_assignment_id`,`permission_id`),
  KEY `assignment_removed_permissions_users_ibfk_1` (`permission_id`),
  KEY `assignment_removed_permissions_users_ibfk_2` (`user_assignment_id`) USING BTREE,
  CONSTRAINT `assignment_removed_permissions_users_ibfk_1` FOREIGN KEY (`permission_id`) REFERENCES `permissions` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `assignment_removed_permissions_users_ibfk_2` FOREIGN KEY (`user_assignment_id`) REFERENCES `assignment_users_modules` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `assignment_users_emails`
--

DROP TABLE IF EXISTS `assignment_users_emails`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `assignment_users_emails` (
  `user_id` int NOT NULL,
  `email_id` int NOT NULL,
  KEY `users_emails_assignment_ibfk_1` (`email_id`),
  KEY `users_emails_assignment_ibfk_2` (`user_id`),
  CONSTRAINT `assignment_users_emails_ibfk_1` FOREIGN KEY (`email_id`) REFERENCES `emails` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `assignment_users_emails_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `assignment_users_modules`
--

DROP TABLE IF EXISTS `assignment_users_modules`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `assignment_users_modules` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT ' Уникальный идентификатор',
  `user_id` int NOT NULL,
  `module_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `assignment_users_modules_ibfk_1` (`module_id`),
  KEY `assignment_users_modules_ibfk_2` (`user_id`),
  CONSTRAINT `assignment_users_modules_ibfk_1` FOREIGN KEY (`module_id`) REFERENCES `modules` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `assignment_users_modules_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `assignment_users_passwords`
--

DROP TABLE IF EXISTS `assignment_users_passwords`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `assignment_users_passwords` (
  `user_id` int NOT NULL,
  `password_id` int NOT NULL,
  KEY `users_passwords_assignment_ibfk_1` (`password_id`),
  KEY `users_passwords_assignment_ibfk_2` (`user_id`),
  CONSTRAINT `assignment_users_passwords_ibfk_1` FOREIGN KEY (`password_id`) REFERENCES `passwords` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `assignment_users_passwords_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `assignment_users_roles`
--

DROP TABLE IF EXISTS `assignment_users_roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `assignment_users_roles` (
  `user_assignment_id` int NOT NULL,
  `role_id` int NOT NULL,
  PRIMARY KEY (`user_assignment_id`,`role_id`),
  KEY `assignment_users_roles_ibfk1` (`role_id`),
  KEY `assignment_users_roles_ibfk2` (`user_assignment_id`),
  CONSTRAINT `assignment_users_roles_ibfk1` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `assignment_users_roles_ibfk2` FOREIGN KEY (`user_assignment_id`) REFERENCES `assignment_users_modules` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `assignment_users_socials`
--

DROP TABLE IF EXISTS `assignment_users_socials`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `assignment_users_socials` (
  `user_id` int NOT NULL,
  `social_id` int NOT NULL,
  KEY `assignment_users_socials_ibfk_1` (`social_id`),
  KEY `assignment_users_socials_ibfk_2` (`user_id`),
  CONSTRAINT `assignment_users_socials_ibfk_1` FOREIGN KEY (`social_id`) REFERENCES `socials` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `assignment_users_socials_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `assignment_users_structures`
--

DROP TABLE IF EXISTS `assignment_users_structures`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `assignment_users_structures` (
  `user_id` int NOT NULL,
  `structure_id` int NOT NULL,
  KEY `assignment_users_structures_ibfk_1` (`structure_id`),
  KEY `assignment_users_structures_ibfk_2` (`user_id`),
  CONSTRAINT `assignment_users_structures_ibfk_1` FOREIGN KEY (`structure_id`) REFERENCES `organizational_structure` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `assignment_users_structures_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `emails`
--

DROP TABLE IF EXISTS `emails`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `emails` (
  `id` int NOT NULL AUTO_INCREMENT,
  `value` varchar(100) NOT NULL COMMENT 'Адрес почты',
  `type` varchar(20) NOT NULL COMMENT 'Тип почты',
  `verify` tinyint(1) NOT NULL DEFAULT '0' COMMENT 'Подтверждение',
  `active_until` datetime NOT NULL COMMENT 'Активна до',
  PRIMARY KEY (`id`),
  UNIQUE KEY `value` (`value`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `history`
--

DROP TABLE IF EXISTS `history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `history` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'Уникальный идентификатор',
  `user_id` int NOT NULL,
  `action_id` int NOT NULL,
  `object_id` int NOT NULL,
  `module_id` int NOT NULL,
  `action_describe` varchar(256) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `make_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `history_ibfk_1` (`user_id`),
  KEY `history_ibfk_2` (`module_id`),
  KEY `history_ibfk_3` (`action_id`),
  KEY `history_ibfk_4` (`object_id`),
  CONSTRAINT `history_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `history_ibfk_2` FOREIGN KEY (`module_id`) REFERENCES `modules` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `history_ibfk_3` FOREIGN KEY (`action_id`) REFERENCES `actions` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `history_ibfk_4` FOREIGN KEY (`object_id`) REFERENCES `objects` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `modules`
--

DROP TABLE IF EXISTS `modules`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `modules` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'Уникальный идентификатор',
  `module_type_id` int NOT NULL COMMENT 'Тип модуля',
  `name` varchar(50) DEFAULT NULL COMMENT 'Имя модуля',
  `description` varchar(256) DEFAULT NULL COMMENT 'Короткое описание модуля',
  `version` varchar(8) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT 'Версия модуля',
  `code` varchar(36) DEFAULT NULL COMMENT 'Уникальный код',
  PRIMARY KEY (`id`),
  KEY `modules_ibfk_1` (`module_type_id`),
  CONSTRAINT `modules_ibfk_1` FOREIGN KEY (`module_type_id`) REFERENCES `modules_types` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `modules_types`
--

DROP TABLE IF EXISTS `modules_types`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `modules_types` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'Уникальный идентификатор',
  `name` varchar(50) NOT NULL COMMENT 'Имя типа модуля',
  `code` varchar(36) DEFAULT NULL COMMENT 'Уникальный код',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `objects`
--

DROP TABLE IF EXISTS `objects`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `objects` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'Уникальный идентификатор',
  `name` varchar(50) NOT NULL COMMENT 'Имя объекта взаимодействия',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `organizational_structure`
--

DROP TABLE IF EXISTS `organizational_structure`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `organizational_structure` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'Уникальный идентификатор',
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT 'Имя элемента',
  `type` smallint DEFAULT NULL COMMENT 'Тип элемента',
  `deletable` smallint NOT NULL DEFAULT '1' COMMENT 'Удаляемый?',
  `movable` smallint NOT NULL DEFAULT '1' COMMENT 'Двигаемый?',
  `updatable` smallint NOT NULL DEFAULT '1' COMMENT 'Обновляемый?',
  `insertable` smallint NOT NULL DEFAULT '1' COMMENT 'Потомки?',
  `lft` int NOT NULL,
  `rgt` int NOT NULL,
  `level` int NOT NULL,
  `tree_id` int DEFAULT NULL,
  `parent_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `parent_id` (`parent_id`),
  KEY `organizational_structure_rgt_idx` (`rgt`),
  KEY `organizational_structure_level_idx` (`level`),
  KEY `organizational_structure_lft_idx` (`lft`),
  CONSTRAINT `organizational_structure_ibfk_1` FOREIGN KEY (`parent_id`) REFERENCES `organizational_structure` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=60 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `passwords`
--

DROP TABLE IF EXISTS `passwords`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `passwords` (
  `id` int NOT NULL AUTO_INCREMENT,
  `value` varchar(100) NOT NULL COMMENT 'Захешированный пароль',
  `blocked` tinyint(1) NOT NULL DEFAULT '0' COMMENT 'Статус блокировки пароля',
  `first_time_use` tinyint(1) NOT NULL DEFAULT '1' COMMENT 'Использован впервые?',
  `numer_of_uses` int NOT NULL DEFAULT '0' COMMENT 'Количество использований',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Создан',
  `active_until` datetime NOT NULL COMMENT 'Активен до',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `permissions`
--

DROP TABLE IF EXISTS `permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `permissions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `action_id` int NOT NULL,
  `object_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `permissions_ibfk_1` (`action_id`),
  KEY `permissions_ibfk_2` (`object_id`),
  CONSTRAINT `permissions_ibfk_1` FOREIGN KEY (`action_id`) REFERENCES `actions` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `permissions_ibfk_2` FOREIGN KEY (`object_id`) REFERENCES `objects` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `roles`
--

DROP TABLE IF EXISTS `roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `roles` (
  `id` int NOT NULL AUTO_INCREMENT,
  `module_type_id` int NOT NULL,
  `name` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `roles_ibfk_1` (`module_type_id`),
  CONSTRAINT `roles_ibfk_1` FOREIGN KEY (`module_type_id`) REFERENCES `modules_types` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `socials`
--

DROP TABLE IF EXISTS `socials`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `socials` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT ' Уникальный идентификатор',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'Уникальный идентификатор',
  `login` varchar(20) DEFAULT NULL COMMENT 'Уникальный логин',
  `photo` varchar(50) DEFAULT NULL COMMENT 'Имя файла фотокарточки',
  `name` varchar(20) DEFAULT NULL COMMENT 'Имя',
  `surname` varchar(20) DEFAULT NULL COMMENT 'Фамилия',
  `patronymic` varchar(20) DEFAULT NULL COMMENT 'Отчество',
  `phone` varchar(18) DEFAULT NULL COMMENT 'Телефон',
  `about_me` text COMMENT 'О себе (например, должность)',
  `birth_date` date DEFAULT NULL COMMENT 'Дата рождения',
  `employment_date` date DEFAULT NULL COMMENT 'Дата трудоустройства',
  `status` tinyint(1) NOT NULL COMMENT 'Статус записи пользователя',
  PRIMARY KEY (`id`),
  UNIQUE KEY `login` (`login`),
  UNIQUE KEY `phone` (`phone`),
  CONSTRAINT `users_chk_1` CHECK ((`status` in (0,1)))
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping routines for database 'innerInformationSystem_System'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2021-04-22 15:33:03
