-- phpMyAdmin SQL Dump
-- version 5.2.3
-- https://www.phpmyadmin.net/
--
-- Host: localhost:8889
-- Generation Time: Oct 28, 2026 at 03:46 PM
-- Server version: 8.0.44
-- PHP Version: 8.3.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `information_schema`
--

-- --------------------------------------------------------

--
-- Stand-in structure for view `ADMINISTRABLE_ROLE_AUTHORIZATIONS`
-- (See below for the actual view)
--
CREATE TABLE `ADMINISTRABLE_ROLE_AUTHORIZATIONS` (
`GRANTEE` varchar(97)
,`GRANTEE_HOST` varchar(256)
,`HOST` varchar(256)
,`IS_DEFAULT` varchar(3)
,`IS_GRANTABLE` varchar(3)
,`IS_MANDATORY` varchar(3)
,`ROLE_HOST` varchar(256)
,`ROLE_NAME` varchar(255)
,`USER` varchar(97)
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `APPLICABLE_ROLES`
-- (See below for the actual view)
--
CREATE TABLE `APPLICABLE_ROLES` (
`GRANTEE` varchar(97)
,`GRANTEE_HOST` varchar(256)
,`HOST` varchar(256)
,`IS_DEFAULT` varchar(3)
,`IS_GRANTABLE` varchar(3)
,`IS_MANDATORY` varchar(3)
,`ROLE_HOST` varchar(256)
,`ROLE_NAME` varchar(255)
,`USER` varchar(97)
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `CHARACTER_SETS`
-- (See below for the actual view)
--
CREATE TABLE `CHARACTER_SETS` (
`CHARACTER_SET_NAME` varchar(64)
,`DEFAULT_COLLATE_NAME` varchar(64)
,`DESCRIPTION` varchar(2048)
,`MAXLEN` int unsigned
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `CHECK_CONSTRAINTS`
-- (See below for the actual view)
--
CREATE TABLE `CHECK_CONSTRAINTS` (
`CHECK_CLAUSE` longtext
,`CONSTRAINT_CATALOG` varchar(64)
,`CONSTRAINT_NAME` varchar(64)
,`CONSTRAINT_SCHEMA` varchar(64)
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `COLLATIONS`
-- (See below for the actual view)
--
CREATE TABLE `COLLATIONS` (
`CHARACTER_SET_NAME` varchar(64)
,`COLLATION_NAME` varchar(64)
,`ID` bigint unsigned
,`IS_COMPILED` varchar(3)
,`IS_DEFAULT` varchar(3)
,`PAD_ATTRIBUTE` enum('PAD SPACE','NO PAD')
,`SORTLEN` int unsigned
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `COLLATION_CHARACTER_SET_APPLICABILITY`
-- (See below for the actual view)
--
CREATE TABLE `COLLATION_CHARACTER_SET_APPLICABILITY` (
`CHARACTER_SET_NAME` varchar(64)
,`COLLATION_NAME` varchar(64)
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `COLUMNS`
-- (See below for the actual view)
--
CREATE TABLE `COLUMNS` (
`CHARACTER_MAXIMUM_LENGTH` bigint
,`CHARACTER_OCTET_LENGTH` bigint
,`CHARACTER_SET_NAME` varchar(64)
,`COLLATION_NAME` varchar(64)
,`COLUMN_COMMENT` text
,`COLUMN_DEFAULT` text
,`COLUMN_KEY` enum('','PRI','UNI','MUL')
,`COLUMN_NAME` varchar(64)
,`COLUMN_TYPE` mediumtext
,`DATA_TYPE` longtext
,`DATETIME_PRECISION` int unsigned
,`EXTRA` varchar(256)
,`GENERATION_EXPRESSION` longtext
,`IS_NULLABLE` varchar(3)
,`NUMERIC_PRECISION` bigint unsigned
,`NUMERIC_SCALE` bigint unsigned
,`ORDINAL_POSITION` int unsigned
,`PRIVILEGES` varchar(154)
,`SRS_ID` int unsigned
,`TABLE_CATALOG` varchar(64)
,`TABLE_NAME` varchar(64)
,`TABLE_SCHEMA` varchar(64)
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `COLUMNS_EXTENSIONS`
-- (See below for the actual view)
--
CREATE TABLE `COLUMNS_EXTENSIONS` (
`COLUMN_NAME` varchar(64)
,`ENGINE_ATTRIBUTE` json
,`SECONDARY_ENGINE_ATTRIBUTE` json
,`TABLE_CATALOG` varchar(64)
,`TABLE_NAME` varchar(64)
,`TABLE_SCHEMA` varchar(64)
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `COLUMN_PRIVILEGES`
-- (See below for the actual view)
--
CREATE TABLE `COLUMN_PRIVILEGES` (
`COLUMN_NAME` varchar(64)
,`GRANTEE` varchar(292)
,`IS_GRANTABLE` varchar(3)
,`PRIVILEGE_TYPE` varchar(64)
,`TABLE_CATALOG` varchar(512)
,`TABLE_NAME` varchar(64)
,`TABLE_SCHEMA` varchar(64)
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `COLUMN_STATISTICS`
-- (See below for the actual view)
--
CREATE TABLE `COLUMN_STATISTICS` (
`COLUMN_NAME` varchar(64)
,`HISTOGRAM` json
,`SCHEMA_NAME` varchar(64)
,`TABLE_NAME` varchar(64)
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `ENABLED_ROLES`
-- (See below for the actual view)
--
CREATE TABLE `ENABLED_ROLES` (
`IS_DEFAULT` varchar(3)
,`IS_MANDATORY` varchar(3)
,`ROLE_HOST` varchar(255)
,`ROLE_NAME` varchar(255)
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `ENGINES`
-- (See below for the actual view)
--
CREATE TABLE `ENGINES` (
`COMMENT` varchar(80)
,`ENGINE` varchar(64)
,`SAVEPOINTS` varchar(3)
,`SUPPORT` varchar(8)
,`TRANSACTIONS` varchar(3)
,`XA` varchar(3)
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `EVENTS`
-- (See below for the actual view)
--
CREATE TABLE `EVENTS` (
`CHARACTER_SET_CLIENT` varchar(64)
,`COLLATION_CONNECTION` varchar(64)
,`CREATED` timestamp
,`DATABASE_COLLATION` varchar(64)
,`DEFINER` varchar(288)
,`ENDS` datetime
,`EVENT_BODY` varchar(3)
,`EVENT_CATALOG` varchar(64)
,`EVENT_COMMENT` varchar(2048)
,`EVENT_DEFINITION` longtext
,`EVENT_NAME` varchar(64)
,`EVENT_SCHEMA` varchar(64)
,`EVENT_TYPE` varchar(9)
,`EXECUTE_AT` datetime
,`INTERVAL_FIELD` enum('YEAR','QUARTER','MONTH','DAY','HOUR','MINUTE','WEEK','SECOND','MICROSECOND','YEAR_MONTH','DAY_HOUR','DAY_MINUTE','DAY_SECOND','HOUR_MINUTE','HOUR_SECOND','MINUTE_SECOND','DAY_MICROSECOND','HOUR_MICROSECOND','MINUTE_MICROSECOND','SECOND_MICROSECOND')
,`INTERVAL_VALUE` varchar(256)
,`LAST_ALTERED` timestamp
,`LAST_EXECUTED` datetime
,`ON_COMPLETION` varchar(12)
,`ORIGINATOR` int unsigned
,`SQL_MODE` set('REAL_AS_FLOAT','PIPES_AS_CONCAT','ANSI_QUOTES','IGNORE_SPACE','NOT_USED','ONLY_FULL_GROUP_BY','NO_UNSIGNED_SUBTRACTION','NO_DIR_IN_CREATE','NOT_USED_9','NOT_USED_10','NOT_USED_11','NOT_USED_12','NOT_USED_13','NOT_USED_14','NOT_USED_15','NOT_USED_16','NOT_USED_17','NOT_USED_18','ANSI','NO_AUTO_VALUE_ON_ZERO','NO_BACKSLASH_ESCAPES','STRICT_TRANS_TABLES','STRICT_ALL_TABLES','NO_ZERO_IN_DATE','NO_ZERO_DATE','ALLOW_INVALID_DATES','ERROR_FOR_DIVISION_BY_ZERO','TRADITIONAL','NOT_USED_29','HIGH_NOT_PRECEDENCE','NO_ENGINE_SUBSTITUTION','PAD_CHAR_TO_FULL_LENGTH','TIME_TRUNCATE_FRACTIONAL')
,`STARTS` datetime
,`STATUS` enum('ENABLED','DISABLED','SLAVESIDE_DISABLED')
,`TIME_ZONE` varchar(64)
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `FILES`
-- (See below for the actual view)
--
CREATE TABLE `FILES` (
`AUTOEXTEND_SIZE` bigint
,`AVG_ROW_LENGTH` binary(0)
,`CHECK_TIME` binary(0)
,`CHECKSUM` binary(0)
,`CREATE_TIME` binary(0)
,`CREATION_TIME` binary(0)
,`DATA_FREE` bigint
,`DATA_LENGTH` binary(0)
,`DELETED_ROWS` binary(0)
,`ENGINE` varchar(64)
,`EXTENT_SIZE` bigint
,`EXTRA` varchar(256)
,`FILE_ID` bigint
,`FILE_NAME` text
,`FILE_TYPE` varchar(256)
,`FREE_EXTENTS` bigint
,`FULLTEXT_KEYS` binary(0)
,`INDEX_LENGTH` binary(0)
,`INITIAL_SIZE` bigint
,`LAST_ACCESS_TIME` binary(0)
,`LAST_UPDATE_TIME` binary(0)
,`LOGFILE_GROUP_NAME` varchar(256)
,`LOGFILE_GROUP_NUMBER` bigint
,`MAX_DATA_LENGTH` binary(0)
,`MAXIMUM_SIZE` bigint
,`RECOVER_TIME` binary(0)
,`ROW_FORMAT` varchar(256)
,`STATUS` varchar(256)
,`TABLE_CATALOG` char(0)
,`TABLE_NAME` binary(0)
,`TABLE_ROWS` binary(0)
,`TABLE_SCHEMA` binary(0)
,`TABLESPACE_NAME` varchar(268)
,`TOTAL_EXTENTS` bigint
,`TRANSACTION_COUNTER` binary(0)
,`UPDATE_COUNT` binary(0)
,`UPDATE_TIME` binary(0)
,`VERSION` bigint
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `INNODB_BUFFER_PAGE`
-- (See below for the actual view)
--
CREATE TABLE `INNODB_BUFFER_PAGE` (
`ACCESS_TIME` bigint unsigned
,`BLOCK_ID` bigint unsigned
,`COMPRESSED_SIZE` bigint unsigned
,`DATA_SIZE` bigint unsigned
,`FIX_COUNT` bigint unsigned
,`FLUSH_TYPE` bigint unsigned
,`FREE_PAGE_CLOCK` bigint unsigned
,`INDEX_NAME` varchar(1024)
,`IO_FIX` varchar(64)
,`IS_HASHED` varchar(3)
,`IS_OLD` varchar(3)
,`IS_STALE` varchar(3)
,`NEWEST_MODIFICATION` bigint unsigned
,`NUMBER_RECORDS` bigint unsigned
,`OLDEST_MODIFICATION` bigint unsigned
,`PAGE_NUMBER` bigint unsigned
,`PAGE_STATE` varchar(64)
,`PAGE_TYPE` varchar(64)
,`POOL_ID` bigint unsigned
,`SPACE` bigint unsigned
,`TABLE_NAME` varchar(1024)
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `INNODB_BUFFER_PAGE_LRU`
-- (See below for the actual view)
--
CREATE TABLE `INNODB_BUFFER_PAGE_LRU` (
`ACCESS_TIME` bigint unsigned
,`COMPRESSED` varchar(3)
,`COMPRESSED_SIZE` bigint unsigned
,`DATA_SIZE` bigint unsigned
,`FIX_COUNT` bigint unsigned
,`FLUSH_TYPE` bigint unsigned
,`FREE_PAGE_CLOCK` bigint unsigned
,`INDEX_NAME` varchar(1024)
,`IO_FIX` varchar(64)
,`IS_HASHED` varchar(3)
,`IS_OLD` varchar(3)
,`LRU_POSITION` bigint unsigned
,`NEWEST_MODIFICATION` bigint unsigned
,`NUMBER_RECORDS` bigint unsigned
,`OLDEST_MODIFICATION` bigint unsigned
,`PAGE_NUMBER` bigint unsigned
,`PAGE_TYPE` varchar(64)
,`POOL_ID` bigint unsigned
,`SPACE` bigint unsigned
,`TABLE_NAME` varchar(1024)
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `INNODB_BUFFER_POOL_STATS`
-- (See below for the actual view)
--
CREATE TABLE `INNODB_BUFFER_POOL_STATS` (
`DATABASE_PAGES` bigint unsigned
,`FREE_BUFFERS` bigint unsigned
,`HIT_RATE` bigint unsigned
,`LRU_IO_CURRENT` bigint unsigned
,`LRU_IO_TOTAL` bigint unsigned
,`MODIFIED_DATABASE_PAGES` bigint unsigned
,`NOT_YOUNG_MAKE_PER_THOUSAND_GETS` bigint unsigned
,`NUMBER_PAGES_CREATED` bigint unsigned
,`NUMBER_PAGES_GET` bigint unsigned
,`NUMBER_PAGES_READ` bigint unsigned
,`NUMBER_PAGES_READ_AHEAD` bigint unsigned
,`NUMBER_PAGES_WRITTEN` bigint unsigned
,`NUMBER_READ_AHEAD_EVICTED` bigint unsigned
,`OLD_DATABASE_PAGES` bigint unsigned
,`PAGES_CREATE_RATE` float(12,0)
,`PAGES_MADE_NOT_YOUNG_RATE` float(12,0)
,`PAGES_MADE_YOUNG` bigint unsigned
,`PAGES_MADE_YOUNG_RATE` float(12,0)
,`PAGES_NOT_MADE_YOUNG` bigint unsigned
,`PAGES_READ_RATE` float(12,0)
,`PAGES_WRITTEN_RATE` float(12,0)
,`PENDING_DECOMPRESS` bigint unsigned
,`PENDING_FLUSH_LIST` bigint unsigned
,`PENDING_FLUSH_LRU` bigint unsigned
,`PENDING_READS` bigint unsigned
,`POOL_ID` bigint unsigned
,`POOL_SIZE` bigint unsigned
,`READ_AHEAD_EVICTED_RATE` float(12,0)
,`READ_AHEAD_RATE` float(12,0)
,`UNCOMPRESS_CURRENT` bigint unsigned
,`UNCOMPRESS_TOTAL` bigint unsigned
,`YOUNG_MAKE_PER_THOUSAND_GETS` bigint unsigned
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `INNODB_CACHED_INDEXES`
-- (See below for the actual view)
--
CREATE TABLE `INNODB_CACHED_INDEXES` (
`INDEX_ID` bigint unsigned
,`N_CACHED_PAGES` bigint unsigned
,`SPACE_ID` int unsigned
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `INNODB_CMP`
-- (See below for the actual view)
--
CREATE TABLE `INNODB_CMP` (
`compress_ops` int
,`compress_ops_ok` int
,`compress_time` int
,`page_size` int
,`uncompress_ops` int
,`uncompress_time` int
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `INNODB_CMPMEM`
-- (See below for the actual view)
--
CREATE TABLE `INNODB_CMPMEM` (
`buffer_pool_instance` int
,`page_size` int
,`pages_free` int
,`pages_used` int
,`relocation_ops` bigint
,`relocation_time` int
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `INNODB_CMPMEM_RESET`
-- (See below for the actual view)
--
CREATE TABLE `INNODB_CMPMEM_RESET` (
`buffer_pool_instance` int
,`page_size` int
,`pages_free` int
,`pages_used` int
,`relocation_ops` bigint
,`relocation_time` int
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `INNODB_CMP_PER_INDEX`
-- (See below for the actual view)
--
CREATE TABLE `INNODB_CMP_PER_INDEX` (
`compress_ops` int
,`compress_ops_ok` int
,`compress_time` int
,`database_name` varchar(192)
,`index_name` varchar(192)
,`table_name` varchar(192)
,`uncompress_ops` int
,`uncompress_time` int
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `INNODB_CMP_PER_INDEX_RESET`
-- (See below for the actual view)
--
CREATE TABLE `INNODB_CMP_PER_INDEX_RESET` (
`compress_ops` int
,`compress_ops_ok` int
,`compress_time` int
,`database_name` varchar(192)
,`index_name` varchar(192)
,`table_name` varchar(192)
,`uncompress_ops` int
,`uncompress_time` int
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `INNODB_CMP_RESET`
-- (See below for the actual view)
--
CREATE TABLE `INNODB_CMP_RESET` (
`compress_ops` int
,`compress_ops_ok` int
,`compress_time` int
,`page_size` int
,`uncompress_ops` int
,`uncompress_time` int
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `INNODB_COLUMNS`
-- (See below for the actual view)
--
CREATE TABLE `INNODB_COLUMNS` (
`DEFAULT_VALUE` text
,`HAS_DEFAULT` int
,`LEN` int
,`MTYPE` int
,`NAME` varchar(193)
,`POS` bigint unsigned
,`PRTYPE` int
,`TABLE_ID` bigint unsigned
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `INNODB_DATAFILES`
-- (See below for the actual view)
--
CREATE TABLE `INNODB_DATAFILES` (
`PATH` varchar(512)
,`SPACE` varbinary(256)
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `INNODB_FIELDS`
-- (See below for the actual view)
--
CREATE TABLE `INNODB_FIELDS` (
`INDEX_ID` varbinary(256)
,`NAME` varchar(64)
,`POS` bigint unsigned
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `INNODB_FOREIGN`
-- (See below for the actual view)
--
CREATE TABLE `INNODB_FOREIGN` (
`FOR_NAME` varchar(129)
,`ID` varchar(129)
,`N_COLS` bigint
,`REF_NAME` varchar(129)
,`TYPE` bigint unsigned
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `INNODB_FOREIGN_COLS`
-- (See below for the actual view)
--
CREATE TABLE `INNODB_FOREIGN_COLS` (
`FOR_COL_NAME` varchar(64)
,`ID` varchar(129)
,`POS` int unsigned
,`REF_COL_NAME` varchar(64)
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `INNODB_FT_BEING_DELETED`
-- (See below for the actual view)
--
CREATE TABLE `INNODB_FT_BEING_DELETED` (
`DOC_ID` bigint unsigned
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `INNODB_FT_CONFIG`
-- (See below for the actual view)
--
CREATE TABLE `INNODB_FT_CONFIG` (
`KEY` varchar(193)
,`VALUE` varchar(193)
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `INNODB_FT_DEFAULT_STOPWORD`
-- (See below for the actual view)
--
CREATE TABLE `INNODB_FT_DEFAULT_STOPWORD` (
`value` varchar(18)
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `INNODB_FT_DELETED`
-- (See below for the actual view)
--
CREATE TABLE `INNODB_FT_DELETED` (
`DOC_ID` bigint unsigned
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `INNODB_FT_INDEX_CACHE`
-- (See below for the actual view)
--
CREATE TABLE `INNODB_FT_INDEX_CACHE` (
`DOC_COUNT` bigint unsigned
,`DOC_ID` bigint unsigned
,`FIRST_DOC_ID` bigint unsigned
,`LAST_DOC_ID` bigint unsigned
,`POSITION` bigint unsigned
,`WORD` varchar(337)
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `INNODB_FT_INDEX_TABLE`
-- (See below for the actual view)
--
CREATE TABLE `INNODB_FT_INDEX_TABLE` (
`DOC_COUNT` bigint unsigned
,`DOC_ID` bigint unsigned
,`FIRST_DOC_ID` bigint unsigned
,`LAST_DOC_ID` bigint unsigned
,`POSITION` bigint unsigned
,`WORD` varchar(337)
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `INNODB_INDEXES`
-- (See below for the actual view)
--
CREATE TABLE `INNODB_INDEXES` (
`INDEX_ID` bigint unsigned
,`MERGE_THRESHOLD` int
,`N_FIELDS` int
,`NAME` varchar(193)
,`PAGE_NO` int
,`SPACE` int
,`TABLE_ID` bigint unsigned
,`TYPE` int
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `INNODB_METRICS`
-- (See below for the actual view)
--
CREATE TABLE `INNODB_METRICS` (
`AVG_COUNT` float(12,0)
,`AVG_COUNT_RESET` float(12,0)
,`COMMENT` varchar(193)
,`COUNT` bigint
,`COUNT_RESET` bigint
,`MAX_COUNT` bigint
,`MAX_COUNT_RESET` bigint
,`MIN_COUNT` bigint
,`MIN_COUNT_RESET` bigint
,`NAME` varchar(193)
,`STATUS` varchar(193)
,`SUBSYSTEM` varchar(193)
,`TIME_DISABLED` datetime
,`TIME_ELAPSED` bigint
,`TIME_ENABLED` datetime
,`TIME_RESET` datetime
,`TYPE` varchar(193)
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `INNODB_SESSION_TEMP_TABLESPACES`
-- (See below for the actual view)
--
CREATE TABLE `INNODB_SESSION_TEMP_TABLESPACES` (
`ID` int unsigned
,`PATH` varchar(4001)
,`PURPOSE` varchar(192)
,`SIZE` bigint unsigned
,`SPACE` int unsigned
,`STATE` varchar(192)
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `INNODB_TABLES`
-- (See below for the actual view)
--
CREATE TABLE `INNODB_TABLES` (
`FLAG` int
,`INSTANT_COLS` int
,`N_COLS` int
,`NAME` varchar(655)
,`ROW_FORMAT` varchar(12)
,`SPACE` bigint
,`SPACE_TYPE` varchar(10)
,`TABLE_ID` bigint unsigned
,`ZIP_PAGE_SIZE` int unsigned
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `INNODB_TABLESPACES`
-- (See below for the actual view)
--
CREATE TABLE `INNODB_TABLESPACES` (
`ALLOCATED_SIZE` bigint unsigned
,`AUTOEXTEND_SIZE` bigint unsigned
,`ENCRYPTION` varchar(1)
,`FILE_SIZE` bigint unsigned
,`FLAG` int unsigned
,`FS_BLOCK_SIZE` int unsigned
,`NAME` varchar(655)
,`PAGE_SIZE` int unsigned
,`ROW_FORMAT` varchar(22)
,`SERVER_VERSION` varchar(10)
,`SPACE` int unsigned
,`SPACE_TYPE` varchar(10)
,`SPACE_VERSION` int unsigned
,`STATE` varchar(10)
,`ZIP_PAGE_SIZE` int unsigned
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `INNODB_TABLESPACES_BRIEF`
-- (See below for the actual view)
--
CREATE TABLE `INNODB_TABLESPACES_BRIEF` (
`FLAG` varbinary(256)
,`NAME` varchar(268)
,`PATH` varchar(512)
,`SPACE` varbinary(256)
,`SPACE_TYPE` varchar(7)
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `INNODB_TABLESTATS`
-- (See below for the actual view)
--
CREATE TABLE `INNODB_TABLESTATS` (
`AUTOINC` bigint unsigned
,`CLUST_INDEX_SIZE` bigint unsigned
,`MODIFIED_COUNTER` bigint unsigned
,`NAME` varchar(193)
,`NUM_ROWS` bigint unsigned
,`OTHER_INDEX_SIZE` bigint unsigned
,`REF_COUNT` int
,`STATS_INITIALIZED` varchar(193)
,`TABLE_ID` bigint unsigned
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `INNODB_TEMP_TABLE_INFO`
-- (See below for the actual view)
--
CREATE TABLE `INNODB_TEMP_TABLE_INFO` (
`N_COLS` int unsigned
,`NAME` varchar(64)
,`SPACE` int unsigned
,`TABLE_ID` bigint unsigned
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `INNODB_TRX`
-- (See below for the actual view)
--
CREATE TABLE `INNODB_TRX` (
`trx_adaptive_hash_latched` int
,`trx_adaptive_hash_timeout` bigint unsigned
,`trx_autocommit_non_locking` int
,`trx_concurrency_tickets` bigint unsigned
,`trx_foreign_key_checks` int
,`trx_id` bigint unsigned
,`trx_is_read_only` int
,`trx_isolation_level` varchar(16)
,`trx_last_foreign_key_error` varchar(256)
,`trx_lock_memory_bytes` bigint unsigned
,`trx_lock_structs` bigint unsigned
,`trx_mysql_thread_id` bigint unsigned
,`trx_operation_state` varchar(64)
,`trx_query` varchar(1024)
,`trx_requested_lock_id` varchar(105)
,`trx_rows_locked` bigint unsigned
,`trx_rows_modified` bigint unsigned
,`trx_schedule_weight` bigint unsigned
,`trx_started` datetime
,`trx_state` varchar(13)
,`trx_tables_in_use` bigint unsigned
,`trx_tables_locked` bigint unsigned
,`trx_unique_checks` int
,`trx_wait_started` datetime
,`trx_weight` bigint unsigned
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `INNODB_VIRTUAL`
-- (See below for the actual view)
--
CREATE TABLE `INNODB_VIRTUAL` (
`BASE_POS` int unsigned
,`POS` int unsigned
,`TABLE_ID` bigint unsigned
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `KEYWORDS`
-- (See below for the actual view)
--
CREATE TABLE `KEYWORDS` (
`RESERVED` int
,`WORD` varchar(128)
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `KEY_COLUMN_USAGE`
-- (See below for the actual view)
--
CREATE TABLE `KEY_COLUMN_USAGE` (
`COLUMN_NAME` varchar(64)
,`CONSTRAINT_CATALOG` varchar(64)
,`CONSTRAINT_NAME` varchar(64)
,`CONSTRAINT_SCHEMA` varchar(64)
,`ORDINAL_POSITION` int unsigned
,`POSITION_IN_UNIQUE_CONSTRAINT` int unsigned
,`REFERENCED_COLUMN_NAME` varchar(64)
,`REFERENCED_TABLE_NAME` varchar(64)
,`REFERENCED_TABLE_SCHEMA` varchar(64)
,`TABLE_CATALOG` varchar(64)
,`TABLE_NAME` varchar(64)
,`TABLE_SCHEMA` varchar(64)
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `OPTIMIZER_TRACE`
-- (See below for the actual view)
--
CREATE TABLE `OPTIMIZER_TRACE` (
`INSUFFICIENT_PRIVILEGES` tinyint(1)
,`MISSING_BYTES_BEYOND_MAX_MEM_SIZE` int
,`QUERY` varchar(65535)
,`TRACE` varchar(65535)
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `PARAMETERS`
-- (See below for the actual view)
--
CREATE TABLE `PARAMETERS` (
`CHARACTER_MAXIMUM_LENGTH` bigint
,`CHARACTER_OCTET_LENGTH` bigint
,`CHARACTER_SET_NAME` varchar(64)
,`COLLATION_NAME` varchar(64)
,`DATA_TYPE` longtext
,`DATETIME_PRECISION` int unsigned
,`DTD_IDENTIFIER` mediumtext
,`NUMERIC_PRECISION` int unsigned
,`NUMERIC_SCALE` bigint
,`ORDINAL_POSITION` bigint unsigned
,`PARAMETER_MODE` varchar(5)
,`PARAMETER_NAME` varchar(64)
,`ROUTINE_TYPE` enum('FUNCTION','PROCEDURE')
,`SPECIFIC_CATALOG` varchar(64)
,`SPECIFIC_NAME` varchar(64)
,`SPECIFIC_SCHEMA` varchar(64)
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `PARTITIONS`
-- (See below for the actual view)
--
CREATE TABLE `PARTITIONS` (
`AVG_ROW_LENGTH` bigint unsigned
,`CHECK_TIME` datetime
,`CHECKSUM` bigint
,`CREATE_TIME` timestamp
,`DATA_FREE` bigint unsigned
,`DATA_LENGTH` bigint unsigned
,`INDEX_LENGTH` bigint unsigned
,`MAX_DATA_LENGTH` bigint unsigned
,`NODEGROUP` varchar(256)
,`PARTITION_COMMENT` text
,`PARTITION_DESCRIPTION` text
,`PARTITION_EXPRESSION` varchar(2048)
,`PARTITION_METHOD` varchar(13)
,`PARTITION_NAME` varchar(64)
,`PARTITION_ORDINAL_POSITION` int unsigned
,`SUBPARTITION_EXPRESSION` varchar(2048)
,`SUBPARTITION_METHOD` varchar(13)
,`SUBPARTITION_NAME` varchar(64)
,`SUBPARTITION_ORDINAL_POSITION` int unsigned
,`TABLE_CATALOG` varchar(64)
,`TABLE_NAME` varchar(64)
,`TABLE_ROWS` bigint unsigned
,`TABLE_SCHEMA` varchar(64)
,`TABLESPACE_NAME` varchar(268)
,`UPDATE_TIME` datetime
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `PLUGINS`
-- (See below for the actual view)
--
CREATE TABLE `PLUGINS` (
`LOAD_OPTION` varchar(64)
,`PLUGIN_AUTHOR` varchar(64)
,`PLUGIN_DESCRIPTION` varchar(65535)
,`PLUGIN_LIBRARY` varchar(64)
,`PLUGIN_LIBRARY_VERSION` varchar(20)
,`PLUGIN_LICENSE` varchar(80)
,`PLUGIN_NAME` varchar(64)
,`PLUGIN_STATUS` varchar(10)
,`PLUGIN_TYPE` varchar(80)
,`PLUGIN_TYPE_VERSION` varchar(20)
,`PLUGIN_VERSION` varchar(20)
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `PROCESSLIST`
-- (See below for the actual view)
--
CREATE TABLE `PROCESSLIST` (
`COMMAND` varchar(16)
,`DB` varchar(64)
,`HOST` varchar(261)
,`ID` bigint unsigned
,`INFO` varchar(65535)
,`STATE` varchar(64)
,`TIME` int
,`USER` varchar(32)
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `PROFILING`
-- (See below for the actual view)
--
CREATE TABLE `PROFILING` (
`BLOCK_OPS_IN` int
,`BLOCK_OPS_OUT` int
,`CONTEXT_INVOLUNTARY` int
,`CONTEXT_VOLUNTARY` int
,`CPU_SYSTEM` decimal(905,0)
,`CPU_USER` decimal(905,0)
,`DURATION` decimal(905,0)
,`MESSAGES_RECEIVED` int
,`MESSAGES_SENT` int
,`PAGE_FAULTS_MAJOR` int
,`PAGE_FAULTS_MINOR` int
,`QUERY_ID` int
,`SEQ` int
,`SOURCE_FILE` varchar(20)
,`SOURCE_FUNCTION` varchar(30)
,`SOURCE_LINE` int
,`STATE` varchar(30)
,`SWAPS` int
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `REFERENTIAL_CONSTRAINTS`
-- (See below for the actual view)
--
CREATE TABLE `REFERENTIAL_CONSTRAINTS` (
`CONSTRAINT_CATALOG` varchar(64)
,`CONSTRAINT_NAME` varchar(64)
,`CONSTRAINT_SCHEMA` varchar(64)
,`DELETE_RULE` enum('NO ACTION','RESTRICT','CASCADE','SET NULL','SET DEFAULT')
,`MATCH_OPTION` enum('NONE','PARTIAL','FULL')
,`REFERENCED_TABLE_NAME` varchar(64)
,`TABLE_NAME` varchar(64)
,`UNIQUE_CONSTRAINT_CATALOG` varchar(64)
,`UNIQUE_CONSTRAINT_NAME` varchar(64)
,`UNIQUE_CONSTRAINT_SCHEMA` varchar(64)
,`UPDATE_RULE` enum('NO ACTION','RESTRICT','CASCADE','SET NULL','SET DEFAULT')
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `RESOURCE_GROUPS`
-- (See below for the actual view)
--
CREATE TABLE `RESOURCE_GROUPS` (
`RESOURCE_GROUP_ENABLED` tinyint(1)
,`RESOURCE_GROUP_NAME` varchar(64)
,`RESOURCE_GROUP_TYPE` enum('SYSTEM','USER')
,`THREAD_PRIORITY` int
,`VCPU_IDS` blob
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `ROLE_COLUMN_GRANTS`
-- (See below for the actual view)
--
CREATE TABLE `ROLE_COLUMN_GRANTS` (
`COLUMN_NAME` char(64)
,`GRANTEE` char(32)
,`GRANTEE_HOST` char(255)
,`GRANTOR` varchar(97)
,`GRANTOR_HOST` varchar(256)
,`IS_GRANTABLE` varchar(3)
,`PRIVILEGE_TYPE` set('Select','Insert','Update','References')
,`TABLE_CATALOG` varchar(3)
,`TABLE_NAME` char(64)
,`TABLE_SCHEMA` char(64)
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `ROLE_ROUTINE_GRANTS`
-- (See below for the actual view)
--
CREATE TABLE `ROLE_ROUTINE_GRANTS` (
`GRANTEE` char(32)
,`GRANTEE_HOST` char(255)
,`GRANTOR` varchar(97)
,`GRANTOR_HOST` varchar(256)
,`IS_GRANTABLE` varchar(3)
,`PRIVILEGE_TYPE` set('Execute','Alter Routine','Grant')
,`ROUTINE_CATALOG` varchar(3)
,`ROUTINE_NAME` char(64)
,`ROUTINE_SCHEMA` char(64)
,`SPECIFIC_CATALOG` varchar(3)
,`SPECIFIC_NAME` char(64)
,`SPECIFIC_SCHEMA` char(64)
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `ROLE_TABLE_GRANTS`
-- (See below for the actual view)
--
CREATE TABLE `ROLE_TABLE_GRANTS` (
`GRANTEE` char(32)
,`GRANTEE_HOST` char(255)
,`GRANTOR` varchar(97)
,`GRANTOR_HOST` varchar(256)
,`IS_GRANTABLE` varchar(3)
,`PRIVILEGE_TYPE` set('Select','Insert','Update','Delete','Create','Drop','Grant','References','Index','Alter','Create View','Show view','Trigger')
,`TABLE_CATALOG` varchar(3)
,`TABLE_NAME` char(64)
,`TABLE_SCHEMA` char(64)
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `ROUTINES`
-- (See below for the actual view)
--
CREATE TABLE `ROUTINES` (
`CHARACTER_MAXIMUM_LENGTH` bigint
,`CHARACTER_OCTET_LENGTH` bigint
,`CHARACTER_SET_CLIENT` varchar(64)
,`CHARACTER_SET_NAME` varchar(64)
,`COLLATION_CONNECTION` varchar(64)
,`COLLATION_NAME` varchar(64)
,`CREATED` timestamp
,`DATA_TYPE` longtext
,`DATABASE_COLLATION` varchar(64)
,`DATETIME_PRECISION` int unsigned
,`DEFINER` varchar(288)
,`DTD_IDENTIFIER` longtext
,`EXTERNAL_LANGUAGE` varchar(64)
,`EXTERNAL_NAME` binary(0)
,`IS_DETERMINISTIC` varchar(3)
,`LAST_ALTERED` timestamp
,`NUMERIC_PRECISION` int unsigned
,`NUMERIC_SCALE` int unsigned
,`PARAMETER_STYLE` varchar(3)
,`ROUTINE_BODY` varchar(3)
,`ROUTINE_CATALOG` varchar(64)
,`ROUTINE_COMMENT` text
,`ROUTINE_DEFINITION` longtext
,`ROUTINE_NAME` varchar(64)
,`ROUTINE_SCHEMA` varchar(64)
,`ROUTINE_TYPE` enum('FUNCTION','PROCEDURE')
,`SECURITY_TYPE` enum('DEFAULT','INVOKER','DEFINER')
,`SPECIFIC_NAME` varchar(64)
,`SQL_DATA_ACCESS` enum('CONTAINS SQL','NO SQL','READS SQL DATA','MODIFIES SQL DATA')
,`SQL_MODE` set('REAL_AS_FLOAT','PIPES_AS_CONCAT','ANSI_QUOTES','IGNORE_SPACE','NOT_USED','ONLY_FULL_GROUP_BY','NO_UNSIGNED_SUBTRACTION','NO_DIR_IN_CREATE','NOT_USED_9','NOT_USED_10','NOT_USED_11','NOT_USED_12','NOT_USED_13','NOT_USED_14','NOT_USED_15','NOT_USED_16','NOT_USED_17','NOT_USED_18','ANSI','NO_AUTO_VALUE_ON_ZERO','NO_BACKSLASH_ESCAPES','STRICT_TRANS_TABLES','STRICT_ALL_TABLES','NO_ZERO_IN_DATE','NO_ZERO_DATE','ALLOW_INVALID_DATES','ERROR_FOR_DIVISION_BY_ZERO','TRADITIONAL','NOT_USED_29','HIGH_NOT_PRECEDENCE','NO_ENGINE_SUBSTITUTION','PAD_CHAR_TO_FULL_LENGTH','TIME_TRUNCATE_FRACTIONAL')
,`SQL_PATH` binary(0)
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `SCHEMATA`
-- (See below for the actual view)
--
CREATE TABLE `SCHEMATA` (
`CATALOG_NAME` varchar(64)
,`DEFAULT_CHARACTER_SET_NAME` varchar(64)
,`DEFAULT_COLLATION_NAME` varchar(64)
,`DEFAULT_ENCRYPTION` enum('NO','YES')
,`SCHEMA_NAME` varchar(64)
,`SQL_PATH` binary(0)
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `SCHEMATA_EXTENSIONS`
-- (See below for the actual view)
--
CREATE TABLE `SCHEMATA_EXTENSIONS` (
`CATALOG_NAME` varchar(64)
,`OPTIONS` varchar(256)
,`SCHEMA_NAME` varchar(64)
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `SCHEMA_PRIVILEGES`
-- (See below for the actual view)
--
CREATE TABLE `SCHEMA_PRIVILEGES` (
`GRANTEE` varchar(292)
,`IS_GRANTABLE` varchar(3)
,`PRIVILEGE_TYPE` varchar(64)
,`TABLE_CATALOG` varchar(512)
,`TABLE_SCHEMA` varchar(64)
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `STATISTICS`
-- (See below for the actual view)
--
CREATE TABLE `STATISTICS` (
`CARDINALITY` bigint
,`COLLATION` varchar(1)
,`COLUMN_NAME` varchar(64)
,`COMMENT` varchar(8)
,`EXPRESSION` longtext
,`INDEX_COMMENT` varchar(2048)
,`INDEX_NAME` varchar(64)
,`INDEX_SCHEMA` varchar(64)
,`INDEX_TYPE` varchar(11)
,`IS_VISIBLE` varchar(3)
,`NON_UNIQUE` int
,`NULLABLE` varchar(3)
,`PACKED` binary(0)
,`SEQ_IN_INDEX` int unsigned
,`SUB_PART` bigint
,`TABLE_CATALOG` varchar(64)
,`TABLE_NAME` varchar(64)
,`TABLE_SCHEMA` varchar(64)
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `ST_GEOMETRY_COLUMNS`
-- (See below for the actual view)
--
CREATE TABLE `ST_GEOMETRY_COLUMNS` (
`COLUMN_NAME` varchar(64)
,`GEOMETRY_TYPE_NAME` longtext
,`SRS_ID` int unsigned
,`SRS_NAME` varchar(80)
,`TABLE_CATALOG` varchar(64)
,`TABLE_NAME` varchar(64)
,`TABLE_SCHEMA` varchar(64)
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `ST_SPATIAL_REFERENCE_SYSTEMS`
-- (See below for the actual view)
--
CREATE TABLE `ST_SPATIAL_REFERENCE_SYSTEMS` (
`DEFINITION` varchar(4096)
,`DESCRIPTION` varchar(2048)
,`ORGANIZATION` varchar(256)
,`ORGANIZATION_COORDSYS_ID` int unsigned
,`SRS_ID` int unsigned
,`SRS_NAME` varchar(80)
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `ST_UNITS_OF_MEASURE`
-- (See below for the actual view)
--
CREATE TABLE `ST_UNITS_OF_MEASURE` (
`CONVERSION_FACTOR` double
,`DESCRIPTION` varchar(255)
,`UNIT_NAME` varchar(255)
,`UNIT_TYPE` varchar(7)
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `TABLES`
-- (See below for the actual view)
--
CREATE TABLE `TABLES` (
`AUTO_INCREMENT` bigint unsigned
,`AVG_ROW_LENGTH` bigint unsigned
,`CHECK_TIME` datetime
,`CHECKSUM` bigint
,`CREATE_OPTIONS` varchar(256)
,`CREATE_TIME` timestamp
,`DATA_FREE` bigint unsigned
,`DATA_LENGTH` bigint unsigned
,`ENGINE` varchar(64)
,`INDEX_LENGTH` bigint unsigned
,`MAX_DATA_LENGTH` bigint unsigned
,`ROW_FORMAT` enum('Fixed','Dynamic','Compressed','Redundant','Compact','Paged')
,`TABLE_CATALOG` varchar(64)
,`TABLE_COLLATION` varchar(64)
,`TABLE_COMMENT` text
,`TABLE_NAME` varchar(64)
,`TABLE_ROWS` bigint unsigned
,`TABLE_SCHEMA` varchar(64)
,`TABLE_TYPE` enum('BASE TABLE','VIEW','SYSTEM VIEW')
,`UPDATE_TIME` datetime
,`VERSION` int
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `TABLESPACES`
-- (See below for the actual view)
--
CREATE TABLE `TABLESPACES` (
`AUTOEXTEND_SIZE` bigint unsigned
,`ENGINE` varchar(64)
,`EXTENT_SIZE` bigint unsigned
,`LOGFILE_GROUP_NAME` varchar(64)
,`MAXIMUM_SIZE` bigint unsigned
,`NODEGROUP_ID` bigint unsigned
,`TABLESPACE_COMMENT` varchar(2048)
,`TABLESPACE_NAME` varchar(64)
,`TABLESPACE_TYPE` varchar(64)
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `TABLESPACES_EXTENSIONS`
-- (See below for the actual view)
--
CREATE TABLE `TABLESPACES_EXTENSIONS` (
`ENGINE_ATTRIBUTE` json
,`TABLESPACE_NAME` varchar(268)
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `TABLES_EXTENSIONS`
-- (See below for the actual view)
--
CREATE TABLE `TABLES_EXTENSIONS` (
`ENGINE_ATTRIBUTE` json
,`SECONDARY_ENGINE_ATTRIBUTE` json
,`TABLE_CATALOG` varchar(64)
,`TABLE_NAME` varchar(64)
,`TABLE_SCHEMA` varchar(64)
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `TABLE_CONSTRAINTS`
-- (See below for the actual view)
--
CREATE TABLE `TABLE_CONSTRAINTS` (
`CONSTRAINT_CATALOG` varchar(64)
,`CONSTRAINT_NAME` varchar(64)
,`CONSTRAINT_SCHEMA` varchar(64)
,`CONSTRAINT_TYPE` varchar(11)
,`ENFORCED` varchar(3)
,`TABLE_NAME` varchar(64)
,`TABLE_SCHEMA` varchar(64)
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `TABLE_CONSTRAINTS_EXTENSIONS`
-- (See below for the actual view)
--
CREATE TABLE `TABLE_CONSTRAINTS_EXTENSIONS` (
`CONSTRAINT_CATALOG` varchar(64)
,`CONSTRAINT_NAME` varchar(64)
,`CONSTRAINT_SCHEMA` varchar(64)
,`ENGINE_ATTRIBUTE` json
,`SECONDARY_ENGINE_ATTRIBUTE` json
,`TABLE_NAME` varchar(64)
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `TABLE_PRIVILEGES`
-- (See below for the actual view)
--
CREATE TABLE `TABLE_PRIVILEGES` (
`GRANTEE` varchar(292)
,`IS_GRANTABLE` varchar(3)
,`PRIVILEGE_TYPE` varchar(64)
,`TABLE_CATALOG` varchar(512)
,`TABLE_NAME` varchar(64)
,`TABLE_SCHEMA` varchar(64)
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `TRIGGERS`
-- (See below for the actual view)
--
CREATE TABLE `TRIGGERS` (
`ACTION_CONDITION` binary(0)
,`ACTION_ORDER` int unsigned
,`ACTION_ORIENTATION` varchar(3)
,`ACTION_REFERENCE_NEW_ROW` varchar(3)
,`ACTION_REFERENCE_NEW_TABLE` binary(0)
,`ACTION_REFERENCE_OLD_ROW` varchar(3)
,`ACTION_REFERENCE_OLD_TABLE` binary(0)
,`ACTION_STATEMENT` longtext
,`ACTION_TIMING` enum('BEFORE','AFTER')
,`CHARACTER_SET_CLIENT` varchar(64)
,`COLLATION_CONNECTION` varchar(64)
,`CREATED` timestamp(2)
,`DATABASE_COLLATION` varchar(64)
,`DEFINER` varchar(288)
,`EVENT_MANIPULATION` enum('INSERT','UPDATE','DELETE')
,`EVENT_OBJECT_CATALOG` varchar(64)
,`EVENT_OBJECT_SCHEMA` varchar(64)
,`EVENT_OBJECT_TABLE` varchar(64)
,`SQL_MODE` set('REAL_AS_FLOAT','PIPES_AS_CONCAT','ANSI_QUOTES','IGNORE_SPACE','NOT_USED','ONLY_FULL_GROUP_BY','NO_UNSIGNED_SUBTRACTION','NO_DIR_IN_CREATE','NOT_USED_9','NOT_USED_10','NOT_USED_11','NOT_USED_12','NOT_USED_13','NOT_USED_14','NOT_USED_15','NOT_USED_16','NOT_USED_17','NOT_USED_18','ANSI','NO_AUTO_VALUE_ON_ZERO','NO_BACKSLASH_ESCAPES','STRICT_TRANS_TABLES','STRICT_ALL_TABLES','NO_ZERO_IN_DATE','NO_ZERO_DATE','ALLOW_INVALID_DATES','ERROR_FOR_DIVISION_BY_ZERO','TRADITIONAL','NOT_USED_29','HIGH_NOT_PRECEDENCE','NO_ENGINE_SUBSTITUTION','PAD_CHAR_TO_FULL_LENGTH','TIME_TRUNCATE_FRACTIONAL')
,`TRIGGER_CATALOG` varchar(64)
,`TRIGGER_NAME` varchar(64)
,`TRIGGER_SCHEMA` varchar(64)
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `USER_ATTRIBUTES`
-- (See below for the actual view)
--
CREATE TABLE `USER_ATTRIBUTES` (
`ATTRIBUTE` longtext
,`HOST` char(255)
,`USER` char(32)
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `USER_PRIVILEGES`
-- (See below for the actual view)
--
CREATE TABLE `USER_PRIVILEGES` (
`GRANTEE` varchar(292)
,`IS_GRANTABLE` varchar(3)
,`PRIVILEGE_TYPE` varchar(64)
,`TABLE_CATALOG` varchar(512)
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `VIEWS`
-- (See below for the actual view)
--
CREATE TABLE `VIEWS` (
`CHARACTER_SET_CLIENT` varchar(64)
,`CHECK_OPTION` enum('NONE','LOCAL','CASCADED')
,`COLLATION_CONNECTION` varchar(64)
,`DEFINER` varchar(288)
,`IS_UPDATABLE` enum('NO','YES')
,`SECURITY_TYPE` varchar(7)
,`TABLE_CATALOG` varchar(64)
,`TABLE_NAME` varchar(64)
,`TABLE_SCHEMA` varchar(64)
,`VIEW_DEFINITION` longtext
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `VIEW_ROUTINE_USAGE`
-- (See below for the actual view)
--
CREATE TABLE `VIEW_ROUTINE_USAGE` (
`SPECIFIC_CATALOG` varchar(64)
,`SPECIFIC_NAME` varchar(64)
,`SPECIFIC_SCHEMA` varchar(64)
,`TABLE_CATALOG` varchar(64)
,`TABLE_NAME` varchar(64)
,`TABLE_SCHEMA` varchar(64)
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `VIEW_TABLE_USAGE`
-- (See below for the actual view)
--
CREATE TABLE `VIEW_TABLE_USAGE` (
`TABLE_CATALOG` varchar(64)
,`TABLE_NAME` varchar(64)
,`TABLE_SCHEMA` varchar(64)
,`VIEW_CATALOG` varchar(64)
,`VIEW_NAME` varchar(64)
,`VIEW_SCHEMA` varchar(64)
);

-- --------------------------------------------------------

--
-- Structure for view `ADMINISTRABLE_ROLE_AUTHORIZATIONS`
--
DROP TABLE IF EXISTS `ADMINISTRABLE_ROLE_AUTHORIZATIONS`;

CREATE ALGORITHM=UNDEFINED DEFINER=`mysql.infoschema`@`localhost` SQL SECURITY DEFINER VIEW `ADMINISTRABLE_ROLE_AUTHORIZATIONS`  AS SELECT `applicable_roles`.`USER` AS `USER`, `applicable_roles`.`HOST` AS `HOST`, `applicable_roles`.`GRANTEE` AS `GRANTEE`, `applicable_roles`.`GRANTEE_HOST` AS `GRANTEE_HOST`, `applicable_roles`.`ROLE_NAME` AS `ROLE_NAME`, `applicable_roles`.`ROLE_HOST` AS `ROLE_HOST`, `applicable_roles`.`IS_GRANTABLE` AS `IS_GRANTABLE`, `applicable_roles`.`IS_DEFAULT` AS `IS_DEFAULT`, `applicable_roles`.`IS_MANDATORY` AS `IS_MANDATORY` FROM `APPLICABLE_ROLES` WHERE (`applicable_roles`.`IS_GRANTABLE` = 'YES') ;

-- --------------------------------------------------------

--
-- Structure for view `APPLICABLE_ROLES`
--
DROP TABLE IF EXISTS `APPLICABLE_ROLES`;

CREATE ALGORITHM=UNDEFINED DEFINER=`mysql.infoschema`@`localhost` SQL SECURITY DEFINER VIEW `APPLICABLE_ROLES`  AS WITH recursive   `role_graph` (`c_parent_user`,`c_parent_host`,`c_from_user`,`c_from_host`,`c_to_user`,`c_to_host`,`role_path`,`c_with_admin`,`c_enabled`) as (select internal_get_username() AS `INTERNAL_GET_USERNAME()`,internal_get_hostname() AS `INTERNAL_GET_HOSTNAME()`,internal_get_username() AS `INTERNAL_GET_USERNAME()`,internal_get_hostname() AS `INTERNAL_GET_HOSTNAME()`,cast('' as char(64) charset utf8mb4) AS `CAST('' as CHAR(64) CHARSET utf8mb4)`,cast('' as char(255) charset utf8mb4) AS `CAST('' as CHAR(255) CHARSET utf8mb4)`,cast(sha2(concat(quote(internal_get_username()),'@',quote(internal_get_hostname())),256) as char(17000) charset utf8mb4) AS `CAST(SHA2(CONCAT(QUOTE(INTERNAL_GET_USERNAME()),'@',                        QUOTE(INTERNAL_GET_HOSTNAME())), 256)            AS CHAR(17000) CHARSET utf8mb4)`,cast('N' as char(1) charset utf8mb4) AS `CAST('N' as CHAR(1) CHARSET utf8mb4)`,false AS `FALSE` union select internal_get_username() AS `INTERNAL_GET_USERNAME()`,internal_get_hostname() AS `INTERNAL_GET_HOSTNAME()`,`mandatory_roles`.`ROLE_NAME` AS `ROLE_NAME`,`mandatory_roles`.`ROLE_HOST` AS `ROLE_HOST`,internal_get_username() AS `INTERNAL_GET_USERNAME()`,internal_get_hostname() AS `INTERNAL_GET_HOSTNAME()`,cast(sha2(concat(quote(`mandatory_roles`.`ROLE_NAME`),'@',convert(quote(`mandatory_roles`.`ROLE_HOST`) using utf8mb4)),256) as char(17000) charset utf8mb4) AS `CAST(SHA2(CONCAT(QUOTE(ROLE_NAME),'@',                   CONVERT(QUOTE(ROLE_HOST) using utf8mb4)), 256)              AS CHAR(17000) CHARSET utf8mb4)`,cast('N' as char(1) charset utf8mb4) AS `CAST('N' as CHAR(1) CHARSET utf8mb4)`,false AS `FALSE` from json_table(internal_get_mandatory_roles_json(), '$[*]' columns (`ROLE_NAME` varchar(255) character set utf8mb4 path '$.ROLE_NAME', `ROLE_HOST` varchar(255) character set utf8mb4 path '$.ROLE_HOST')) `mandatory_roles` where concat(quote(`mandatory_roles`.`ROLE_NAME`),'@',convert(quote(`mandatory_roles`.`ROLE_HOST`) using utf8mb4)) in (select concat(convert(quote(`mysql`.`role_edges`.`FROM_USER`) using utf8mb4),'@',convert(quote(`mysql`.`role_edges`.`FROM_HOST`) using utf8mb4)) from `mysql`.`role_edges` where ((`mysql`.`role_edges`.`TO_USER` = internal_get_username()) and (convert(`mysql`.`role_edges`.`TO_HOST` using utf8mb4) = convert(internal_get_hostname() using utf8mb4)))) is false union select `role_graph`.`c_parent_user` AS `c_parent_user`,`role_graph`.`c_parent_host` AS `c_parent_host`,`mysql`.`role_edges`.`FROM_USER` AS `FROM_USER`,`mysql`.`role_edges`.`FROM_HOST` AS `FROM_HOST`,`mysql`.`role_edges`.`TO_USER` AS `TO_USER`,`mysql`.`role_edges`.`TO_HOST` AS `TO_HOST`,if((locate(sha2(concat(convert(quote(`mysql`.`role_edges`.`FROM_USER`) using utf8mb4),'@',convert(quote(`mysql`.`role_edges`.`FROM_HOST`) using utf8mb4)),256),`role_graph`.`role_path`) = 0),concat(`role_graph`.`role_path`,'->',convert(sha2(concat(convert(quote(`mysql`.`role_edges`.`FROM_USER`) using utf8mb4),'@',convert(quote(`mysql`.`role_edges`.`FROM_HOST`) using utf8mb4)),256) using utf8mb4)),NULL) AS `IF(LOCATE(SHA2(CONCAT(QUOTE(FROM_USER),'@',                      CONVERT(QUOTE(FROM_HOST) using utf8mb4)), 256),                 role_path) = 0,          CONCAT(role_path,'->', SHA2(CONCAT(QUOTE(FROM_USER),'@',           CONVERT(QUOTE(FROM_HOST) using utf8`,`mysql`.`role_edges`.`WITH_ADMIN_OPTION` AS `WITH_ADMIN_OPTION`,if(((0 <> `role_graph`.`c_enabled`) or (0 <> internal_is_enabled_role(`mysql`.`role_edges`.`FROM_USER`,`mysql`.`role_edges`.`FROM_HOST`))),true,false) AS `IF(c_enabled OR        INTERNAL_IS_ENABLED_ROLE(FROM_USER, FROM_HOST), TRUE, FALSE)` from (`mysql`.`role_edges` join `role_graph`) where ((`mysql`.`role_edges`.`TO_USER` = `role_graph`.`c_from_user`) and (convert(`mysql`.`role_edges`.`TO_HOST` using utf8mb4) = `role_graph`.`c_from_host`) and (`role_graph`.`role_path` is not null))) select distinct `role_graph`.`c_parent_user` AS `USER`,`role_graph`.`c_parent_host` AS `HOST`,`role_graph`.`c_to_user` AS `GRANTEE`,`role_graph`.`c_to_host` AS `GRANTEE_HOST`,`role_graph`.`c_from_user` AS `ROLE_NAME`,`role_graph`.`c_from_host` AS `ROLE_HOST`,if((`role_graph`.`c_with_admin` = 'N'),'NO','YES') AS `IS_GRANTABLE`,(select if(count(0),'YES','NO') from `mysql`.`default_roles` where ((`mysql`.`default_roles`.`DEFAULT_ROLE_USER` = `role_graph`.`c_from_user`) and (convert(`mysql`.`default_roles`.`DEFAULT_ROLE_HOST` using utf8mb4) = `role_graph`.`c_from_host`) and (`mysql`.`default_roles`.`USER` = `role_graph`.`c_parent_user`) and (convert(`mysql`.`default_roles`.`HOST` using utf8mb4) = `role_graph`.`c_parent_host`))) AS `IS_DEFAULT`,if(internal_is_mandatory_role(`role_graph`.`c_from_user`,`role_graph`.`c_from_host`),'YES','NO') AS `IS_MANDATORY` from `role_graph` where (`role_graph`.`c_to_user` <> '')  ;

-- --------------------------------------------------------

--
-- Structure for view `CHARACTER_SETS`
--
DROP TABLE IF EXISTS `CHARACTER_SETS`;

CREATE ALGORITHM=UNDEFINED DEFINER=`mysql.infoschema`@`localhost` SQL SECURITY DEFINER VIEW `CHARACTER_SETS`  AS SELECT `cs`.`name` AS `CHARACTER_SET_NAME`, `col`.`name` AS `DEFAULT_COLLATE_NAME`, `cs`.`comment` AS `DESCRIPTION`, `cs`.`mb_max_length` AS `MAXLEN` FROM (`mysql`.`character_sets` `cs` join `mysql`.`collations` `col` on((`cs`.`default_collation_id` = `col`.`id`))) ;

-- --------------------------------------------------------

--
-- Structure for view `CHECK_CONSTRAINTS`
--
DROP TABLE IF EXISTS `CHECK_CONSTRAINTS`;

CREATE ALGORITHM=UNDEFINED DEFINER=`mysql.infoschema`@`localhost` SQL SECURITY DEFINER VIEW `CHECK_CONSTRAINTS`  AS SELECT (`cat`.`name` collate utf8mb3_tolower_ci) AS `CONSTRAINT_CATALOG`, (`sch`.`name` collate utf8mb3_tolower_ci) AS `CONSTRAINT_SCHEMA`, `cc`.`name` AS `CONSTRAINT_NAME`, `cc`.`check_clause_utf8` AS `CHECK_CLAUSE` FROM (((`mysql`.`check_constraints` `cc` join `mysql`.`tables` `tbl` on((`cc`.`table_id` = `tbl`.`id`))) join `mysql`.`schemata` `sch` on((`tbl`.`schema_id` = `sch`.`id`))) join `mysql`.`catalogs` `cat` on((`cat`.`id` = `sch`.`catalog_id`))) WHERE ((0 <> can_access_table(`sch`.`name`,`tbl`.`name`)) AND (0 <> is_visible_dd_object(`tbl`.`hidden`))) ;

-- --------------------------------------------------------

--
-- Structure for view `COLLATIONS`
--
DROP TABLE IF EXISTS `COLLATIONS`;

CREATE ALGORITHM=UNDEFINED DEFINER=`mysql.infoschema`@`localhost` SQL SECURITY DEFINER VIEW `COLLATIONS`  AS SELECT `col`.`name` AS `COLLATION_NAME`, `cs`.`name` AS `CHARACTER_SET_NAME`, `col`.`id` AS `ID`, if(exists(select 1 from `mysql`.`character_sets` where (`mysql`.`character_sets`.`default_collation_id` = `col`.`id`)),'Yes','') AS `IS_DEFAULT`, if(`col`.`is_compiled`,'Yes','') AS `IS_COMPILED`, `col`.`sort_length` AS `SORTLEN`, `col`.`pad_attribute` AS `PAD_ATTRIBUTE` FROM (`mysql`.`collations` `col` join `mysql`.`character_sets` `cs` on((`col`.`character_set_id` = `cs`.`id`))) ;

-- --------------------------------------------------------

--
-- Structure for view `COLLATION_CHARACTER_SET_APPLICABILITY`
--
DROP TABLE IF EXISTS `COLLATION_CHARACTER_SET_APPLICABILITY`;

CREATE ALGORITHM=UNDEFINED DEFINER=`mysql.infoschema`@`localhost` SQL SECURITY DEFINER VIEW `COLLATION_CHARACTER_SET_APPLICABILITY`  AS SELECT `col`.`name` AS `COLLATION_NAME`, `cs`.`name` AS `CHARACTER_SET_NAME` FROM (`mysql`.`character_sets` `cs` join `mysql`.`collations` `col` on((`cs`.`id` = `col`.`character_set_id`))) ;

-- --------------------------------------------------------

--
-- Structure for view `COLUMNS`
--
DROP TABLE IF EXISTS `COLUMNS`;

CREATE ALGORITHM=UNDEFINED DEFINER=`mysql.infoschema`@`localhost` SQL SECURITY DEFINER VIEW `COLUMNS`  AS SELECT (`cat`.`name` collate utf8mb3_tolower_ci) AS `TABLE_CATALOG`, (`sch`.`name` collate utf8mb3_tolower_ci) AS `TABLE_SCHEMA`, (`tbl`.`name` collate utf8mb3_tolower_ci) AS `TABLE_NAME`, (`col`.`name` collate utf8mb3_tolower_ci) AS `COLUMN_NAME`, `col`.`ordinal_position` AS `ORDINAL_POSITION`, `col`.`default_value_utf8` AS `COLUMN_DEFAULT`, if((`col`.`is_nullable` = 1),'YES','NO') AS `IS_NULLABLE`, substring_index(substring_index(`col`.`column_type_utf8`,'(',1),' ',1) AS `DATA_TYPE`, internal_dd_char_length(`col`.`type`,`col`.`char_length`,`coll`.`name`,0) AS `CHARACTER_MAXIMUM_LENGTH`, internal_dd_char_length(`col`.`type`,`col`.`char_length`,`coll`.`name`,1) AS `CHARACTER_OCTET_LENGTH`, if((`col`.`numeric_precision` = 0),NULL,`col`.`numeric_precision`) AS `NUMERIC_PRECISION`, if(((`col`.`numeric_scale` = 0) and (`col`.`numeric_precision` = 0)),NULL,`col`.`numeric_scale`) AS `NUMERIC_SCALE`, `col`.`datetime_precision` AS `DATETIME_PRECISION`, (case `col`.`type` when 'MYSQL_TYPE_STRING' then if((`cs`.`name` = 'binary'),NULL,`cs`.`name`) when 'MYSQL_TYPE_VAR_STRING' then if((`cs`.`name` = 'binary'),NULL,`cs`.`name`) when 'MYSQL_TYPE_VARCHAR' then if((`cs`.`name` = 'binary'),NULL,`cs`.`name`) when 'MYSQL_TYPE_TINY_BLOB' then if((`cs`.`name` = 'binary'),NULL,`cs`.`name`) when 'MYSQL_TYPE_MEDIUM_BLOB' then if((`cs`.`name` = 'binary'),NULL,`cs`.`name`) when 'MYSQL_TYPE_BLOB' then if((`cs`.`name` = 'binary'),NULL,`cs`.`name`) when 'MYSQL_TYPE_LONG_BLOB' then if((`cs`.`name` = 'binary'),NULL,`cs`.`name`) when 'MYSQL_TYPE_ENUM' then if((`cs`.`name` = 'binary'),NULL,`cs`.`name`) when 'MYSQL_TYPE_SET' then if((`cs`.`name` = 'binary'),NULL,`cs`.`name`) else NULL end) AS `CHARACTER_SET_NAME`, (case `col`.`type` when 'MYSQL_TYPE_STRING' then if((`cs`.`name` = 'binary'),NULL,`coll`.`name`) when 'MYSQL_TYPE_VAR_STRING' then if((`cs`.`name` = 'binary'),NULL,`coll`.`name`) when 'MYSQL_TYPE_VARCHAR' then if((`cs`.`name` = 'binary'),NULL,`coll`.`name`) when 'MYSQL_TYPE_TINY_BLOB' then if((`cs`.`name` = 'binary'),NULL,`coll`.`name`) when 'MYSQL_TYPE_MEDIUM_BLOB' then if((`cs`.`name` = 'binary'),NULL,`coll`.`name`) when 'MYSQL_TYPE_BLOB' then if((`cs`.`name` = 'binary'),NULL,`coll`.`name`) when 'MYSQL_TYPE_LONG_BLOB' then if((`cs`.`name` = 'binary'),NULL,`coll`.`name`) when 'MYSQL_TYPE_ENUM' then if((`cs`.`name` = 'binary'),NULL,`coll`.`name`) when 'MYSQL_TYPE_SET' then if((`cs`.`name` = 'binary'),NULL,`coll`.`name`) else NULL end) AS `COLLATION_NAME`, `col`.`column_type_utf8` AS `COLUMN_TYPE`, `col`.`column_key` AS `COLUMN_KEY`, internal_get_dd_column_extra((`col`.`generation_expression_utf8` is null),`col`.`is_virtual`,`col`.`is_auto_increment`,`col`.`update_option`,if(length(`col`.`default_option`),true,false),`col`.`options`,`col`.`hidden`,`tbl`.`type`) AS `EXTRA`, get_dd_column_privileges(`sch`.`name`,`tbl`.`name`,`col`.`name`) AS `PRIVILEGES`, ifnull(`col`.`comment`,'') AS `COLUMN_COMMENT`, ifnull(`col`.`generation_expression_utf8`,'') AS `GENERATION_EXPRESSION`, `col`.`srs_id` AS `SRS_ID` FROM (((((`mysql`.`columns` `col` join `mysql`.`tables` `tbl` on((`col`.`table_id` = `tbl`.`id`))) join `mysql`.`schemata` `sch` on((`tbl`.`schema_id` = `sch`.`id`))) join `mysql`.`catalogs` `cat` on((`cat`.`id` = `sch`.`catalog_id`))) join `mysql`.`collations` `coll` on((`col`.`collation_id` = `coll`.`id`))) join `mysql`.`character_sets` `cs` on((`coll`.`character_set_id` = `cs`.`id`))) WHERE ((0 <> internal_get_view_warning_or_error(`sch`.`name`,`tbl`.`name`,`tbl`.`type`,`tbl`.`options`)) AND (0 <> can_access_column(`sch`.`name`,`tbl`.`name`,`col`.`name`)) AND (0 <> is_visible_dd_object(`tbl`.`hidden`,(`col`.`hidden` not in ('Visible','User')),`col`.`options`))) ;

-- --------------------------------------------------------

--
-- Structure for view `COLUMNS_EXTENSIONS`
--
DROP TABLE IF EXISTS `COLUMNS_EXTENSIONS`;

CREATE ALGORITHM=UNDEFINED DEFINER=`mysql.infoschema`@`localhost` SQL SECURITY DEFINER VIEW `COLUMNS_EXTENSIONS`  AS SELECT `cat`.`name` AS `TABLE_CATALOG`, `sch`.`name` AS `TABLE_SCHEMA`, `tbl`.`name` AS `TABLE_NAME`, (`col`.`name` collate utf8mb3_tolower_ci) AS `COLUMN_NAME`, `col`.`engine_attribute` AS `ENGINE_ATTRIBUTE`, `col`.`secondary_engine_attribute` AS `SECONDARY_ENGINE_ATTRIBUTE` FROM (((`mysql`.`columns` `col` join `mysql`.`tables` `tbl` on((`col`.`table_id` = `tbl`.`id`))) join `mysql`.`schemata` `sch` on((`tbl`.`schema_id` = `sch`.`id`))) join `mysql`.`catalogs` `cat` on((`cat`.`id` = `sch`.`catalog_id`))) WHERE ((0 <> internal_get_view_warning_or_error(`sch`.`name`,`tbl`.`name`,`tbl`.`type`,`tbl`.`options`)) AND (0 <> can_access_column(`sch`.`name`,`tbl`.`name`,`col`.`name`)) AND (0 <> is_visible_dd_object(`tbl`.`hidden`,(`col`.`hidden` not in ('Visible','User')),`col`.`options`))) ;

-- --------------------------------------------------------

--
-- Structure for view `COLUMN_PRIVILEGES`
--
DROP TABLE IF EXISTS `COLUMN_PRIVILEGES`;

CREATE TEMPORARY TABLE `COLUMN_PRIVILEGES` (
  `GRANTEE` varchar(292) NOT NULL DEFAULT '',
  `TABLE_CATALOG` varchar(512) NOT NULL DEFAULT '',
  `TABLE_SCHEMA` varchar(64) NOT NULL DEFAULT '',
  `TABLE_NAME` varchar(64) NOT NULL DEFAULT '',
  `COLUMN_NAME` varchar(64) NOT NULL DEFAULT '',
  `PRIVILEGE_TYPE` varchar(64) NOT NULL DEFAULT '',
  `IS_GRANTABLE` varchar(3) NOT NULL DEFAULT ''
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3;

-- --------------------------------------------------------

--
-- Structure for view `COLUMN_STATISTICS`
--
DROP TABLE IF EXISTS `COLUMN_STATISTICS`;

CREATE ALGORITHM=UNDEFINED DEFINER=`mysql.infoschema`@`localhost` SQL SECURITY DEFINER VIEW `COLUMN_STATISTICS`  AS SELECT `mysql`.`column_statistics`.`schema_name` AS `SCHEMA_NAME`, `mysql`.`column_statistics`.`table_name` AS `TABLE_NAME`, `mysql`.`column_statistics`.`column_name` AS `COLUMN_NAME`, `mysql`.`column_statistics`.`histogram` AS `HISTOGRAM` FROM `mysql`.`column_statistics` WHERE (0 <> can_access_table(`mysql`.`column_statistics`.`schema_name`,`mysql`.`column_statistics`.`table_name`)) ;

-- --------------------------------------------------------

--
-- Structure for view `ENABLED_ROLES`
--
DROP TABLE IF EXISTS `ENABLED_ROLES`;

CREATE ALGORITHM=UNDEFINED DEFINER=`mysql.infoschema`@`localhost` SQL SECURITY DEFINER VIEW `ENABLED_ROLES`  AS SELECT `current_user_enabled_roles`.`ROLE_NAME` AS `ROLE_NAME`, `current_user_enabled_roles`.`ROLE_HOST` AS `ROLE_HOST`, (select if(count(0),'YES','NO') from `mysql`.`default_roles` where ((`mysql`.`default_roles`.`DEFAULT_ROLE_USER` = `current_user_enabled_roles`.`ROLE_NAME`) and (convert(`mysql`.`default_roles`.`DEFAULT_ROLE_HOST` using utf8mb4) = `current_user_enabled_roles`.`ROLE_HOST`) and (`mysql`.`default_roles`.`USER` = internal_get_username()) and (convert(`mysql`.`default_roles`.`HOST` using utf8mb4) = convert(internal_get_hostname() using utf8mb4)))) AS `IS_DEFAULT`, if(internal_is_mandatory_role(`current_user_enabled_roles`.`ROLE_NAME`,`current_user_enabled_roles`.`ROLE_HOST`),'YES','NO') AS `IS_MANDATORY` FROM json_table(internal_get_enabled_role_json(), '$[*]' columns (`ROLE_NAME` varchar(255) character set utf8mb4 path '$.ROLE_NAME', `ROLE_HOST` varchar(255) character set utf8mb4 path '$.ROLE_HOST')) AS `current_user_enabled_roles` ;

-- --------------------------------------------------------

--
-- Structure for view `ENGINES`
--
DROP TABLE IF EXISTS `ENGINES`;

CREATE TEMPORARY TABLE `ENGINES` (
  `ENGINE` varchar(64) NOT NULL DEFAULT '',
  `SUPPORT` varchar(8) NOT NULL DEFAULT '',
  `COMMENT` varchar(80) NOT NULL DEFAULT '',
  `TRANSACTIONS` varchar(3) DEFAULT NULL,
  `XA` varchar(3) DEFAULT NULL,
  `SAVEPOINTS` varchar(3) DEFAULT NULL
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3;

-- --------------------------------------------------------

--
-- Structure for view `EVENTS`
--
DROP TABLE IF EXISTS `EVENTS`;

CREATE ALGORITHM=UNDEFINED DEFINER=`mysql.infoschema`@`localhost` SQL SECURITY DEFINER VIEW `EVENTS`  AS SELECT (`cat`.`name` collate utf8mb3_tolower_ci) AS `EVENT_CATALOG`, (`sch`.`name` collate utf8mb3_tolower_ci) AS `EVENT_SCHEMA`, `evt`.`name` AS `EVENT_NAME`, `evt`.`definer` AS `DEFINER`, `evt`.`time_zone` AS `TIME_ZONE`, 'SQL' AS `EVENT_BODY`, `evt`.`definition_utf8` AS `EVENT_DEFINITION`, if((`evt`.`interval_value` is null),'ONE TIME','RECURRING') AS `EVENT_TYPE`, convert_tz(`evt`.`execute_at`,'+00:00',`evt`.`time_zone`) AS `EXECUTE_AT`, convert_interval_to_user_interval(`evt`.`interval_value`,`evt`.`interval_field`) AS `INTERVAL_VALUE`, `evt`.`interval_field` AS `INTERVAL_FIELD`, `evt`.`sql_mode` AS `SQL_MODE`, convert_tz(`evt`.`starts`,'+00:00',`evt`.`time_zone`) AS `STARTS`, convert_tz(`evt`.`ends`,'+00:00',`evt`.`time_zone`) AS `ENDS`, `evt`.`status` AS `STATUS`, if((`evt`.`on_completion` = 'DROP'),'NOT PRESERVE','PRESERVE') AS `ON_COMPLETION`, `evt`.`created` AS `CREATED`, `evt`.`last_altered` AS `LAST_ALTERED`, convert_tz(`evt`.`last_executed`,'+00:00',`evt`.`time_zone`) AS `LAST_EXECUTED`, `evt`.`comment` AS `EVENT_COMMENT`, `evt`.`originator` AS `ORIGINATOR`, `cs_client`.`name` AS `CHARACTER_SET_CLIENT`, `coll_conn`.`name` AS `COLLATION_CONNECTION`, `coll_db`.`name` AS `DATABASE_COLLATION` FROM ((((((`mysql`.`events` `evt` join `mysql`.`schemata` `sch` on((`evt`.`schema_id` = `sch`.`id`))) join `mysql`.`catalogs` `cat` on((`cat`.`id` = `sch`.`catalog_id`))) join `mysql`.`collations` `coll_client` on((`coll_client`.`id` = `evt`.`client_collation_id`))) join `mysql`.`character_sets` `cs_client` on((`cs_client`.`id` = `coll_client`.`character_set_id`))) join `mysql`.`collations` `coll_conn` on((`coll_conn`.`id` = `evt`.`connection_collation_id`))) join `mysql`.`collations` `coll_db` on((`coll_db`.`id` = `evt`.`schema_collation_id`))) WHERE (0 <> can_access_event(`sch`.`name`)) ;

-- --------------------------------------------------------

--
-- Structure for view `FILES`
--
DROP TABLE IF EXISTS `FILES`;

CREATE ALGORITHM=UNDEFINED DEFINER=`mysql.infoschema`@`localhost` SQL SECURITY DEFINER VIEW `FILES`  AS SELECT internal_tablespace_id(`ts`.`name`,`tsf`.`file_name`,`ts`.`engine`,`ts`.`se_private_data`) AS `FILE_ID`, replace(if(((locate(left(`tsf`.`file_name`,1),'./') = 0) and (substr(`tsf`.`file_name`,2,1) <> ':')),concat('./',`tsf`.`file_name`),`tsf`.`file_name`),'\\','/') AS `FILE_NAME`, internal_tablespace_type(`ts`.`name`,`tsf`.`file_name`,`ts`.`engine`,`ts`.`se_private_data`) AS `FILE_TYPE`, `ts`.`name` AS `TABLESPACE_NAME`, '' AS `TABLE_CATALOG`, NULL AS `TABLE_SCHEMA`, NULL AS `TABLE_NAME`, internal_tablespace_logfile_group_name(`ts`.`name`,`tsf`.`file_name`,`ts`.`engine`,`ts`.`se_private_data`) AS `LOGFILE_GROUP_NAME`, internal_tablespace_logfile_group_number(`ts`.`name`,`tsf`.`file_name`,`ts`.`engine`,`ts`.`se_private_data`) AS `LOGFILE_GROUP_NUMBER`, `ts`.`engine` AS `ENGINE`, NULL AS `FULLTEXT_KEYS`, NULL AS `DELETED_ROWS`, NULL AS `UPDATE_COUNT`, internal_tablespace_free_extents(`ts`.`name`,`tsf`.`file_name`,`ts`.`engine`,`ts`.`se_private_data`) AS `FREE_EXTENTS`, internal_tablespace_total_extents(`ts`.`name`,`tsf`.`file_name`,`ts`.`engine`,`ts`.`se_private_data`) AS `TOTAL_EXTENTS`, internal_tablespace_extent_size(`ts`.`name`,`tsf`.`file_name`,`ts`.`engine`,`ts`.`se_private_data`) AS `EXTENT_SIZE`, internal_tablespace_initial_size(`ts`.`name`,`tsf`.`file_name`,`ts`.`engine`,`ts`.`se_private_data`) AS `INITIAL_SIZE`, internal_tablespace_maximum_size(`ts`.`name`,`tsf`.`file_name`,`ts`.`engine`,`ts`.`se_private_data`) AS `MAXIMUM_SIZE`, internal_tablespace_autoextend_size(`ts`.`name`,`tsf`.`file_name`,`ts`.`engine`,`ts`.`se_private_data`) AS `AUTOEXTEND_SIZE`, NULL AS `CREATION_TIME`, NULL AS `LAST_UPDATE_TIME`, NULL AS `LAST_ACCESS_TIME`, NULL AS `RECOVER_TIME`, NULL AS `TRANSACTION_COUNTER`, internal_tablespace_version(`ts`.`name`,`tsf`.`file_name`,`ts`.`engine`,`ts`.`se_private_data`) AS `VERSION`, internal_tablespace_row_format(`ts`.`name`,`tsf`.`file_name`,`ts`.`engine`,`ts`.`se_private_data`) AS `ROW_FORMAT`, NULL AS `TABLE_ROWS`, NULL AS `AVG_ROW_LENGTH`, NULL AS `DATA_LENGTH`, NULL AS `MAX_DATA_LENGTH`, NULL AS `INDEX_LENGTH`, internal_tablespace_data_free(`ts`.`name`,`tsf`.`file_name`,`ts`.`engine`,`ts`.`se_private_data`) AS `DATA_FREE`, NULL AS `CREATE_TIME`, NULL AS `UPDATE_TIME`, NULL AS `CHECK_TIME`, NULL AS `CHECKSUM`, internal_tablespace_status(`ts`.`name`,`tsf`.`file_name`,`ts`.`engine`,`ts`.`se_private_data`) AS `STATUS`, internal_tablespace_extra(`ts`.`name`,`tsf`.`file_name`,`ts`.`engine`,`ts`.`se_private_data`) AS `EXTRA` FROM (`mysql`.`tablespaces` `ts` join `mysql`.`tablespace_files` `tsf` on((`ts`.`id` = `tsf`.`tablespace_id`))) ;

-- --------------------------------------------------------

--
-- Structure for view `INNODB_BUFFER_PAGE`
--
DROP TABLE IF EXISTS `INNODB_BUFFER_PAGE`;

CREATE TEMPORARY TABLE `INNODB_BUFFER_PAGE` (
  `POOL_ID` bigint UNSIGNED NOT NULL DEFAULT '0',
  `BLOCK_ID` bigint UNSIGNED NOT NULL DEFAULT '0',
  `SPACE` bigint UNSIGNED NOT NULL DEFAULT '0',
  `PAGE_NUMBER` bigint UNSIGNED NOT NULL DEFAULT '0',
  `PAGE_TYPE` varchar(64) DEFAULT NULL,
  `FLUSH_TYPE` bigint UNSIGNED NOT NULL DEFAULT '0',
  `FIX_COUNT` bigint UNSIGNED NOT NULL DEFAULT '0',
  `IS_HASHED` varchar(3) DEFAULT NULL,
  `NEWEST_MODIFICATION` bigint UNSIGNED NOT NULL DEFAULT '0',
  `OLDEST_MODIFICATION` bigint UNSIGNED NOT NULL DEFAULT '0',
  `ACCESS_TIME` bigint UNSIGNED NOT NULL DEFAULT '0',
  `TABLE_NAME` varchar(1024) DEFAULT NULL,
  `INDEX_NAME` varchar(1024) DEFAULT NULL,
  `NUMBER_RECORDS` bigint UNSIGNED NOT NULL DEFAULT '0',
  `DATA_SIZE` bigint UNSIGNED NOT NULL DEFAULT '0',
  `COMPRESSED_SIZE` bigint UNSIGNED NOT NULL DEFAULT '0',
  `PAGE_STATE` varchar(64) DEFAULT NULL,
  `IO_FIX` varchar(64) DEFAULT NULL,
  `IS_OLD` varchar(3) DEFAULT NULL,
  `FREE_PAGE_CLOCK` bigint UNSIGNED NOT NULL DEFAULT '0',
  `IS_STALE` varchar(3) DEFAULT NULL
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3;

-- --------------------------------------------------------

--
-- Structure for view `INNODB_BUFFER_PAGE_LRU`
--
DROP TABLE IF EXISTS `INNODB_BUFFER_PAGE_LRU`;

CREATE TEMPORARY TABLE `INNODB_BUFFER_PAGE_LRU` (
  `POOL_ID` bigint UNSIGNED NOT NULL DEFAULT '0',
  `LRU_POSITION` bigint UNSIGNED NOT NULL DEFAULT '0',
  `SPACE` bigint UNSIGNED NOT NULL DEFAULT '0',
  `PAGE_NUMBER` bigint UNSIGNED NOT NULL DEFAULT '0',
  `PAGE_TYPE` varchar(64) DEFAULT NULL,
  `FLUSH_TYPE` bigint UNSIGNED NOT NULL DEFAULT '0',
  `FIX_COUNT` bigint UNSIGNED NOT NULL DEFAULT '0',
  `IS_HASHED` varchar(3) DEFAULT NULL,
  `NEWEST_MODIFICATION` bigint UNSIGNED NOT NULL DEFAULT '0',
  `OLDEST_MODIFICATION` bigint UNSIGNED NOT NULL DEFAULT '0',
  `ACCESS_TIME` bigint UNSIGNED NOT NULL DEFAULT '0',
  `TABLE_NAME` varchar(1024) DEFAULT NULL,
  `INDEX_NAME` varchar(1024) DEFAULT NULL,
  `NUMBER_RECORDS` bigint UNSIGNED NOT NULL DEFAULT '0',
  `DATA_SIZE` bigint UNSIGNED NOT NULL DEFAULT '0',
  `COMPRESSED_SIZE` bigint UNSIGNED NOT NULL DEFAULT '0',
  `COMPRESSED` varchar(3) DEFAULT NULL,
  `IO_FIX` varchar(64) DEFAULT NULL,
  `IS_OLD` varchar(3) DEFAULT NULL,
  `FREE_PAGE_CLOCK` bigint UNSIGNED NOT NULL DEFAULT '0'
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3;

-- --------------------------------------------------------

--
-- Structure for view `INNODB_BUFFER_POOL_STATS`
--
DROP TABLE IF EXISTS `INNODB_BUFFER_POOL_STATS`;

CREATE TEMPORARY TABLE `INNODB_BUFFER_POOL_STATS` (
  `POOL_ID` bigint UNSIGNED NOT NULL DEFAULT '0',
  `POOL_SIZE` bigint UNSIGNED NOT NULL DEFAULT '0',
  `FREE_BUFFERS` bigint UNSIGNED NOT NULL DEFAULT '0',
  `DATABASE_PAGES` bigint UNSIGNED NOT NULL DEFAULT '0',
  `OLD_DATABASE_PAGES` bigint UNSIGNED NOT NULL DEFAULT '0',
  `MODIFIED_DATABASE_PAGES` bigint UNSIGNED NOT NULL DEFAULT '0',
  `PENDING_DECOMPRESS` bigint UNSIGNED NOT NULL DEFAULT '0',
  `PENDING_READS` bigint UNSIGNED NOT NULL DEFAULT '0',
  `PENDING_FLUSH_LRU` bigint UNSIGNED NOT NULL DEFAULT '0',
  `PENDING_FLUSH_LIST` bigint UNSIGNED NOT NULL DEFAULT '0',
  `PAGES_MADE_YOUNG` bigint UNSIGNED NOT NULL DEFAULT '0',
  `PAGES_NOT_MADE_YOUNG` bigint UNSIGNED NOT NULL DEFAULT '0',
  `PAGES_MADE_YOUNG_RATE` double NOT NULL DEFAULT '0',
  `PAGES_MADE_NOT_YOUNG_RATE` double NOT NULL DEFAULT '0',
  `NUMBER_PAGES_READ` bigint UNSIGNED NOT NULL DEFAULT '0',
  `NUMBER_PAGES_CREATED` bigint UNSIGNED NOT NULL DEFAULT '0',
  `NUMBER_PAGES_WRITTEN` bigint UNSIGNED NOT NULL DEFAULT '0',
  `PAGES_READ_RATE` double NOT NULL DEFAULT '0',
  `PAGES_CREATE_RATE` double NOT NULL DEFAULT '0',
  `PAGES_WRITTEN_RATE` double NOT NULL DEFAULT '0',
  `NUMBER_PAGES_GET` bigint UNSIGNED NOT NULL DEFAULT '0',
  `HIT_RATE` bigint UNSIGNED NOT NULL DEFAULT '0',
  `YOUNG_MAKE_PER_THOUSAND_GETS` bigint UNSIGNED NOT NULL DEFAULT '0',
  `NOT_YOUNG_MAKE_PER_THOUSAND_GETS` bigint UNSIGNED NOT NULL DEFAULT '0',
  `NUMBER_PAGES_READ_AHEAD` bigint UNSIGNED NOT NULL DEFAULT '0',
  `NUMBER_READ_AHEAD_EVICTED` bigint UNSIGNED NOT NULL DEFAULT '0',
  `READ_AHEAD_RATE` double NOT NULL DEFAULT '0',
  `READ_AHEAD_EVICTED_RATE` double NOT NULL DEFAULT '0',
  `LRU_IO_TOTAL` bigint UNSIGNED NOT NULL DEFAULT '0',
  `LRU_IO_CURRENT` bigint UNSIGNED NOT NULL DEFAULT '0',
  `UNCOMPRESS_TOTAL` bigint UNSIGNED NOT NULL DEFAULT '0',
  `UNCOMPRESS_CURRENT` bigint UNSIGNED NOT NULL DEFAULT '0'
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3;

-- --------------------------------------------------------

--
-- Structure for view `INNODB_CACHED_INDEXES`
--
DROP TABLE IF EXISTS `INNODB_CACHED_INDEXES`;

CREATE TEMPORARY TABLE `INNODB_CACHED_INDEXES` (
  `SPACE_ID` int UNSIGNED NOT NULL DEFAULT '0',
  `INDEX_ID` bigint UNSIGNED NOT NULL DEFAULT '0',
  `N_CACHED_PAGES` bigint UNSIGNED NOT NULL DEFAULT '0'
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3;

-- --------------------------------------------------------

--
-- Structure for view `INNODB_CMP`
--
DROP TABLE IF EXISTS `INNODB_CMP`;

CREATE TEMPORARY TABLE `INNODB_CMP` (
  `page_size` int NOT NULL DEFAULT '0',
  `compress_ops` int NOT NULL DEFAULT '0',
  `compress_ops_ok` int NOT NULL DEFAULT '0',
  `compress_time` int NOT NULL DEFAULT '0',
  `uncompress_ops` int NOT NULL DEFAULT '0',
  `uncompress_time` int NOT NULL DEFAULT '0'
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3;

-- --------------------------------------------------------

--
-- Structure for view `INNODB_CMPMEM`
--
DROP TABLE IF EXISTS `INNODB_CMPMEM`;

CREATE TEMPORARY TABLE `INNODB_CMPMEM` (
  `page_size` int NOT NULL DEFAULT '0',
  `buffer_pool_instance` int NOT NULL DEFAULT '0',
  `pages_used` int NOT NULL DEFAULT '0',
  `pages_free` int NOT NULL DEFAULT '0',
  `relocation_ops` bigint NOT NULL DEFAULT '0',
  `relocation_time` int NOT NULL DEFAULT '0'
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3;

-- --------------------------------------------------------

--
-- Structure for view `INNODB_CMPMEM_RESET`
--
DROP TABLE IF EXISTS `INNODB_CMPMEM_RESET`;

CREATE TEMPORARY TABLE `INNODB_CMPMEM_RESET` (
  `page_size` int NOT NULL DEFAULT '0',
  `buffer_pool_instance` int NOT NULL DEFAULT '0',
  `pages_used` int NOT NULL DEFAULT '0',
  `pages_free` int NOT NULL DEFAULT '0',
  `relocation_ops` bigint NOT NULL DEFAULT '0',
  `relocation_time` int NOT NULL DEFAULT '0'
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3;

-- --------------------------------------------------------

--
-- Structure for view `INNODB_CMP_PER_INDEX`
--
DROP TABLE IF EXISTS `INNODB_CMP_PER_INDEX`;

CREATE TEMPORARY TABLE `INNODB_CMP_PER_INDEX` (
  `database_name` varchar(192) NOT NULL DEFAULT '',
  `table_name` varchar(192) NOT NULL DEFAULT '',
  `index_name` varchar(192) NOT NULL DEFAULT '',
  `compress_ops` int NOT NULL DEFAULT '0',
  `compress_ops_ok` int NOT NULL DEFAULT '0',
  `compress_time` int NOT NULL DEFAULT '0',
  `uncompress_ops` int NOT NULL DEFAULT '0',
  `uncompress_time` int NOT NULL DEFAULT '0'
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3;

-- --------------------------------------------------------

--
-- Structure for view `INNODB_CMP_PER_INDEX_RESET`
--
DROP TABLE IF EXISTS `INNODB_CMP_PER_INDEX_RESET`;

CREATE TEMPORARY TABLE `INNODB_CMP_PER_INDEX_RESET` (
  `database_name` varchar(192) NOT NULL DEFAULT '',
  `table_name` varchar(192) NOT NULL DEFAULT '',
  `index_name` varchar(192) NOT NULL DEFAULT '',
  `compress_ops` int NOT NULL DEFAULT '0',
  `compress_ops_ok` int NOT NULL DEFAULT '0',
  `compress_time` int NOT NULL DEFAULT '0',
  `uncompress_ops` int NOT NULL DEFAULT '0',
  `uncompress_time` int NOT NULL DEFAULT '0'
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3;

-- --------------------------------------------------------

--
-- Structure for view `INNODB_CMP_RESET`
--
DROP TABLE IF EXISTS `INNODB_CMP_RESET`;

CREATE TEMPORARY TABLE `INNODB_CMP_RESET` (
  `page_size` int NOT NULL DEFAULT '0',
  `compress_ops` int NOT NULL DEFAULT '0',
  `compress_ops_ok` int NOT NULL DEFAULT '0',
  `compress_time` int NOT NULL DEFAULT '0',
  `uncompress_ops` int NOT NULL DEFAULT '0',
  `uncompress_time` int NOT NULL DEFAULT '0'
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3;

-- --------------------------------------------------------

--
-- Structure for view `INNODB_COLUMNS`
--
DROP TABLE IF EXISTS `INNODB_COLUMNS`;

CREATE TEMPORARY TABLE `INNODB_COLUMNS` (
  `TABLE_ID` bigint UNSIGNED NOT NULL DEFAULT '0',
  `NAME` varchar(193) NOT NULL DEFAULT '',
  `POS` bigint UNSIGNED NOT NULL DEFAULT '0',
  `MTYPE` int NOT NULL DEFAULT '0',
  `PRTYPE` int NOT NULL DEFAULT '0',
  `LEN` int NOT NULL DEFAULT '0',
  `HAS_DEFAULT` int NOT NULL DEFAULT '0',
  `DEFAULT_VALUE` mediumblob
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;

-- --------------------------------------------------------

--
-- Structure for view `INNODB_DATAFILES`
--
DROP TABLE IF EXISTS `INNODB_DATAFILES`;

CREATE ALGORITHM=UNDEFINED DEFINER=`mysql.infoschema`@`localhost` SQL SECURITY DEFINER VIEW `INNODB_DATAFILES`  AS SELECT get_dd_tablespace_private_data(`ts`.`se_private_data`,'id') AS `SPACE`, `ts_files`.`file_name` AS `PATH` FROM (`mysql`.`tablespace_files` `ts_files` join `mysql`.`tablespaces` `ts` on((`ts`.`id` = `ts_files`.`tablespace_id`))) WHERE ((`ts`.`se_private_data` is not null) AND (`ts`.`engine` = 'InnoDB') AND (`ts`.`name` <> 'mysql') AND (`ts`.`name` <> 'innodb_temporary')) ;

-- --------------------------------------------------------

--
-- Structure for view `INNODB_FIELDS`
--
DROP TABLE IF EXISTS `INNODB_FIELDS`;

CREATE ALGORITHM=UNDEFINED DEFINER=`mysql.infoschema`@`localhost` SQL SECURITY DEFINER VIEW `INNODB_FIELDS`  AS SELECT get_dd_index_private_data(`idx`.`se_private_data`,'id') AS `INDEX_ID`, `col`.`name` AS `NAME`, (`fld`.`ordinal_position` - 1) AS `POS` FROM (((`mysql`.`index_column_usage` `fld` join `mysql`.`columns` `col` on((`fld`.`column_id` = `col`.`id`))) join `mysql`.`indexes` `idx` on((`fld`.`index_id` = `idx`.`id`))) join `mysql`.`tables` `tbl` on((`tbl`.`id` = `idx`.`table_id`))) WHERE ((`tbl`.`type` <> 'VIEW') AND (`tbl`.`hidden` = 'Visible') AND (0 = `fld`.`hidden`) AND (`tbl`.`se_private_id` is not null) AND (`tbl`.`engine` = 'INNODB')) ;

-- --------------------------------------------------------

--
-- Structure for view `INNODB_FOREIGN`
--
DROP TABLE IF EXISTS `INNODB_FOREIGN`;

CREATE ALGORITHM=UNDEFINED DEFINER=`mysql.infoschema`@`localhost` SQL SECURITY DEFINER VIEW `INNODB_FOREIGN`  AS SELECT (concat(`sch`.`name`,'/',`fk`.`name`) collate utf8mb3_tolower_ci) AS `ID`, concat(`sch`.`name`,'/',`tbl`.`name`) AS `FOR_NAME`, concat(`fk`.`referenced_table_schema`,'/',`fk`.`referenced_table_name`) AS `REF_NAME`, count(0) AS `N_COLS`, (((((if((`fk`.`delete_rule` = 'CASCADE'),1,0) | if((`fk`.`delete_rule` = 'SET NULL'),2,0)) | if((`fk`.`update_rule` = 'CASCADE'),4,0)) | if((`fk`.`update_rule` = 'SET NULL'),8,0)) | if((`fk`.`delete_rule` = 'NO ACTION'),16,0)) | if((`fk`.`update_rule` = 'NO ACTION'),32,0)) AS `TYPE` FROM (((`mysql`.`foreign_keys` `fk` join `mysql`.`tables` `tbl` on((`fk`.`table_id` = `tbl`.`id`))) join `mysql`.`schemata` `sch` on((`fk`.`schema_id` = `sch`.`id`))) join `mysql`.`foreign_key_column_usage` `col` on((`fk`.`id` = `col`.`foreign_key_id`))) WHERE ((`tbl`.`type` <> 'VIEW') AND (`tbl`.`hidden` = 'Visible') AND (`tbl`.`se_private_id` is not null) AND (`tbl`.`engine` = 'INNODB')) GROUP BY `fk`.`id` ;

-- --------------------------------------------------------

--
-- Structure for view `INNODB_FOREIGN_COLS`
--
DROP TABLE IF EXISTS `INNODB_FOREIGN_COLS`;

CREATE ALGORITHM=UNDEFINED DEFINER=`mysql.infoschema`@`localhost` SQL SECURITY DEFINER VIEW `INNODB_FOREIGN_COLS`  AS SELECT (concat(`sch`.`name`,'/',`fk`.`name`) collate utf8mb3_tolower_ci) AS `ID`, `col`.`name` AS `FOR_COL_NAME`, `fk_col`.`referenced_column_name` AS `REF_COL_NAME`, `fk_col`.`ordinal_position` AS `POS` FROM ((((`mysql`.`foreign_key_column_usage` `fk_col` join `mysql`.`foreign_keys` `fk` on((`fk`.`id` = `fk_col`.`foreign_key_id`))) join `mysql`.`tables` `tbl` on((`fk`.`table_id` = `tbl`.`id`))) join `mysql`.`schemata` `sch` on((`fk`.`schema_id` = `sch`.`id`))) join `mysql`.`columns` `col` on(((`tbl`.`id` = `col`.`table_id`) and (`fk_col`.`column_id` = `col`.`id`)))) WHERE ((`tbl`.`type` <> 'VIEW') AND (`tbl`.`hidden` = 'Visible') AND (`tbl`.`se_private_id` is not null) AND (`tbl`.`engine` = 'INNODB')) ;

-- --------------------------------------------------------

--
-- Structure for view `INNODB_FT_BEING_DELETED`
--
DROP TABLE IF EXISTS `INNODB_FT_BEING_DELETED`;

CREATE TEMPORARY TABLE `INNODB_FT_BEING_DELETED` (
  `DOC_ID` bigint UNSIGNED NOT NULL DEFAULT '0'
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3;

-- --------------------------------------------------------

--
-- Structure for view `INNODB_FT_CONFIG`
--
DROP TABLE IF EXISTS `INNODB_FT_CONFIG`;

CREATE TEMPORARY TABLE `INNODB_FT_CONFIG` (
  `KEY` varchar(193) NOT NULL DEFAULT '',
  `VALUE` varchar(193) NOT NULL DEFAULT ''
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3;

-- --------------------------------------------------------

--
-- Structure for view `INNODB_FT_DEFAULT_STOPWORD`
--
DROP TABLE IF EXISTS `INNODB_FT_DEFAULT_STOPWORD`;

CREATE TEMPORARY TABLE `INNODB_FT_DEFAULT_STOPWORD` (
  `value` varchar(18) NOT NULL DEFAULT ''
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3;

-- --------------------------------------------------------

--
-- Structure for view `INNODB_FT_DELETED`
--
DROP TABLE IF EXISTS `INNODB_FT_DELETED`;

CREATE TEMPORARY TABLE `INNODB_FT_DELETED` (
  `DOC_ID` bigint UNSIGNED NOT NULL DEFAULT '0'
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3;

-- --------------------------------------------------------

--
-- Structure for view `INNODB_FT_INDEX_CACHE`
--
DROP TABLE IF EXISTS `INNODB_FT_INDEX_CACHE`;

CREATE TEMPORARY TABLE `INNODB_FT_INDEX_CACHE` (
  `WORD` varchar(337) NOT NULL DEFAULT '',
  `FIRST_DOC_ID` bigint UNSIGNED NOT NULL DEFAULT '0',
  `LAST_DOC_ID` bigint UNSIGNED NOT NULL DEFAULT '0',
  `DOC_COUNT` bigint UNSIGNED NOT NULL DEFAULT '0',
  `DOC_ID` bigint UNSIGNED NOT NULL DEFAULT '0',
  `POSITION` bigint UNSIGNED NOT NULL DEFAULT '0'
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3;

-- --------------------------------------------------------

--
-- Structure for view `INNODB_FT_INDEX_TABLE`
--
DROP TABLE IF EXISTS `INNODB_FT_INDEX_TABLE`;

CREATE TEMPORARY TABLE `INNODB_FT_INDEX_TABLE` (
  `WORD` varchar(337) NOT NULL DEFAULT '',
  `FIRST_DOC_ID` bigint UNSIGNED NOT NULL DEFAULT '0',
  `LAST_DOC_ID` bigint UNSIGNED NOT NULL DEFAULT '0',
  `DOC_COUNT` bigint UNSIGNED NOT NULL DEFAULT '0',
  `DOC_ID` bigint UNSIGNED NOT NULL DEFAULT '0',
  `POSITION` bigint UNSIGNED NOT NULL DEFAULT '0'
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3;

-- --------------------------------------------------------

--
-- Structure for view `INNODB_INDEXES`
--
DROP TABLE IF EXISTS `INNODB_INDEXES`;

CREATE TEMPORARY TABLE `INNODB_INDEXES` (
  `INDEX_ID` bigint UNSIGNED NOT NULL DEFAULT '0',
  `NAME` varchar(193) NOT NULL DEFAULT '',
  `TABLE_ID` bigint UNSIGNED NOT NULL DEFAULT '0',
  `TYPE` int NOT NULL DEFAULT '0',
  `N_FIELDS` int NOT NULL DEFAULT '0',
  `PAGE_NO` int NOT NULL DEFAULT '0',
  `SPACE` int NOT NULL DEFAULT '0',
  `MERGE_THRESHOLD` int NOT NULL DEFAULT '0'
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3;

-- --------------------------------------------------------

--
-- Structure for view `INNODB_METRICS`
--
DROP TABLE IF EXISTS `INNODB_METRICS`;

CREATE TEMPORARY TABLE `INNODB_METRICS` (
  `NAME` varchar(193) NOT NULL DEFAULT '',
  `SUBSYSTEM` varchar(193) NOT NULL DEFAULT '',
  `COUNT` bigint NOT NULL DEFAULT '0',
  `MAX_COUNT` bigint DEFAULT NULL,
  `MIN_COUNT` bigint DEFAULT NULL,
  `AVG_COUNT` double DEFAULT NULL,
  `COUNT_RESET` bigint NOT NULL DEFAULT '0',
  `MAX_COUNT_RESET` bigint DEFAULT NULL,
  `MIN_COUNT_RESET` bigint DEFAULT NULL,
  `AVG_COUNT_RESET` double DEFAULT NULL,
  `TIME_ENABLED` datetime DEFAULT NULL,
  `TIME_DISABLED` datetime DEFAULT NULL,
  `TIME_ELAPSED` bigint DEFAULT NULL,
  `TIME_RESET` datetime DEFAULT NULL,
  `STATUS` varchar(193) NOT NULL DEFAULT '',
  `TYPE` varchar(193) NOT NULL DEFAULT '',
  `COMMENT` varchar(193) NOT NULL DEFAULT ''
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3;

-- --------------------------------------------------------

--
-- Structure for view `INNODB_SESSION_TEMP_TABLESPACES`
--
DROP TABLE IF EXISTS `INNODB_SESSION_TEMP_TABLESPACES`;

CREATE TEMPORARY TABLE `INNODB_SESSION_TEMP_TABLESPACES` (
  `ID` int UNSIGNED NOT NULL DEFAULT '0',
  `SPACE` int UNSIGNED NOT NULL DEFAULT '0',
  `PATH` varchar(4001) NOT NULL DEFAULT '',
  `SIZE` bigint UNSIGNED NOT NULL DEFAULT '0',
  `STATE` varchar(192) NOT NULL DEFAULT '',
  `PURPOSE` varchar(192) NOT NULL DEFAULT ''
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3;

-- --------------------------------------------------------

--
-- Structure for view `INNODB_TABLES`
--
DROP TABLE IF EXISTS `INNODB_TABLES`;

CREATE TEMPORARY TABLE `INNODB_TABLES` (
  `TABLE_ID` bigint UNSIGNED NOT NULL DEFAULT '0',
  `NAME` varchar(655) NOT NULL DEFAULT '',
  `FLAG` int NOT NULL DEFAULT '0',
  `N_COLS` int NOT NULL DEFAULT '0',
  `SPACE` bigint NOT NULL DEFAULT '0',
  `ROW_FORMAT` varchar(12) DEFAULT NULL,
  `ZIP_PAGE_SIZE` int UNSIGNED NOT NULL DEFAULT '0',
  `SPACE_TYPE` varchar(10) DEFAULT NULL,
  `INSTANT_COLS` int NOT NULL DEFAULT '0',
  `TOTAL_ROW_VERSIONS` int NOT NULL DEFAULT '0'
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3;

-- --------------------------------------------------------

--
-- Structure for view `INNODB_TABLESPACES`
--
DROP TABLE IF EXISTS `INNODB_TABLESPACES`;

CREATE TEMPORARY TABLE `INNODB_TABLESPACES` (
  `SPACE` int UNSIGNED NOT NULL DEFAULT '0',
  `NAME` varchar(655) NOT NULL DEFAULT '',
  `FLAG` int UNSIGNED NOT NULL DEFAULT '0',
  `ROW_FORMAT` varchar(22) DEFAULT NULL,
  `PAGE_SIZE` int UNSIGNED NOT NULL DEFAULT '0',
  `ZIP_PAGE_SIZE` int UNSIGNED NOT NULL DEFAULT '0',
  `SPACE_TYPE` varchar(10) DEFAULT NULL,
  `FS_BLOCK_SIZE` int UNSIGNED NOT NULL DEFAULT '0',
  `FILE_SIZE` bigint UNSIGNED NOT NULL DEFAULT '0',
  `ALLOCATED_SIZE` bigint UNSIGNED NOT NULL DEFAULT '0',
  `AUTOEXTEND_SIZE` bigint UNSIGNED NOT NULL DEFAULT '0',
  `SERVER_VERSION` varchar(10) DEFAULT NULL,
  `SPACE_VERSION` int UNSIGNED NOT NULL DEFAULT '0',
  `ENCRYPTION` varchar(1) DEFAULT NULL,
  `STATE` varchar(10) DEFAULT NULL
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3;

-- --------------------------------------------------------

--
-- Structure for view `INNODB_TABLESPACES_BRIEF`
--
DROP TABLE IF EXISTS `INNODB_TABLESPACES_BRIEF`;

CREATE ALGORITHM=UNDEFINED DEFINER=`mysql.infoschema`@`localhost` SQL SECURITY DEFINER VIEW `INNODB_TABLESPACES_BRIEF`  AS SELECT get_dd_tablespace_private_data(`ts`.`se_private_data`,'id') AS `SPACE`, `ts`.`name` AS `NAME`, `ts_files`.`file_name` AS `PATH`, get_dd_tablespace_private_data(`ts`.`se_private_data`,'flags') AS `FLAG`, if((get_dd_tablespace_private_data(`ts`.`se_private_data`,'id') = 0),'System',if((((get_dd_tablespace_private_data(`ts`.`se_private_data`,'flags') & 2048) >> 11) <> 0),'General','Single')) AS `SPACE_TYPE` FROM (`mysql`.`tablespace_files` `ts_files` join `mysql`.`tablespaces` `ts` on((`ts`.`id` = `ts_files`.`tablespace_id`))) WHERE ((`ts`.`se_private_data` is not null) AND (`ts`.`engine` = 'InnoDB') AND (`ts`.`name` <> 'mysql') AND (`ts`.`name` <> 'innodb_temporary')) ;

-- --------------------------------------------------------

--
-- Structure for view `INNODB_TABLESTATS`
--
DROP TABLE IF EXISTS `INNODB_TABLESTATS`;

CREATE TEMPORARY TABLE `INNODB_TABLESTATS` (
  `TABLE_ID` bigint UNSIGNED NOT NULL DEFAULT '0',
  `NAME` varchar(193) NOT NULL DEFAULT '',
  `STATS_INITIALIZED` varchar(193) NOT NULL DEFAULT '',
  `NUM_ROWS` bigint UNSIGNED NOT NULL DEFAULT '0',
  `CLUST_INDEX_SIZE` bigint UNSIGNED NOT NULL DEFAULT '0',
  `OTHER_INDEX_SIZE` bigint UNSIGNED NOT NULL DEFAULT '0',
  `MODIFIED_COUNTER` bigint UNSIGNED NOT NULL DEFAULT '0',
  `AUTOINC` bigint UNSIGNED NOT NULL DEFAULT '0',
  `REF_COUNT` int NOT NULL DEFAULT '0'
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3;

-- --------------------------------------------------------

--
-- Structure for view `INNODB_TEMP_TABLE_INFO`
--
DROP TABLE IF EXISTS `INNODB_TEMP_TABLE_INFO`;

CREATE TEMPORARY TABLE `INNODB_TEMP_TABLE_INFO` (
  `TABLE_ID` bigint UNSIGNED NOT NULL DEFAULT '0',
  `NAME` varchar(64) DEFAULT NULL,
  `N_COLS` int UNSIGNED NOT NULL DEFAULT '0',
  `SPACE` int UNSIGNED NOT NULL DEFAULT '0'
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3;

-- --------------------------------------------------------

--
-- Structure for view `INNODB_TRX`
--
DROP TABLE IF EXISTS `INNODB_TRX`;

CREATE TEMPORARY TABLE `INNODB_TRX` (
  `trx_id` bigint UNSIGNED NOT NULL DEFAULT '0',
  `trx_state` varchar(13) NOT NULL DEFAULT '',
  `trx_started` datetime NOT NULL DEFAULT '0000-00-00 00:00:00',
  `trx_requested_lock_id` varchar(126) DEFAULT NULL,
  `trx_wait_started` datetime DEFAULT NULL,
  `trx_weight` bigint UNSIGNED NOT NULL DEFAULT '0',
  `trx_mysql_thread_id` bigint UNSIGNED NOT NULL DEFAULT '0',
  `trx_query` varchar(1024) DEFAULT NULL,
  `trx_operation_state` varchar(64) DEFAULT NULL,
  `trx_tables_in_use` bigint UNSIGNED NOT NULL DEFAULT '0',
  `trx_tables_locked` bigint UNSIGNED NOT NULL DEFAULT '0',
  `trx_lock_structs` bigint UNSIGNED NOT NULL DEFAULT '0',
  `trx_lock_memory_bytes` bigint UNSIGNED NOT NULL DEFAULT '0',
  `trx_rows_locked` bigint UNSIGNED NOT NULL DEFAULT '0',
  `trx_rows_modified` bigint UNSIGNED NOT NULL DEFAULT '0',
  `trx_concurrency_tickets` bigint UNSIGNED NOT NULL DEFAULT '0',
  `trx_isolation_level` varchar(16) NOT NULL DEFAULT '',
  `trx_unique_checks` int NOT NULL DEFAULT '0',
  `trx_foreign_key_checks` int NOT NULL DEFAULT '0',
  `trx_last_foreign_key_error` varchar(256) DEFAULT NULL,
  `trx_adaptive_hash_latched` int NOT NULL DEFAULT '0',
  `trx_adaptive_hash_timeout` bigint UNSIGNED NOT NULL DEFAULT '0',
  `trx_is_read_only` int NOT NULL DEFAULT '0',
  `trx_autocommit_non_locking` int NOT NULL DEFAULT '0',
  `trx_schedule_weight` bigint UNSIGNED DEFAULT NULL
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3;

-- --------------------------------------------------------

--
-- Structure for view `INNODB_VIRTUAL`
--
DROP TABLE IF EXISTS `INNODB_VIRTUAL`;

CREATE TEMPORARY TABLE `INNODB_VIRTUAL` (
  `TABLE_ID` bigint UNSIGNED NOT NULL DEFAULT '0',
  `POS` int UNSIGNED NOT NULL DEFAULT '0',
  `BASE_POS` int UNSIGNED NOT NULL DEFAULT '0'
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3;

-- --------------------------------------------------------

--
-- Structure for view `KEYWORDS`
--
DROP TABLE IF EXISTS `KEYWORDS`;

CREATE ALGORITHM=UNDEFINED DEFINER=`mysql.infoschema`@`localhost` SQL SECURITY DEFINER VIEW `KEYWORDS`  AS SELECT `j`.`word` AS `WORD`, `j`.`reserved` AS `RESERVED` FROM json_table('[["ACCESSIBLE",1],["ACCOUNT",0],["ACTION",0],["ACTIVE",0],["ADD",1],["ADMIN",0],["AFTER",0],["AGAINST",0],["AGGREGATE",0],["ALGORITHM",0],["ALL",1],["ALTER",1],["ALWAYS",0],["ANALYZE",1],["AND",1],["ANY",0],["ARRAY",0],["AS",1],["ASC",1],["ASCII",0],["ASENSITIVE",1],["ASSIGN_GTIDS_TO_ANONYMOUS_TRANSACTIONS",0],["AT",0],["ATTRIBUTE",0],["AUTHENTICATION",0],["AUTOEXTEND_SIZE",0],["AUTO_INCREMENT",0],["AVG",0],["AVG_ROW_LENGTH",0],["BACKUP",0],["BEFORE",1],["BEGIN",0],["BETWEEN",1],["BIGINT",1],["BINARY",1],["BINLOG",0],["BIT",0],["BLOB",1],["BLOCK",0],["BOOL",0],["BOOLEAN",0],["BOTH",1],["BTREE",0],["BUCKETS",0],["BULK",0],["BY",1],["BYTE",0],["CACHE",0],["CALL",1],["CASCADE",1],["CASCADED",0],["CASE",1],["CATALOG_NAME",0],["CHAIN",0],["CHALLENGE_RESPONSE",0],["CHANGE",1],["CHANGED",0],["CHANNEL",0],["CHAR",1],["CHARACTER",1],["CHARSET",0],["CHECK",1],["CHECKSUM",0],["CIPHER",0],["CLASS_ORIGIN",0],["CLIENT",0],["CLONE",0],["CLOSE",0],["COALESCE",0],["CODE",0],["COLLATE",1],["COLLATION",0],["COLUMN",1],["COLUMNS",0],["COLUMN_FORMAT",0],["COLUMN_NAME",0],["COMMENT",0],["COMMIT",0],["COMMITTED",0],["COMPACT",0],["COMPLETION",0],["COMPONENT",0],["COMPRESSED",0],["COMPRESSION",0],["CONCURRENT",0],["CONDITION",1],["CONNECTION",0],["CONSISTENT",0],["CONSTRAINT",1],["CONSTRAINT_CATALOG",0],["CONSTRAINT_NAME",0],["CONSTRAINT_SCHEMA",0],["CONTAINS",0],["CONTEXT",0],["CONTINUE",1],["CONVERT",1],["CPU",0],["CREATE",1],["CROSS",1],["CUBE",1],["CUME_DIST",1],["CURRENT",0],["CURRENT_DATE",1],["CURRENT_TIME",1],["CURRENT_TIMESTAMP",1],["CURRENT_USER",1],["CURSOR",1],["CURSOR_NAME",0],["DATA",0],["DATABASE",1],["DATABASES",1],["DATAFILE",0],["DATE",0],["DATETIME",0],["DAY",0],["DAY_HOUR",1],["DAY_MICROSECOND",1],["DAY_MINUTE",1],["DAY_SECOND",1],["DEALLOCATE",0],["DEC",1],["DECIMAL",1],["DECLARE",1],["DEFAULT",1],["DEFAULT_AUTH",0],["DEFINER",0],["DEFINITION",0],["DELAYED",1],["DELAY_KEY_WRITE",0],["DELETE",1],["DENSE_RANK",1],["DESC",1],["DESCRIBE",1],["DESCRIPTION",0],["DETERMINISTIC",1],["DIAGNOSTICS",0],["DIRECTORY",0],["DISABLE",0],["DISCARD",0],["DISK",0],["DISTINCT",1],["DISTINCTROW",1],["DIV",1],["DO",0],["DOUBLE",1],["DROP",1],["DUAL",1],["DUMPFILE",0],["DUPLICATE",0],["DYNAMIC",0],["EACH",1],["ELSE",1],["ELSEIF",1],["EMPTY",1],["ENABLE",0],["ENCLOSED",1],["ENCRYPTION",0],["END",0],["ENDS",0],["ENFORCED",0],["ENGINE",0],["ENGINES",0],["ENGINE_ATTRIBUTE",0],["ENUM",0],["ERROR",0],["ERRORS",0],["ESCAPE",0],["ESCAPED",1],["EVENT",0],["EVENTS",0],["EVERY",0],["EXCEPT",1],["EXCHANGE",0],["EXCLUDE",0],["EXECUTE",0],["EXISTS",1],["EXIT",1],["EXPANSION",0],["EXPIRE",0],["EXPLAIN",1],["EXPORT",0],["EXTENDED",0],["EXTENT_SIZE",0],["FACTOR",0],["FAILED_LOGIN_ATTEMPTS",0],["FALSE",1],["FAST",0],["FAULTS",0],["FETCH",1],["FIELDS",0],["FILE",0],["FILE_BLOCK_SIZE",0],["FILTER",0],["FINISH",0],["FIRST",0],["FIRST_VALUE",1],["FIXED",0],["FLOAT",1],["FLOAT4",1],["FLOAT8",1],["FLUSH",0],["FOLLOWING",0],["FOLLOWS",0],["FOR",1],["FORCE",1],["FOREIGN",1],["FORMAT",0],["FOUND",0],["FROM",1],["FULL",0],["FULLTEXT",1],["FUNCTION",1],["GENERAL",0],["GENERATE",0],["GENERATED",1],["GEOMCOLLECTION",0],["GEOMETRY",0],["GEOMETRYCOLLECTION",0],["GET",1],["GET_FORMAT",0],["GET_MASTER_PUBLIC_KEY",0],["GET_SOURCE_PUBLIC_KEY",0],["GLOBAL",0],["GRANT",1],["GRANTS",0],["GROUP",1],["GROUPING",1],["GROUPS",1],["GROUP_REPLICATION",0],["GTID_ONLY",0],["HANDLER",0],["HASH",0],["HAVING",1],["HELP",0],["HIGH_PRIORITY",1],["HISTOGRAM",0],["HISTORY",0],["HOST",0],["HOSTS",0],["HOUR",0],["HOUR_MICROSECOND",1],["HOUR_MINUTE",1],["HOUR_SECOND",1],["IDENTIFIED",0],["IF",1],["IGNORE",1],["IGNORE_SERVER_IDS",0],["IMPORT",0],["IN",1],["INACTIVE",0],["INDEX",1],["INDEXES",0],["INFILE",1],["INITIAL",0],["INITIAL_SIZE",0],["INITIATE",0],["INNER",1],["INOUT",1],["INSENSITIVE",1],["INSERT",1],["INSERT_METHOD",0],["INSTALL",0],["INSTANCE",0],["INT",1],["INT1",1],["INT2",1],["INT3",1],["INT4",1],["INT8",1],["INTEGER",1],["INTERSECT",1],["INTERVAL",1],["INTO",1],["INVISIBLE",0],["INVOKER",0],["IO",0],["IO_AFTER_GTIDS",1],["IO_BEFORE_GTIDS",1],["IO_THREAD",0],["IPC",0],["IS",1],["ISOLATION",0],["ISSUER",0],["ITERATE",1],["JOIN",1],["JSON",0],["JSON_TABLE",1],["JSON_VALUE",0],["KEY",1],["KEYRING",0],["KEYS",1],["KEY_BLOCK_SIZE",0],["KILL",1],["LAG",1],["LANGUAGE",0],["LAST",0],["LAST_VALUE",1],["LATERAL",1],["LEAD",1],["LEADING",1],["LEAVE",1],["LEAVES",0],["LEFT",1],["LESS",0],["LEVEL",0],["LIKE",1],["LIMIT",1],["LINEAR",1],["LINES",1],["LINESTRING",0],["LIST",0],["LOAD",1],["LOCAL",0],["LOCALTIME",1],["LOCALTIMESTAMP",1],["LOCK",1],["LOCKED",0],["LOCKS",0],["LOGFILE",0],["LOGS",0],["LONG",1],["LONGBLOB",1],["LONGTEXT",1],["LOOP",1],["LOW_PRIORITY",1],["MASTER",0],["MASTER_AUTO_POSITION",0],["MASTER_BIND",1],["MASTER_COMPRESSION_ALGORITHMS",0],["MASTER_CONNECT_RETRY",0],["MASTER_DELAY",0],["MASTER_HEARTBEAT_PERIOD",0],["MASTER_HOST",0],["MASTER_LOG_FILE",0],["MASTER_LOG_POS",0],["MASTER_PASSWORD",0],["MASTER_PORT",0],["MASTER_PUBLIC_KEY_PATH",0],["MASTER_RETRY_COUNT",0],["MASTER_SSL",0],["MASTER_SSL_CA",0],["MASTER_SSL_CAPATH",0],["MASTER_SSL_CERT",0],["MASTER_SSL_CIPHER",0],["MASTER_SSL_CRL",0],["MASTER_SSL_CRLPATH",0],["MASTER_SSL_KEY",0],["MASTER_SSL_VERIFY_SERVER_CERT",1],["MASTER_TLS_CIPHERSUITES",0],["MASTER_TLS_VERSION",0],["MASTER_USER",0],["MASTER_ZSTD_COMPRESSION_LEVEL",0],["MATCH",1],["MAXVALUE",1],["MAX_CONNECTIONS_PER_HOUR",0],["MAX_QUERIES_PER_HOUR",0],["MAX_ROWS",0],["MAX_SIZE",0],["MAX_UPDATES_PER_HOUR",0],["MAX_USER_CONNECTIONS",0],["MEDIUM",0],["MEDIUMBLOB",1],["MEDIUMINT",1],["MEDIUMTEXT",1],["MEMBER",0],["MEMORY",0],["MERGE",0],["MESSAGE_TEXT",0],["MICROSECOND",0],["MIDDLEINT",1],["MIGRATE",0],["MINUTE",0],["MINUTE_MICROSECOND",1],["MINUTE_SECOND",1],["MIN_ROWS",0],["MOD",1],["MODE",0],["MODIFIES",1],["MODIFY",0],["MONTH",0],["MULTILINESTRING",0],["MULTIPOINT",0],["MULTIPOLYGON",0],["MUTEX",0],["MYSQL_ERRNO",0],["NAME",0],["NAMES",0],["NATIONAL",0],["NATURAL",1],["NCHAR",0],["NDB",0],["NDBCLUSTER",0],["NESTED",0],["NETWORK_NAMESPACE",0],["NEVER",0],["NEW",0],["NEXT",0],["NO",0],["NODEGROUP",0],["NONE",0],["NOT",1],["NOWAIT",0],["NO_WAIT",0],["NO_WRITE_TO_BINLOG",1],["NTH_VALUE",1],["NTILE",1],["NULL",1],["NULLS",0],["NUMBER",0],["NUMERIC",1],["NVARCHAR",0],["OF",1],["OFF",0],["OFFSET",0],["OJ",0],["OLD",0],["ON",1],["ONE",0],["ONLY",0],["OPEN",0],["OPTIMIZE",1],["OPTIMIZER_COSTS",1],["OPTION",1],["OPTIONAL",0],["OPTIONALLY",1],["OPTIONS",0],["OR",1],["ORDER",1],["ORDINALITY",0],["ORGANIZATION",0],["OTHERS",0],["OUT",1],["OUTER",1],["OUTFILE",1],["OVER",1],["OWNER",0],["PACK_KEYS",0],["PAGE",0],["PARSER",0],["PARTIAL",0],["PARTITION",1],["PARTITIONING",0],["PARTITIONS",0],["PASSWORD",0],["PASSWORD_LOCK_TIME",0],["PATH",0],["PERCENT_RANK",1],["PERSIST",0],["PERSIST_ONLY",0],["PHASE",0],["PLUGIN",0],["PLUGINS",0],["PLUGIN_DIR",0],["POINT",0],["POLYGON",0],["PORT",0],["PRECEDES",0],["PRECEDING",0],["PRECISION",1],["PREPARE",0],["PRESERVE",0],["PREV",0],["PRIMARY",1],["PRIVILEGES",0],["PRIVILEGE_CHECKS_USER",0],["PROCEDURE",1],["PROCESS",0],["PROCESSLIST",0],["PROFILE",0],["PROFILES",0],["PROXY",0],["PURGE",1],["QUARTER",0],["QUERY",0],["QUICK",0],["RANDOM",0],["RANGE",1],["RANK",1],["READ",1],["READS",1],["READ_ONLY",0],["READ_WRITE",1],["REAL",1],["REBUILD",0],["RECOVER",0],["RECURSIVE",1],["REDO_BUFFER_SIZE",0],["REDUNDANT",0],["REFERENCE",0],["REFERENCES",1],["REGEXP",1],["REGISTRATION",0],["RELAY",0],["RELAYLOG",0],["RELAY_LOG_FILE",0],["RELAY_LOG_POS",0],["RELAY_THREAD",0],["RELEASE",1],["RELOAD",0],["REMOVE",0],["RENAME",1],["REORGANIZE",0],["REPAIR",0],["REPEAT",1],["REPEATABLE",0],["REPLACE",1],["REPLICA",0],["REPLICAS",0],["REPLICATE_DO_DB",0],["REPLICATE_DO_TABLE",0],["REPLICATE_IGNORE_DB",0],["REPLICATE_IGNORE_TABLE",0],["REPLICATE_REWRITE_DB",0],["REPLICATE_WILD_DO_TABLE",0],["REPLICATE_WILD_IGNORE_TABLE",0],["REPLICATION",0],["REQUIRE",1],["REQUIRE_ROW_FORMAT",0],["REQUIRE_TABLE_PRIMARY_KEY_CHECK",0],["RESET",0],["RESIGNAL",1],["RESOURCE",0],["RESPECT",0],["RESTART",0],["RESTORE",0],["RESTRICT",1],["RESUME",0],["RETAIN",0],["RETURN",1],["RETURNED_SQLSTATE",0],["RETURNING",0],["RETURNS",0],["REUSE",0],["REVERSE",0],["REVOKE",1],["RIGHT",1],["RLIKE",1],["ROLE",0],["ROLLBACK",0],["ROLLUP",0],["ROTATE",0],["ROUTINE",0],["ROW",1],["ROWS",1],["ROW_COUNT",0],["ROW_FORMAT",0],["ROW_NUMBER",1],["RTREE",0],["SAVEPOINT",0],["SCHEDULE",0],["SCHEMA",1],["SCHEMAS",1],["SCHEMA_NAME",0],["SECOND",0],["SECONDARY",0],["SECONDARY_ENGINE",0],["SECONDARY_ENGINE_ATTRIBUTE",0],["SECONDARY_LOAD",0],["SECONDARY_UNLOAD",0],["SECOND_MICROSECOND",1],["SECURITY",0],["SELECT",1],["SENSITIVE",1],["SEPARATOR",1],["SERIAL",0],["SERIALIZABLE",0],["SERVER",0],["SESSION",0],["SET",1],["SHARE",0],["SHOW",1],["SHUTDOWN",0],["SIGNAL",1],["SIGNED",0],["SIMPLE",0],["SKIP",0],["SLAVE",0],["SLOW",0],["SMALLINT",1],["SNAPSHOT",0],["SOCKET",0],["SOME",0],["SONAME",0],["SOUNDS",0],["SOURCE",0],["SOURCE_AUTO_POSITION",0],["SOURCE_BIND",0],["SOURCE_COMPRESSION_ALGORITHMS",0],["SOURCE_CONNECTION_AUTO_FAILOVER",0],["SOURCE_CONNECT_RETRY",0],["SOURCE_DELAY",0],["SOURCE_HEARTBEAT_PERIOD",0],["SOURCE_HOST",0],["SOURCE_LOG_FILE",0],["SOURCE_LOG_POS",0],["SOURCE_PASSWORD",0],["SOURCE_PORT",0],["SOURCE_PUBLIC_KEY_PATH",0],["SOURCE_RETRY_COUNT",0],["SOURCE_SSL",0],["SOURCE_SSL_CA",0],["SOURCE_SSL_CAPATH",0],["SOURCE_SSL_CERT",0],["SOURCE_SSL_CIPHER",0],["SOURCE_SSL_CRL",0],["SOURCE_SSL_CRLPATH",0],["SOURCE_SSL_KEY",0],["SOURCE_SSL_VERIFY_SERVER_CERT",0],["SOURCE_TLS_CIPHERSUITES",0],["SOURCE_TLS_VERSION",0],["SOURCE_USER",0],["SOURCE_ZSTD_COMPRESSION_LEVEL",0],["SPATIAL",1],["SPECIFIC",1],["SQL",1],["SQLEXCEPTION",1],["SQLSTATE",1],["SQLWARNING",1],["SQL_AFTER_GTIDS",0],["SQL_AFTER_MTS_GAPS",0],["SQL_BEFORE_GTIDS",0],["SQL_BIG_RESULT",1],["SQL_BUFFER_RESULT",0],["SQL_CALC_FOUND_ROWS",1],["SQL_NO_CACHE",0],["SQL_SMALL_RESULT",1],["SQL_THREAD",0],["SQL_TSI_DAY",0],["SQL_TSI_HOUR",0],["SQL_TSI_MINUTE",0],["SQL_TSI_MONTH",0],["SQL_TSI_QUARTER",0],["SQL_TSI_SECOND",0],["SQL_TSI_WEEK",0],["SQL_TSI_YEAR",0],["SRID",0],["SSL",1],["STACKED",0],["START",0],["STARTING",1],["STARTS",0],["STATS_AUTO_RECALC",0],["STATS_PERSISTENT",0],["STATS_SAMPLE_PAGES",0],["STATUS",0],["STOP",0],["STORAGE",0],["STORED",1],["STRAIGHT_JOIN",1],["STREAM",0],["STRING",0],["SUBCLASS_ORIGIN",0],["SUBJECT",0],["SUBPARTITION",0],["SUBPARTITIONS",0],["SUPER",0],["SUSPEND",0],["SWAPS",0],["SWITCHES",0],["SYSTEM",1],["TABLE",1],["TABLES",0],["TABLESPACE",0],["TABLE_CHECKSUM",0],["TABLE_NAME",0],["TEMPORARY",0],["TEMPTABLE",0],["TERMINATED",1],["TEXT",0],["THAN",0],["THEN",1],["THREAD_PRIORITY",0],["TIES",0],["TIME",0],["TIMESTAMP",0],["TIMESTAMPADD",0],["TIMESTAMPDIFF",0],["TINYBLOB",1],["TINYINT",1],["TINYTEXT",1],["TLS",0],["TO",1],["TRAILING",1],["TRANSACTION",0],["TRIGGER",1],["TRIGGERS",0],["TRUE",1],["TRUNCATE",0],["TYPE",0],["TYPES",0],["UNBOUNDED",0],["UNCOMMITTED",0],["UNDEFINED",0],["UNDO",1],["UNDOFILE",0],["UNDO_BUFFER_SIZE",0],["UNICODE",0],["UNINSTALL",0],["UNION",1],["UNIQUE",1],["UNKNOWN",0],["UNLOCK",1],["UNREGISTER",0],["UNSIGNED",1],["UNTIL",0],["UPDATE",1],["UPGRADE",0],["URL",0],["USAGE",1],["USE",1],["USER",0],["USER_RESOURCES",0],["USE_FRM",0],["USING",1],["UTC_DATE",1],["UTC_TIME",1],["UTC_TIMESTAMP",1],["VALIDATION",0],["VALUE",0],["VALUES",1],["VARBINARY",1],["VARCHAR",1],["VARCHARACTER",1],["VARIABLES",0],["VARYING",1],["VCPU",0],["VIEW",0],["VIRTUAL",1],["VISIBLE",0],["WAIT",0],["WARNINGS",0],["WEEK",0],["WEIGHT_STRING",0],["WHEN",1],["WHERE",1],["WHILE",1],["WINDOW",1],["WITH",1],["WITHOUT",0],["WORK",0],["WRAPPER",0],["WRITE",1],["X509",0],["XA",0],["XID",0],["XML",0],["XOR",1],["YEAR",0],["YEAR_MONTH",1],["ZEROFILL",1],["ZONE",0]]', '$[*]' columns (`word` varchar(128) character set utf8mb4 path '$[0]', `reserved` int path '$[1]')) AS `j` ;

-- --------------------------------------------------------

--
-- Structure for view `KEY_COLUMN_USAGE`
--
DROP TABLE IF EXISTS `KEY_COLUMN_USAGE`;

CREATE ALGORITHM=UNDEFINED DEFINER=`mysql.infoschema`@`localhost` SQL SECURITY DEFINER VIEW `KEY_COLUMN_USAGE`  AS SELECT (`cat`.`name` collate utf8mb3_tolower_ci) AS `CONSTRAINT_CATALOG`, (`sch`.`name` collate utf8mb3_tolower_ci) AS `CONSTRAINT_SCHEMA`, `constraints`.`CONSTRAINT_NAME` AS `CONSTRAINT_NAME`, (`cat`.`name` collate utf8mb3_tolower_ci) AS `TABLE_CATALOG`, (`sch`.`name` collate utf8mb3_tolower_ci) AS `TABLE_SCHEMA`, (`tbl`.`name` collate utf8mb3_tolower_ci) AS `TABLE_NAME`, (`col`.`name` collate utf8mb3_tolower_ci) AS `COLUMN_NAME`, `constraints`.`ORDINAL_POSITION` AS `ORDINAL_POSITION`, `constraints`.`POSITION_IN_UNIQUE_CONSTRAINT` AS `POSITION_IN_UNIQUE_CONSTRAINT`, `constraints`.`REFERENCED_TABLE_SCHEMA` AS `REFERENCED_TABLE_SCHEMA`, `constraints`.`REFERENCED_TABLE_NAME` AS `REFERENCED_TABLE_NAME`, `constraints`.`REFERENCED_COLUMN_NAME` AS `REFERENCED_COLUMN_NAME` FROM (((`mysql`.`tables` `tbl` join `mysql`.`schemata` `sch` on((`tbl`.`schema_id` = `sch`.`id`))) join `mysql`.`catalogs` `cat` on((`cat`.`id` = `sch`.`catalog_id`))) join (lateral (select `idx`.`name` AS `CONSTRAINT_NAME`,`icu`.`ordinal_position` AS `ORDINAL_POSITION`,NULL AS `POSITION_IN_UNIQUE_CONSTRAINT`,NULL AS `REFERENCED_TABLE_SCHEMA`,NULL AS `REFERENCED_TABLE_NAME`,NULL AS `REFERENCED_COLUMN_NAME`,`icu`.`column_id` AS `column_id`,((0 <> `idx`.`hidden`) or (0 <> `icu`.`hidden`)) AS `HIDDEN` from (`mysql`.`indexes` `idx` join `mysql`.`index_column_usage` `icu` on((`icu`.`index_id` = `idx`.`id`))) where ((`idx`.`table_id` = `tbl`.`id`) and (`idx`.`type` in ('PRIMARY','UNIQUE'))) union all select (`fk`.`name` collate utf8mb3_tolower_ci) AS `CONSTRAINT_NAME`,`fkcu`.`ordinal_position` AS `ORDINAL_POSITION`,`fkcu`.`ordinal_position` AS `POSITION_IN_UNIQUE_CONSTRAINT`,`fk`.`referenced_table_schema` AS `REFERENCED_TABLE_SCHEMA`,`fk`.`referenced_table_name` AS `REFERENCED_TABLE_NAME`,`fkcu`.`referenced_column_name` AS `REFERENCED_COLUMN_NAME`,`fkcu`.`column_id` AS `column_id`,false AS `HIDDEN` from (`mysql`.`foreign_keys` `fk` join `mysql`.`foreign_key_column_usage` `fkcu` on((`fkcu`.`foreign_key_id` = `fk`.`id`))) where (`fk`.`table_id` = `tbl`.`id`)) `constraints` join `mysql`.`columns` `col` on((`constraints`.`column_id` = `col`.`id`)))) WHERE ((0 <> can_access_column(`sch`.`name`,`tbl`.`name`,`col`.`name`)) AND (0 <> is_visible_dd_object(`tbl`.`hidden`,((`col`.`hidden` not in ('Visible','User')) OR (0 <> `constraints`.`HIDDEN`)),`col`.`options`))) ;

-- --------------------------------------------------------

--
-- Structure for view `OPTIMIZER_TRACE`
--
DROP TABLE IF EXISTS `OPTIMIZER_TRACE`;

CREATE TEMPORARY TABLE `OPTIMIZER_TRACE` (
  `QUERY` longtext NOT NULL,
  `TRACE` longtext NOT NULL,
  `MISSING_BYTES_BEYOND_MAX_MEM_SIZE` int NOT NULL DEFAULT '0',
  `INSUFFICIENT_PRIVILEGES` tinyint NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;

-- --------------------------------------------------------

--
-- Structure for view `PARAMETERS`
--
DROP TABLE IF EXISTS `PARAMETERS`;

CREATE ALGORITHM=UNDEFINED DEFINER=`mysql.infoschema`@`localhost` SQL SECURITY DEFINER VIEW `PARAMETERS`  AS SELECT (`cat`.`name` collate utf8mb3_tolower_ci) AS `SPECIFIC_CATALOG`, (`sch`.`name` collate utf8mb3_tolower_ci) AS `SPECIFIC_SCHEMA`, `rtn`.`name` AS `SPECIFIC_NAME`, if((`rtn`.`type` = 'FUNCTION'),(`prm`.`ordinal_position` - 1),`prm`.`ordinal_position`) AS `ORDINAL_POSITION`, if(((`rtn`.`type` = 'FUNCTION') and (`prm`.`ordinal_position` = 1)),NULL,`prm`.`mode`) AS `PARAMETER_MODE`, if(((`rtn`.`type` = 'FUNCTION') and (`prm`.`ordinal_position` = 1)),NULL,`prm`.`name`) AS `PARAMETER_NAME`, substring_index(substring_index(`prm`.`data_type_utf8`,'(',1),' ',1) AS `DATA_TYPE`, internal_dd_char_length(`prm`.`data_type`,`prm`.`char_length`,`col`.`name`,0) AS `CHARACTER_MAXIMUM_LENGTH`, internal_dd_char_length(`prm`.`data_type`,`prm`.`char_length`,`col`.`name`,1) AS `CHARACTER_OCTET_LENGTH`, `prm`.`numeric_precision` AS `NUMERIC_PRECISION`, if((`prm`.`numeric_precision` is null),NULL,ifnull(`prm`.`numeric_scale`,0)) AS `NUMERIC_SCALE`, `prm`.`datetime_precision` AS `DATETIME_PRECISION`, (case `prm`.`data_type` when 'MYSQL_TYPE_STRING' then if((`cs`.`name` = 'binary'),NULL,`cs`.`name`) when 'MYSQL_TYPE_VAR_STRING' then if((`cs`.`name` = 'binary'),NULL,`cs`.`name`) when 'MYSQL_TYPE_VARCHAR' then if((`cs`.`name` = 'binary'),NULL,`cs`.`name`) when 'MYSQL_TYPE_TINY_BLOB' then if((`cs`.`name` = 'binary'),NULL,`cs`.`name`) when 'MYSQL_TYPE_MEDIUM_BLOB' then if((`cs`.`name` = 'binary'),NULL,`cs`.`name`) when 'MYSQL_TYPE_BLOB' then if((`cs`.`name` = 'binary'),NULL,`cs`.`name`) when 'MYSQL_TYPE_LONG_BLOB' then if((`cs`.`name` = 'binary'),NULL,`cs`.`name`) when 'MYSQL_TYPE_ENUM' then if((`cs`.`name` = 'binary'),NULL,`cs`.`name`) when 'MYSQL_TYPE_SET' then if((`cs`.`name` = 'binary'),NULL,`cs`.`name`) else NULL end) AS `CHARACTER_SET_NAME`, (case `prm`.`data_type` when 'MYSQL_TYPE_STRING' then if((`cs`.`name` = 'binary'),NULL,`col`.`name`) when 'MYSQL_TYPE_VAR_STRING' then if((`cs`.`name` = 'binary'),NULL,`col`.`name`) when 'MYSQL_TYPE_VARCHAR' then if((`cs`.`name` = 'binary'),NULL,`col`.`name`) when 'MYSQL_TYPE_TINY_BLOB' then if((`cs`.`name` = 'binary'),NULL,`col`.`name`) when 'MYSQL_TYPE_MEDIUM_BLOB' then if((`cs`.`name` = 'binary'),NULL,`col`.`name`) when 'MYSQL_TYPE_BLOB' then if((`cs`.`name` = 'binary'),NULL,`col`.`name`) when 'MYSQL_TYPE_LONG_BLOB' then if((`cs`.`name` = 'binary'),NULL,`col`.`name`) when 'MYSQL_TYPE_ENUM' then if((`cs`.`name` = 'binary'),NULL,`col`.`name`) when 'MYSQL_TYPE_SET' then if((`cs`.`name` = 'binary'),NULL,`col`.`name`) else NULL end) AS `COLLATION_NAME`, `prm`.`data_type_utf8` AS `DTD_IDENTIFIER`, `rtn`.`type` AS `ROUTINE_TYPE` FROM (((((`mysql`.`parameters` `prm` join `mysql`.`routines` `rtn` on((`prm`.`routine_id` = `rtn`.`id`))) join `mysql`.`schemata` `sch` on((`rtn`.`schema_id` = `sch`.`id`))) join `mysql`.`catalogs` `cat` on((`cat`.`id` = `sch`.`catalog_id`))) join `mysql`.`collations` `col` on((`prm`.`collation_id` = `col`.`id`))) join `mysql`.`character_sets` `cs` on((`col`.`character_set_id` = `cs`.`id`))) WHERE (0 <> can_access_routine(`sch`.`name`,`rtn`.`name`,`rtn`.`type`,`rtn`.`definer`,false)) ;

-- --------------------------------------------------------

--
-- Structure for view `PARTITIONS`
--
DROP TABLE IF EXISTS `PARTITIONS`;

CREATE ALGORITHM=UNDEFINED DEFINER=`mysql.infoschema`@`localhost` SQL SECURITY DEFINER VIEW `PARTITIONS`  AS SELECT (`cat`.`name` collate utf8mb3_tolower_ci) AS `TABLE_CATALOG`, (`sch`.`name` collate utf8mb3_tolower_ci) AS `TABLE_SCHEMA`, `tbl`.`name` AS `TABLE_NAME`, `part`.`name` AS `PARTITION_NAME`, `sub_part`.`name` AS `SUBPARTITION_NAME`, (`part`.`number` + 1) AS `PARTITION_ORDINAL_POSITION`, (`sub_part`.`number` + 1) AS `SUBPARTITION_ORDINAL_POSITION`, (case `tbl`.`partition_type` when 'HASH' then 'HASH' when 'RANGE' then 'RANGE' when 'LIST' then 'LIST' when 'AUTO' then 'AUTO' when 'KEY_51' then 'KEY' when 'KEY_55' then 'KEY' when 'LINEAR_KEY_51' then 'LINEAR KEY' when 'LINEAR_KEY_55' then 'LINEAR KEY' when 'LINEAR_HASH' then 'LINEAR HASH' when 'RANGE_COLUMNS' then 'RANGE COLUMNS' when 'LIST_COLUMNS' then 'LIST COLUMNS' else NULL end) AS `PARTITION_METHOD`, (case `tbl`.`subpartition_type` when 'HASH' then 'HASH' when 'RANGE' then 'RANGE' when 'LIST' then 'LIST' when 'AUTO' then 'AUTO' when 'KEY_51' then 'KEY' when 'KEY_55' then 'KEY' when 'LINEAR_KEY_51' then 'LINEAR KEY' when 'LINEAR_KEY_55' then 'LINEAR KEY' when 'LINEAR_HASH' then 'LINEAR HASH' when 'RANGE_COLUMNS' then 'RANGE COLUMNS' when 'LIST_COLUMNS' then 'LIST COLUMNS' else NULL end) AS `SUBPARTITION_METHOD`, `tbl`.`partition_expression_utf8` AS `PARTITION_EXPRESSION`, `tbl`.`subpartition_expression_utf8` AS `SUBPARTITION_EXPRESSION`, `part`.`description_utf8` AS `PARTITION_DESCRIPTION`, internal_table_rows(`sch`.`name`,`tbl`.`name`,if((`tbl`.`partition_type` is null),`tbl`.`engine`,''),`tbl`.`se_private_id`,(`tbl`.`hidden` <> 'Visible'),if((`sub_part`.`name` is null),if((`part`.`name` is null),`tbl`.`se_private_data`,`part_ts`.`se_private_data`),`sub_part_ts`.`se_private_data`),0,0,ifnull(`sub_part`.`name`,`part`.`name`)) AS `TABLE_ROWS`, internal_avg_row_length(`sch`.`name`,`tbl`.`name`,if((`tbl`.`partition_type` is null),`tbl`.`engine`,''),`tbl`.`se_private_id`,(`tbl`.`hidden` <> 'Visible'),if((`sub_part`.`name` is null),if((`part`.`name` is null),`tbl`.`se_private_data`,`part_ts`.`se_private_data`),`sub_part_ts`.`se_private_data`),0,0,ifnull(`sub_part`.`name`,`part`.`name`)) AS `AVG_ROW_LENGTH`, internal_data_length(`sch`.`name`,`tbl`.`name`,if((`tbl`.`partition_type` is null),`tbl`.`engine`,''),`tbl`.`se_private_id`,(`tbl`.`hidden` <> 'Visible'),if((`sub_part`.`name` is null),if((`part`.`name` is null),`tbl`.`se_private_data`,`part_ts`.`se_private_data`),`sub_part_ts`.`se_private_data`),0,0,ifnull(`sub_part`.`name`,`part`.`name`)) AS `DATA_LENGTH`, internal_max_data_length(`sch`.`name`,`tbl`.`name`,if((`tbl`.`partition_type` is null),`tbl`.`engine`,''),`tbl`.`se_private_id`,(`tbl`.`hidden` <> 'Visible'),if((`sub_part`.`name` is null),if((`part`.`name` is null),`tbl`.`se_private_data`,`part_ts`.`se_private_data`),`sub_part_ts`.`se_private_data`),0,0,ifnull(`sub_part`.`name`,`part`.`name`)) AS `MAX_DATA_LENGTH`, internal_index_length(`sch`.`name`,`tbl`.`name`,if((`tbl`.`partition_type` is null),`tbl`.`engine`,''),`tbl`.`se_private_id`,(`tbl`.`hidden` <> 'Visible'),if((`sub_part`.`name` is null),if((`part`.`name` is null),`tbl`.`se_private_data`,`part_ts`.`se_private_data`),`sub_part_ts`.`se_private_data`),0,0,ifnull(`sub_part`.`name`,`part`.`name`)) AS `INDEX_LENGTH`, internal_data_free(`sch`.`name`,`tbl`.`name`,if((`tbl`.`partition_type` is null),`tbl`.`engine`,''),`tbl`.`se_private_id`,(`tbl`.`hidden` <> 'Visible'),if((`sub_part`.`name` is null),if((`part`.`name` is null),`tbl`.`se_private_data`,`part_ts`.`se_private_data`),`sub_part_ts`.`se_private_data`),0,0,ifnull(`sub_part`.`name`,`part`.`name`)) AS `DATA_FREE`, `tbl`.`created` AS `CREATE_TIME`, internal_update_time(`sch`.`name`,`tbl`.`name`,if((`tbl`.`partition_type` is null),`tbl`.`engine`,''),`tbl`.`se_private_id`,(`tbl`.`hidden` <> 'Visible'),if((`sub_part`.`name` is null),if((`part`.`name` is null),`tbl`.`se_private_data`,`part_ts`.`se_private_data`),`sub_part_ts`.`se_private_data`),0,0,ifnull(`sub_part`.`name`,`part`.`name`)) AS `UPDATE_TIME`, internal_check_time(`sch`.`name`,`tbl`.`name`,if((`tbl`.`partition_type` is null),`tbl`.`engine`,''),`tbl`.`se_private_id`,(`tbl`.`hidden` <> 'Visible'),if((`sub_part`.`name` is null),if((`part`.`name` is null),`tbl`.`se_private_data`,`part_ts`.`se_private_data`),`sub_part_ts`.`se_private_data`),0,0,ifnull(`sub_part`.`name`,`part`.`name`)) AS `CHECK_TIME`, internal_checksum(`sch`.`name`,`tbl`.`name`,if((`tbl`.`partition_type` is null),`tbl`.`engine`,''),`tbl`.`se_private_id`,(`tbl`.`hidden` <> 'Visible'),if((`sub_part`.`name` is null),if((`part`.`name` is null),`tbl`.`se_private_data`,`part_ts`.`se_private_data`),`sub_part_ts`.`se_private_data`),0,0,ifnull(`sub_part`.`name`,`part`.`name`)) AS `CHECKSUM`, if((`sub_part`.`name` is null),ifnull(`part`.`comment`,''),ifnull(`sub_part`.`comment`,'')) AS `PARTITION_COMMENT`, if((`part`.`name` is null),'',internal_get_partition_nodegroup(if((`sub_part`.`name` is null),`part`.`options`,`sub_part`.`options`))) AS `NODEGROUP`, ifnull(`sub_part_ts`.`name`,`part_ts`.`name`) AS `TABLESPACE_NAME` FROM ((((((`mysql`.`tables` `tbl` join `mysql`.`schemata` `sch` on((`sch`.`id` = `tbl`.`schema_id`))) join `mysql`.`catalogs` `cat` on((`cat`.`id` = `sch`.`catalog_id`))) left join `mysql`.`table_partitions` `part` on((`part`.`table_id` = `tbl`.`id`))) left join `mysql`.`table_partitions` `sub_part` on((`sub_part`.`parent_partition_id` = `part`.`id`))) left join `mysql`.`tablespaces` `part_ts` on((`part_ts`.`id` = `part`.`tablespace_id`))) left join `mysql`.`tablespaces` `sub_part_ts` on(((`sub_part`.`tablespace_id` is not null) and (`sub_part_ts`.`id` = `sub_part`.`tablespace_id`)))) WHERE ((0 <> can_access_table(`sch`.`name`,`tbl`.`name`)) AND (0 <> is_visible_dd_object(`tbl`.`hidden`)) AND (`part`.`parent_partition_id` is null)) ;

-- --------------------------------------------------------

--
-- Structure for view `PLUGINS`
--
DROP TABLE IF EXISTS `PLUGINS`;

CREATE TEMPORARY TABLE `PLUGINS` (
  `PLUGIN_NAME` varchar(64) NOT NULL DEFAULT '',
  `PLUGIN_VERSION` varchar(20) NOT NULL DEFAULT '',
  `PLUGIN_STATUS` varchar(10) NOT NULL DEFAULT '',
  `PLUGIN_TYPE` varchar(80) NOT NULL DEFAULT '',
  `PLUGIN_TYPE_VERSION` varchar(20) NOT NULL DEFAULT '',
  `PLUGIN_LIBRARY` varchar(64) DEFAULT NULL,
  `PLUGIN_LIBRARY_VERSION` varchar(20) DEFAULT NULL,
  `PLUGIN_AUTHOR` varchar(64) DEFAULT NULL,
  `PLUGIN_DESCRIPTION` longtext,
  `PLUGIN_LICENSE` varchar(80) DEFAULT NULL,
  `LOAD_OPTION` varchar(64) NOT NULL DEFAULT ''
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;

-- --------------------------------------------------------

--
-- Structure for view `PROCESSLIST`
--
DROP TABLE IF EXISTS `PROCESSLIST`;

CREATE TEMPORARY TABLE `PROCESSLIST` (
  `ID` bigint UNSIGNED NOT NULL DEFAULT '0',
  `USER` varchar(32) NOT NULL DEFAULT '',
  `HOST` varchar(261) NOT NULL DEFAULT '',
  `DB` varchar(64) DEFAULT NULL,
  `COMMAND` varchar(16) NOT NULL DEFAULT '',
  `TIME` int NOT NULL DEFAULT '0',
  `STATE` varchar(64) DEFAULT NULL,
  `INFO` longtext
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;

-- --------------------------------------------------------

--
-- Structure for view `PROFILING`
--
DROP TABLE IF EXISTS `PROFILING`;

CREATE TEMPORARY TABLE `PROFILING` (
  `QUERY_ID` int NOT NULL DEFAULT '0',
  `SEQ` int NOT NULL DEFAULT '0',
  `STATE` varchar(30) NOT NULL DEFAULT '',
  `DURATION` decimal(9,6) NOT NULL DEFAULT '0.000000',
  `CPU_USER` decimal(9,6) DEFAULT NULL,
  `CPU_SYSTEM` decimal(9,6) DEFAULT NULL,
  `CONTEXT_VOLUNTARY` int DEFAULT NULL,
  `CONTEXT_INVOLUNTARY` int DEFAULT NULL,
  `BLOCK_OPS_IN` int DEFAULT NULL,
  `BLOCK_OPS_OUT` int DEFAULT NULL,
  `MESSAGES_SENT` int DEFAULT NULL,
  `MESSAGES_RECEIVED` int DEFAULT NULL,
  `PAGE_FAULTS_MAJOR` int DEFAULT NULL,
  `PAGE_FAULTS_MINOR` int DEFAULT NULL,
  `SWAPS` int DEFAULT NULL,
  `SOURCE_FUNCTION` varchar(30) DEFAULT NULL,
  `SOURCE_FILE` varchar(20) DEFAULT NULL,
  `SOURCE_LINE` int DEFAULT NULL
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3;

-- --------------------------------------------------------

--
-- Structure for view `REFERENTIAL_CONSTRAINTS`
--
DROP TABLE IF EXISTS `REFERENTIAL_CONSTRAINTS`;

CREATE ALGORITHM=UNDEFINED DEFINER=`mysql.infoschema`@`localhost` SQL SECURITY DEFINER VIEW `REFERENTIAL_CONSTRAINTS`  AS SELECT `cat`.`name` AS `CONSTRAINT_CATALOG`, `sch`.`name` AS `CONSTRAINT_SCHEMA`, (`fk`.`name` collate utf8mb3_tolower_ci) AS `CONSTRAINT_NAME`, `fk`.`referenced_table_catalog` AS `UNIQUE_CONSTRAINT_CATALOG`, `fk`.`referenced_table_schema` AS `UNIQUE_CONSTRAINT_SCHEMA`, `fk`.`unique_constraint_name` AS `UNIQUE_CONSTRAINT_NAME`, `fk`.`match_option` AS `MATCH_OPTION`, `fk`.`update_rule` AS `UPDATE_RULE`, `fk`.`delete_rule` AS `DELETE_RULE`, `tbl`.`name` AS `TABLE_NAME`, `fk`.`referenced_table_name` AS `REFERENCED_TABLE_NAME` FROM (((`mysql`.`foreign_keys` `fk` join `mysql`.`tables` `tbl` on((`fk`.`table_id` = `tbl`.`id`))) join `mysql`.`schemata` `sch` on((`fk`.`schema_id` = `sch`.`id`))) join `mysql`.`catalogs` `cat` on((`cat`.`id` = `sch`.`catalog_id`))) WHERE ((0 <> can_access_table(`sch`.`name`,`tbl`.`name`)) AND (0 <> is_visible_dd_object(`tbl`.`hidden`))) ;

-- --------------------------------------------------------

--
-- Structure for view `RESOURCE_GROUPS`
--
DROP TABLE IF EXISTS `RESOURCE_GROUPS`;

CREATE ALGORITHM=UNDEFINED DEFINER=`mysql.infoschema`@`localhost` SQL SECURITY DEFINER VIEW `RESOURCE_GROUPS`  AS SELECT `res`.`resource_group_name` AS `RESOURCE_GROUP_NAME`, `res`.`resource_group_type` AS `RESOURCE_GROUP_TYPE`, `res`.`resource_group_enabled` AS `RESOURCE_GROUP_ENABLED`, convert_cpu_id_mask(`res`.`cpu_id_mask`) AS `VCPU_IDS`, `res`.`thread_priority` AS `THREAD_PRIORITY` FROM `mysql`.`resource_groups` AS `res` WHERE (0 <> can_access_resource_group(`res`.`resource_group_name`)) ;

-- --------------------------------------------------------

--
-- Structure for view `ROLE_COLUMN_GRANTS`
--
DROP TABLE IF EXISTS `ROLE_COLUMN_GRANTS`;

CREATE ALGORITHM=UNDEFINED DEFINER=`mysql.infoschema`@`localhost` SQL SECURITY DEFINER VIEW `ROLE_COLUMN_GRANTS`  AS WITH recursive   `role_graph` (`c_parent_user`,`c_parent_host`,`c_from_user`,`c_from_host`,`c_to_user`,`c_to_host`,`role_path`,`c_with_admin`,`c_enabled`) as (select internal_get_username() AS `INTERNAL_GET_USERNAME()`,internal_get_hostname() AS `INTERNAL_GET_HOSTNAME()`,internal_get_username() AS `INTERNAL_GET_USERNAME()`,internal_get_hostname() AS `INTERNAL_GET_HOSTNAME()`,cast('' as char(64) charset utf8mb4) AS `CAST('' as CHAR(64) CHARSET utf8mb4)`,cast('' as char(255) charset utf8mb4) AS `CAST('' as CHAR(255) CHARSET utf8mb4)`,cast(sha2(concat(quote(internal_get_username()),'@',quote(internal_get_hostname())),256) as char(17000) charset utf8mb4) AS `CAST(SHA2(CONCAT(QUOTE(INTERNAL_GET_USERNAME()),'@',                        QUOTE(INTERNAL_GET_HOSTNAME())), 256)            AS CHAR(17000) CHARSET utf8mb4)`,cast('N' as char(1) charset utf8mb4) AS `CAST('N' as CHAR(1) CHARSET utf8mb4)`,false AS `FALSE` union select internal_get_username() AS `INTERNAL_GET_USERNAME()`,internal_get_hostname() AS `INTERNAL_GET_HOSTNAME()`,`mandatory_roles`.`ROLE_NAME` AS `ROLE_NAME`,`mandatory_roles`.`ROLE_HOST` AS `ROLE_HOST`,internal_get_username() AS `INTERNAL_GET_USERNAME()`,internal_get_hostname() AS `INTERNAL_GET_HOSTNAME()`,cast(sha2(concat(quote(`mandatory_roles`.`ROLE_NAME`),'@',convert(quote(`mandatory_roles`.`ROLE_HOST`) using utf8mb4)),256) as char(17000) charset utf8mb4) AS `CAST(SHA2(CONCAT(QUOTE(ROLE_NAME),'@',                   CONVERT(QUOTE(ROLE_HOST) using utf8mb4)), 256)              AS CHAR(17000) CHARSET utf8mb4)`,cast('N' as char(1) charset utf8mb4) AS `CAST('N' as CHAR(1) CHARSET utf8mb4)`,false AS `FALSE` from json_table(internal_get_mandatory_roles_json(), '$[*]' columns (`ROLE_NAME` varchar(255) character set utf8mb4 path '$.ROLE_NAME', `ROLE_HOST` varchar(255) character set utf8mb4 path '$.ROLE_HOST')) `mandatory_roles` where concat(quote(`mandatory_roles`.`ROLE_NAME`),'@',convert(quote(`mandatory_roles`.`ROLE_HOST`) using utf8mb4)) in (select concat(convert(quote(`mysql`.`role_edges`.`FROM_USER`) using utf8mb4),'@',convert(quote(`mysql`.`role_edges`.`FROM_HOST`) using utf8mb4)) from `mysql`.`role_edges` where ((`mysql`.`role_edges`.`TO_USER` = internal_get_username()) and (convert(`mysql`.`role_edges`.`TO_HOST` using utf8mb4) = convert(internal_get_hostname() using utf8mb4)))) is false union select `role_graph`.`c_parent_user` AS `c_parent_user`,`role_graph`.`c_parent_host` AS `c_parent_host`,`mysql`.`role_edges`.`FROM_USER` AS `FROM_USER`,`mysql`.`role_edges`.`FROM_HOST` AS `FROM_HOST`,`mysql`.`role_edges`.`TO_USER` AS `TO_USER`,`mysql`.`role_edges`.`TO_HOST` AS `TO_HOST`,if((locate(sha2(concat(convert(quote(`mysql`.`role_edges`.`FROM_USER`) using utf8mb4),'@',convert(quote(`mysql`.`role_edges`.`FROM_HOST`) using utf8mb4)),256),`role_graph`.`role_path`) = 0),concat(`role_graph`.`role_path`,'->',convert(sha2(concat(convert(quote(`mysql`.`role_edges`.`FROM_USER`) using utf8mb4),'@',convert(quote(`mysql`.`role_edges`.`FROM_HOST`) using utf8mb4)),256) using utf8mb4)),NULL) AS `IF(LOCATE(SHA2(CONCAT(QUOTE(FROM_USER),'@',                      CONVERT(QUOTE(FROM_HOST) using utf8mb4)), 256),                 role_path) = 0,          CONCAT(role_path,'->', SHA2(CONCAT(QUOTE(FROM_USER),'@',           CONVERT(QUOTE(FROM_HOST) using utf8`,`mysql`.`role_edges`.`WITH_ADMIN_OPTION` AS `WITH_ADMIN_OPTION`,if(((0 <> `role_graph`.`c_enabled`) or (0 <> internal_is_enabled_role(`mysql`.`role_edges`.`FROM_USER`,`mysql`.`role_edges`.`FROM_HOST`))),true,false) AS `IF(c_enabled OR        INTERNAL_IS_ENABLED_ROLE(FROM_USER, FROM_HOST), TRUE, FALSE)` from (`mysql`.`role_edges` join `role_graph`) where ((`mysql`.`role_edges`.`TO_USER` = `role_graph`.`c_from_user`) and (convert(`mysql`.`role_edges`.`TO_HOST` using utf8mb4) = `role_graph`.`c_from_host`) and (`role_graph`.`role_path` is not null))) select distinct internal_get_username(`tp`.`Grantor`) AS `GRANTOR`,internal_get_hostname(`tp`.`Grantor`) AS `GRANTOR_HOST`,`cp`.`User` AS `GRANTEE`,`cp`.`Host` AS `GRANTEE_HOST`,'def' AS `TABLE_CATALOG`,`cp`.`Db` AS `TABLE_SCHEMA`,`cp`.`Table_name` AS `TABLE_NAME`,`cp`.`Column_name` AS `COLUMN_NAME`,`cp`.`Column_priv` AS `PRIVILEGE_TYPE`,if((find_in_set('Grant',`tp`.`Table_priv`) > 0),'YES','NO') AS `IS_GRANTABLE` from ((`mysql`.`tables_priv` `tp` join `role_graph` `rg` on(((`tp`.`User` = `rg`.`c_from_user`) and (convert(`tp`.`Host` using utf8mb4) = `rg`.`c_from_host`)))) join `mysql`.`columns_priv` `cp` on(((convert(`tp`.`Host` using utf8mb4) = `cp`.`Host`) and (`cp`.`Db` = `tp`.`Db`) and (`cp`.`User` = `tp`.`User`) and (`cp`.`Table_name` = `tp`.`Table_name`)))) where ((`cp`.`Column_priv` > 0) and (`rg`.`c_to_user` <> '') and (`rg`.`c_enabled` = true))  ;

-- --------------------------------------------------------

--
-- Structure for view `ROLE_ROUTINE_GRANTS`
--
DROP TABLE IF EXISTS `ROLE_ROUTINE_GRANTS`;

CREATE ALGORITHM=UNDEFINED DEFINER=`mysql.infoschema`@`localhost` SQL SECURITY DEFINER VIEW `ROLE_ROUTINE_GRANTS`  AS WITH recursive   `role_graph` (`c_parent_user`,`c_parent_host`,`c_from_user`,`c_from_host`,`c_to_user`,`c_to_host`,`role_path`,`c_with_admin`,`c_enabled`) as (select internal_get_username() AS `INTERNAL_GET_USERNAME()`,internal_get_hostname() AS `INTERNAL_GET_HOSTNAME()`,internal_get_username() AS `INTERNAL_GET_USERNAME()`,internal_get_hostname() AS `INTERNAL_GET_HOSTNAME()`,cast('' as char(64) charset utf8mb4) AS `CAST('' as CHAR(64) CHARSET utf8mb4)`,cast('' as char(255) charset utf8mb4) AS `CAST('' as CHAR(255) CHARSET utf8mb4)`,cast(sha2(concat(quote(internal_get_username()),'@',quote(internal_get_hostname())),256) as char(17000) charset utf8mb4) AS `CAST(SHA2(CONCAT(QUOTE(INTERNAL_GET_USERNAME()),'@',                        QUOTE(INTERNAL_GET_HOSTNAME())), 256)            AS CHAR(17000) CHARSET utf8mb4)`,cast('N' as char(1) charset utf8mb4) AS `CAST('N' as CHAR(1) CHARSET utf8mb4)`,false AS `FALSE` union select internal_get_username() AS `INTERNAL_GET_USERNAME()`,internal_get_hostname() AS `INTERNAL_GET_HOSTNAME()`,`mandatory_roles`.`ROLE_NAME` AS `ROLE_NAME`,`mandatory_roles`.`ROLE_HOST` AS `ROLE_HOST`,internal_get_username() AS `INTERNAL_GET_USERNAME()`,internal_get_hostname() AS `INTERNAL_GET_HOSTNAME()`,cast(sha2(concat(quote(`mandatory_roles`.`ROLE_NAME`),'@',convert(quote(`mandatory_roles`.`ROLE_HOST`) using utf8mb4)),256) as char(17000) charset utf8mb4) AS `CAST(SHA2(CONCAT(QUOTE(ROLE_NAME),'@',                   CONVERT(QUOTE(ROLE_HOST) using utf8mb4)), 256)              AS CHAR(17000) CHARSET utf8mb4)`,cast('N' as char(1) charset utf8mb4) AS `CAST('N' as CHAR(1) CHARSET utf8mb4)`,false AS `FALSE` from json_table(internal_get_mandatory_roles_json(), '$[*]' columns (`ROLE_NAME` varchar(255) character set utf8mb4 path '$.ROLE_NAME', `ROLE_HOST` varchar(255) character set utf8mb4 path '$.ROLE_HOST')) `mandatory_roles` where concat(quote(`mandatory_roles`.`ROLE_NAME`),'@',convert(quote(`mandatory_roles`.`ROLE_HOST`) using utf8mb4)) in (select concat(convert(quote(`mysql`.`role_edges`.`FROM_USER`) using utf8mb4),'@',convert(quote(`mysql`.`role_edges`.`FROM_HOST`) using utf8mb4)) from `mysql`.`role_edges` where ((`mysql`.`role_edges`.`TO_USER` = internal_get_username()) and (convert(`mysql`.`role_edges`.`TO_HOST` using utf8mb4) = convert(internal_get_hostname() using utf8mb4)))) is false union select `role_graph`.`c_parent_user` AS `c_parent_user`,`role_graph`.`c_parent_host` AS `c_parent_host`,`mysql`.`role_edges`.`FROM_USER` AS `FROM_USER`,`mysql`.`role_edges`.`FROM_HOST` AS `FROM_HOST`,`mysql`.`role_edges`.`TO_USER` AS `TO_USER`,`mysql`.`role_edges`.`TO_HOST` AS `TO_HOST`,if((locate(sha2(concat(convert(quote(`mysql`.`role_edges`.`FROM_USER`) using utf8mb4),'@',convert(quote(`mysql`.`role_edges`.`FROM_HOST`) using utf8mb4)),256),`role_graph`.`role_path`) = 0),concat(`role_graph`.`role_path`,'->',convert(sha2(concat(convert(quote(`mysql`.`role_edges`.`FROM_USER`) using utf8mb4),'@',convert(quote(`mysql`.`role_edges`.`FROM_HOST`) using utf8mb4)),256) using utf8mb4)),NULL) AS `IF(LOCATE(SHA2(CONCAT(QUOTE(FROM_USER),'@',                      CONVERT(QUOTE(FROM_HOST) using utf8mb4)), 256),                 role_path) = 0,          CONCAT(role_path,'->', SHA2(CONCAT(QUOTE(FROM_USER),'@',           CONVERT(QUOTE(FROM_HOST) using utf8`,`mysql`.`role_edges`.`WITH_ADMIN_OPTION` AS `WITH_ADMIN_OPTION`,if(((0 <> `role_graph`.`c_enabled`) or (0 <> internal_is_enabled_role(`mysql`.`role_edges`.`FROM_USER`,`mysql`.`role_edges`.`FROM_HOST`))),true,false) AS `IF(c_enabled OR        INTERNAL_IS_ENABLED_ROLE(FROM_USER, FROM_HOST), TRUE, FALSE)` from (`mysql`.`role_edges` join `role_graph`) where ((`mysql`.`role_edges`.`TO_USER` = `role_graph`.`c_from_user`) and (convert(`mysql`.`role_edges`.`TO_HOST` using utf8mb4) = `role_graph`.`c_from_host`) and (`role_graph`.`role_path` is not null))) select distinct internal_get_username(`pp`.`Grantor`) AS `GRANTOR`,internal_get_hostname(`pp`.`Grantor`) AS `GRANTOR_HOST`,`pp`.`User` AS `GRANTEE`,`pp`.`Host` AS `GRANTEE_HOST`,'def' AS `SPECIFIC_CATALOG`,`pp`.`Db` AS `SPECIFIC_SCHEMA`,`pp`.`Routine_name` AS `SPECIFIC_NAME`,'def' AS `ROUTINE_CATALOG`,`pp`.`Db` AS `ROUTINE_SCHEMA`,`pp`.`Routine_name` AS `ROUTINE_NAME`,`pp`.`Proc_priv` AS `PRIVILEGE_TYPE`,if((find_in_set('Grant',`pp`.`Proc_priv`) > 0),'YES','NO') AS `IS_GRANTABLE` from (`mysql`.`procs_priv` `pp` join `role_graph` `rg` on(((`pp`.`User` = `rg`.`c_from_user`) and (convert(`pp`.`Host` using utf8mb4) = `rg`.`c_from_host`)))) where ((`pp`.`Proc_priv` > 0) and (`rg`.`c_to_user` <> '') and (`rg`.`c_enabled` = true))  ;

-- --------------------------------------------------------

--
-- Structure for view `ROLE_TABLE_GRANTS`
--
DROP TABLE IF EXISTS `ROLE_TABLE_GRANTS`;

CREATE ALGORITHM=UNDEFINED DEFINER=`mysql.infoschema`@`localhost` SQL SECURITY DEFINER VIEW `ROLE_TABLE_GRANTS`  AS WITH recursive   `role_graph` (`c_parent_user`,`c_parent_host`,`c_from_user`,`c_from_host`,`c_to_user`,`c_to_host`,`role_path`,`c_with_admin`,`c_enabled`) as (select internal_get_username() AS `INTERNAL_GET_USERNAME()`,internal_get_hostname() AS `INTERNAL_GET_HOSTNAME()`,internal_get_username() AS `INTERNAL_GET_USERNAME()`,internal_get_hostname() AS `INTERNAL_GET_HOSTNAME()`,cast('' as char(64) charset utf8mb4) AS `CAST('' as CHAR(64) CHARSET utf8mb4)`,cast('' as char(255) charset utf8mb4) AS `CAST('' as CHAR(255) CHARSET utf8mb4)`,cast(sha2(concat(quote(internal_get_username()),'@',quote(internal_get_hostname())),256) as char(17000) charset utf8mb4) AS `CAST(SHA2(CONCAT(QUOTE(INTERNAL_GET_USERNAME()),'@',                        QUOTE(INTERNAL_GET_HOSTNAME())), 256)            AS CHAR(17000) CHARSET utf8mb4)`,cast('N' as char(1) charset utf8mb4) AS `CAST('N' as CHAR(1) CHARSET utf8mb4)`,false AS `FALSE` union select internal_get_username() AS `INTERNAL_GET_USERNAME()`,internal_get_hostname() AS `INTERNAL_GET_HOSTNAME()`,`mandatory_roles`.`ROLE_NAME` AS `ROLE_NAME`,`mandatory_roles`.`ROLE_HOST` AS `ROLE_HOST`,internal_get_username() AS `INTERNAL_GET_USERNAME()`,internal_get_hostname() AS `INTERNAL_GET_HOSTNAME()`,cast(sha2(concat(quote(`mandatory_roles`.`ROLE_NAME`),'@',convert(quote(`mandatory_roles`.`ROLE_HOST`) using utf8mb4)),256) as char(17000) charset utf8mb4) AS `CAST(SHA2(CONCAT(QUOTE(ROLE_NAME),'@',                   CONVERT(QUOTE(ROLE_HOST) using utf8mb4)), 256)              AS CHAR(17000) CHARSET utf8mb4)`,cast('N' as char(1) charset utf8mb4) AS `CAST('N' as CHAR(1) CHARSET utf8mb4)`,false AS `FALSE` from json_table(internal_get_mandatory_roles_json(), '$[*]' columns (`ROLE_NAME` varchar(255) character set utf8mb4 path '$.ROLE_NAME', `ROLE_HOST` varchar(255) character set utf8mb4 path '$.ROLE_HOST')) `mandatory_roles` where concat(quote(`mandatory_roles`.`ROLE_NAME`),'@',convert(quote(`mandatory_roles`.`ROLE_HOST`) using utf8mb4)) in (select concat(convert(quote(`mysql`.`role_edges`.`FROM_USER`) using utf8mb4),'@',convert(quote(`mysql`.`role_edges`.`FROM_HOST`) using utf8mb4)) from `mysql`.`role_edges` where ((`mysql`.`role_edges`.`TO_USER` = internal_get_username()) and (convert(`mysql`.`role_edges`.`TO_HOST` using utf8mb4) = convert(internal_get_hostname() using utf8mb4)))) is false union select `role_graph`.`c_parent_user` AS `c_parent_user`,`role_graph`.`c_parent_host` AS `c_parent_host`,`mysql`.`role_edges`.`FROM_USER` AS `FROM_USER`,`mysql`.`role_edges`.`FROM_HOST` AS `FROM_HOST`,`mysql`.`role_edges`.`TO_USER` AS `TO_USER`,`mysql`.`role_edges`.`TO_HOST` AS `TO_HOST`,if((locate(sha2(concat(convert(quote(`mysql`.`role_edges`.`FROM_USER`) using utf8mb4),'@',convert(quote(`mysql`.`role_edges`.`FROM_HOST`) using utf8mb4)),256),`role_graph`.`role_path`) = 0),concat(`role_graph`.`role_path`,'->',convert(sha2(concat(convert(quote(`mysql`.`role_edges`.`FROM_USER`) using utf8mb4),'@',convert(quote(`mysql`.`role_edges`.`FROM_HOST`) using utf8mb4)),256) using utf8mb4)),NULL) AS `IF(LOCATE(SHA2(CONCAT(QUOTE(FROM_USER),'@',                      CONVERT(QUOTE(FROM_HOST) using utf8mb4)), 256),                 role_path) = 0,          CONCAT(role_path,'->', SHA2(CONCAT(QUOTE(FROM_USER),'@',           CONVERT(QUOTE(FROM_HOST) using utf8`,`mysql`.`role_edges`.`WITH_ADMIN_OPTION` AS `WITH_ADMIN_OPTION`,if(((0 <> `role_graph`.`c_enabled`) or (0 <> internal_is_enabled_role(`mysql`.`role_edges`.`FROM_USER`,`mysql`.`role_edges`.`FROM_HOST`))),true,false) AS `IF(c_enabled OR        INTERNAL_IS_ENABLED_ROLE(FROM_USER, FROM_HOST), TRUE, FALSE)` from (`mysql`.`role_edges` join `role_graph`) where ((`mysql`.`role_edges`.`TO_USER` = `role_graph`.`c_from_user`) and (convert(`mysql`.`role_edges`.`TO_HOST` using utf8mb4) = `role_graph`.`c_from_host`) and (`role_graph`.`role_path` is not null))) select distinct internal_get_username(`tp`.`Grantor`) AS `GRANTOR`,internal_get_hostname(`tp`.`Grantor`) AS `GRANTOR_HOST`,`tp`.`User` AS `GRANTEE`,`tp`.`Host` AS `GRANTEE_HOST`,'def' AS `TABLE_CATALOG`,`tp`.`Db` AS `TABLE_SCHEMA`,`tp`.`Table_name` AS `TABLE_NAME`,`tp`.`Table_priv` AS `PRIVILEGE_TYPE`,if((find_in_set('Grant',`tp`.`Table_priv`) > 0),'YES','NO') AS `IS_GRANTABLE` from (`mysql`.`tables_priv` `tp` join `role_graph` `rg` on(((`tp`.`User` = `rg`.`c_from_user`) and (convert(`tp`.`Host` using utf8mb4) = `rg`.`c_from_host`)))) where ((`tp`.`Table_priv` > 0) and (`rg`.`c_to_user` <> '') and (`rg`.`c_enabled` = true))  ;

-- --------------------------------------------------------

--
-- Structure for view `ROUTINES`
--
DROP TABLE IF EXISTS `ROUTINES`;

CREATE ALGORITHM=UNDEFINED DEFINER=`mysql.infoschema`@`localhost` SQL SECURITY DEFINER VIEW `ROUTINES`  AS SELECT `rtn`.`name` AS `SPECIFIC_NAME`, (`cat`.`name` collate utf8mb3_tolower_ci) AS `ROUTINE_CATALOG`, (`sch`.`name` collate utf8mb3_tolower_ci) AS `ROUTINE_SCHEMA`, `rtn`.`name` AS `ROUTINE_NAME`, `rtn`.`type` AS `ROUTINE_TYPE`, if((`rtn`.`type` = 'PROCEDURE'),'',substring_index(substring_index(`rtn`.`result_data_type_utf8`,'(',1),' ',1)) AS `DATA_TYPE`, internal_dd_char_length(`rtn`.`result_data_type`,`rtn`.`result_char_length`,`coll_result`.`name`,0) AS `CHARACTER_MAXIMUM_LENGTH`, internal_dd_char_length(`rtn`.`result_data_type`,`rtn`.`result_char_length`,`coll_result`.`name`,1) AS `CHARACTER_OCTET_LENGTH`, `rtn`.`result_numeric_precision` AS `NUMERIC_PRECISION`, `rtn`.`result_numeric_scale` AS `NUMERIC_SCALE`, `rtn`.`result_datetime_precision` AS `DATETIME_PRECISION`, (case `rtn`.`result_data_type` when 'MYSQL_TYPE_STRING' then if((`cs_result`.`name` = 'binary'),NULL,`cs_result`.`name`) when 'MYSQL_TYPE_VAR_STRING' then if((`cs_result`.`name` = 'binary'),NULL,`cs_result`.`name`) when 'MYSQL_TYPE_VARCHAR' then if((`cs_result`.`name` = 'binary'),NULL,`cs_result`.`name`) when 'MYSQL_TYPE_TINY_BLOB' then if((`cs_result`.`name` = 'binary'),NULL,`cs_result`.`name`) when 'MYSQL_TYPE_MEDIUM_BLOB' then if((`cs_result`.`name` = 'binary'),NULL,`cs_result`.`name`) when 'MYSQL_TYPE_BLOB' then if((`cs_result`.`name` = 'binary'),NULL,`cs_result`.`name`) when 'MYSQL_TYPE_LONG_BLOB' then if((`cs_result`.`name` = 'binary'),NULL,`cs_result`.`name`) when 'MYSQL_TYPE_ENUM' then if((`cs_result`.`name` = 'binary'),NULL,`cs_result`.`name`) when 'MYSQL_TYPE_SET' then if((`cs_result`.`name` = 'binary'),NULL,`cs_result`.`name`) else NULL end) AS `CHARACTER_SET_NAME`, (case `rtn`.`result_data_type` when 'MYSQL_TYPE_STRING' then if((`cs_result`.`name` = 'binary'),NULL,`coll_result`.`name`) when 'MYSQL_TYPE_VAR_STRING' then if((`cs_result`.`name` = 'binary'),NULL,`coll_result`.`name`) when 'MYSQL_TYPE_VARCHAR' then if((`cs_result`.`name` = 'binary'),NULL,`coll_result`.`name`) when 'MYSQL_TYPE_TINY_BLOB' then if((`cs_result`.`name` = 'binary'),NULL,`coll_result`.`name`) when 'MYSQL_TYPE_MEDIUM_BLOB' then if((`cs_result`.`name` = 'binary'),NULL,`coll_result`.`name`) when 'MYSQL_TYPE_BLOB' then if((`cs_result`.`name` = 'binary'),NULL,`coll_result`.`name`) when 'MYSQL_TYPE_LONG_BLOB' then if((`cs_result`.`name` = 'binary'),NULL,`coll_result`.`name`) when 'MYSQL_TYPE_ENUM' then if((`cs_result`.`name` = 'binary'),NULL,`coll_result`.`name`) when 'MYSQL_TYPE_SET' then if((`cs_result`.`name` = 'binary'),NULL,`coll_result`.`name`) else NULL end) AS `COLLATION_NAME`, if((`rtn`.`type` = 'PROCEDURE'),NULL,`rtn`.`result_data_type_utf8`) AS `DTD_IDENTIFIER`, 'SQL' AS `ROUTINE_BODY`, if(can_access_routine(`sch`.`name`,`rtn`.`name`,`rtn`.`type`,`rtn`.`definer`,true),`rtn`.`definition_utf8`,NULL) AS `ROUTINE_DEFINITION`, NULL AS `EXTERNAL_NAME`, `rtn`.`external_language` AS `EXTERNAL_LANGUAGE`, 'SQL' AS `PARAMETER_STYLE`, if((`rtn`.`is_deterministic` = 0),'NO','YES') AS `IS_DETERMINISTIC`, `rtn`.`sql_data_access` AS `SQL_DATA_ACCESS`, NULL AS `SQL_PATH`, `rtn`.`security_type` AS `SECURITY_TYPE`, `rtn`.`created` AS `CREATED`, `rtn`.`last_altered` AS `LAST_ALTERED`, `rtn`.`sql_mode` AS `SQL_MODE`, `rtn`.`comment` AS `ROUTINE_COMMENT`, `rtn`.`definer` AS `DEFINER`, `cs_client`.`name` AS `CHARACTER_SET_CLIENT`, `coll_conn`.`name` AS `COLLATION_CONNECTION`, `coll_db`.`name` AS `DATABASE_COLLATION` FROM ((((((((`mysql`.`routines` `rtn` join `mysql`.`schemata` `sch` on((`rtn`.`schema_id` = `sch`.`id`))) join `mysql`.`catalogs` `cat` on((`cat`.`id` = `sch`.`catalog_id`))) join `mysql`.`collations` `coll_client` on((`coll_client`.`id` = `rtn`.`client_collation_id`))) join `mysql`.`character_sets` `cs_client` on((`cs_client`.`id` = `coll_client`.`character_set_id`))) join `mysql`.`collations` `coll_conn` on((`coll_conn`.`id` = `rtn`.`connection_collation_id`))) join `mysql`.`collations` `coll_db` on((`coll_db`.`id` = `rtn`.`schema_collation_id`))) left join `mysql`.`collations` `coll_result` on((`coll_result`.`id` = `rtn`.`result_collation_id`))) left join `mysql`.`character_sets` `cs_result` on((`cs_result`.`id` = `coll_result`.`character_set_id`))) WHERE (0 <> can_access_routine(`sch`.`name`,`rtn`.`name`,`rtn`.`type`,`rtn`.`definer`,false)) ;

-- --------------------------------------------------------

--
-- Structure for view `SCHEMATA`
--
DROP TABLE IF EXISTS `SCHEMATA`;

CREATE ALGORITHM=UNDEFINED DEFINER=`mysql.infoschema`@`localhost` SQL SECURITY DEFINER VIEW `SCHEMATA`  AS SELECT (`cat`.`name` collate utf8mb3_tolower_ci) AS `CATALOG_NAME`, (`sch`.`name` collate utf8mb3_tolower_ci) AS `SCHEMA_NAME`, `cs`.`name` AS `DEFAULT_CHARACTER_SET_NAME`, `col`.`name` AS `DEFAULT_COLLATION_NAME`, NULL AS `SQL_PATH`, `sch`.`default_encryption` AS `DEFAULT_ENCRYPTION` FROM (((`mysql`.`schemata` `sch` join `mysql`.`catalogs` `cat` on((`cat`.`id` = `sch`.`catalog_id`))) join `mysql`.`collations` `col` on((`sch`.`default_collation_id` = `col`.`id`))) join `mysql`.`character_sets` `cs` on((`col`.`character_set_id` = `cs`.`id`))) WHERE (0 <> can_access_database(`sch`.`name`)) ;

-- --------------------------------------------------------

--
-- Structure for view `SCHEMATA_EXTENSIONS`
--
DROP TABLE IF EXISTS `SCHEMATA_EXTENSIONS`;

CREATE ALGORITHM=UNDEFINED DEFINER=`mysql.infoschema`@`localhost` SQL SECURITY DEFINER VIEW `SCHEMATA_EXTENSIONS`  AS SELECT (`cat`.`name` collate utf8mb3_tolower_ci) AS `CATALOG_NAME`, (`sch`.`name` collate utf8mb3_tolower_ci) AS `SCHEMA_NAME`, get_dd_schema_options(`sch`.`options`) AS `OPTIONS` FROM (`mysql`.`schemata` `sch` join `mysql`.`catalogs` `cat` on((`cat`.`id` = `sch`.`catalog_id`))) WHERE (0 <> can_access_database(`sch`.`name`)) ;

-- --------------------------------------------------------

--
-- Structure for view `SCHEMA_PRIVILEGES`
--
DROP TABLE IF EXISTS `SCHEMA_PRIVILEGES`;

CREATE TEMPORARY TABLE `SCHEMA_PRIVILEGES` (
  `GRANTEE` varchar(292) NOT NULL DEFAULT '',
  `TABLE_CATALOG` varchar(512) NOT NULL DEFAULT '',
  `TABLE_SCHEMA` varchar(64) NOT NULL DEFAULT '',
  `PRIVILEGE_TYPE` varchar(64) NOT NULL DEFAULT '',
  `IS_GRANTABLE` varchar(3) NOT NULL DEFAULT ''
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3;

-- --------------------------------------------------------

--
-- Structure for view `STATISTICS`
--
DROP TABLE IF EXISTS `STATISTICS`;

CREATE ALGORITHM=UNDEFINED DEFINER=`mysql.infoschema`@`localhost` SQL SECURITY DEFINER VIEW `STATISTICS`  AS SELECT (`cat`.`name` collate utf8mb3_tolower_ci) AS `TABLE_CATALOG`, (`sch`.`name` collate utf8mb3_tolower_ci) AS `TABLE_SCHEMA`, (`tbl`.`name` collate utf8mb3_tolower_ci) AS `TABLE_NAME`, if(((`idx`.`type` = 'PRIMARY') or (`idx`.`type` = 'UNIQUE')),0,1) AS `NON_UNIQUE`, (`sch`.`name` collate utf8mb3_tolower_ci) AS `INDEX_SCHEMA`, (`idx`.`name` collate utf8mb3_tolower_ci) AS `INDEX_NAME`, `icu`.`ordinal_position` AS `SEQ_IN_INDEX`, if((`col`.`hidden` = 'SQL'),NULL,(`col`.`name` collate utf8mb3_tolower_ci)) AS `COLUMN_NAME`, (case when (`icu`.`order` = 'DESC') then 'D' when (`icu`.`order` = 'ASC') then 'A' else NULL end) AS `COLLATION`, internal_index_column_cardinality(`sch`.`name`,`tbl`.`name`,`idx`.`name`,`col`.`name`,`idx`.`ordinal_position`,`icu`.`ordinal_position`,if((`tbl`.`partition_type` is null),`tbl`.`engine`,''),`tbl`.`se_private_id`,((`tbl`.`hidden` <> 'Visible') or (0 <> `idx`.`hidden`) or (0 <> `icu`.`hidden`)),coalesce(`stat`.`cardinality`,cast(-(1) as unsigned)),coalesce(cast(`stat`.`cached_time` as unsigned),0)) AS `CARDINALITY`, get_dd_index_sub_part_length(`icu`.`length`,`col`.`type`,`col`.`char_length`,`col`.`collation_id`,`idx`.`type`) AS `SUB_PART`, NULL AS `PACKED`, if((`col`.`is_nullable` = 1),'YES','') AS `NULLABLE`, (case when (`idx`.`type` = 'SPATIAL') then 'SPATIAL' when (`idx`.`algorithm` = 'SE_PRIVATE') then '' else `idx`.`algorithm` end) AS `INDEX_TYPE`, if(((`idx`.`type` = 'PRIMARY') or (`idx`.`type` = 'UNIQUE')),'',if(internal_keys_disabled(`tbl`.`options`),'disabled','')) AS `COMMENT`, `idx`.`comment` AS `INDEX_COMMENT`, if(`idx`.`is_visible`,'YES','NO') AS `IS_VISIBLE`, if((`col`.`hidden` = 'SQL'),`col`.`generation_expression_utf8`,NULL) AS `EXPRESSION` FROM (((((((`mysql`.`index_column_usage` `icu` join `mysql`.`indexes` `idx` on((`idx`.`id` = `icu`.`index_id`))) join `mysql`.`tables` `tbl` on((`idx`.`table_id` = `tbl`.`id`))) join `mysql`.`columns` `col` on((`icu`.`column_id` = `col`.`id`))) join `mysql`.`schemata` `sch` on((`tbl`.`schema_id` = `sch`.`id`))) join `mysql`.`catalogs` `cat` on((`cat`.`id` = `sch`.`catalog_id`))) join `mysql`.`collations` `coll` on((`tbl`.`collation_id` = `coll`.`id`))) left join `mysql`.`index_stats` `stat` on(((`tbl`.`name` = `stat`.`table_name`) and (`sch`.`name` = `stat`.`schema_name`) and (`idx`.`name` = `stat`.`index_name`) and (`col`.`name` = `stat`.`column_name`)))) WHERE ((0 <> can_access_table(`sch`.`name`,`tbl`.`name`)) AND (0 <> is_visible_dd_object(`tbl`.`hidden`,((0 <> `idx`.`hidden`) OR (0 <> `icu`.`hidden`)),`idx`.`options`))) ;

-- --------------------------------------------------------

--
-- Structure for view `ST_GEOMETRY_COLUMNS`
--
DROP TABLE IF EXISTS `ST_GEOMETRY_COLUMNS`;

CREATE ALGORITHM=UNDEFINED DEFINER=`mysql.infoschema`@`localhost` SQL SECURITY DEFINER VIEW `ST_GEOMETRY_COLUMNS`  AS SELECT `cols`.`TABLE_CATALOG` AS `TABLE_CATALOG`, `cols`.`TABLE_SCHEMA` AS `TABLE_SCHEMA`, `cols`.`TABLE_NAME` AS `TABLE_NAME`, `cols`.`COLUMN_NAME` AS `COLUMN_NAME`, `srs`.`SRS_NAME` AS `SRS_NAME`, `cols`.`SRS_ID` AS `SRS_ID`, `cols`.`DATA_TYPE` AS `GEOMETRY_TYPE_NAME` FROM (`COLUMNS` `cols` left join `ST_SPATIAL_REFERENCE_SYSTEMS` `srs` on((`cols`.`SRS_ID` = `srs`.`SRS_ID`))) WHERE (`cols`.`DATA_TYPE` in ('geometry','point','linestring','polygon','multipoint','multilinestring','multipolygon','geomcollection')) ;

-- --------------------------------------------------------

--
-- Structure for view `ST_SPATIAL_REFERENCE_SYSTEMS`
--
DROP TABLE IF EXISTS `ST_SPATIAL_REFERENCE_SYSTEMS`;

CREATE ALGORITHM=UNDEFINED DEFINER=`mysql.infoschema`@`localhost` SQL SECURITY DEFINER VIEW `ST_SPATIAL_REFERENCE_SYSTEMS`  AS SELECT `mysql`.`st_spatial_reference_systems`.`name` AS `SRS_NAME`, `mysql`.`st_spatial_reference_systems`.`id` AS `SRS_ID`, `mysql`.`st_spatial_reference_systems`.`organization` AS `ORGANIZATION`, `mysql`.`st_spatial_reference_systems`.`organization_coordsys_id` AS `ORGANIZATION_COORDSYS_ID`, `mysql`.`st_spatial_reference_systems`.`definition` AS `DEFINITION`, `mysql`.`st_spatial_reference_systems`.`description` AS `DESCRIPTION` FROM `mysql`.`st_spatial_reference_systems` ;

-- --------------------------------------------------------

--
-- Structure for view `ST_UNITS_OF_MEASURE`
--
DROP TABLE IF EXISTS `ST_UNITS_OF_MEASURE`;

CREATE ALGORITHM=UNDEFINED DEFINER=`mysql.infoschema`@`localhost` SQL SECURITY DEFINER VIEW `ST_UNITS_OF_MEASURE`  AS SELECT `st_units_of_measure`.`UNIT_NAME` AS `UNIT_NAME`, `st_units_of_measure`.`UNIT_TYPE` AS `UNIT_TYPE`, `st_units_of_measure`.`CONVERSION_FACTOR` AS `CONVERSION_FACTOR`, `st_units_of_measure`.`DESCRIPTION` AS `DESCRIPTION` FROM json_table('[["British chain (Sears 1922 truncated)","LINEAR","",20.116756],["British foot (Sears 1922 truncated)","LINEAR","",0.30479933333333337],["chain","LINEAR","",20.1168],["yard","LINEAR","",0.9144],["British foot (1936)","LINEAR","",0.3048007491],["British link (Sears 1922 truncated)","LINEAR","",0.20116756],["Gold Coast foot","LINEAR","",0.3047997101815088],["Indian yard (1937)","LINEAR","",0.91439523],["link","LINEAR","",0.201168],["Indian yard","LINEAR","",0.9143985307444408],["Indian yard (1975)","LINEAR","",0.9143985],["Indian yard (1962)","LINEAR","",0.9143988],["Indian foot (1975)","LINEAR","",0.3047995],["Indian foot (1937)","LINEAR","",0.30479841],["Indian foot","LINEAR","",0.30479951024814694],["Indian foot (1962)","LINEAR","",0.3047996],["British foot (1865)","LINEAR","",0.30480083333333335],["British link (Benoit 1895 B)","LINEAR","",0.2011678249437587],["Statute mile","LINEAR","",1609.344],["British chain (Benoit 1895 B)","LINEAR","",20.116782494375872],["British foot (Benoit 1895 B)","LINEAR","",0.30479973476327077],["British link (Benoit 1895 A)","LINEAR","",0.201167824],["British yard (Sears 1922 truncated)","LINEAR","",0.914398],["British yard (Benoit 1895 B)","LINEAR","",0.9143992042898124],["foot","LINEAR","",0.3048],["British foot (Benoit 1895 A)","LINEAR","",0.3047997333333333],["British yard (Benoit 1895 A)","LINEAR","",0.9143992],["British chain (Sears 1922)","LINEAR","",20.116765121552632],["Clarke\'s link","LINEAR","",0.201166195164],["Clarke\'s chain","LINEAR","",20.1166195164],["British chain (Benoit 1895 A)","LINEAR","",20.1167824],["Clarke\'s yard","LINEAR","",0.9143917962],["US survey foot","LINEAR","",0.30480060960121924],["kilometre","LINEAR","",1000],["centimetre","LINEAR","",0.01],["British yard (Sears 1922)","LINEAR","",0.9143984146160287],["US survey mile","LINEAR","",1609.3472186944375],["metre","LINEAR","",1],["US survey link","LINEAR","",0.2011684023368047],["nautical mile","LINEAR","",1852],["British foot (Sears 1922)","LINEAR","",0.3047994715386762],["British link (Sears 1922)","LINEAR","",0.2011676512155263],["fathom","LINEAR","",1.8288],["US survey chain","LINEAR","",20.11684023368047],["German legal metre","LINEAR","",1.0000135965],["Clarke\'s foot","LINEAR","",0.3047972654],["millimetre","LINEAR","",0.001]]', '$[*]' columns (`UNIT_NAME` varchar(255) character set utf8mb4 path '$[0]', `UNIT_TYPE` varchar(7) character set utf8mb4 path '$[1]', `DESCRIPTION` varchar(255) character set utf8mb4 path '$[2]', `CONVERSION_FACTOR` double path '$[3]')) AS `ST_UNITS_OF_MEASURE` ;

-- --------------------------------------------------------

--
-- Structure for view `TABLES`
--
DROP TABLE IF EXISTS `TABLES`;

CREATE ALGORITHM=UNDEFINED DEFINER=`mysql.infoschema`@`localhost` SQL SECURITY DEFINER VIEW `TABLES`  AS SELECT (`cat`.`name` collate utf8mb3_tolower_ci) AS `TABLE_CATALOG`, (`sch`.`name` collate utf8mb3_tolower_ci) AS `TABLE_SCHEMA`, (`tbl`.`name` collate utf8mb3_tolower_ci) AS `TABLE_NAME`, `tbl`.`type` AS `TABLE_TYPE`, if((`tbl`.`type` = 'BASE TABLE'),`tbl`.`engine`,NULL) AS `ENGINE`, if((`tbl`.`type` = 'VIEW'),NULL,10) AS `VERSION`, `tbl`.`row_format` AS `ROW_FORMAT`, if((`tbl`.`type` = 'VIEW'),NULL,internal_table_rows(`sch`.`name`,`tbl`.`name`,if((`tbl`.`partition_type` is null),`tbl`.`engine`,''),`tbl`.`se_private_id`,(`tbl`.`hidden` <> 'Visible'),`ts`.`se_private_data`,coalesce(`stat`.`table_rows`,0),coalesce(cast(`stat`.`cached_time` as unsigned),0))) AS `TABLE_ROWS`, if((`tbl`.`type` = 'VIEW'),NULL,internal_avg_row_length(`sch`.`name`,`tbl`.`name`,if((`tbl`.`partition_type` is null),`tbl`.`engine`,''),`tbl`.`se_private_id`,(`tbl`.`hidden` <> 'Visible'),`ts`.`se_private_data`,coalesce(`stat`.`avg_row_length`,0),coalesce(cast(`stat`.`cached_time` as unsigned),0))) AS `AVG_ROW_LENGTH`, if((`tbl`.`type` = 'VIEW'),NULL,internal_data_length(`sch`.`name`,`tbl`.`name`,if((`tbl`.`partition_type` is null),`tbl`.`engine`,''),`tbl`.`se_private_id`,(`tbl`.`hidden` <> 'Visible'),`ts`.`se_private_data`,coalesce(`stat`.`data_length`,0),coalesce(cast(`stat`.`cached_time` as unsigned),0))) AS `DATA_LENGTH`, if((`tbl`.`type` = 'VIEW'),NULL,internal_max_data_length(`sch`.`name`,`tbl`.`name`,if((`tbl`.`partition_type` is null),`tbl`.`engine`,''),`tbl`.`se_private_id`,(`tbl`.`hidden` <> 'Visible'),`ts`.`se_private_data`,coalesce(`stat`.`max_data_length`,0),coalesce(cast(`stat`.`cached_time` as unsigned),0))) AS `MAX_DATA_LENGTH`, if((`tbl`.`type` = 'VIEW'),NULL,internal_index_length(`sch`.`name`,`tbl`.`name`,if((`tbl`.`partition_type` is null),`tbl`.`engine`,''),`tbl`.`se_private_id`,(`tbl`.`hidden` <> 'Visible'),`ts`.`se_private_data`,coalesce(`stat`.`index_length`,0),coalesce(cast(`stat`.`cached_time` as unsigned),0))) AS `INDEX_LENGTH`, if((`tbl`.`type` = 'VIEW'),NULL,internal_data_free(`sch`.`name`,`tbl`.`name`,if((`tbl`.`partition_type` is null),`tbl`.`engine`,''),`tbl`.`se_private_id`,(`tbl`.`hidden` <> 'Visible'),`ts`.`se_private_data`,coalesce(`stat`.`data_free`,0),coalesce(cast(`stat`.`cached_time` as unsigned),0))) AS `DATA_FREE`, if((`tbl`.`type` = 'VIEW'),NULL,internal_auto_increment(`sch`.`name`,`tbl`.`name`,if((`tbl`.`partition_type` is null),`tbl`.`engine`,''),`tbl`.`se_private_id`,((0 <> is_visible_dd_object(`tbl`.`hidden`,false,`tbl`.`options`)) is false),`ts`.`se_private_data`,coalesce(`stat`.`auto_increment`,0),coalesce(cast(`stat`.`cached_time` as unsigned),0),`tbl`.`se_private_data`)) AS `AUTO_INCREMENT`, `tbl`.`created` AS `CREATE_TIME`, if((`tbl`.`type` = 'VIEW'),NULL,internal_update_time(`sch`.`name`,`tbl`.`name`,if((`tbl`.`partition_type` is null),`tbl`.`engine`,''),`tbl`.`se_private_id`,(`tbl`.`hidden` <> 'Visible'),`ts`.`se_private_data`,coalesce(cast(`stat`.`update_time` as unsigned),0),coalesce(cast(`stat`.`cached_time` as unsigned),0))) AS `UPDATE_TIME`, if((`tbl`.`type` = 'VIEW'),NULL,internal_check_time(`sch`.`name`,`tbl`.`name`,if((`tbl`.`partition_type` is null),`tbl`.`engine`,''),`tbl`.`se_private_id`,(`tbl`.`hidden` <> 'Visible'),`ts`.`se_private_data`,coalesce(cast(`stat`.`check_time` as unsigned),0),coalesce(cast(`stat`.`cached_time` as unsigned),0))) AS `CHECK_TIME`, `col`.`name` AS `TABLE_COLLATION`, if((`tbl`.`type` = 'VIEW'),NULL,internal_checksum(`sch`.`name`,`tbl`.`name`,if((`tbl`.`partition_type` is null),`tbl`.`engine`,''),`tbl`.`se_private_id`,(`tbl`.`hidden` <> 'Visible'),`ts`.`se_private_data`,coalesce(`stat`.`checksum`,0),coalesce(cast(`stat`.`cached_time` as unsigned),0))) AS `CHECKSUM`, if((`tbl`.`type` = 'VIEW'),NULL,get_dd_create_options(`tbl`.`options`,if((ifnull(`tbl`.`partition_expression`,'NOT_PART_TBL') = 'NOT_PART_TBL'),0,1),if((`sch`.`default_encryption` = 'YES'),1,0))) AS `CREATE_OPTIONS`, internal_get_comment_or_error(`sch`.`name`,`tbl`.`name`,`tbl`.`type`,`tbl`.`options`,`tbl`.`comment`) AS `TABLE_COMMENT` FROM (((((`mysql`.`tables` `tbl` join `mysql`.`schemata` `sch` on((`tbl`.`schema_id` = `sch`.`id`))) join `mysql`.`catalogs` `cat` on((`cat`.`id` = `sch`.`catalog_id`))) left join `mysql`.`collations` `col` on((`tbl`.`collation_id` = `col`.`id`))) left join `mysql`.`tablespaces` `ts` on((`tbl`.`tablespace_id` = `ts`.`id`))) left join `mysql`.`table_stats` `stat` on(((`tbl`.`name` = `stat`.`table_name`) and (`sch`.`name` = `stat`.`schema_name`)))) WHERE ((0 <> can_access_table(`sch`.`name`,`tbl`.`name`)) AND (0 <> is_visible_dd_object(`tbl`.`hidden`))) ;

-- --------------------------------------------------------

--
-- Structure for view `TABLESPACES`
--
DROP TABLE IF EXISTS `TABLESPACES`;

CREATE TEMPORARY TABLE `TABLESPACES` (
  `TABLESPACE_NAME` varchar(64) NOT NULL DEFAULT '',
  `ENGINE` varchar(64) NOT NULL DEFAULT '',
  `TABLESPACE_TYPE` varchar(64) DEFAULT NULL,
  `LOGFILE_GROUP_NAME` varchar(64) DEFAULT NULL,
  `EXTENT_SIZE` bigint UNSIGNED DEFAULT NULL,
  `AUTOEXTEND_SIZE` bigint UNSIGNED DEFAULT NULL,
  `MAXIMUM_SIZE` bigint UNSIGNED DEFAULT NULL,
  `NODEGROUP_ID` bigint UNSIGNED DEFAULT NULL,
  `TABLESPACE_COMMENT` varchar(2048) DEFAULT NULL
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3;

-- --------------------------------------------------------

--
-- Structure for view `TABLESPACES_EXTENSIONS`
--
DROP TABLE IF EXISTS `TABLESPACES_EXTENSIONS`;

CREATE ALGORITHM=UNDEFINED DEFINER=`mysql.infoschema`@`localhost` SQL SECURITY DEFINER VIEW `TABLESPACES_EXTENSIONS`  AS SELECT `tsps`.`name` AS `TABLESPACE_NAME`, `tsps`.`engine_attribute` AS `ENGINE_ATTRIBUTE` FROM `mysql`.`tablespaces` AS `tsps` ;

-- --------------------------------------------------------

--
-- Structure for view `TABLES_EXTENSIONS`
--
DROP TABLE IF EXISTS `TABLES_EXTENSIONS`;

CREATE ALGORITHM=UNDEFINED DEFINER=`mysql.infoschema`@`localhost` SQL SECURITY DEFINER VIEW `TABLES_EXTENSIONS`  AS SELECT `cat`.`name` AS `TABLE_CATALOG`, `sch`.`name` AS `TABLE_SCHEMA`, `tbl`.`name` AS `TABLE_NAME`, `tbl`.`engine_attribute` AS `ENGINE_ATTRIBUTE`, `tbl`.`secondary_engine_attribute` AS `SECONDARY_ENGINE_ATTRIBUTE` FROM ((`mysql`.`tables` `tbl` join `mysql`.`schemata` `sch` on((`tbl`.`schema_id` = `sch`.`id`))) join `mysql`.`catalogs` `cat` on((`cat`.`id` = `sch`.`catalog_id`))) WHERE ((0 <> can_access_table(`sch`.`name`,`tbl`.`name`)) AND (0 <> is_visible_dd_object(`tbl`.`hidden`))) ;

-- --------------------------------------------------------

--
-- Structure for view `TABLE_CONSTRAINTS`
--
DROP TABLE IF EXISTS `TABLE_CONSTRAINTS`;

CREATE ALGORITHM=UNDEFINED DEFINER=`mysql.infoschema`@`localhost` SQL SECURITY DEFINER VIEW `TABLE_CONSTRAINTS`  AS SELECT (`cat`.`name` collate utf8mb3_tolower_ci) AS `CONSTRAINT_CATALOG`, (`sch`.`name` collate utf8mb3_tolower_ci) AS `CONSTRAINT_SCHEMA`, `constraints`.`CONSTRAINT_NAME` AS `CONSTRAINT_NAME`, (`sch`.`name` collate utf8mb3_tolower_ci) AS `TABLE_SCHEMA`, (`tbl`.`name` collate utf8mb3_tolower_ci) AS `TABLE_NAME`, `constraints`.`CONSTRAINT_TYPE` AS `CONSTRAINT_TYPE`, `constraints`.`ENFORCED` AS `ENFORCED` FROM (((`mysql`.`tables` `tbl` join `mysql`.`schemata` `sch` on((`tbl`.`schema_id` = `sch`.`id`))) join `mysql`.`catalogs` `cat` on((`cat`.`id` = `sch`.`catalog_id`))) join lateral (select `idx`.`name` AS `CONSTRAINT_NAME`,if((`idx`.`type` = 'PRIMARY'),'PRIMARY KEY',`idx`.`type`) AS `CONSTRAINT_TYPE`,'YES' AS `ENFORCED` from `mysql`.`indexes` `idx` where ((`idx`.`table_id` = `tbl`.`id`) and (`idx`.`type` in ('PRIMARY','UNIQUE')) and (0 <> is_visible_dd_object(`tbl`.`hidden`,`idx`.`hidden`,`idx`.`options`))) union all select (`fk`.`name` collate utf8mb3_tolower_ci) AS `CONSTRAINT_NAME`,'FOREIGN KEY' AS `CONSTRAINT_TYPE`,'YES' AS `ENFORCED` from `mysql`.`foreign_keys` `fk` where (`fk`.`table_id` = `tbl`.`id`) union all select `cc`.`name` AS `CONSTRAINT_NAME`,'CHECK' AS `CONSTRAINT_TYPE`,`cc`.`enforced` AS `ENFORCED` from `mysql`.`check_constraints` `cc` where (`cc`.`table_id` = `tbl`.`id`)) `constraints`) WHERE ((0 <> can_access_table(`sch`.`name`,`tbl`.`name`)) AND (0 <> is_visible_dd_object(`tbl`.`hidden`))) ;

-- --------------------------------------------------------

--
-- Structure for view `TABLE_CONSTRAINTS_EXTENSIONS`
--
DROP TABLE IF EXISTS `TABLE_CONSTRAINTS_EXTENSIONS`;

CREATE ALGORITHM=UNDEFINED DEFINER=`mysql.infoschema`@`localhost` SQL SECURITY DEFINER VIEW `TABLE_CONSTRAINTS_EXTENSIONS`  AS SELECT `cat`.`name` AS `CONSTRAINT_CATALOG`, `sch`.`name` AS `CONSTRAINT_SCHEMA`, `idx`.`name` AS `CONSTRAINT_NAME`, `tbl`.`name` AS `TABLE_NAME`, `idx`.`engine_attribute` AS `ENGINE_ATTRIBUTE`, `idx`.`secondary_engine_attribute` AS `SECONDARY_ENGINE_ATTRIBUTE` FROM (((`mysql`.`indexes` `idx` join `mysql`.`tables` `tbl` on((`idx`.`table_id` = `tbl`.`id`))) join `mysql`.`schemata` `sch` on((`tbl`.`schema_id` = `sch`.`id`))) join `mysql`.`catalogs` `cat` on((`cat`.`id` = `sch`.`catalog_id`))) WHERE ((0 <> can_access_table(`sch`.`name`,`tbl`.`name`)) AND (0 <> is_visible_dd_object(`tbl`.`hidden`,false,`idx`.`options`))) ;

-- --------------------------------------------------------

--
-- Structure for view `TABLE_PRIVILEGES`
--
DROP TABLE IF EXISTS `TABLE_PRIVILEGES`;

CREATE TEMPORARY TABLE `TABLE_PRIVILEGES` (
  `GRANTEE` varchar(292) NOT NULL DEFAULT '',
  `TABLE_CATALOG` varchar(512) NOT NULL DEFAULT '',
  `TABLE_SCHEMA` varchar(64) NOT NULL DEFAULT '',
  `TABLE_NAME` varchar(64) NOT NULL DEFAULT '',
  `PRIVILEGE_TYPE` varchar(64) NOT NULL DEFAULT '',
  `IS_GRANTABLE` varchar(3) NOT NULL DEFAULT ''
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3;

-- --------------------------------------------------------

--
-- Structure for view `TRIGGERS`
--
DROP TABLE IF EXISTS `TRIGGERS`;

CREATE ALGORITHM=UNDEFINED DEFINER=`mysql.infoschema`@`localhost` SQL SECURITY DEFINER VIEW `TRIGGERS`  AS SELECT (`cat`.`name` collate utf8mb3_tolower_ci) AS `TRIGGER_CATALOG`, (`sch`.`name` collate utf8mb3_tolower_ci) AS `TRIGGER_SCHEMA`, `trg`.`name` AS `TRIGGER_NAME`, `trg`.`event_type` AS `EVENT_MANIPULATION`, (`cat`.`name` collate utf8mb3_tolower_ci) AS `EVENT_OBJECT_CATALOG`, (`sch`.`name` collate utf8mb3_tolower_ci) AS `EVENT_OBJECT_SCHEMA`, (`tbl`.`name` collate utf8mb3_tolower_ci) AS `EVENT_OBJECT_TABLE`, `trg`.`action_order` AS `ACTION_ORDER`, NULL AS `ACTION_CONDITION`, `trg`.`action_statement_utf8` AS `ACTION_STATEMENT`, 'ROW' AS `ACTION_ORIENTATION`, `trg`.`action_timing` AS `ACTION_TIMING`, NULL AS `ACTION_REFERENCE_OLD_TABLE`, NULL AS `ACTION_REFERENCE_NEW_TABLE`, 'OLD' AS `ACTION_REFERENCE_OLD_ROW`, 'NEW' AS `ACTION_REFERENCE_NEW_ROW`, `trg`.`created` AS `CREATED`, `trg`.`sql_mode` AS `SQL_MODE`, `trg`.`definer` AS `DEFINER`, `cs_client`.`name` AS `CHARACTER_SET_CLIENT`, `coll_conn`.`name` AS `COLLATION_CONNECTION`, `coll_db`.`name` AS `DATABASE_COLLATION` FROM (((((((`mysql`.`triggers` `trg` join `mysql`.`tables` `tbl` on((`tbl`.`id` = `trg`.`table_id`))) join `mysql`.`schemata` `sch` on((`tbl`.`schema_id` = `sch`.`id`))) join `mysql`.`catalogs` `cat` on((`cat`.`id` = `sch`.`catalog_id`))) join `mysql`.`collations` `coll_client` on((`coll_client`.`id` = `trg`.`client_collation_id`))) join `mysql`.`character_sets` `cs_client` on((`cs_client`.`id` = `coll_client`.`character_set_id`))) join `mysql`.`collations` `coll_conn` on((`coll_conn`.`id` = `trg`.`connection_collation_id`))) join `mysql`.`collations` `coll_db` on((`coll_db`.`id` = `trg`.`schema_collation_id`))) WHERE ((`tbl`.`type` <> 'VIEW') AND (0 <> can_access_trigger(`sch`.`name`,`tbl`.`name`)) AND (0 <> is_visible_dd_object(`tbl`.`hidden`))) ;

-- --------------------------------------------------------

--
-- Structure for view `USER_ATTRIBUTES`
--
DROP TABLE IF EXISTS `USER_ATTRIBUTES`;

CREATE ALGORITHM=UNDEFINED DEFINER=`mysql.infoschema`@`localhost` SQL SECURITY DEFINER VIEW `USER_ATTRIBUTES`  AS SELECT `mysql`.`user`.`User` AS `USER`, `mysql`.`user`.`Host` AS `HOST`, json_unquote(json_extract(`mysql`.`user`.`User_attributes`,'$.metadata')) AS `ATTRIBUTE` FROM `mysql`.`user` WHERE (0 <> can_access_user(`mysql`.`user`.`User`,`mysql`.`user`.`Host`)) ;

-- --------------------------------------------------------

--
-- Structure for view `USER_PRIVILEGES`
--
DROP TABLE IF EXISTS `USER_PRIVILEGES`;

CREATE TEMPORARY TABLE `USER_PRIVILEGES` (
  `GRANTEE` varchar(292) NOT NULL DEFAULT '',
  `TABLE_CATALOG` varchar(512) NOT NULL DEFAULT '',
  `PRIVILEGE_TYPE` varchar(64) NOT NULL DEFAULT '',
  `IS_GRANTABLE` varchar(3) NOT NULL DEFAULT ''
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3;

-- --------------------------------------------------------

--
-- Structure for view `VIEWS`
--
DROP TABLE IF EXISTS `VIEWS`;

CREATE ALGORITHM=UNDEFINED DEFINER=`mysql.infoschema`@`localhost` SQL SECURITY DEFINER VIEW `VIEWS`  AS SELECT (`cat`.`name` collate utf8mb3_tolower_ci) AS `TABLE_CATALOG`, (`sch`.`name` collate utf8mb3_tolower_ci) AS `TABLE_SCHEMA`, (`vw`.`name` collate utf8mb3_tolower_ci) AS `TABLE_NAME`, if((can_access_view(`sch`.`name`,`vw`.`name`,`vw`.`view_definer`,`vw`.`options`) = true),`vw`.`view_definition_utf8`,'') AS `VIEW_DEFINITION`, `vw`.`view_check_option` AS `CHECK_OPTION`, `vw`.`view_is_updatable` AS `IS_UPDATABLE`, `vw`.`view_definer` AS `DEFINER`, if((`vw`.`view_security_type` = 'DEFAULT'),'DEFINER',`vw`.`view_security_type`) AS `SECURITY_TYPE`, `cs`.`name` AS `CHARACTER_SET_CLIENT`, `conn_coll`.`name` AS `COLLATION_CONNECTION` FROM (((((`mysql`.`tables` `vw` join `mysql`.`schemata` `sch` on((`vw`.`schema_id` = `sch`.`id`))) join `mysql`.`catalogs` `cat` on((`cat`.`id` = `sch`.`catalog_id`))) join `mysql`.`collations` `conn_coll` on((`conn_coll`.`id` = `vw`.`view_connection_collation_id`))) join `mysql`.`collations` `client_coll` on((`client_coll`.`id` = `vw`.`view_client_collation_id`))) join `mysql`.`character_sets` `cs` on((`cs`.`id` = `client_coll`.`character_set_id`))) WHERE ((0 <> can_access_table(`sch`.`name`,`vw`.`name`)) AND (`vw`.`type` = 'VIEW')) ;

-- --------------------------------------------------------

--
-- Structure for view `VIEW_ROUTINE_USAGE`
--
DROP TABLE IF EXISTS `VIEW_ROUTINE_USAGE`;

CREATE ALGORITHM=UNDEFINED DEFINER=`mysql.infoschema`@`localhost` SQL SECURITY DEFINER VIEW `VIEW_ROUTINE_USAGE`  AS SELECT (`cat`.`name` collate utf8mb3_tolower_ci) AS `TABLE_CATALOG`, (`sch`.`name` collate utf8mb3_tolower_ci) AS `TABLE_SCHEMA`, (`vw`.`name` collate utf8mb3_tolower_ci) AS `TABLE_NAME`, (`vru`.`routine_catalog` collate utf8mb3_tolower_ci) AS `SPECIFIC_CATALOG`, (`vru`.`routine_schema` collate utf8mb3_tolower_ci) AS `SPECIFIC_SCHEMA`, `vru`.`routine_name` AS `SPECIFIC_NAME` FROM ((((`mysql`.`tables` `vw` join `mysql`.`schemata` `sch` on((`vw`.`schema_id` = `sch`.`id`))) join `mysql`.`catalogs` `cat` on((`cat`.`id` = `sch`.`catalog_id`))) join `mysql`.`view_routine_usage` `vru` on((`vru`.`view_id` = `vw`.`id`))) join `mysql`.`routines` `rtn` on(((`vru`.`routine_catalog` = `cat`.`name`) and (`vru`.`routine_schema` = `sch`.`name`) and (`vru`.`routine_name` = `rtn`.`name`)))) WHERE ((`vw`.`type` = 'VIEW') AND (0 <> can_access_routine(`vru`.`routine_schema`,`vru`.`routine_name`,`rtn`.`type`,`rtn`.`definer`,false)) AND (0 <> can_access_view(`sch`.`name`,`vw`.`name`,`vw`.`view_definer`,`vw`.`options`))) ;

-- --------------------------------------------------------

--
-- Structure for view `VIEW_TABLE_USAGE`
--
DROP TABLE IF EXISTS `VIEW_TABLE_USAGE`;

CREATE ALGORITHM=UNDEFINED DEFINER=`mysql.infoschema`@`localhost` SQL SECURITY DEFINER VIEW `VIEW_TABLE_USAGE`  AS SELECT (`cat`.`name` collate utf8mb3_tolower_ci) AS `VIEW_CATALOG`, (`sch`.`name` collate utf8mb3_tolower_ci) AS `VIEW_SCHEMA`, (`vw`.`name` collate utf8mb3_tolower_ci) AS `VIEW_NAME`, (`vtu`.`table_catalog` collate utf8mb3_tolower_ci) AS `TABLE_CATALOG`, (`vtu`.`table_schema` collate utf8mb3_tolower_ci) AS `TABLE_SCHEMA`, (`vtu`.`table_name` collate utf8mb3_tolower_ci) AS `TABLE_NAME` FROM (((`mysql`.`tables` `vw` join `mysql`.`schemata` `sch` on((`vw`.`schema_id` = `sch`.`id`))) join `mysql`.`catalogs` `cat` on((`cat`.`id` = `sch`.`catalog_id`))) join `mysql`.`view_table_usage` `vtu` on((`vtu`.`view_id` = `vw`.`id`))) WHERE ((0 <> can_access_table(`vtu`.`table_schema`,`vtu`.`table_name`)) AND (`vw`.`type` = 'VIEW') AND (0 <> can_access_view(`sch`.`name`,`vw`.`name`,`vw`.`view_definer`,`vw`.`options`))) ;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
