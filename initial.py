from flask import Flask, render_template, redirect, url_for 
from flask_sqlalchemy import SQLAlchemy
import random
import numpy as np
from datetime import datetime, date, timedelta
from statistics import mean 

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db' # points to the SQLite database file
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # saves resources
db = SQLAlchemy(app) # creates an instance


#models 
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    published_date = db.Column(db.String(10), nullable=False)
    status = db.Column(db.String(10), default="available")
    pages = db.Column(db.Integer, nullable=False, default=0)
    goodread_rating = db.Column(db.Float, nullable=False, default=0.0)
    loans = db.relationship('Loan', backref='book', lazy=True)     #backref to Loans


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    loans = db.relationship('Loan', backref='user', lazy=True)


class Loan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    loan_date = db.Column(db.Date, nullable=False)
    return_date = db.Column(db.Date, nullable=True)


#populate db
def seed_database():

    with app.app_context():

        db.drop_all()
        db.create_all()

        #seed books
        mean_rating = 3.5
        std_dev_rating = 1.0
        for i in range(100):
            rating = max(0, min(5, np.random.normal(mean_rating, std_dev_rating)))

            year = random.randint(1900, 2024)
            month = random.randint(1, 12)

            try:
                day = random.randint(1, (datetime(year, month + 1, 1) - datetime(year, month, 1)).days)
            except ValueError:  #for December or invalid date combinations
                day = random.randint(1, 31)

            #format date to 'YYYY-MM-DD' format
            published_date = f"{year}-{month:02d}-{day:02d}"

            book = Book(
                title=f"Book {i+1}",
                author=f"Author {random.randint(1, 10)}",
                published_date=published_date,
                pages=random.randint(80, 1000),
                goodread_rating=round(rating, 2),
            )
            db.session.add(book)

        #seed users
        for i in range(5):
            user = User(name=f"User {i+1}")
            db.session.add(user)

        db.session.commit()

        #seed loans
        users = User.query.all()
        books = Book.query.all()

        for user in users:
            loan_count = random.randint(3, 10)
            loaned_books = random.sample(books, loan_count)
            for book in loaned_books:
                loan_date = date.today() - timedelta(days=random.randint(1, 365))
                # 50% chance of the book being returned
                if random.choice([True, False]):
                    return_date = loan_date + timedelta(days=random.randint(1, 30))
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
    

#-------------------ROUTES------------------------
@app.route('/')
def main_menu():
    return render_template('main_menu.html') 


@app.route('/books') #book list
def books():
    books = Book.query.all()
    return render_template('books.html', books=books)


@app.route('/availability')
def availability():
    return render_template('availability.html', available_books=available_books, borrowed_books=borrowed_books)


@app.route('/availability/available_books')
def available_books():
    available_books = Book.query.filter_by(status="available").all()
    return render_template('available_books.html', available_books=available_books)

@app.route('/availability/borrowed_books')
def borrowed_books():
    borrowed_books = Book.query.filter_by(status="borrowed").all()
    return render_template('borrowed_books.html', borrowed_books=borrowed_books)



@app.route('/user_loans')
def user_loans_menu():
    users = User.query.all()  
    return render_template('user_loans_menu.html', users=users)


@app.route('/user_loans/<int:user_id>')
def user_loans(user_id):
    user = User.query.get(user_id)
    loans = Loan.query.filter_by(user_id=user_id).all()
    
    returned_loans = [loan for loan in loans if loan.return_date is not None]
    not_returned_loans = [loan for loan in loans if loan.return_date is None]
    returned_loans.sort(key=lambda loan: loan.return_date, reverse=True)

    return render_template('user_loans.html', 
                           user=user, 
                           returned_loans=returned_loans, 
                           not_returned_loans=not_returned_loans)


@app.route('/loan_statistics')
def loan_statistics():
    total_loans = Loan.query.count()
    loaned_books = Loan.query.filter(Loan.return_date.is_(None)).count()    
    returned_books = total_loans - loaned_books
    
    #calculate the average loan duration in days only for those with a return date
    loan_duration_avg = db.session.query(db.func.avg( 
        (Loan.return_date - Loan.loan_date).label('duration')
    )).filter(Loan.return_date != None).scalar()
    
    if loan_duration_avg is None:
        loan_duration_avg = 0.0
    
    return render_template('loan_stats.html', 
                           total_loans=total_loans, 
                           loaned_books=loaned_books, 
                           returned_books=returned_books, 
                           loan_duration_avg=loan_duration_avg)

@app.route('/statistics')
def statistics():
    loans_2024 = Loan.query.filter(Loan.loan_date.between('2024-01-01', '2024-12-31')).all()
    avg_loans_per_user = len(loans_2024) / User.query.count() if User.query.count() > 0 else 0

    returned_loans = [loan for loan in loans_2024 if loan.return_date]
    durations = [(loan.return_date - loan.loan_date).days for loan in returned_loans]
    avg_duration = mean(durations) if durations else 0

    avg_duration = round(avg_duration, 2)

    #books borrowed
    borrowed_stats = db.session.query(
        Loan.user_id, db.func.count(Loan.id).label('loan_count')
    ).group_by(Loan.user_id).order_by(db.desc('loan_count')).limit(3).all()
    borrowed_data = {
        'labels': [User.query.get(stat[0]).name for stat in borrowed_stats],
        'values': [stat[1] for stat in borrowed_stats],
    }

    #loan duration
    duration_stats = db.session.query(
        Loan.user_id, db.func.avg(db.func.julianday(Loan.return_date) - db.func.julianday(Loan.loan_date)).label('avg_duration')
    ).filter(Loan.return_date.isnot(None)).group_by(Loan.user_id).order_by(db.desc('avg_duration')).limit(3).all()
    duration_data = {
        'labels': [User.query.get(stat[0]).name for stat in duration_stats],
        'values': [stat[1] for stat in duration_stats],
    }

    return render_template(
        'statistics.html',
        avg_loans_per_user=avg_loans_per_user,
        avg_duration=avg_duration,
        borrowed_data=borrowed_data,
        duration_data=duration_data,
    )



if __name__ == "__main__":
    seed_database()
    app.run(debug=True)