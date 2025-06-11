# knight-frank
# NPS Survey Web Application

A secure, multi-user Net Promoter Score (NPS) survey platform built with React and Django REST Framework. Registered users can create unique survey links, collect one-time customer responses without storing personal data, and view user-specific metrics and visualizations on a private dashboard.

---

## ✅ Problem Statement Compliance

### 🔐 User Authentication
- Register/Login via `/api/register/`, `/api/token/` (JWT - SimpleJWT).
- JWT stored in `localStorage`, used in Axios (api.js) for secure access.
- Data isolation via `user=request.user` across backend and frontend.

### ✉️ Survey Sending
- Unique links via UUID + signed token; no customer info stored.
- Supports optional campaign ID and custom expiration dates (default: 7 days).
- Sharing options: Email, WhatsApp, SMS, LinkedIn, Twitter/X, system share.
- Expired/responded links are disabled for sharing.

### 📩 Survey Response Handling
- One response per link (score + optional comment).
- No personal info (email, name, IP) is stored.
- Each response is tied to the link creator.

### 📊 Dashboard (User-Specific)
- NPS Score, Promoters/Passives/Detractors, response count.
- Filters: Date range, campaign dropdown.
- Visualizations:
  - Bar chart (breakdown of respondent types).
  - Line chart (NPS trend over time).

---

## 🚀 Tech Stack

- **Frontend**: React, Bootstrap, Chart.js, Axios  
- **Backend**: Django, DRF, PostgreSQL, SimpleJWT   
- **Tools**: Python 3.13, Node.js, Git

---

## ⚙️ Setup Instructions

### 🔧 Prerequisites

- Python 3.13, Node.js, PostgreSQL, npm

### 🐍 Backend Setup

```bash
git clone <repository-url>
cd nps-survey/backend

# Virtual Environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# .env
SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_URL=postgresql://nps_user:securepassword@localhost:5432/nps_survey

# Migrations
python manage.py migrate
python manage.py runserver



## Setup Instructions

1. Open a terminal and go to the frontend folder:

   ```bash
   cd frontend/nps-survey-frontend
   ```

2. Install all required packages:

   ```bash
   npm install
   ```

3. Create a `.env` file in the root folder and add this line:

   ```env
   REACT_APP_API_URL=http://127.0.0.1:8000/api/
   ```

4. Start the development server:

   ```bash
   npm start
   ```

5. Visit the app in your browser:

   ```
   http://localhost:3000
   ```

## Build for Production

```bash
npm run build
```

## Notes

* Make sure the Django backend is running at the API URL.
* JWT is stored in `localStorage` and added to requests via `api.js`.
* Only active, unresponded links can be shared.
* All data is user-specific; no customer personal info is stored.

