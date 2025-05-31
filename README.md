# 🕒 Employee Attendance Monitoring System (EAMS)

This is a Python-based system to track employee attendance using biometric login and location verification, built for construction firms with distributed sites. It was developed as part of the final year Information Systems project.

## 📌 Problem Statement
Manual attendance tracking at construction sites leads to:
- Time theft (buddy punching)
- Human errors in payroll
- Compliance risks
- No real-time workforce visibility

---

## ✅ Solution
The **Employee Attendance Monitoring System (EAMS)**:
- Replaces manual logs with biometric + GPS login
- Automates clock-in/out with time calculations
- Provides real-time reports and notifications
- Enables role-based access (Admin / Employee)

---

## 🛠️ Tech Stack
| Category         | Tools Used              |
|------------------|--------------------------|
| Language         | Python                   |
| UI               | Tkinter / CustomTkinter |
| Backend          | MySQL                    |
| UI Design        | Figma                    |
| Version Control  | Git + GitHub             |

---

## 🔑 Features

### 🎯 Core Functionalities
- ✅ Secure employee login (email + password)
- ✅ Role-based dashboard (Employee & Admin)
- ✅ Real-time attendance logging
- ✅ Monthly attendance reports
- ✅ CSV export for payroll
- ✅ Leave request and approval system

### 🚫 Out of Scope
- ❌ Mobile App (planned future scope)
- ❌ Integration with external HR systems

---

## 📐 System Design

### Entity Relationship Diagram (ERD)
- `users`: Common login table (employee/admin)
- `employees` / `admins`: Linked by `user_id`
- `attendance`: Tracks check-in/check-out and hours worked

### Data Flow Diagrams (DFDs)
- Level 0 and Context DFD included in report

### Use Case Highlights
- UC-01: Clock-in/Clock-out with GPS
- UC-02: Admin dashboard with export
- UC-03: Employee profile management

---

## 📊 Reports & Analytics
- Daily/Monthly reports
- Absentee trend analysis
- Auto-alerts for late logins, early exits
- Export to CSV

---

## 💾 Database Schema (MySQL)
```sql
CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  first_name VARCHAR(255),
  last_name VARCHAR(255),
  email VARCHAR(255) UNIQUE NOT NULL,
  password VARCHAR(255) NOT NULL,
  role ENUM('employee', 'admin') NOT NULL
);

CREATE TABLE employees (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT UNIQUE NOT NULL,
  designation VARCHAR(255) NOT NULL,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE attendance (
  id INT AUTO_INCREMENT PRIMARY KEY,
  employee_id INT NOT NULL,
  check_in TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  check_out TIMESTAMP NULL,
  work_hours INT GENERATED ALWAYS AS (TIMESTAMPDIFF(HOUR, check_in, check_out)) STORED,
  FOREIGN KEY (employee_id) REFERENCES users(id) ON DELETE CASCADE
);
