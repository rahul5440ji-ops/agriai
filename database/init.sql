-- AgriAI database initialization
-- Creates tables and seed data for local SQLite development.
-- Production can use PostgreSQL with appropriate DATABASE_URL.

-- Reference crops used by the application
INSERT INTO crops (name, season, unit) VALUES
    ('wheat', 'rabi', 'quintal'),
    ('rice', 'kharif', 'quintal'),
    ('maize', 'kharif', 'quintal'),
    ('sugarcane', 'kharif', 'tonne'),
    ('cotton', 'kharif', 'quintal'),
    ('pulses', 'rabi', 'quintal'),
    ('groundnut', 'kharif', 'quintal'),
    ('mustard', 'rabi', 'quintal'),
    ('potato', 'rabi', 'quintal'),
    ('tomato', 'kharif', 'quintal')
ON CONFLICT (name) DO NOTHING;