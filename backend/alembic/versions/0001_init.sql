CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "vector";

CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS goals (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  description TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  archived BOOLEAN NOT NULL DEFAULT false,
  due_date DATE
);

CREATE TABLE IF NOT EXISTS books (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  isbn13 TEXT UNIQUE NOT NULL,
  title TEXT NOT NULL,
  author TEXT,
  publisher TEXT,
  pubyear INTEGER,
  ndc TEXT,
  ndlc TEXT,
  embedding VECTOR(768)
);

CREATE TABLE IF NOT EXISTS goal_books (
  goal_id UUID NOT NULL REFERENCES goals(id) ON DELETE CASCADE,
  book_id UUID NOT NULL REFERENCES books(id),
  position INTEGER NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('unread','reading','done')),
  completed_at TIMESTAMPTZ,
  PRIMARY KEY (goal_id, book_id)
);

CREATE OR REPLACE VIEW goal_progress AS
SELECT
  g.id AS goal_id,
  COUNT(gb.book_id) AS total_books,
  COUNT(*) FILTER (WHERE gb.status='done') AS done_books,
  CASE WHEN COUNT(gb.book_id)=0 THEN 0.0
       ELSE ROUND(COUNT(*) FILTER (WHERE gb.status='done')::numeric
                  / COUNT(gb.book_id)::numeric, 4) END AS progress_ratio
FROM goals g
LEFT JOIN goal_books gb ON g.id = gb.goal_id
GROUP BY g.id;

CREATE OR REPLACE FUNCTION touch_goals_updated_at() RETURNS trigger AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_goals_touch
BEFORE UPDATE ON goals
FOR EACH ROW EXECUTE FUNCTION touch_goals_updated_at();
