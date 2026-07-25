-- scripts/schema.sql
CREATE TABLE IF NOT EXISTS videos (
    video_id    TEXT PRIMARY KEY,
    creator_id  TEXT NOT NULL,
    category    TEXT NOT NULL,
    duration_s  FLOAT NOT NULL,
    created_at  BIGINT NOT NULL  -- unix ms
);

CREATE TABLE IF NOT EXISTS users (
    user_id             TEXT PRIMARY KEY,
    interest_vector_json TEXT NOT NULL,  -- JSON array of 256 floats
    watch_frac_bias     FLOAT NOT NULL DEFAULT 0.0,
    like_rate_bias      FLOAT NOT NULL DEFAULT 0.0
);

CREATE TABLE IF NOT EXISTS interactions (
    id          BIGSERIAL PRIMARY KEY,
    user_id     TEXT NOT NULL,
    video_id    TEXT NOT NULL,
    label       SMALLINT NOT NULL,  -- 0 or 1
    watch_frac  FLOAT NOT NULL,
    event_type  TEXT NOT NULL,
    created_at  BIGINT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_interactions_user ON interactions(user_id);
CREATE INDEX IF NOT EXISTS idx_interactions_created ON interactions(created_at DESC);

CREATE TABLE IF NOT EXISTS training_runs (
    id          BIGSERIAL PRIMARY KEY,
    version     INT NOT NULL,
    started_at  BIGINT NOT NULL,
    finished_at BIGINT,
    loss_json   TEXT,   -- JSON array of per-epoch loss floats
    auc         FLOAT
);
