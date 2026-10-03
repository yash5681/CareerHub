# CAREERHUB — Professional Indian Job Portal

[![Django](https://img.shields.io/badge/Django-5.2-44B78B?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Ready-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)](https://getbootstrap.com/)
[![Razorpay](https://img.shields.io/badge/Razorpay-Integrated-0C2340?style=for-the-badge&logo=razorpay&logoColor=white)](https://razorpay.com/)
[![i18n](https://img.shields.io/badge/i18n-English%20%7C%20Hindi%20%7C%20Gujarati-B87333?style=for-the-badge)](https://docs.djangoproject.com/en/5.2/topics/i18n/)

**CareerHub** is an enterprise-grade, portfolio-ready Indian job marketplace connecting ambitious professionals with leading startups, IT service powerhouses, and Fortune 500 enterprises. Built on a clean Django architecture with a corporate **Brown + White** design aesthetic, it delivers end-to-end functionality across candidate discovery, resume building, recruitment pipelines, video interviews, direct messaging, and Razorpay subscriptions.

---

## 🌟 Key Platform Features

### 1. Job Seeker Experience
- **Smart Job Search & Filtering**: Multi-parameter search by role, skills, Indian cities/states, CTC (in ₹ LPA), experience level, and work mode (On-site, Hybrid, Remote).
- **Dual Resume System**:
  - **Resume Upload**: Upload PDF/DOCX resumes with strict extension and 5MB size validation.
  - **Interactive Resume Builder**: Automatically compiles ATS-friendly, clean printable resumes with templates (*Modern Elegant*, *Classic Corporate*, *Minimalist Tech*).
- **Application Tracking Pipeline**: Real-time progress monitor (*Applied* &rarr; *Under Review* &rarr; *Shortlisted* &rarr; *Interview Scheduled* &rarr; *Selected / Rejected*).
- **Saved Bookmarks & Job Alerts**: Save opportunities with 1-click AJAX and configure automated email/in-app alert criteria.
- **Intelligent Recommendations**: Match engine delivering opportunities tailored to candidate skills and location preferences.
- **Direct Recruiter Messaging**: Threaded in-app chat with real-time AJAX response.

### 2. Employer & Recruiter Portal
- **Employer Branding & Company Profiles**: Showcase company culture, office perks, verified employer trust badges, and open job roles.
- **Comprehensive Job Publishing**: Multi-field job composer supporting draft/publish states, salary confidentiality toggles, and skills tagging.
- **Candidate Pipeline Management**: Full applicant tracking system (ATS) with status filter tabs, candidate search, and private notes.
- **Interview Scheduling**: Book video calls (Google Meet / Zoom / Teams) or in-person rounds with automatic candidate notifications.
- **Subscription Management**: Database-driven plans (*Free Starter*, *Professional Recruiter*, *Enterprise Business*) integrated with Razorpay.

### 3. Custom Administrative Console
- **Analytics & Platform KPIs**: Live user distribution, active job metrics, revenue ledger, and application conversion funnel.
- **Moderation & Trust Safety**: Review candidate grievances on fraudulent listings with 1-click resolve/dismiss workflows.
- **Taxonomy Management**: Full governance over job categories, technical skills, and verified employer badges.
- **Django SuperAdmin Integration**: Direct access to Django's native administrative interface.

### 4. Multilingual & Localization (i18n)
- Native language switcher in top navbar supporting:
  - **English (India)**
  - **हिन्दी (Hindi)**
  - **ગુજરાતી (Gujarati)**
- Full PO/MO gettext integration across UI headers, form validation, and dashboard states.

---

## 🎨 Design System: Brown + White

The platform utilizes a consistent, warm corporate aesthetic:
- **Primary Brand Color**: `#4A2E1F` (Rich Espresso Brown)
- **Primary Dark / Hover**: `#361F13`
- **Warm Bronze Accent**: `#B87333`
- **Surface**: `#FFFFFF` (Crisp White)
- **Canvas / Background**: `#FAF8F5` (Soft Alabaster)
- **Typography**: Plus Jakarta Sans

---

## 🛠️ Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Backend** | Python 3.11, Django 5.2 (ORM, Authentication, Forms, Messages, i18n) |
| **Database** | PostgreSQL (Production) / Django ORM with `psycopg2-binary` |
| **Frontend** | HTML5, CSS3, JavaScript ES6+, Bootstrap 5.3, Font Awesome 6.5 |
| **Payments** | Razorpay Payment Gateway (Server-side HMAC-SHA256 signature verification) |
| **Static & Media** | WhiteNoise Static Files Compression, Pillow |

---

## 🚀 Installation & Local Setup

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/careerhub.git
cd careerhub
```

### 2. Create and Activate Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Ensure your database and Razorpay test credentials are set in `.env`:
```ini
SECRET_KEY=your-secure-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=careerhub_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

RAZORPAY_KEY_ID=rzp_test_CareerHubDemo123
RAZORPAY_KEY_SECRET=CareerHubSecretMock987654
```

### 5. Apply Migrations & Seed Demo Data
```bash
# Run database migrations
python manage.py migrate

# Seed realistic Indian tech companies, jobs, seekers, and recruiters
python manage.py seed_data
```

### 6. Run the Development Server
```bash
python manage.py runserver
```
Visit `http://127.0.0.1:8000/` in your browser.

---

## 🔑 Demo Accounts

Use these pre-configured accounts created by `python manage.py seed_data`:

| Role | Email | Password | Access |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin@careerhub.in` | `Admin@CareerHub2026` | Custom Admin Console (`/dashboard/admin/`) & Django Admin |
| **Recruiter (Razorpay)** | `priya.nair@razorpay.com` | `Password@123` | Employer Dashboard, Post Jobs, Candidate Pipeline |
| **Job Seeker** | `rahul.sharma@example.com` | `Password@123` | Seeker Dashboard, Resumes, Applications, Saved Jobs |

---

## 🧪 Running Automated Tests

Run the comprehensive test suite verifying registration, search, application pipeline, duplicate application prevention, interview booking, and Razorpay signature verification:

```bash
python manage.py test tests
```

---

## 📁 Clean Modular Architecture

```
careerhub/
│
├── manage.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
│
├── config/
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── apps/
│   ├── accounts/         # Custom User model, RBAC, Profile models
│   ├── companies/        # Companies, verified badges, reviews
│   ├── jobs/             # Job postings, filters, search, categories, alerts
│   ├── applications/     # Application pipeline, status audit trail
│   ├── resumes/          # Resume upload validation & ATS Builder
│   ├── interviews/       # Video call & in-person round scheduler
│   ├── messaging/        # Direct recruiter-seeker threaded chat
│   ├── notifications/    # Database-backed event notifications
│   ├── payments/         # Razorpay checkout & signature verification
│   ├── reviews/          # Employee moderation & rating reviews
│   ├── reports/          # Trust & Safety fraud grievance reports
│   ├── blog/             # Career guidance & interview prep articles
│   ├── dashboard/        # Role-based dashboards & analytics
│   └── core/             # Home, About, Contact, i18n, Error handlers
│
├── templates/            # Bootstrap 5 responsive templates
├── static/               # CSS tokens, JS AJAX handlers, SVG logos
├── media/                # User uploaded resumes and avatars
└── locale/               # English, Hindi (hi), Gujarati (gu) catalogs
```

---

## 🛡️ Production Deployment Checklist

1. Set `DEBUG=False` in production environment.
2. Configure PostgreSQL database credentials in `.env`.
3. Set your live Razorpay API Key ID and Secret.
4. Run `python manage.py collectstatic` (WhiteNoise automatically compresses assets).
5. Deploy behind Gunicorn / Nginx with HTTPS enabled.

---

## 📄 License
This project is licensed under the MIT License — feel free to use it for portfolio showcases, job interviews, or academic demonstration.
