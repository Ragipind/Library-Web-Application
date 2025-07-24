# 📚 Library Management System (Flask + SQLite)

A web-based system to manage library operations including:
- Book management
- Member records
- Book issue/return with fine
- Due date email reminders via Gmail SMTP

## 🚀 Technologies
- **Frontend**: HTML, CSS, Bootstrap, JavaScript
- **Backend**: Flask (Python)
- **Database**: SQLite
- **Email**: Gmail SMTP
- **Deployment**: PythonAnywhere

## 📦 Features
- Admin login, secure access
- Add/Edit/Delete/Search Books
- Add/Delete Members
- Issue/Return books
- Late fine tracking
- Email reminder for due returns
- Daily/Weekly/Monthly reports

## 📬 Setup Email
Enable 2FA on Gmail and create an [App Password](https://support.google.com/accounts/answer/185833).

## 🔧 Run Locally
```bash
git clone <this-project>
cd LMS
pip install -r requirements.txt
python app.py
