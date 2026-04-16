-- ============================================================================
-- Audio Posts Support
-- Adds columns for audio content type with music/speech distinction
-- ============================================================================

-- Add audio URL for uploaded/generated audio files
ALTER TABLE posts ADD COLUMN audio_url TEXT;

-- Audio type: 'music' or 'speech'
-- Speech requires transcription, music does not
ALTER TABLE posts ADD COLUMN audio_type TEXT CHECK(audio_type IN ('music', 'speech'));

-- Transcription text for speech-type audio
ALTER TABLE posts ADD COLUMN audio_transcription TEXT;

-- Duration in seconds (optional, for display purposes)
ALTER TABLE posts ADD COLUMN audio_duration INTEGER;

-- Index for finding audio posts
CREATE INDEX idx_posts_audio ON posts(audio_type) WHERE audio_url IS NOT NULL;
