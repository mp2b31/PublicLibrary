# PublicLibrary

This is a simple Flask-based web application for managing a library system. It allows users to view books, check availability, and view loan statistics. This app supports the following features:

- View the list of available books and borrowed books
- See users' loan history
- View loan statistics, including average loan duration and other descriptive statistics
- Switch between statistical visualizations

## Installation
1. Clone the repository:
```bash
 git clone https://github.com/mp2b31/PublicLibrary.git
```

2. Set up a Virtual Environment:
Navigate to the project directory:
```
cd PublicLibrary
```
Create and activate a virtual environment:
#### On Windows:
```
python -m venv venv venv\Scripts\activate
```
#### On macOS/Linux
```
python3 -m venv venv source venv/bin/activate
```

3. Install dependencies:
```bash
 pip install -r requirements.txt
 ```

4. Run the application:
```
python initial.py
```

5. Acess the application:
Open your browser and navigate to the following URL:
http://127.0.0.1:5000/


## Available Routes

The application provides the following routes for interacting with the library system:

### 1. **Main Menu**
- **Route**: `/`
- **Description**: Displays the main menu with links to various sections of the app, such as books, loan history, and statistics.

### 2. **Book List**
- **Route**: `/books`
- **Description**: Displays a list of all the books in the library. This page fetches all books from the database and presents them in a table format.

### 3. **Availability**
- **Route**: `/availability`
- **Description**: Displays the availability of books in two sections:
  - **Available Books**: Displays a list of books that are currently available for borrowing.
  - **Borrowed Books**: Displays a list of books that are currently borrowed by users.

#### Subroutes for Availability:
- **Available Books**  
  - **Route**: `/availability/available_books`
  - **Description**: Shows the books that are available for borrowing.

- **Borrowed Books**  
  - **Route**: `/availability/borrowed_books`
  - **Description**: Shows the books that are currently borrowed and not yet returned.

### 4. **User Loans Menu**
- **Route**: `/user_loans`
- **Description**: Displays a list of all users. Clicking on any user's name will show their loan history, including the books they've borrowed.

### 5. **User Loan History**
- **Route**: `/user_loans/<int:user_id>`
- **Description**: Displays a list of loans for a specific user, including:
  - **Returned Books**: Books that have been returned.
  - **Not Yet Returned Books**: Books that are still loaned out and not yet returned, sorted by the return date.

### 6. **Loan Statistics**
- **Route**: `/loan_statistics`
- **Description**: Displays statistics related to loans, including:
  - Total number of loans in the system.
  - Number of books that are currently loaned out.
  - The number of returned books.
  - The average loan duration (in days) for returned books.

### 7. **Descriptive Statistics**
- **Route**: `/statistics`
- **Description**: Displays descriptive statistics for the library's loan data, including:
  - The average number of loans per user for the year 2024.
  - The average loan duration for returned books in 2024.
  - Graphs showing the top 3 users who have borrowed the most books and the users with the longest average loan durations.
 
## License
This project is licensed under the [MIT License](LICENSE).
