# Lab 4: Search Queries in SQL & Library Web Application

- **Student Name:** Taha Mohamed, Noor Elhawary
- **Student ID:** `2304236,2304253`
- **Course:** Database Systems (Computer and Communications Engineering)
- **Institution:** Alexandria National University (ANU)

---

## Project Structure

```text
lab4-2304236/
├── problem2_DDL.sql        # Database schema creation (library)
├── problem2_DML.sql        # Sample dataset population
├── problem2_Queries.sql    # All SQL queries covering F2.1 – F2.6
├── README.md               # Setup and execution documentation
└── website/                # Flask web application
    ├── app.py              # Backend routes, Prepared Statements & DB logic
    ├── .env                # Environment variables (excluded from Git)
    └── templates/
        ├── index.html          # Main dashboard with Lab 4 navigation
        ├── lab4_books.html     # F2.1 Search & F2.2 Full Catalogue
        └── lab4_reports.html   # F2.3 Reports, F2.4 Loans, F2.5 Top Stats, F2.6 Authors
```

---

## Implemented Features (Part 2: Library Database)

- **F2.1 — Book Search & Filtering:** Search books dynamically by title keyword (`LIKE`), price range (`BETWEEN`), and category (`WHERE`), sorted cheapest-first (`ORDER BY price ASC`). Uses parameterized **Prepared Statements** (`%s`) to prevent SQL injection.
- **F2.2 — Complete Library Catalogue:** Displays full book details joined across `BOOK`, `AUTHOR`, `PUBLISHER`, and `CATEGORY`.
- **F2.3 — Aggregated Reports:**
  - Book count and average price per category (`GROUP BY`, `COUNT`, `AVG`).
  - Authors with at least 2 books (`HAVING COUNT(*) >= 2`).
  - Library price summary (`SUM`, `MIN`, `MAX`).
- **F2.4 — Loan & Activity Tracking:**
  - Unreturned loans (`WHERE return_date IS NULL`).
  - Inactive members with zero loans (`LEFT JOIN ... WHERE loan_id IS NULL`).
  - Books that have never been borrowed (`LEFT JOIN ... WHERE loan_id IS NULL`).
- **F2.5 — Popularity Analytics:**
  - Top 3 most borrowed books (`ORDER BY ... DESC LIMIT 3`).
  - Top active reader with the highest number of loans.
- **F2.6 — Author & Origin Insights:**
  - Complete list of all authors alongside their book counts, including authors with 0 books (`LEFT JOIN`).
  - Books where the author and publisher share the same country (`WHERE a.country = p.country`).

---

## Setup & Execution Instructions

### 1. Database Setup (MariaDB / MySQL)
Import the schema and seed data into MariaDB:

```bash
mariadb -u root -p < problem2_DDL.sql
mariadb -u root -p < problem2_DML.sql
```

*(Ensure the `registration` database for user authentication/To-Do features is also initialized as configured in `website/.env`.)*

### 2. Environment Configuration
Inside `website/`, create a `.env` file with your local database credentials:

```env
DB_HOST=127.0.0.1
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=registration
SECRET_KEY=your_secret_key
```

### 3. Running the Flask Application
Navigate to the `website/` directory, activate the virtual environment, and launch the server:

```bash
cd website
python -m venv .venv
source .venv/bin/activate      # On Fish shell: source .venv/bin/activate.fish
pip install flask pymysql python-dotenv bcrypt
python app.py
```

Open `http://127.0.0.1:5000` in your browser, log in, and navigate to **Lab 4: Books & Search** or **Lab 4: Reports & Loans**.