-- Database schema for the application
-- Generated from SQLModel classes

-- Create user table
CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create session table
CREATE TABLE IF NOT EXISTS session (
    id TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
);

-- Create thread table
CREATE TABLE IF NOT EXISTS thread (
    id TEXT PRIMARY KEY,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for frequently queried columns
CREATE INDEX IF NOT EXISTS idx_user_email ON user(email);
CREATE INDEX IF NOT EXISTS idx_session_user_id ON session(user_id);

create extension if not exists vector;

-- Create file_objects tablea
CREATE TABLE IF NOT EXISTS file_objects (
    id TEXT PRIMARY KEY,
    file_name TEXT NOT NULL DEFAULT '',
    description TEXT NOT NULL DEFAULT '',
    created_by TEXT NOT NULL,
    embedding VECTOR NOT NULL,
    session_id TEXT NOT NULL,
    file_type TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

create table file_chunks
(
    id          varchar not null
        primary key,
    file_id     varchar not null,
    embedding   vector(1536),
    content     varchar not null,
    chunk_index integer not null
);


CREATE OR REPLACE VIEW public.v_file_chunks AS
SELECT fc.id,
       fc.file_id,
       fc.chunk_index,
       fc.content,
       fc.embedding,
       fo.file_name,
       fo.file_type,
       fo.session_id,
       fo.created_by,
       fo.created_at,
       description,
       fo.s3_url,
       fo.s3_key
FROM file_chunks fc
         JOIN file_objects fo ON fo.id::text = fc.file_id::text
