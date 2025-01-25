import os
from initial import app, db, Book, Loan, User  # import models and DB instance
from datetime import datetime
from statistics import mean

with app.app_context():

    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'library.db')  # reference the db inside 'instance' folder

    #initialize Flask app and DB if necessary
    if not os.path.exists(db_path):
        print("Database not found. Please make sure the application is set up properly.")
        exit()

    def calculate_statistics():
        print("\n--- Library Descriptive Statistics ---")

        total_books = Book.query.count()
        print(f"Total Books: {total_books}")

        available_books = Book.query.filter_by(status="available").count()
        borrowed_books = Book.query.filter_by(status="borrowed").count()
        print(f"Available Books: {available_books}")
        print(f"Borrowed Books: {borrowed_books}")

        ratings = [book.goodread_rating for book in Book.query.all()]
        avg_rating = mean(ratings) if ratings else 0
        print(f"Average Goodreads Rating: {avg_rating:.2f}")

        total_users = User.query.count()
        print(f"Total Users: {total_users}")

        loans_per_user = {user.name: Loan.query.filter_by(user_id=user.id).count() for user in User.query.all()}
        print("\nLoans per User:")
        for user, loan_count in loans_per_user.items():
            print(f"  - {user}: {loan_count} loans")

        #avg loan duration (only for completed loans)
        completed_loans = Loan.query.filter(Loan.return_date.isnot(None)).all()
        durations = [(loan.return_date - loan.loan_date).days for loan in completed_loans]
        avg_duration = mean(durations) if durations else 0
        print(f"\nAverage Loan Duration: {avg_duration:.2f} days")


        most_borrowed_books = db.session.query(Loan.book_id, db.func.count(Loan.book_id).label("loan_count")) \
                                .group_by(Loan.book_id) \
                                .order_by(db.desc("loan_count")) \
                                .all()
        
        if most_borrowed_books:
            most_borrowed_book_id = most_borrowed_books[0][0]
            most_borrowed_book = db.session.get(Book, most_borrowed_book_id)  
            print(f"Most Borrowed Book: {most_borrowed_book.title} by {most_borrowed_book.author} ({most_borrowed_books[0][1]} times)")
        else:
            print("No books have been borrowed yet.")

    if __name__ == "__main__":
        calculate_statistics()
