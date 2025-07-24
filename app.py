from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_mail import Mail, Message
from datetime import datetime, timedelta

from models import db, Member, Book, Borrow
from forms import LoginForm, RegisterForm, AddBookForm, BorrowForm
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object('config.Config')

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
mail = Mail(app)
migrate = Migrate(app, db)

@login_manager.user_loader
def load_user(user_id):
    return Member.query.get(int(user_id))
# @app.route('/')
# def Home():
#     return render_template('Home.html')

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    user_form = LoginForm(prefix="user")
    admin_form = LoginForm(prefix="admin")

    if user_form.validate_on_submit() and user_form.submit.data:
        user = Member.query.filter_by(username=user_form.username.data).first()
        if user and user.check_password(user_form.password.data):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('User login failed.', 'danger')

    if admin_form.validate_on_submit() and admin_form.submit.data:
        admin = Member.query.filter_by(username=admin_form.username.data, is_admin=True).first()
        if admin and admin.check_password(admin_form.password.data):
            login_user(admin)
            return redirect(url_for('dashboard'))
        flash('Admin login failed.', 'danger')

    return render_template('login.html', user_form=user_form, admin_form=admin_form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = Member(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('User registered successfully!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/add_book', methods=['GET', 'POST'])
@login_required
def add_book():
    form = AddBookForm()
    if form.validate_on_submit():
        new_book = Book(
            title=form.title.data,
            author=form.author.data,
            category=form.category.data,
            copies=form.copies.data
        )
        db.session.add(new_book)
        db.session.commit()
        flash('Book added successfully!', 'success')
        return redirect(url_for('books'))
    return render_template('add_book.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    borrowed_books = Borrow.query.filter_by(member_id=current_user.id, returned=False).all()
    return render_template('dashboard.html', borrowed_books=borrowed_books)

@app.route('/borrow/<int:book_id>', methods=['GET', 'POST'])
@login_required
def borrow(book_id):
    current_borrows = Borrow.query.filter_by(member_id=current_user.id, returned=False).count()
    if current_borrows >= 3:
        flash("You have reached your borrow limit (3 books). Return some to borrow more.")
        return redirect(url_for('dashboard'))

    book = Book.query.get(book_id)
    if not book:
        flash("Book not found.")
        return redirect(url_for('dashboard'))

    if Borrow.query.filter_by(member_id=current_user.id, book_id=book.id, returned=False).first():
        flash("You have already borrowed this book.")
        return redirect(url_for('dashboard'))

    due_date = datetime.utcnow() + timedelta(days=7)
    borrow = Borrow(member_id=current_user.id, book_id=book.id, due_date=due_date)
    db.session.add(borrow)
    db.session.commit()
    flash(f"Borrowed '{book.title}' successfully! Due in 7 days.")
    return redirect(url_for('dashboard'))

@app.route('/return/<int:borrow_id>')
@login_required
def return_book(borrow_id):
    borrow = Borrow.query.get(borrow_id)
    if borrow and borrow.member_id == current_user.id:
        borrow.returned = True
        db.session.commit()
        flash("Book returned successfully.")
    return redirect(url_for('dashboard'))

@app.route('/send_reminders')
@login_required
def send_reminders():
    if not current_user.is_admin:
        flash("Only admins can send reminders.")
        return redirect(url_for('dashboard'))

    tomorrow = datetime.utcnow() + timedelta(days=1)
    reminders = Borrow.query.filter(Borrow.due_date <= tomorrow, Borrow.returned == False).all()
    for borrow in reminders:
        user = Member.query.get(borrow.member_id)
        book = Book.query.get(borrow.book_id)
        msg = Message(
            subject="Library Due Reminder",
            sender=app.config['MAIL_USERNAME'],
            recipients=[user.email],
            body=f"Dear {user.username},\n\nReminder: Your book '{book.title}' is due on {borrow.due_date.date()}.\nPlease return it on time.\n\nThanks!"
        )
        mail.send(msg)
    flash(f"{len(reminders)} reminders sent.")
    return redirect(url_for('dashboard'))
 
@app.route('/books')
@login_required
def books():
    all_books = Book.query.all()
    return render_template('books.html', books=all_books)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/help')
def help_page():
    return render_template('help.html')

@app.route('/issued-books')
@login_required
def issued_books():
    return render_template('issued_books.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
