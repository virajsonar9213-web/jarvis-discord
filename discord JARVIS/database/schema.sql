-- JARVIS Database Schema
-- SQLite database for the Discord AI assistant

-- Enable foreign keys
PRAGMA foreign_keys = ON;

-- Users table: stores authorized Discord users
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    discord_id INTEGER NOT NULL UNIQUE,
    username TEXT NOT NULL,
    is_owner BOOLEAN NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Bot settings: configurable bot-wide settings
CREATE TABLE IF NOT EXISTS bot_settings (
    key TEXT PRIMARY KEY NOT NULL,
    value TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Servers: configured Discord servers
CREATE TABLE IF NOT EXISTS servers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guild_id INTEGER NOT NULL UNIQUE,
    enabled BOOLEAN NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Channels: channel-specific configuration
CREATE TABLE IF NOT EXISTS channels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    channel_id INTEGER NOT NULL UNIQUE,
    guild_id INTEGER NOT NULL,
    can_read BOOLEAN NOT NULL DEFAULT 1,
    can_respond BOOLEAN NOT NULL DEFAULT 0,
    should_ignore BOOLEAN NOT NULL DEFAULT 0,
    is_private_assistant BOOLEAN NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (guild_id) REFERENCES servers(guild_id)
);

-- Channel monitored users: which users' messages to monitor in each channel
CREATE TABLE IF NOT EXISTS channel_monitored_users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    channel_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    UNIQUE(channel_id, user_id),
    FOREIGN KEY (channel_id) REFERENCES channels(channel_id) ON DELETE CASCADE
);

-- Channel ignored users: users to ignore in each channel
CREATE TABLE IF NOT EXISTS channel_ignored_users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    channel_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    UNIQUE(channel_id, user_id),
    FOREIGN KEY (channel_id) REFERENCES channels(channel_id) ON DELETE CASCADE
);

-- Memories: JARVIS's conversation memory
CREATE TABLE IF NOT EXISTS memories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,  -- NULL for shared memories
    category TEXT NOT NULL DEFAULT 'general',
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES users(discord_id)
);

-- Conversations: tracked conversation sessions
CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    channel_id INTEGER,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_message_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES users(discord_id)
);

-- Messages: stored messages for context and summarization
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    discord_message_id TEXT NOT NULL,
    channel_id INTEGER NOT NULL,
    author_id INTEGER NOT NULL,
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_processed BOOLEAN NOT NULL DEFAULT 0,
    FOREIGN KEY (channel_id) REFERENCES channels(channel_id)
);

-- Notification settings: per-user notification preferences
CREATE TABLE IF NOT EXISTS notification_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE,
    enabled BOOLEAN NOT NULL DEFAULT 1,
    quiet_hours_start TEXT,
    quiet_hours_end TEXT,
    keyword_filters TEXT,  -- JSON array of keywords
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(discord_id)
);

-- Reminders/tasks: user reminders and task list
CREATE TABLE IF NOT EXISTS reminders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    scheduled_for TIMESTAMP NOT NULL,
    is_completed BOOLEAN NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(discord_id)
);

-- Pending approvals: actions awaiting user approval
CREATE TABLE IF NOT EXISTS pending_approvals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    action_type TEXT NOT NULL,
    action_data TEXT NOT NULL,  -- JSON with action details
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    is_resolved BOOLEAN NOT NULL DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(discord_id)
);

-- Audit log: record of JARVIS actions
CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action TEXT NOT NULL,
    details TEXT,
    channel_id INTEGER,
    guild_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Schema version tracking for migrations
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY NOT NULL,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert initial schema version
INSERT OR IGNORE INTO schema_version (version) VALUES (1);
