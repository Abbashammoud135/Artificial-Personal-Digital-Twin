
-- =========================
-- USERS
-- =========================

CREATE TABLE Users (
    user_id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    full_name NVARCHAR(150) NOT NULL,
    email NVARCHAR(255) UNIQUE NOT NULL,
    created_at DATETIME DEFAULT GETDATE()
);
