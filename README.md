# Gestion Cabinet Médical — Odoo 16

A complete medical clinic management module built with **Odoo 16**.

The project was developed as an academic ERP application to manage the main activities of a medical clinic, including patients, doctors, appointments, consultations, prescriptions, medicines and user access rights.

---

## Project Overview

The objective of this project is to centralize the daily operations of a medical clinic in a single Odoo module.

The application provides:

- Patient management
- Doctor management
- Appointment scheduling
- Medical consultations
- Prescription management
- Medicine management
- Automatic email notifications
- PDF reports
- User roles and access control
- Dashboard and interface customization

---

## Main Features

### Patient Management

The module allows users to manage patient information such as:

- Full name
- Date of birth
- Automatically calculated age
- Gender
- Phone number
- Email
- Address
- City
- Postal code
- Blood group
- Allergies
- Medical history
- Chronic diseases
- Patient photo
- Internal notes

Patient records also include statistics such as:

- Number of appointments
- Number of consultations
- Last consultation date

---

### Doctor Management

Doctors can be managed with information including:

- Full name
- Medical specialization
- Phone number
- Professional email
- Medical license number
- Qualifications
- Years of experience
- Availability by day
- Working hours
- Professional biography
- Linked Odoo user account

---

### Appointment Management

The system manages appointments between patients and doctors.

Main capabilities include:

- Appointment scheduling
- Doctor assignment
- Patient assignment
- Appointment status management
- Priority handling
- Automatic appointment confirmation emails
- Automatic cancellation emails

---

## Email Notifications

The module includes email templates for:

- Appointment confirmation
- Appointment cancellation

Emails can include:

- Appointment reference
- Doctor name
- Specialty
- Appointment date
- Appointment time
- Priority
- Appointment reason
- Clinic contact information

---

## Medical Consultations

The consultation module allows doctors to manage medical consultations and patient follow-up.

Consultation records can be linked to:

- Patients
- Doctors
- Appointments
- Prescriptions

---

## Prescription Management

The module includes prescription management and PDF report generation.

Prescriptions can be associated with:

- Patients
- Doctors
- Consultations
- Medicines

---

## Medicine Management

The application provides a dedicated module for managing medicines used in prescriptions.

---

## Security and User Roles

The application implements role-based access control.

### Doctor

Doctors can access:

- Their own appointments
- Their own consultations
- Their own prescriptions
- Patient information in read-only mode

### Reception

Reception users can:

- View and manage all appointments
- View and manage patient records

### Clinic Manager

The Clinic Manager inherits permissions from both Reception and Doctor roles and has full access to clinic functionality.

Record rules are used to restrict access depending on the logged-in user.

---

## Reports

The module includes printable reports for:

- Medical consultations
- Prescriptions

Reports are generated using Odoo reporting features and XML templates.

---

## Technologies Used

### ERP Platform

- Odoo 16

### Backend

- Python
- Odoo ORM

### Frontend

- XML
- Odoo Views
- CSS

### Database

- PostgreSQL

### Communication

- Odoo Mail module
- Automated email templates

### Reporting

- Odoo PDF / QWeb reports

---

## Project Structure

```text
clinicAAAA/
│
├── __init__.py
├── __manifest__.py
│
├── models/
│   ├── __init__.py
│   ├── patient.py
│   ├── doctor.py
│   ├── appointment.py
│   ├── consultation.py
│   ├── prescription.py
│   └── medicine.py
│
├── views/
│   ├── menus.xml
│   ├── patient_views.xml
│   ├── doctor_views.xml
│   ├── appointment_views.xml
│   ├── consultation_views.xml
│   ├── prescription_views.xml
│   ├── medicine_views.xml
│   └── dashboard.xml
│
├── security/
│   ├── groups.xml
│   ├── record_rules.xml
│   └── ir.model.access.csv
│
├── data/
│   ├── sequences.xml
│   └── email_templates.xml
│
├── reports/
│   ├── prescription_report.xml
│   └── consultation_report.xml
│
└── static/
    └── src/
        └── css/
            ├── clinic.css
            └── custom_styles.css
