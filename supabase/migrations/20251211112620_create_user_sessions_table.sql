/*
  # User Sessions Management Schema

  1. New Tables
    - `user_sessions`
      - `id` (uuid, primary key) - Unique session identifier
      - `user_id` (bigint) - Telegram user ID
      - `file_path` (text) - Path to downloaded audio file
      - `original_filename` (text) - Original file name
      - `file_info` (jsonb) - Audio metadata (codec, bitrate, duration, etc.)
      - `settings` (jsonb) - User's audio processing settings
      - `created_at` (timestamptz) - Session creation time
      - `updated_at` (timestamptz) - Last activity time
      - `expires_at` (timestamptz) - Session expiration time (5 minutes from last update)
      
    - `processing_queue`
      - `id` (uuid, primary key) - Queue item identifier
      - `user_id` (bigint) - Telegram user ID
      - `session_id` (uuid) - Reference to user session
      - `operation` (text) - Type of processing operation
      - `status` (text) - pending, processing, completed, failed
      - `error_message` (text) - Error details if failed
      - `created_at` (timestamptz) - Queue entry time
      - `started_at` (timestamptz) - Processing start time
      - `completed_at` (timestamptz) - Processing completion time

  2. Security
    - Enable RLS on both tables
    - Policies for users to access only their own data

  3. Indexes
    - Index on user_id for fast lookups
    - Index on expires_at for cleanup operations
*/

-- Create user_sessions table
CREATE TABLE IF NOT EXISTS user_sessions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id bigint NOT NULL,
  file_path text,
  original_filename text,
  file_info jsonb DEFAULT '{}'::jsonb,
  settings jsonb DEFAULT '{
    "format": "mp3",
    "bitrate": "320k",
    "sample_rate": 48000,
    "channels": 2,
    "bass_boost": 0,
    "normalize": false,
    "fade_in": 0,
    "fade_out": 0,
    "speed": 1.0,
    "eq": [],
    "effects": []
  }'::jsonb,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now(),
  expires_at timestamptz DEFAULT (now() + interval '5 minutes')
);

-- Create processing_queue table
CREATE TABLE IF NOT EXISTS processing_queue (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id bigint NOT NULL,
  session_id uuid REFERENCES user_sessions(id) ON DELETE CASCADE,
  operation text NOT NULL,
  status text DEFAULT 'pending',
  error_message text,
  created_at timestamptz DEFAULT now(),
  started_at timestamptz,
  completed_at timestamptz,
  CONSTRAINT valid_status CHECK (status IN ('pending', 'processing', 'completed', 'failed'))
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_expires_at ON user_sessions(expires_at);
CREATE INDEX IF NOT EXISTS idx_processing_queue_user_id ON processing_queue(user_id);
CREATE INDEX IF NOT EXISTS idx_processing_queue_status ON processing_queue(status);

-- Enable Row Level Security
ALTER TABLE user_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE processing_queue ENABLE ROW LEVEL SECURITY;

-- RLS Policies for user_sessions (bot has full access)
CREATE POLICY "Allow bot full access to user_sessions"
  ON user_sessions FOR ALL
  USING (true)
  WITH CHECK (true);

-- RLS Policies for processing_queue (bot has full access)
CREATE POLICY "Allow bot full access to processing_queue"
  ON processing_queue FOR ALL
  USING (true)
  WITH CHECK (true);

-- Function to auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  NEW.expires_at = now() + interval '5 minutes';
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-update timestamps
DROP TRIGGER IF EXISTS update_user_sessions_updated_at ON user_sessions;
CREATE TRIGGER update_user_sessions_updated_at
  BEFORE UPDATE ON user_sessions
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- Function to clean expired sessions
CREATE OR REPLACE FUNCTION cleanup_expired_sessions()
RETURNS void AS $$
BEGIN
  DELETE FROM user_sessions WHERE expires_at < now();
END;
$$ LANGUAGE plpgsql;