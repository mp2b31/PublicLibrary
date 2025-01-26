import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from collections import defaultdict
from sqlalchemy import func
from datetime import datetime
from initial import app, db, Book, Loan, User


def calculate_stats():
    with app.app_context():

        #author with the most books in the library catalog
        most_books_author = (
            db.session.query(Book.author, func.count(Book.id).label("book_count"))
            .group_by(Book.author)
            .order_by(func.count(Book.id).desc())
            .first()
        )
        print("\nThe author that has the most books in our library catalog is:")
        print(f"{most_books_author.author} ({most_books_author.book_count} books)\n" if most_books_author else "No data available.\n")

        #most borrowed author
        most_borrowed_author = (
            db.session.query(Book.author, func.count(Loan.id).label("loan_count"))
            .join(Loan, Loan.book_id == Book.id)
            .group_by(Book.author)
            .order_by(func.count(Loan.id).desc())
            .first()
        )
        print("\nThe most borrowed author by all users is:")
        print(f"{most_borrowed_author.author} ({most_borrowed_author.loan_count} times borrowed)\n" if most_borrowed_author else "No data available.\n")

        #for each user, the list of authors they have exclusively borrowed
        print("\nList of authors exclusively borrowed by each of our users:")
        users = User.query.all()
        for user in users:
            
            user_authors = set(                    #authors borrowed by this user
                db.session.query(Book.author)
                .join(Loan, Loan.book_id == Book.id)
                .filter(Loan.user_id == user.id)
                .distinct()
            )
            
            other_users_authors = set(              #authors borrowed by other users
                db.session.query(Book.author)
                .join(Loan, Loan.book_id == Book.id)
                .filter(Loan.user_id != user.id)
                .distinct()
            )

            exclusive_authors = user_authors - other_users_authors

            print(f"User: {user.name}")
            if exclusive_authors:
                for author in exclusive_authors:
                    print(f"  - {author[0]}")  #'author' is a tuple with one value
            else:
                print("  No exclusive authors.")
            print()

        #most borrowed book since library’s opening
        most_borrowed_book = (
            db.session.query(Book.title, func.count(Loan.id).label("loan_count"))
            .join(Loan, Loan.book_id == Book.id)
            .group_by(Book.id)
            .order_by(func.count(Loan.id).desc())
            .first()
        )
        print("\nThe most borrowed book since our library’s opening is:")
        print(f"{most_borrowed_book.title} ({most_borrowed_book.loan_count} times borrowed)\n" if most_borrowed_book else "No data available.\n")

        #user with the most simultaneous unreturned loans
        users_with_loans = User.query.all()
        max_simultaneous_loans = 0
        user_with_max_loans = None
        max_loans_dates = []

        for user in users_with_loans:
            loans = Loan.query.filter_by(user_id=user.id).order_by(Loan.loan_date).all()
            unreturned_loans = []

            for loan in loans:
                if loan.return_date is None:      #only unreturned loans
                    unreturned_loans.append(loan)
            
            loan_periods = []  
            for loan in unreturned_loans:
                loan_start = loan.loan_date
                loan_end = datetime.now()          #use current date as end date
                loan_periods.append((loan_start, loan_end))

            loan_periods.sort(key=lambda x: x[0])   #sort by start date

            simultaneous_loans = 0
            current_dates = []

            for loan_start, loan_end in loan_periods:
                simultaneous_loans += 1  
                current_dates.append(f"Loan start: {loan_start.strftime('%Y-%m-%d')}, Loan end: Not yet returned")

                if simultaneous_loans > max_simultaneous_loans:
                    max_simultaneous_loans = simultaneous_loans
                    user_with_max_loans = user
                    max_loans_dates = current_dates.copy()

            #clear for next iteration
            simultaneous_loans = 0
            current_dates.clear()

        print("\nThe user with the most simultaneous unreturned loans is:")
        if user_with_max_loans:
            print(f"User: {user_with_max_loans.name} ({max_simultaneous_loans} simultaneous unreturned loans)")
            print("Dates during this period:")
            for date in max_loans_dates:
                print(f"  - {date}")
        else:
            print("No unreturned loans found.")



        #make the plots
        ratings = [book.goodread_rating for book in Book.query.all()]

        #KDE (kernel density estimate) for Goodreads ratings
        plt.figure(figsize=(8, 6))
        sns.kdeplot(ratings, fill=True, color='crimson')
        plt.title('Estimated Probability Density of Goodreads Ratings')
        plt.xlabel('Goodreads Rating')
        plt.ylabel('Density')
        plt.grid(True)
        plt.show()

        borrowed_books = Loan.query.filter(Loan.return_date.isnot(None)).all()
        pages = []
        borrowing_durations = []

        for loan in borrowed_books:
            book = loan.book
            loan_duration = (loan.return_date - loan.loan_date).days  # Borrowing duration in days
            pages.append(book.pages)
            borrowing_durations.append(loan_duration)


        plt.figure(figsize=(8, 6))
        plt.scatter(pages, borrowing_durations, color='darkorange', alpha=0.6)
        plt.title('Pages vs Borrowing Duration (in days)')
        plt.xlabel('Number of Pages')
        plt.ylabel('Borrowing Duration (days)')
        plt.grid(True)
        plt.show()



if __name__ == "__main__":
    calculate_stats()