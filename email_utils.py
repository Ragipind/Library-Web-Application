import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from models import db, Member, Transaction

def send_due_reminders():
    upcoming_due = datetime.now() - timedelta(days=13)  # Books about to be late (14 days limit)
    transactions = Transaction.query.filter(
        Transaction.return_date == None,
        Transaction.issue_date <= upcoming_due
    ).all()

    for tx in transactions:
        member = tx.member
        msg = MIMEText(f"Dear {member.name},\n\nPlease return your book '{tx.book.title}' to avoid fines.\n\nLibrary System")
        msg['Subject'] = 'Library Book Due Reminder'
        msg['From'] = 'yourlibrary@example.com'
        msg['To'] = member.email

        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
                smtp.starttls()
                smtp.login('yourlibrary@gmail.com', 'your-app-password')
                smtp.send_message(msg)
                print(f"Reminder sent to {member.email}")
        except Exception as e:
            print(f"Error sending email to {member.email}: {e}")
