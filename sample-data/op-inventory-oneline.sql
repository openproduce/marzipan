-- MySQL dump 10.11
--
-- Host: localhost    Database: inventory
-- ------------------------------------------------------
-- Server version	5.0.51a-24+lenny5-log

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `barcode_items`
--

DROP TABLE IF EXISTS `barcode_items`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `barcode_items` (
  `id` int(11) NOT NULL auto_increment,
  `item_id` int(11) NOT NULL,
  `barcode` varchar(16) default NULL,
  PRIMARY KEY  (`id`),
  KEY `item_id` (`item_id`)
) ENGINE=MyISAM AUTO_INCREMENT=666667448 DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

LOCK TABLES `barcode_items` WRITE;
/*!40000 ALTER TABLE `barcode_items` DISABLE KEYS */;
INSERT INTO `barcode_items` VALUES (1,1,'123456789012'); 
/*!40000 ALTER TABLE `barcode_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `categories`
--

DROP TABLE IF EXISTS `categories`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `categories` (
  `id` int(11) NOT NULL auto_increment,
  `name` varchar(255) NOT NULL,
  PRIMARY KEY  (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=24 DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;


--
-- Dumping data for table `categories`
--

LOCK TABLES `categories` WRITE;
/*!40000 ALTER TABLE `categories` DISABLE KEYS */;
INSERT INTO `categories` VALUES (1,'produce'),(10,'tea'),(3,'frozen'),(4,'refrigerated'),(6,'drygoods'),(12,'drinks (single-serve)'),(8,'spices'),(9,'household'),(11,'cereal'),(13,'organic'),(14,'local'),(15,'meat'),(16,'bakery'),(19,'fruit spreads'),(20,'juice'),(21,'dairy'),(22,'vegan'),(23,'instacart');
/*!40000 ALTER TABLE `categories` ENABLE KEYS */;
UNLOCK TABLES;


--
-- Table structure for table `category_items`
--

DROP TABLE IF EXISTS `category_items`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `category_items` (
  `id` int(11) NOT NULL auto_increment,
  `item_id` int(11) NOT NULL,
  `cat_id` int(11) NOT NULL,
  PRIMARY KEY  (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=4565 DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `category_items`
--

LOCK TABLES `category_items` WRITE;
/*!40000 ALTER TABLE `category_items` DISABLE KEYS */;
INSERT INTO `category_items` VALUES (1,1,1);
/*!40000 ALTER TABLE `category_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `clerks`
--

DROP TABLE IF EXISTS `clerks`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `clerks` (
  `id` int(11) NOT NULL auto_increment,
  `name` varchar(255) NOT NULL,
  `is_valid` tinyint(1) default NULL,
  PRIMARY KEY  (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=24 DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;
--
-- Dumping data for table `clerks`
--

LOCK TABLES `clerks` WRITE;
/*!40000 ALTER TABLE `clerks` DISABLE KEYS */;
INSERT INTO `clerks` VALUES (1,'Testclerk',1);
/*!40000 ALTER TABLE `clerks` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `coupon_items` (apparently deprecated, doesn't appear in code)
--

DROP TABLE IF EXISTS `coupon_items`;



--
-- Table structure for table `deliveries`
--

DROP TABLE IF EXISTS `deliveries`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `deliveries` (
  `id` int(11) NOT NULL auto_increment,
  `time_delivered` datetime default NULL,
  `item_id` int(11) NOT NULL,
  `amount` decimal(8,2) default NULL,
  `dist_id` int(11) default NULL,
  PRIMARY KEY  (`id`),
  KEY `dist_id` (`dist_id`)
) ENGINE=MyISAM AUTO_INCREMENT=50580 DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `deliveries`
--

LOCK TABLES `deliveries` WRITE;
/*!40000 ALTER TABLE `deliveries` DISABLE KEYS */;
INSERT INTO `deliveries` VALUES (1,'2015-01-01 02:22:22',1,'3.00',NULL);
/*!40000 ALTER TABLE `deliveries` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `distributor_items`
--

DROP TABLE IF EXISTS `distributor_items`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `distributor_items` (
  `id` int(11) NOT NULL auto_increment,
  `item_id` int(11) NOT NULL,
  `dist_id` int(11) NOT NULL,
  `dist_item_id` varchar(255) default NULL, -- what is this?
  `wholesale_price` decimal(8,2) default NULL,
  `case_size` decimal(8,2) default NULL,
  `case_unit_id` int(11) default NULL,
  PRIMARY KEY  (`id`),
  KEY `item_id` (`item_id`),
  KEY `dist_id` (`dist_id`),
  KEY `case_unit_id` (`case_unit_id`)
) ENGINE=MyISAM AUTO_INCREMENT=4750 DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `distributor_items`
--

LOCK TABLES `distributor_items` WRITE;
/*!40000 ALTER TABLE `distributor_items` DISABLE KEYS */;
INSERT INTO `distributor_items` VALUES (1,1,1,'210987654321','76.54','12.00',1); 
/*!40000 ALTER TABLE `distributor_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `distributors`
--

DROP TABLE IF EXISTS `distributors`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `distributors` (
  `id` int(11) NOT NULL auto_increment,
  `name` varchar(255) NOT NULL,
  `phone` varchar(10) default NULL,
  PRIMARY KEY  (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=72 DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `distributors`
--

LOCK TABLES `distributors` WRITE;
/*!40000 ALTER TABLE `distributors` DISABLE KEYS */;
INSERT INTO `distributors` VALUES (1,'TestDistributor',NULL);
/*!40000 ALTER TABLE `distributors` ENABLE KEYS */;
UNLOCK TABLES;


--
-- Table structure for table `item_count_log`
--

DROP TABLE IF EXISTS `item_count_log`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `item_count_log` (
  `id` int(11) NOT NULL auto_increment,
  `item_id` int(11) NOT NULL,
  `old_count` int(11) default NULL,
  `new_count` int(11) default NULL,
  `is_manual_count` tinyint(4) NOT NULL default '1',
  `when_logged` datetime default NULL,
  PRIMARY KEY  (`id`),
  KEY `item_id` (`item_id`)
) ENGINE=MyISAM AUTO_INCREMENT=587098 DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `item_count_log`
--

LOCK TABLES `item_count_log` WRITE;
/*!40000 ALTER TABLE `item_count_log` DISABLE KEYS */;
INSERT INTO `item_count_log` VALUES (1,1,0,6,1,'2015-01-01 02:22:22');
/*!40000 ALTER TABLE `item_count_log` ENABLE KEYS */;
UNLOCK TABLES;


--
-- Table structure for table `items`
--

DROP TABLE IF EXISTS `items`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `items` (
  `id` int(11) NOT NULL auto_increment,
  `name` varchar(255) NOT NULL,
  `price_id` int(11) NOT NULL,
  `tax_category_id` int(11) NOT NULL,
  `plu` varchar(5) default NULL,
  `size` decimal(8,4) default NULL,
  `size_unit_id` int(11) default NULL,
  `count` int(11) NOT NULL,
  `count_timestamp` datetime default NULL,
  `last_manual_count` int(11) default NULL,
  `last_manual_count_timestamp` datetime default NULL,
  `is_discontinued` tinyint(1) NOT NULL,
  `notes` text,
  `display_name` text,
  `description` text,
  `weight` float,
  PRIMARY KEY  (`id`),
  KEY `price_id` (`price_id`),
  KEY `size_unit_id` (`size_unit_id`),
  KEY `tax_category_id` (`tax_category_id`)
) ENGINE=MyISAM AUTO_INCREMENT=4196 DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;
LOCK TABLES `items` WRITE;
/*!40000 ALTER bbbTABLE `items` DISABLE KEYS */;
INSERT INTO `items` VALUES (1,'test item name',1,1,'','1.0000',1,5,'2015-01-01 02:22:22',0,NULL,1,NULL);
/*!40000 ALTER TABLE `items` ENABLE KEYS */;
UNLOCK TABLES;


/*!50003 SET @SAVE_SQL_MODE=@@SQL_MODE*/;

DELIMITER ;;
/*!50003 SET SESSION SQL_MODE="" */;;
/*!50003 CREATE */ /*!50017 DEFINER=`root`@`localhost` */ /*!50003 TRIGGER `new_item_count_logger` AFTER INSERT ON `items` FOR EACH ROW begin
                insert into item_count_log(item_id, old_count,new_count, is_manual_count, when_logged) values (NEW.id, NULL, NEW.count, 1, now());
            end */;;

/*!50003 SET SESSION SQL_MODE="" */;;
/*!50003 CREATE */ /*!50017 DEFINER=`root`@`localhost` */ /*!50003 TRIGGER `item_count_logger` BEFORE UPDATE ON `items` FOR EACH ROW begin
                if NEW.count <> OLD.count or OLD.count is null then
                   if NEW.last_manual_count <> OLD.last_manual_count or OLD.last_manual_count is null then
                       insert into item_count_log(item_id, old_count, new_count, is_manual_count, when_logged) values (NEW.id, OLD.count, NEW.count, 1, now());
                   else
                       insert into item_count_log(item_id, old_count, new_count, is_manual_count, when_logged) values (NEW.id, OLD.count, NEW.count, 0, now());
                   end if;
            end if;
            end */;;

DELIMITER ;
/*!50003 SET SESSION SQL_MODE=@SAVE_SQL_MODE*/;

--
-- Table structure for table `price_changes`
--

DROP TABLE IF EXISTS `price_changes`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `price_changes` (
  `id` int(11) NOT NULL auto_increment,
  `old_price_id` int(11) NOT NULL,
  `new_price_id` int(11) NOT NULL,
  `special_id` int(11) default NULL,
  PRIMARY KEY  (`id`),
  KEY `special_id` (`special_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `price_changes`
--

LOCK TABLES `price_changes` WRITE;
/*!40000 ALTER TABLE `price_changes` DISABLE KEYS */;
/*!40000 ALTER TABLE `price_changes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `prices`
--

DROP TABLE IF EXISTS `prices`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `prices` (
  `id` int(11) NOT NULL auto_increment,
  `sale_unit_id` int(11) NOT NULL,
  `unit_cost` decimal(10,4) NOT NULL,
  `is_tax_flat` tinyint(1) NOT NULL,
  PRIMARY KEY  (`id`),
  KEY `sale_unit_id` (`sale_unit_id`)
) ENGINE=MyISAM AUTO_INCREMENT=4165 DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `prices`
--

LOCK TABLES `prices` WRITE;
/*!40000 ALTER TABLE `prices` DISABLE KEYS */;
INSERT INTO `prices` VALUES (1,1,'2.2200',0); 
/*!40000 ALTER TABLE `prices` ENABLE KEYS */;
UNLOCK TABLES;


--
-- Table structure for table `sale_units`
--

DROP TABLE IF EXISTS `sale_units`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `sale_units` (
  `id` int(11) NOT NULL auto_increment,
  `name` varchar(20) NOT NULL,
  `unit_type` int(11) NOT NULL,
  PRIMARY KEY  (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=12 DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `sale_units`
--

LOCK TABLES `sale_units` WRITE;
/*!40000 ALTER TABLE `sale_units` DISABLE KEYS */;
INSERT INTO `sale_units` VALUES (1,'each',0),(2,'count',0),(3,'oz',1),(4,'lbs',1),(5,'g',1),(6,'kg',1),(7,'fl oz',2),(8,'pt',2),(9,'qt',2),(10,'mL',2),(11,'L',2);
/*!40000 ALTER TABLE `sale_units` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `specials`
--

DROP TABLE IF EXISTS `specials`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `specials` (
  `id` int(11) NOT NULL auto_increment,
  `name` varchar(255) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  PRIMARY KEY  (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `specials`
--

LOCK TABLES `specials` WRITE;
/*!40000 ALTER TABLE `specials` DISABLE KEYS */;
/*!40000 ALTER TABLE `specials` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tax_categories`
--

DROP TABLE IF EXISTS `tax_categories`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `tax_categories` (
  `id` int(11) NOT NULL auto_increment,
  `name` varchar(255) NOT NULL,
  `rate` decimal(4,4) default NULL,
  PRIMARY KEY  (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=7 DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `tax_categories`
--

LOCK TABLES `tax_categories` WRITE;
/*!40000 ALTER TABLE `tax_categories` DISABLE KEYS */;
INSERT INTO `tax_categories` VALUES (1,'food','0.0225'),(2,'medical','0.0225'),(3,'general','0.0975'),(4,'soda','0.1275'),(5,'candy','0.1275'),(6,'none','0.0000');
/*!40000 ALTER TABLE `tax_categories` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2015-03-16  8:15:04
