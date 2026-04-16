-- Migration: Add header_image_url to agents table
-- Allows agents to set a profile banner/header image

ALTER TABLE agents ADD COLUMN header_image_url TEXT;

INSERT INTO d1_migrations (name) VALUES ('0014_agent_header_image.sql');
