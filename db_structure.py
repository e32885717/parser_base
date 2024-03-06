sqlite_initcmd = """CREATE TABLE IF NOT EXISTS "anonymous_data" (
	"SSID"	TEXT,
	"BSSID"	TEXT,
	"format"	INTEGER,
	"sec"	TEXT,
	"passwords"	TEXT,
	"WPS_keys"	TEXT,
	"lat"	REAL,
	"lon"	REAL,
	"time"	INTEGER,
	"scanned_time" INTEGER
);
CREATE TABLE IF NOT EXISTS "networks" (
	"SSID"	TEXT,
	"BSSID"	TEXT,
	"format"	INTEGER,
	"sec"	TEXT,
	"passwords"	TEXT,
	"WPS_keys"	TEXT,
	"lat"	REAL,
	"lon"	REAL,
	"time"	INTEGER,
	"subtask_id"	INTEGER,
	"scanned_by"	INTEGER
, "scanned_time"	INTEGER
);
CREATE TABLE IF NOT EXISTS "subtasks" (
	"id"	INTEGER,
	"min_maxTileX"	TEXT,
	"min_maxTileY"	TEXT,
	"max_area"	INTEGER,
	"min_max_progress"	TEXT,
	"parent_task"	INTEGER,
	"processing_by"	INTEGER,
	"last_ping"	INTEGER,
	"progress"	INTEGER,
	"comment"	TEXT,
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "tasks" (
	"id"	INTEGER,
	"min_maxTileX"	TEXT,
	"min_maxTileY"	TEXT,
	"max_area"	INTEGER,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "users" (
	"id"	INTEGER,
	"login"	TEXT UNIQUE,
	"password"	TEXT,
	PRIMARY KEY("id")
);"""


mariadb_initcmd = """CREATE DATABASE IF NOT EXISTS `parser_base`;
USE `parser_base`;
CREATE TABLE IF NOT EXISTS `anonymous_data` (
  `SSID` text DEFAULT NULL,
  `BSSID` text DEFAULT NULL,
  `format` smallint(6) DEFAULT NULL,
  `sec` tinytext DEFAULT NULL,
  `passwords` text DEFAULT NULL,
  `WPS_keys` text DEFAULT NULL,
  `lat` double DEFAULT NULL,
  `lon` double DEFAULT NULL,
  `time` int(11) DEFAULT NULL,
  `scanned_time` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
CREATE TABLE IF NOT EXISTS `networks` (
  `SSID` text DEFAULT NULL,
  `BSSID` text DEFAULT NULL,
  `format` smallint(6) DEFAULT NULL,
  `sec` tinytext DEFAULT NULL,
  `passwords` text DEFAULT NULL,
  `WPS_keys` text DEFAULT NULL,
  `lat` double DEFAULT NULL,
  `lon` double DEFAULT NULL,
  `time` int(11) DEFAULT NULL,
  `subtask_id` int(11) DEFAULT NULL,
  `scanned_by` int(11)  DEFAULT NULL,
  `scanned_time` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
CREATE TABLE IF NOT EXISTS `subtasks` (
	`id` int(11) AUTO_INCREMENT,
	`min_maxTileX` tinytext DEFAULT NULL,
	`min_maxTileY` tinytext DEFAULT NULL,
	`max_area` int(11) DEFAULT NULL,
	`min_max_progress` tinytext DEFAULT NULL,
	`parent_task` int(11) DEFAULT NULL,
	`processing_by` int(11) DEFAULT NULL,
	`last_ping` int(11) DEFAULT NULL,
	`progress` int(11) DEFAULT NULL,
	`comment` text DEFAULT NULL,
	PRIMARY KEY(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
CREATE TABLE IF NOT EXISTS `tasks` (
	`id` int(11) AUTO_INCREMENT,
	`min_maxTileX` text DEFAULT NULL,
	`min_maxTileY` text DEFAULT NULL,
	`max_area` int(11) DEFAULT NULL,
	PRIMARY KEY(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
CREATE TABLE IF NOT EXISTS `users` (
	`id` int(11) DEFAULT NULL,
	`login` text DEFAULT NULL UNIQUE,
	`password` text DEFAULT NULL,
	PRIMARY KEY(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;"""

stdescription = [
    ["id"],
    ["min_maxTileX"],
    ["min_maxTileY"],
    ["max_area"],
    ["min_max_progress"],
    ["parent_task"],
    ["processing_by"],
    ["last_ping"],
    ["progress"],
    ["comment"]
]