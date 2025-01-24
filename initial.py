from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import random
import datetime
import numpy as np

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db' # tells it which db
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # saves resources
db = SQLAlchemy(app) # creates an instance


# Book model 
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    published_date = db.Column(db.String(10), nullable=False)
    status = db.Column(db.String(10), default="available")
    pages = db.Column(db.Integer, nullable=False, default=0)
    goodread_rating = db.Column(db.Float, nullable=False, default=0.0)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

# Loan model
class Loan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    loan_date = db.Column(db.Date, nullable=False)
    return_date = db.Column(db.Date, nullable=True)


# Populate db
def seed_database():
    db.drop_all()
    db.create_all()

    # Seed books
    mean_rating = 3.5
    std_dev_rating = 1.0
    for i in range(100):
        rating = max(0, min(5, np.random.normal(mean_rating, std_dev_rating)))
        book = Book(
            title=f"Book {i+1}",
            author=f"Author {random.randint(1, 10)}",
            published_date=f"{random.randint(1900, 2023)}-03-31",
            pages=random.randint(80, 1000),
            goodread_rating=round(rating, 2),
        )
        db.session.add(book)

    # Seed users
    for i in range(5):
        user = User(name=f"User {i+1}")
        db.session.add(user)

    db.session.commit()

    # Seed loans
    users = User.query.all()
    books = Book.query.all()

    for user in users:
        loan_count = random.randint(3, 10)
        loaned_books = random.sample(books, loan_count)
        for book in loaned_books:
            loan_date = datetime.date.today() - datetime.timedelta(days=random.randint(1, 365))
            # 50% chance of the book being returned
            if random.choice([True, False]):
                return_date = loan_date + datetime.timedelta(days=random.randint(1, 30))
                book.status = "available"
            else:
                return_date = None
                book.status = "borrowed"
            
            loan = Loan(
                book_id=book.id,
                user_id=user.id,
                loan_date=loan_date,
                return_date=return_date,
            )
            db.session.add(loan)

    db.session.commit()
    

@app.route('/')
def home():
    return "The library simulation is populated."

if __name__ == "__main__":
    app.run(debug=True)