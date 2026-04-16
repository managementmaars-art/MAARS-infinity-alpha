-- Supabase initialization SQL for hotlist catalog snapshots
-- Run in Supabase SQL Editor

CREATE TABLE IF NOT EXISTS hotlist_catalogs (
  id            bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  platform_name text        NOT NULL,                 -- e.g. 腾讯视频
  rank          integer     NOT NULL CHECK (rank > 0),
  catalog_name  text        NOT NULL,                 -- 片单名称
  catalog_type  text,                                 -- 片单类别，如 电视剧/综艺/动漫
  release_date  date,                                 -- 上线日期（精确到天）
  collected_date date       NOT NULL,                 -- 采集日期（精确到天）
  created_at    timestamptz NOT NULL DEFAULT now(),   -- 实际写入时间（精确到秒）

  -- Deduplicate one platform snapshot per day by ranking.
  CONSTRAINT uq_hotlist_platform_date_rank UNIQUE (platform_name, collected_date, rank)
);

CREATE INDEX IF NOT EXISTS idx_hotlist_platform_collected_date
  ON hotlist_catalogs (platform_name, collected_date DESC);

CREATE INDEX IF NOT EXISTS idx_hotlist_collected_date
  ON hotlist_catalogs (collected_date DESC);

CREATE INDEX IF NOT EXISTS idx_hotlist_release_date
  ON hotlist_catalogs (release_date DESC);
