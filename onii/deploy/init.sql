CREATE SCHEMA IF NOT EXISTS "app";

--异步任务队列表
CREATE TABLE  IF NOT EXISTS "app"."django_q_ormq" (
  "id" serial PRIMARY KEY,
  "key" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "payload" text COLLATE "pg_catalog"."default" NOT NULL,
  "lock" timestamptz(6)
);

-- 异步任务表
CREATE TABLE  IF NOT EXISTS "app"."django_q_task" (
  "id" varchar(32) PRIMARY KEY,
  "name" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "func" varchar(256) COLLATE "pg_catalog"."default" NOT NULL,
  "hook" varchar(256) COLLATE "pg_catalog"."default",
  "args" text COLLATE "pg_catalog"."default",
  "kwargs" text COLLATE "pg_catalog"."default",
  "result" text COLLATE "pg_catalog"."default",
  "started" timestamptz(6) NOT NULL,
  "stopped" timestamptz(6) NOT NULL,
  "success" bool NOT NULL,
  "group" varchar(100) COLLATE "pg_catalog"."default",
  "attempt_count" int4 NOT NULL
);

-- 异步任务进度表
CREATE TABLE  IF NOT EXISTS "app"."django_q_process" (
  "id" serial PRIMARY KEY,
  "task_name" varchar(100) COLLATE "pg_catalog"."default",
  "process" numeric(5,4),
  "task_id" varchar(32) COLLATE "pg_catalog"."default",
  "func" varchar(256) COLLATE "pg_catalog"."default",
  "hook" varchar(256) COLLATE "pg_catalog"."default",
  "args" text COLLATE "pg_catalog"."default",
  "kwargs" text COLLATE "pg_catalog"."default",
  "group" varchar(100) COLLATE "pg_catalog"."default",
  "started" timestamp(6)
);

-- 异步任务调度表
CREATE TABLE IF NOT EXISTS "app"."django_q_schedule" (
  "id" serial PRIMARY KEY,
  "func" varchar(256) COLLATE "pg_catalog"."default" NOT NULL,
  "hook" varchar(256) COLLATE "pg_catalog"."default",
  "args" text COLLATE "pg_catalog"."default",
  "kwargs" text COLLATE "pg_catalog"."default",
  "schedule_type" varchar(1) COLLATE "pg_catalog"."default" NOT NULL,
  "repeats" int4 NOT NULL,
  "next_run" timestamptz(6),
  "task" varchar(100) COLLATE "pg_catalog"."default",
  "name" varchar(100) COLLATE "pg_catalog"."default",
  "minutes" int2,
  "cron" varchar(100) COLLATE "pg_catalog"."default",
  "cluster" varchar(100) COLLATE "pg_catalog"."default",
  CONSTRAINT "django_q_schedule_minutes_check" CHECK ((minutes >= 0))
);
