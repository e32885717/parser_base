CREATE TABLE "anonymous_data" (
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
CREATE TABLE "networks" (
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
, "scanned_time"	INTEGER)CREATE TABLE "subtasks" (
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
CREATE TABLE "tasks" (
	"id"	INTEGER,
	"min_maxTileX"	TEXT,
	"min_maxTileY"	TEXT,
	"max_area"	INTEGER,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE "users" (
	"id"	INTEGER,
	"login"	TEXT UNIQUE,
	"password"	TEXT,
	PRIMARY KEY("id")
);