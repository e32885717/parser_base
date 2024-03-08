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

sqlite_rsdump = """CREATE TABLE IF NOT EXISTS rsdump (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    time TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    IP INTEGER NOT NULL,
    Port INTEGER UNSIGNED NOT NULL,
    status TEXT NOT NULL,
    Authorization TEXT DEFAULT NULL,
    name TEXT DEFAULT NULL,
    RadioOff INTEGER NOT NULL DEFAULT 0,
    Hidden INTEGER NOT NULL DEFAULT 0,
    BSSID INTEGER UNSIGNED DEFAULT NULL,
    ESSID VARCHAR(32) DEFAULT NULL,
    Security INTEGER UNSIGNED DEFAULT NULL,
    WiFiKey VARCHAR(64) DEFAULT NULL,
    WPSPIN INTEGER UNSIGNED DEFAULT NULL,
    LANIP INTEGER DEFAULT NULL,
    LANMask INTEGER DEFAULT NULL,
    WANIP INTEGER DEFAULT NULL,
    WANMask INTEGER DEFAULT NULL,
    WANGateway INTEGER DEFAULT NULL,
    DNS1 INTEGER DEFAULT NULL,
    DNS2 INTEGER DEFAULT NULL,
    DNS3 INTEGER DEFAULT NULL,
    Comments TEXT DEFAULT NULL
);
CREATE UNIQUE INDEX IF NOT EXISTS WIFI ON rsdump (BSSID, ESSID, WiFiKey);
CREATE INDEX IF NOT EXISTS BSSID_index ON rsdump (BSSID);
CREATE INDEX IF NOT EXISTS ESSID_index ON rsdump (ESSID);
CREATE INDEX IF NOT EXISTS Time_index ON rsdump (time);"""

mariadb_rsdump = """CREATE TABLE IF NOT EXISTS `rsdump` (
	`id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
	`time` TIMESTAMP NOT NULL DEFAULT current_timestamp(),
	`IP` INT(11) NOT NULL,
	`Port` SMALLINT(5) UNSIGNED NOT NULL,
	`status` TINYTEXT NOT NULL COLLATE 'utf8mb4_unicode_ci',
	`Authorization` TINYTEXT NULL DEFAULT NULL COLLATE 'utf8mb4_unicode_ci',
	`name` TINYTEXT NULL DEFAULT NULL COLLATE 'utf8mb4_unicode_ci',
	`RadioOff` BIT(1) NOT NULL DEFAULT b'0',
	`Hidden` BIT(1) NOT NULL DEFAULT b'0',
	`BSSID` BIGINT(20) UNSIGNED NULL DEFAULT NULL,
	`ESSID` VARCHAR(32) NULL DEFAULT NULL COLLATE 'utf8mb4_unicode_ci',
	`Security` TINYINT(3) UNSIGNED NULL DEFAULT NULL,
	`WiFiKey` VARCHAR(64) NULL DEFAULT NULL COLLATE 'utf8mb4_unicode_ci',
	`WPSPIN` INT(10) UNSIGNED NULL DEFAULT NULL,
	`LANIP` INT(11) NULL DEFAULT NULL,
	`LANMask` INT(11) NULL DEFAULT NULL,
	`WANIP` INT(11) NULL DEFAULT NULL,
	`WANMask` INT(11) NULL DEFAULT NULL,
	`WANGateway` INT(11) NULL DEFAULT NULL,
	`DNS1` INT(11) NULL DEFAULT NULL,
	`DNS2` INT(11) NULL DEFAULT NULL,
	`DNS3` INT(11) NULL DEFAULT NULL,
	`Comments` TEXT NULL DEFAULT NULL COLLATE 'utf8mb4_unicode_ci',
	PRIMARY KEY (`id`) USING BTREE,
	UNIQUE INDEX `WIFI` (`BSSID`, `ESSID`, `WiFiKey`) USING BTREE,
	INDEX `BSSID` (`BSSID`) USING BTREE,
	INDEX `ESSID` (`ESSID`) USING BTREE,
	INDEX `Time` (`time`) USING BTREE
) COLLATE='utf8mb4_unicode_ci' ENGINE=InnoDB;"""