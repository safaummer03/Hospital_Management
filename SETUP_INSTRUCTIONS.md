# Hospital Management System - Setup Instructions

## Prerequisites
- Python 3.8 or higher
- Django 4.0 or higher
- Virtual environment (recommended)

## Installation Steps

### 1. Activate Virtual Environment
```bash
cd Hospitalmanagementsystem
env1\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install django
```

### 3. Database Setup
```bash
cd mainproject
python manage.py makemigrations
python manage.py migrate
```

### 4. Create Superuser (Admin)
```bash
python manage.py createsuperuser
```

### 5. Run Development Server
```bash
python manage.py runserver
```

## Initial Data Setup

### 1. Create Departments
Access Django Admin at `http://127.0.0.1:8000/admin/` and create departments:
- Cardiology
- Neurology
- Orthopedics
- Pediatrics
- General Medicine

### 2. Create Doctor Users
1. Create users with role 'DOCTOR'
2. Create corresponding Doctor profiles linked to departments

### 3. Create Staff Users
Create users with role 'STAFF' for administrative tasks

## System Features

### Role-Based Access Control
- **Admin**: Complete system management
- **Doctor**: Patient care, appointments, medical records
- **Staff**: Patient registration, appointment scheduling
- **Patient**: Self-service portal, appointment booking

### Core Modules
1. **User Authentication**: Secure login with role-based redirection
2. **Patient Management**: Registration, profiles, medical history
3. **Doctor Management**: Profiles, departments, schedules
4. **Appointment System**: Online booking, scheduling, status tracking
5. **Medical Records**: Diagnosis, treatment plans, prescriptions
6. **Notifications**: Automated alerts and reminders
7. **Reports**: Analytics and performance metrics

### Key URLs
- Login: `/login/`
- Dashboard: `/dashboard/`
- Patients: `/patients/`
- Appointments: `/appointments/`
- Reports: `/reports/`

## Security Features
- Role-based access control
- CSRF protection
- User authentication required
- Data validation and sanitization

## Database Models
- **User**: Extended with roles and profile information
- **Department**: Hospital departments
- **Doctor**: Doctor profiles with specializations
- **Patient**: Patient profiles with medical information
- **Appointment**: Scheduling and status management
- **MedicalRecord**: Clinical documentation
- **Prescription**: Medication management
- **Notification**: Alert system

## Usage Guidelines

### For Administrators
1. Manage users and roles
2. Create departments and assign doctors
3. Monitor system performance
4. Generate reports and analytics

### For Doctors
1. View daily appointments
2. Access patient medical histories
3. Create medical records and prescriptions
4. Track treatment progress

### For Staff
1. Register new patients
2. Schedule appointments
3. Manage patient information
4. Handle administrative tasks

### For Patients
1. Book appointments online
2. View medical history
3. Access prescriptions
4. Receive notifications

## Troubleshooting

### Common Issues
1. **Migration Errors**: Delete db.sqlite3 and run migrations again
2. **Template Not Found**: Ensure templates directory is configured
3. **Static Files**: Run `python manage.py collectstatic` for production
4. **Permission Denied**: Check user roles and permissions

### Development Tips
1. Use Django Debug Toolbar for development
2. Enable logging for error tracking
3. Regular database backups
4. Test with different user roles

## Production Deployment
1. Set DEBUG = False
2. Configure proper database (PostgreSQL recommended)
3. Set up static file serving
4. Configure email backend for notifications
5. Implement SSL/HTTPS
6. Set up monitoring and logging

## Support
For technical support or feature requests, refer to the project documentation or contact the development team.