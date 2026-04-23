
-- =========================
-- HEALTH PROFILE
-- =========================

CREATE TABLE HealthProfile (
    health_profile_id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    user_id UNIQUEIDENTIFIER NOT NULL,

    age INT,
    height FLOAT,
    weight FLOAT,
    bmi FLOAT,

    blood_type NVARCHAR(10),
    chronic_conditions NVARCHAR(255),

    lifestyle NVARCHAR(100),
    stress_level INT,
    sleep_hours FLOAT,

    last_updated DATETIME DEFAULT GETDATE(),

    CONSTRAINT FK_HealthProfile_Users
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

-- =========================
-- MEDICAL REPORTS
-- =========================

CREATE TABLE MedicalReports (
    report_id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    user_id UNIQUEIDENTIFIER NOT NULL,

    report_type NVARCHAR(100),
    file_url NVARCHAR(500),

    doctor_name NVARCHAR(150),
    hospital NVARCHAR(150),

    uploaded_at DATETIME DEFAULT GETDATE(),

    CONSTRAINT FK_MedicalReports_Users
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

-- =========================
-- HEALTH METRICS
-- =========================

CREATE TABLE HealthMetrics (
    metric_id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    user_id UNIQUEIDENTIFIER NOT NULL,

    metric_type NVARCHAR(100),
    value FLOAT,
    unit NVARCHAR(20),

    source NVARCHAR(50),

    recorded_at DATETIME DEFAULT GETDATE(),

    CONSTRAINT FK_HealthMetrics_Users
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

-- =========================
-- HEALTH ALERTS
-- =========================

CREATE TABLE HealthAlerts (
    alert_id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    user_id UNIQUEIDENTIFIER NOT NULL,

    alert_type NVARCHAR(50),
    title NVARCHAR(255),
    message NVARCHAR(MAX),

    severity INT,
    is_resolved BIT DEFAULT 0,

    generated_by_agent NVARCHAR(100),

    created_at DATETIME DEFAULT GETDATE(),

    CONSTRAINT FK_HealthAlerts_Users
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

-- =========================
-- HEALTH GOALS
-- =========================

CREATE TABLE HealthGoals (
    goal_id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    user_id UNIQUEIDENTIFIER NOT NULL,

    goal_type NVARCHAR(100),
    target_value FLOAT,
    current_value FLOAT,

    deadline DATETIME,
    status NVARCHAR(50),

    created_at DATETIME DEFAULT GETDATE(),

    CONSTRAINT FK_HealthGoals_Users
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

-- =========================
-- HEALTH INSIGHTS
-- =========================

CREATE TABLE HealthInsights (
    insight_id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    user_id UNIQUEIDENTIFIER NOT NULL,

    insight_type NVARCHAR(100),
    message NVARCHAR(MAX),

    confidence FLOAT,

    generated_at DATETIME DEFAULT GETDATE(),

    CONSTRAINT FK_HealthInsights_Users
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);