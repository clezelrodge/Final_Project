-- FileTrack MySQL database schema
-- Database: filetrackdb

CREATE DATABASE IF NOT EXISTS filetrackdb;
USE filetrackdb;

CREATE TABLE IF NOT EXISTS Users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    role ENUM('admin', 'user') NOT NULL DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS LocationRows (
    row_id INT AUTO_INCREMENT PRIMARY KEY,
    row_label VARCHAR(10) NOT NULL UNIQUE,
    description VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS Columns (
    column_id INT AUTO_INCREMENT PRIMARY KEY,
    column_label VARCHAR(10) NOT NULL UNIQUE,
    description VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS Documents (
    doc_id INT AUTO_INCREMENT PRIMARY KEY,
    document_code VARCHAR(30) UNIQUE,
    title VARCHAR(200) NOT NULL,
    student_name VARCHAR(120),
    student_id VARCHAR(50),
    document_type VARCHAR(100),
    rfid_tag VARCHAR(50) NOT NULL UNIQUE,
    row_id INT NULL,
    column_id INT NULL,
    assigned_user_id INT NULL,
    status ENUM('Available', 'Borrowed', 'Pending', 'Returned', 'Missing') DEFAULT 'Available',
    remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_documents_row FOREIGN KEY (row_id) REFERENCES LocationRows(row_id) ON DELETE SET NULL,
    CONSTRAINT fk_documents_column FOREIGN KEY (column_id) REFERENCES Columns(column_id) ON DELETE SET NULL,
    CONSTRAINT fk_documents_user FOREIGN KEY (assigned_user_id) REFERENCES Users(user_id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS AccessLogs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    doc_id INT NOT NULL,
    requested_by_user_id INT NOT NULL,
    processed_by_admin_id INT NOT NULL,
    action ENUM('Check Out', 'Return', 'Search') NOT NULL,
    action_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_access_doc FOREIGN KEY (doc_id) REFERENCES Documents(doc_id) ON DELETE CASCADE,
    CONSTRAINT fk_access_requester FOREIGN KEY (requested_by_user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    CONSTRAINT fk_access_admin FOREIGN KEY (processed_by_admin_id) REFERENCES Users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS HardwareScanLogs (
    scan_id INT AUTO_INCREMENT PRIMARY KEY,
    doc_id INT NULL,
    rfid_tag VARCHAR(50) NOT NULL,
    action_type VARCHAR(30) NOT NULL,
    result_message VARCHAR(255) NOT NULL,
    led_status VARCHAR(20),
    lcd_display TEXT,
    source VARCHAR(50) DEFAULT 'ESP32',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_hardware_doc FOREIGN KEY (doc_id) REFERENCES Documents(doc_id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS PasswordResetCodes (
    reset_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    code_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    used_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_reset_user FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO Users (username, password, full_name, email, role)
VALUES
('admin', '12345', 'System Administrator', 'admin@filetrack.local', 'admin'),
('user', '123', 'FileTrack User', 'user@filetrack.local', 'user')
ON DUPLICATE KEY UPDATE username = VALUES(username);

INSERT INTO LocationRows (row_label, description)
VALUES
('A', 'First Row - Top Shelf'),
('B', 'Second Row - Middle Shelf'),
('C', 'Third Row - Bottom Shelf')
ON DUPLICATE KEY UPDATE description = VALUES(description);

INSERT INTO Columns (column_label, description)
VALUES
('1', 'Student Profile Records'),
('2', 'Counseling and Referral Records'),
('3', 'Good Moral / Incident / Monitoring Records')
ON DUPLICATE KEY UPDATE description = VALUES(description);

-- Sample documents using actual RFID UIDs used in the prototype
INSERT INTO Documents (
    document_code, title, student_name, student_id, document_type,
    rfid_tag, row_id, column_id, assigned_user_id, status, remarks
)
SELECT 'DOC-2026-001', 'Folder001', 'Juan Dela Cruz', '2026-001',
       'Student Profile Record', 'A3 C3 29 14', r.row_id, c.column_id, u.user_id, 'Available',
       'Sample RFID document'
FROM LocationRows r
JOIN Columns c ON c.column_label = '1'
LEFT JOIN Users u ON u.username = 'user'
WHERE r.row_label = 'A'
ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    student_name = VALUES(student_name),
    student_id = VALUES(student_id),
    document_type = VALUES(document_type),
    rfid_tag = VALUES(rfid_tag),
    row_id = VALUES(row_id),
    column_id = VALUES(column_id),
    assigned_user_id = VALUES(assigned_user_id),
    status = VALUES(status),
    remarks = VALUES(remarks);

INSERT INTO Documents (
    document_code, title, student_name, student_id, document_type,
    rfid_tag, row_id, column_id, assigned_user_id, status, remarks
)
SELECT 'DOC-2026-002', 'Folder002', 'Maria Santos', '2026-002',
       'Counseling and Referral Record', '73 06 FA 34', r.row_id, c.column_id, u.user_id, 'Available',
       'Sample RFID document'
FROM LocationRows r
JOIN Columns c ON c.column_label = '2'
LEFT JOIN Users u ON u.username = 'user'
WHERE r.row_label = 'A'
ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    student_name = VALUES(student_name),
    student_id = VALUES(student_id),
    document_type = VALUES(document_type),
    rfid_tag = VALUES(rfid_tag),
    row_id = VALUES(row_id),
    column_id = VALUES(column_id),
    assigned_user_id = VALUES(assigned_user_id),
    status = VALUES(status),
    remarks = VALUES(remarks);

INSERT INTO Documents (
    document_code, title, student_name, student_id, document_type,
    rfid_tag, row_id, column_id, assigned_user_id, status, remarks
)
SELECT 'DOC-2026-003', 'Folder003', 'Ana Lopez', '2026-003',
       'Good Moral / Incident / Monitoring Record', '33 F6 FC 28', r.row_id, c.column_id, u.user_id, 'Available',
       'Sample RFID document'
FROM LocationRows r
JOIN Columns c ON c.column_label = '3'
LEFT JOIN Users u ON u.username = 'user'
WHERE r.row_label = 'A'
ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    student_name = VALUES(student_name),
    student_id = VALUES(student_id),
    document_type = VALUES(document_type),
    rfid_tag = VALUES(rfid_tag),
    row_id = VALUES(row_id),
    column_id = VALUES(column_id),
    assigned_user_id = VALUES(assigned_user_id),
    status = VALUES(status),
    remarks = VALUES(remarks);
