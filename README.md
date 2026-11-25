# 🏥 MediHub - Hospital Management System

A modern, professional web application for comprehensive hospital management with intelligent scheduling, secure medical records, and real-time notifications.

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Flask](https://img.shields.io/badge/flask-2.3-green)
![Vue.js](https://img.shields.io/badge/vue.js-3.x-success)
![Bootstrap](https://img.shields.io/badge/bootstrap-5.3-purple)
![License](https://img.shields.io/badge/license-MIT-green)

## What is this project?

This is a hospital management system I built for managing appointments between doctors and patients. It has three types of users:
- **Admin** - Manages doctors and patients
- **Doctors** - View appointments and update treatment records
- **Patients** - Book appointments and view medical history

## Why I made this

Most hospitals still use paper registers or complicated software. I wanted to make something simple that:
- Lets patients book appointments online
- Helps doctors see their schedule easily
- Gives admins control over everything
- Keeps all medical records in one place

## Features

### For Patients
- Register and login
- Book appointments (choose doctor, date, time slot)
- View appointment history
- See treatment records (diagnosis, medicines prescribed)
- Cancel appointments

### For Doctors
- View today's appointments
- See assigned patients
- Update treatment details (diagnosis, prescription, notes)
- Mark appointments as completed
- Set availability (morning/evening slots for next 7 days)

### For Admin
- Add/edit/blacklist doctors
- Edit/blacklist patients
- View all appointments
- Reschedule or cancel any appointment
- See appointment history for any doctor or patient
- Dashboard with statistics

## Tech Stack

**Frontend:**
- HTML, CSS, JavaScript
- Vue.js 3 (loaded from CDN)
- Bootstrap 5 for styling
- Professional dark theme (#0f172a)

**Backend:**
- Python Flask
- SQLite database
- SQLAlchemy (ORM)
- JWT for authentication

**Background Jobs:**
- Celery (for sending emails)
- Redis (message broker)

## Project Structure

```
hospital-management-system/
├── backend/
│   ├── models/              # Database tables
│   ├── routes/              # API endpoints
│   │   ├── auth.py         # Login/Register
│   │   ├── admin.py        # Admin features
│   │   ├── doctor.py       # Doctor features
│   │   └── patient.py      # Patient features
│   ├── celery_tasks/       # Email sending tasks
│   ├── app.py              # Main Flask app
│   ├── database.py         # Database setup
│   └── seed_db.py          # Create sample data
├── frontend/
│   ├── js/
│   │   ├── app.js          # Main Vue app
│   │   ├── admin.js        # Admin dashboard
│   │   ├── doctor.js       # Doctor dashboard
│   │   ├── patient.js      # Patient dashboard
│   │   └── api.js          # API calls
│   ├── custom.css          # Styling
│   └── index.html          # Main page
└── docs/                    # Documentation
```

## 🚀 Getting Started

For detailed installation and setup instructions, please refer to [`docs/setup.md`](docs/setup.md).

**Quick Start:**
```bash
# Clone and setup
git clone https://github.com/aloktripathi1/hospital-management-system.git
cd hospital-management-system/backend

# Install and run
pip install -r requirements.txt
python seed_db.py
python app.py

# Visit http://localhost:5000
```

The demo seed prompts for passwords without echoing input. Use the usernames
`admin`, `ajay`, or `arjun` and the passwords you entered. For an existing
installation, provisioning and credential rotation are separate from demo seeding.

For persistent sessions or multiple workers, set `MEDIHUB_SECRET_KEY` and
`MEDIHUB_JWT_SECRET_KEY` to separate strong secrets through the environment.
New databases can provision a first admin using `MEDIHUB_INITIAL_ADMIN_PASSWORD`
through the same protected environment.

## Database Tables

- **users** - Login credentials for all users
- **doctors** - Doctor profiles (name, specialization, experience, fees)
- **patients** - Patient info (name, age, gender, medical history)
- **appointments** - Booking records (date, time, status)
- **treatments** - Treatment records (diagnosis, prescription, notes)
- **doctor_availability** - Doctor schedule slots (morning/evening)

## Screenshots

### Homepage
Modern hero section with professional dark theme

![Homepage](screenshots/homepage.png)

### Login/Register
Clean branded login page with stats

![Login](screenshots/login.png)
![Register](screenshots/register.png)

### Admin Dashboard
Manage doctors, patients, and appointments

![Admin Dashboard](screenshots/admin_dashboard.png)

### Doctor Dashboard
View appointments and update treatments

![Doctor Dashboard](screenshots/doctor_dashboard.png)

### Patient Dashboard
Book appointments and view history

![Patient Dashboard](screenshots/patient_dashboard.png)

## What I Learned

- Building REST APIs with Flask
- User authentication with JWT
- Frontend development with Vue.js
- Database design and relationships
- Background job processing with Celery
- UI/UX design principles

## Future Improvements

- [ ] Payment integration for consultation fees
- [ ] Video consultation feature
- [ ] Prescription PDF download

## Documentation

Check the `docs/` folder for more details:
- `setup.md` - Detailed setup instructions
- `architecture.md` - How everything works together
- `bg_jobs.md` - Email system explanation

## Contributing

Feel free to fork this project and make improvements! Some ideas:
- Add more specializations
- Improve UI design
- Add more features (lab reports, pharmacy, etc.)

## License

MIT License
