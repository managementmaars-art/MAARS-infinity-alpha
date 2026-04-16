-- Supabase initialization SQL for capture_results table
-- Run this in the Supabase SQL Editor (Dashboard > SQL Editor > New query)

-- Create the capture_results table
CREATE TABLE IF NOT EXISTS capture_results (
  id            bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  datetime      bigint,                          -- unix milliseconds
  device_serial text,
  app           text,
  scene         text,
  params        text,
  item_id       text,
  item_caption  text,
  item_cdn_url  text,
  item_url      text,
  item_duration numeric,
  user_name     text,
  user_id       text,
  user_alias    text,
  user_auth_entity text,
  tags          text,
  task_id       bigint,
  book_id       text,
  extra         text,
  like_count    integer,
  view_count    integer,
  anchor_point  text,
  comment_count integer,
  collect_count integer,
  forward_count integer,
  share_count   integer,
  pay_mode      text,
  collection    text,
  episode       text,
  publish_time  text,
  created_at    timestamptz NOT NULL DEFAULT now(),

  -- Prevent duplicate uploads for the same task + item
  CONSTRAINT uq_task_item UNIQUE (task_id, item_id)
);

-- Backward-compatible migration for existing tables
ALTER TABLE capture_results
  ADD COLUMN IF NOT EXISTS book_id text;

-- Indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_capture_results_task_id ON capture_results (task_id);
CREATE INDEX IF NOT EXISTS idx_capture_results_book_id ON capture_results (book_id);
CREATE INDEX IF NOT EXISTS idx_capture_results_user_id ON capture_results (user_id);
CREATE INDEX IF NOT EXISTS idx_capture_results_app     ON capture_results (app);
CREATE INDEX IF NOT EXISTS idx_capture_results_item_id ON capture_results (item_id);
CREATE INDEX IF NOT EXISTS idx_capture_results_scene   ON capture_results (scene);

-- Note:
-- - New tables typically have RLS disabled by default.
-- - If you want to expose this table to anon/authenticated clients, enable RLS
--   and add policies explicitly.
