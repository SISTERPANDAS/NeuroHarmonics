-- ============================================================================
-- NeuroHarmonics Database Schema for Supabase PostgreSQL
-- Updated: March 3, 2026
-- ============================================================================

-- Drop existing tables if migrating (comment out for fresh setup)
-- DROP TABLE IF EXISTS feedbacks CASCADE;
-- DROP TABLE IF EXISTS monthly_reports CASCADE;
-- DROP TABLE IF EXISTS eeg_sessions CASCADE;
-- DROP TABLE IF EXISTS community_message CASCADE;
-- DROP TABLE IF EXISTS emotion_logs CASCADE;
-- DROP TABLE IF EXISTS contact_messages CASCADE;
-- DROP TABLE IF EXISTS system_logs CASCADE;
-- DROP TABLE IF EXISTS recommendations CASCADE;
-- DROP TABLE IF EXISTS activities CASCADE;
-- DROP TABLE IF EXISTS admins CASCADE;
-- DROP TABLE IF EXISTS "user" CASCADE;

-- ============================================================================
-- USERS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS "user" (
    id                  SERIAL PRIMARY KEY,
    name                VARCHAR(100),
    username            VARCHAR(100) NOT NULL UNIQUE,
    email               VARCHAR(120) NOT NULL UNIQUE,
    phone               VARCHAR(15),
    password            VARCHAR(255) NOT NULL,
    dob                 DATE,
    age                 INT,
    gender              VARCHAR(20),
    avatar              TEXT,
    role                VARCHAR(20) DEFAULT 'user',
    status              VARCHAR(20) DEFAULT 'active',
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login          TIMESTAMP,
    CONSTRAINT email_valid CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$')
);

-- ============================================================================
-- ADMINS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS admins (
    admin_id            SERIAL PRIMARY KEY,
    name                VARCHAR(100) NOT NULL,
    email               VARCHAR(255) NOT NULL UNIQUE,
    username            VARCHAR(50) NOT NULL UNIQUE,
    phone               VARCHAR(15),
    password            VARCHAR(255) NOT NULL,
    role                VARCHAR(50) DEFAULT 'admin',
    status              VARCHAR(20) DEFAULT 'active',
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login          TIMESTAMP,
    CONSTRAINT email_valid_admin CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$')
);

-- ============================================================================
-- ACTIVITIES TABLE (Yoga, Music, Meditation, etc.)
-- ============================================================================
CREATE TABLE IF NOT EXISTS activities (
    activity_id         SERIAL PRIMARY KEY,
    title               VARCHAR(200) NOT NULL,
    type                VARCHAR(30) NOT NULL CHECK (type IN ('yoga', 'music', 'meditation', 'breathing', 'article', 'video')),
    description         TEXT,
    file_path           TEXT,
    playlist_url        TEXT,
    duration_minutes    INT,
    difficulty_level    VARCHAR(20) DEFAULT 'beginner',
    target_emotions     VARCHAR(255),
    tags                VARCHAR(255),
    is_active           BOOLEAN DEFAULT TRUE,
    created_by          INT REFERENCES admins(admin_id) ON DELETE SET NULL,
    updated_by          INT REFERENCES admins(admin_id) ON DELETE SET NULL,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- EEG SESSIONS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS eeg_sessions (
    session_id          SERIAL PRIMARY KEY,
    user_id             INT NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    session_type        VARCHAR(20) NOT NULL CHECK (session_type IN ('baseline', 'activity', 'monitoring')),
    start_time          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time            TIMESTAMP,
    duration_seconds    INT,
    emotion_label       VARCHAR(50),
    emotion_confidence  FLOAT CHECK (emotion_confidence >= 0 AND emotion_confidence <= 1),
    raw_eeg_data        TEXT,
    chosen_activity_id  INT REFERENCES activities(activity_id) ON DELETE SET NULL,
    notes               TEXT,
    is_complete         BOOLEAN DEFAULT FALSE
);

-- ============================================================================
-- MONTHLY REPORTS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS monthly_reports (
    report_id           SERIAL PRIMARY KEY,
    user_id             INT NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    month               INT NOT NULL CHECK (month >= 1 AND month <= 12),
    year                INT NOT NULL,
    dominant_emotion    VARCHAR(50),
    total_sessions      INT DEFAULT 0,
    negative_count      INT DEFAULT 0,
    positive_count      INT DEFAULT 0,
    neutral_count       INT DEFAULT 0,
    avg_emotion_score   FLOAT,
    flagged_for_therapist BOOLEAN DEFAULT FALSE,
    therapist_notes     TEXT,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP,
    UNIQUE(user_id, month, year),
    CONSTRAINT valid_year CHECK (year >= 2020 AND year <= 2100)
);

-- ============================================================================
-- FEEDBACKS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS feedbacks (
    feedback_id         SERIAL PRIMARY KEY,
    user_id             INT NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    session_id          INT REFERENCES eeg_sessions(session_id) ON DELETE CASCADE,
    activity_id         INT REFERENCES activities(activity_id) ON DELETE CASCADE,
    rating              SMALLINT NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment             TEXT,
    is_helpful          BOOLEAN,
    reviewed_by         INT REFERENCES admins(admin_id) ON DELETE SET NULL,
    admin_response      TEXT,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP
);

-- ============================================================================
-- CONTACT MESSAGES TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS contact_messages (
    id                  SERIAL PRIMARY KEY,
    user_id             INT REFERENCES "user"(id) ON DELETE SET NULL,
    name                VARCHAR(100) NOT NULL,
    email               VARCHAR(120) NOT NULL,
    subject             VARCHAR(200),
    message             TEXT NOT NULL,
    is_resolved         BOOLEAN DEFAULT FALSE,
    admin_reply         TEXT,
    replied_by          INT REFERENCES admins(admin_id) ON DELETE SET NULL,
    timestamp           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    replied_at          TIMESTAMP
);

-- ============================================================================
-- COMMUNITY MESSAGES TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS community_message (
    id                  SERIAL PRIMARY KEY,
    user_id             INT NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    username            VARCHAR(100) NOT NULL,
    content             TEXT NOT NULL,
    likes               INT DEFAULT 0,
    is_flagged          BOOLEAN DEFAULT FALSE,
    timestamp           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP
);

-- ============================================================================
-- EMOTION LOGS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS emotion_logs (
    id                  SERIAL PRIMARY KEY,
    user_id             INT NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    emotion             VARCHAR(50) NOT NULL,
    intensity           SMALLINT CHECK (intensity >= 1 AND intensity <= 10),
    trigger             TEXT,
    activity_type       VARCHAR(30),
    timestamp           TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- RECOMMENDATIONS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS recommendations (
    id                  SERIAL PRIMARY KEY,
    user_id             INT REFERENCES "user"(id) ON DELETE CASCADE,
    emotion             VARCHAR(50) NOT NULL,
    activity_id         INT REFERENCES activities(activity_id) ON DELETE SET NULL,
    content             TEXT,
    reason              TEXT,
    is_active           BOOLEAN DEFAULT TRUE,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- SYSTEM LOGS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS system_logs (
    id                  SERIAL PRIMARY KEY,
    message             TEXT NOT NULL,
    level               VARCHAR(20) CHECK (level IN ('INFO', 'WARNING', 'ERROR', 'DEBUG')),
    module              VARCHAR(100),
    user_id             INT REFERENCES "user"(id) ON DELETE SET NULL,
    metadata            TEXT,
    timestamp           TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_user_email ON "user"(email);
CREATE INDEX IF NOT EXISTS idx_user_username ON "user"(username);
CREATE INDEX IF NOT EXISTS idx_user_created_at ON "user"(created_at);

CREATE INDEX IF NOT EXISTS idx_admin_email ON admins(email);
CREATE INDEX IF NOT EXISTS idx_admin_username ON admins(username);

CREATE INDEX IF NOT EXISTS idx_eeg_user_id ON eeg_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_eeg_start_time ON eeg_sessions(start_time);
CREATE INDEX IF NOT EXISTS idx_eeg_emotion ON eeg_sessions(emotion_label);

CREATE INDEX IF NOT EXISTS idx_monthly_reports_user ON monthly_reports(user_id);
CREATE INDEX IF NOT EXISTS idx_monthly_reports_year_month ON monthly_reports(year, month);
CREATE INDEX IF NOT EXISTS idx_monthly_reports_flagged ON monthly_reports(flagged_for_therapist);

CREATE INDEX IF NOT EXISTS idx_feedbacks_user_id ON feedbacks(user_id);
CREATE INDEX IF NOT EXISTS idx_feedbacks_session_id ON feedbacks(session_id);
CREATE INDEX IF NOT EXISTS idx_feedbacks_activity_id ON feedbacks(activity_id);

CREATE INDEX IF NOT EXISTS idx_emotion_logs_user_id ON emotion_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_emotion_logs_timestamp ON emotion_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_emotion_logs_emotion ON emotion_logs(emotion);

CREATE INDEX IF NOT EXISTS idx_community_msg_user ON community_message(user_id);
CREATE INDEX IF NOT EXISTS idx_community_msg_timestamp ON community_message(timestamp);

CREATE INDEX IF NOT EXISTS idx_contact_msg_user ON contact_messages(user_id);
CREATE INDEX IF NOT EXISTS idx_contact_msg_resolved ON contact_messages(is_resolved);

CREATE INDEX IF NOT EXISTS idx_system_logs_timestamp ON system_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_system_logs_level ON system_logs(level);

-- ============================================================================
-- HELPFUL QUERIES
-- ============================================================================

-- Get user emotion trends for a month
-- SELECT emotion, COUNT(*) as count 
-- FROM emotion_logs 
-- WHERE user_id = 1 AND EXTRACT(MONTH FROM timestamp) = EXTRACT(MONTH FROM NOW())
-- GROUP BY emotion ORDER BY count DESC;

-- Get activities recommended for a specific emotion
-- SELECT * FROM activities 
-- WHERE target_emotions LIKE '%happy%' AND is_active = TRUE;

-- Get flagged users requiring therapist review
-- SELECT u.username, mr.month, mr.year, mr.negative_count
-- FROM monthly_reports mr
-- JOIN "user" u ON mr.user_id = u.id
-- WHERE mr.flagged_for_therapist = TRUE AND mr.therapist_notes IS NULL
-- ORDER BY mr.created_at DESC;

-- Get user session statistics
-- SELECT u.username, COUNT(es.session_id) as total_sessions, AVG(es.emotion_confidence) as avg_confidence
-- FROM "user" u
-- LEFT JOIN eeg_sessions es ON u.id = es.user_id
-- WHERE es.end_time IS NOT NULL
-- GROUP BY u.id, u.username;
