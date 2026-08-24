-- Migration 019: Staff Live Chat & Operator CRM Ticketing
-- Supports bi-directional live chat, ticket claiming, and customer escalation management

BEGIN;

CREATE TABLE IF NOT EXISTS live_chat_tickets (
    ticket_id VARCHAR(64) PRIMARY KEY,
    session_id VARCHAR(64) NOT NULL,
    customer_name VARCHAR(128) DEFAULT 'Anonymous Shopper',
    status VARCHAR(32) NOT NULL DEFAULT 'open', -- 'open', 'claimed', 'resolved'
    operator_id VARCHAR(64) DEFAULT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS live_chat_messages (
    message_id VARCHAR(64) PRIMARY KEY,
    ticket_id VARCHAR(64) NOT NULL REFERENCES live_chat_tickets(ticket_id) ON DELETE CASCADE,
    sender_type VARCHAR(32) NOT NULL, -- 'customer', 'operator', 'system'
    sender_id VARCHAR(64) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_live_chat_tickets_status ON live_chat_tickets(status);
CREATE INDEX IF NOT EXISTS idx_live_chat_messages_ticket ON live_chat_messages(ticket_id);

INSERT INTO orchestration.schema_migration(version) VALUES (19);
COMMIT;
