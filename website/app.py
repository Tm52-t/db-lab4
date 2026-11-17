from flask import Flask, render_template, request, redirect, url_for, session, flash
import pymysql
import bcrypt
import os
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

load_dotenv()

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'static/images'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
app.secret_key = os.getenv('SECRET_KEY')

def get_db_connection():
    return pymysql.connect(
        host=os.getenv('DB_HOST', '127.0.0.1'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD') or os.getenv('DB_PASS'),
        database=os.getenv('DB_NAME', 'registration'),
        cursorclass=pymysql.cursors.DictCursor
    )

# دالة اتصال منفصلة لقاعدة بيانات اللاب (library)
def get_library_connection():
    return pymysql.connect(
        host=os.getenv('DB_HOST', '127.0.0.1'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD') or os.getenv('DB_PASS'),
        database='library',
        cursorclass=pymysql.cursors.DictCursor
    )

# ==========================================
# AUTH & TO-DO ROUTES
# ==========================================

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name'].strip()
        email = request.form['email'].strip()
        password = request.form['password']
        confirm = request.form['confirm_password']
        
        if not name:
            flash('Name is required', 'danger')
            return render_template('register.html')
        if not email:
            flash('Email is required', 'danger')
            return render_template('register.html')
        if not password:
            flash('Password is required', 'danger')
            return render_template('register.html')
        if password != confirm:
            flash('Passwords do not match', 'danger')
            return render_template('register.html')

        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO users (email, name, password_hash) VALUES (%s, %s, %s)', 
                           (email, name, hashed_pw.decode('utf-8')))
            conn.commit()
            
            cursor.execute('SELECT user_id, name FROM users WHERE email = %s', (email,))
            user = cursor.fetchone()
            session['user_id'] = user['user_id']
            session['name'] = user['name']
            
            return redirect(url_for('index'))
        except pymysql.err.IntegrityError as e:
            if e.args[0] == 1062:
                flash('Email Already Exists', 'danger')
        finally:
            cursor.close()
            conn.close()

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip()
        password = request.form['password']

        if not email or not password:
            flash('Invalid email or password', 'danger')
            return render_template('login.html')

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT user_id, name, password_hash FROM users WHERE email = %s', (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            session['user_id'] = user['user_id']
            session['name'] = user['name']
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password', 'danger')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT todo_id, title, is_done, created_at FROM todos WHERE user_id = %s ORDER BY todo_id DESC', (session['user_id'],))
    todos = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('index.html', todos=todos)

@app.route('/add', methods=['POST'])
def add_todo():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    title = request.form['title'].strip()
    if not title:
        flash('Title is required', 'danger')
    elif len(title) > 200:
        flash('Title is too long', 'danger')
    else:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO todos (user_id, title) VALUES (%s, %s)', (session['user_id'], title))
        conn.commit()
        cursor.close()
        conn.close()
        
    return redirect(url_for('index'))

@app.route('/edit/<int:todo_id>', methods=['POST'])
def edit_todo(todo_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    title = request.form['title'].strip()
    if title:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE todos SET title = %s WHERE todo_id = %s AND user_id = %s', 
                       (title, todo_id, session['user_id']))
        conn.commit()
        cursor.close()
        conn.close()
    return redirect(url_for('index'))

@app.route('/toggle/<int:todo_id>', methods=['POST'])
def toggle_todo(todo_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    is_done = request.form['is_done']
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE todos SET is_done = %s WHERE todo_id = %s AND user_id = %s', 
                   (int(is_done), todo_id, session['user_id']))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('index'))

@app.route('/delete/<int:todo_id>', methods=['POST'])
def delete_todo(todo_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM todos WHERE todo_id = %s AND user_id = %s', (todo_id, session['user_id']))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('index'))

# ==========================================
# LAB 3: LIBRARY ROUTES (LEGACY)
# ==========================================

@app.route('/library')
def library():
    conn = get_library_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM AUTHOR")
    authors = cursor.fetchall()
    
    cursor.execute("SELECT * FROM BOOK")
    books = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('library.html', authors=authors, books=books)

@app.route('/add_author', methods=['POST'])
def add_author():
    author_id = request.form['author_id']
    name = request.form['name']
    country = request.form['country']
    photo = request.files.get('photo')
    
    photo_path = None
    if photo and photo.filename:
        filename = secure_filename(photo.filename)
        photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        photo_path = f"images/{filename}"
        
    conn = get_library_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO AUTHOR (author_id, name, country, photo) VALUES (%s, %s, %s, %s)", 
                   (author_id, name, country, photo_path))
    conn.commit()
    cursor.close()
    conn.close()
    
    return redirect(url_for('library'))

@app.route('/add_book', methods=['POST'])
def add_book():
    book_id = request.form['book_id']
    title = request.form['title']
    price = request.form['price']
    author_id = request.form['author_id']
    cover = request.files.get('cover')
    
    cover_path = None
    if cover and cover.filename:
        filename = secure_filename(cover.filename)
        cover.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        cover_path = f"images/{filename}"
        
    conn = get_library_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO BOOK (book_id, title, price, author_id, cover) VALUES (%s, %s, %s, %s, %s)", 
                   (book_id, title, price, author_id, cover_path))
    conn.commit()
    cursor.close()
    conn.close()
    
    return redirect(url_for('library'))

@app.route('/edit_author/<int:id>', methods=['GET', 'POST'])
def edit_author(id):
    conn = get_library_connection()
    cursor = conn.cursor()
    try:
        if request.method == 'POST':
            name = request.form['name'].strip()
            country = request.form['country'].strip()
            photo = request.files.get('photo')

            if not name:
                flash('Name is required', 'danger')
                return redirect(url_for('edit_author', id=id))

            if photo and photo.filename:
                filename = secure_filename(photo.filename)
                photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                cursor.execute(
                    "UPDATE AUTHOR SET name = %s, country = %s, photo = %s WHERE author_id = %s",
                    (name, country, f"images/{filename}", id))
            else:
                cursor.execute(
                    "UPDATE AUTHOR SET name = %s, country = %s WHERE author_id = %s",
                    (name, country, id))
            conn.commit()
            return redirect(url_for('library'))

        cursor.execute("SELECT * FROM AUTHOR WHERE author_id = %s", (id,))
        author = cursor.fetchone()
        if not author:
            flash('Author not found', 'danger')
            return redirect(url_for('library'))
        return render_template('edit_author.html', author=author)
    finally:
        cursor.close()
        conn.close()

@app.route('/edit_book/<int:id>', methods=['GET', 'POST'])
def edit_book(id):
    conn = get_library_connection()
    cursor = conn.cursor()
    try:
        if request.method == 'POST':
            title = request.form['title'].strip()
            price = request.form['price']
            author_id = request.form['author_id']
            cover = request.files.get('cover')

            if not title:
                flash('Title is required', 'danger')
                return redirect(url_for('edit_book', id=id))

            try:
                if cover and cover.filename:
                    filename = secure_filename(cover.filename)
                    cover.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    cursor.execute(
                        "UPDATE BOOK SET title = %s, price = %s, author_id = %s, cover = %s WHERE book_id = %s",
                        (title, price, author_id, f"images/{filename}", id))
                else:
                    cursor.execute(
                        "UPDATE BOOK SET title = %s, price = %s, author_id = %s WHERE book_id = %s",
                        (title, price, author_id, id))
                conn.commit()
            except pymysql.err.IntegrityError:
                flash('Author ID does not exist', 'danger')
                return redirect(url_for('edit_book', id=id))
            return redirect(url_for('library'))

        cursor.execute("SELECT * FROM BOOK WHERE book_id = %s", (id,))
        book = cursor.fetchone()
        if not book:
            flash('Book not found', 'danger')
            return redirect(url_for('library'))
        return render_template('edit_book.html', book=book)
    finally:
        cursor.close()
        conn.close()

@app.route('/delete_book/<int:id>')
def delete_book(id):
    conn = get_library_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM BOOK WHERE book_id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('library'))

@app.route('/delete_author/<int:id>')
def delete_author(id):
    conn = get_library_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM AUTHOR WHERE author_id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('library'))

# ==========================================
# LAB 4: SEARCH QUERIES & REPORTS (F2.1 - F2.6)
# ==========================================

# F2.1 Search Books (Prepared Statements for Bonus) + F2.2 Catalogue
@app.route('/lab4/books', methods=['GET'])
def lab4_books():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_library_connection()
    try:
        with conn.cursor() as cursor:
            # 1. Get all categories for the dropdown filter
            cursor.execute("SELECT * FROM CATEGORY")
            categories = cursor.fetchall()

            # 2. F2.1: Search query using Prepared Statements (%s)
            keyword = request.args.get('keyword', '').strip()
            min_price = request.args.get('min_price', '').strip()
            max_price = request.args.get('max_price', '').strip()
            category_id = request.args.get('category_id', '').strip()

            search_sql = """
                SELECT b.book_id, b.title, b.price, b.publish_year, c.name AS category_name
                FROM BOOK b
                JOIN CATEGORY c ON b.category_id = c.category_id
                WHERE 1=1
            """
            params = []

            if keyword:
                search_sql += " AND b.title LIKE %s"
                params.append(f"%{keyword}%")
            if min_price and max_price:
                search_sql += " AND b.price BETWEEN %s AND %s"
                params.extend([float(min_price), float(max_price)])
            elif min_price:
                search_sql += " AND b.price >= %s"
                params.append(float(min_price))
            elif max_price:
                search_sql += " AND b.price <= %s"
                params.append(float(max_price))
            if category_id:
                search_sql += " AND b.category_id = %s"
                params.append(int(category_id))

            search_sql += " ORDER BY b.price ASC"
            cursor.execute(search_sql, tuple(params))
            search_results = cursor.fetchall()

            # 3. F2.2: Full Catalogue (JOIN)
            cursor.execute("""
                SELECT b.book_id, b.title, b.price, b.publish_year, 
                       a.name AS author_name, p.name AS publisher_name, c.name AS category_name
                FROM BOOK b
                JOIN AUTHOR a ON b.author_id = a.author_id
                JOIN PUBLISHER p ON b.publisher_id = p.publisher_id
                JOIN CATEGORY c ON b.category_id = c.category_id
                ORDER BY b.book_id ASC
            """)
            catalogue = cursor.fetchall()

        return render_template('lab4_books.html', 
                               categories=categories, 
                               search_results=search_results, 
                               catalogue=catalogue)
    finally:
        conn.close()


# F2.3 Reports + F2.4 Loans + F2.5 Most Borrowed + F2.6 Authors & Books
@app.route('/lab4/reports', methods=['GET'])
def lab4_reports():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_library_connection()
    try:
        with conn.cursor() as cursor:
            # F2.3 (a) Books count & avg price per category
            cursor.execute("""
                SELECT c.name AS category_name, COUNT(b.book_id) AS total_books, 
                       COALESCE(ROUND(AVG(b.price), 2), 0) AS avg_price
                FROM CATEGORY c
                LEFT JOIN BOOK b ON c.category_id = b.category_id
                GROUP BY c.category_id, c.name
            """)
            cat_stats = cursor.fetchall()

            # F2.3 (b) Authors with >= 2 books
            cursor.execute("""
                SELECT a.name AS author_name, COUNT(b.book_id) AS book_count
                FROM AUTHOR a
                JOIN BOOK b ON a.author_id = b.author_id
                GROUP BY a.author_id, a.name
                HAVING COUNT(b.book_id) >= 2
            """)
            prolific_authors = cursor.fetchall()

            # F2.3 (c) Library price summary
            cursor.execute("SELECT SUM(price) AS total_price, MIN(price) AS min_price, MAX(price) AS max_price FROM BOOK")
            price_summary = cursor.fetchone()

            # F2.4 (a) Unreturned loans
            cursor.execute("""
                SELECT l.loan_id, b.title AS book_title, m.name AS member_name, l.loan_date
                FROM LOAN l
                JOIN BOOK b ON l.book_id = b.book_id
                JOIN MEMBER m ON l.member_id = m.member_id
                WHERE l.return_date IS NULL
            """)
            unreturned_loans = cursor.fetchall()

            # F2.4 (b) Members who never borrowed
            cursor.execute("""
                SELECT m.member_id, m.name, m.email, m.join_date
                FROM MEMBER m
                LEFT JOIN LOAN l ON m.member_id = l.member_id
                WHERE l.loan_id IS NULL
            """)
            inactive_members = cursor.fetchall()

            # F2.4 (c) Books never borrowed
            cursor.execute("""
                SELECT b.book_id, b.title, b.price, b.publish_year
                FROM BOOK b
                LEFT JOIN LOAN l ON b.book_id = l.book_id
                WHERE l.loan_id IS NULL
            """)
            unborrowed_books = cursor.fetchall()

            # F2.5 (a) Top 3 most borrowed books
            cursor.execute("""
                SELECT b.title AS book_title, COUNT(l.loan_id) AS times_borrowed
                FROM BOOK b
                JOIN LOAN l ON b.book_id = l.book_id
                GROUP BY b.book_id, b.title
                ORDER BY times_borrowed DESC
                LIMIT 3
            """)
            top_books = cursor.fetchall()

            # F2.5 (b) Member with most loans
            cursor.execute("""
                SELECT m.name AS member_name, COUNT(l.loan_id) AS total_loans
                FROM MEMBER m
                JOIN LOAN l ON m.member_id = l.member_id
                GROUP BY m.member_id, m.name
                ORDER BY total_loans DESC
                LIMIT 1
            """)
            top_member = cursor.fetchone()

            # F2.6 (a) All authors with book count (including 0)
            cursor.execute("""
                SELECT a.name AS author_name, a.country, COUNT(b.book_id) AS book_count
                FROM AUTHOR a
                LEFT JOIN BOOK b ON a.author_id = b.author_id
                GROUP BY a.author_id, a.name, a.country
            """)
            all_authors_stats = cursor.fetchall()

            # F2.6 (b) Books where author & publisher share same country
            cursor.execute("""
                SELECT b.title AS book_title, a.name AS author_name, p.name AS publisher_name, a.country
                FROM BOOK b
                JOIN AUTHOR a ON b.author_id = a.author_id
                JOIN PUBLISHER p ON b.publisher_id = p.publisher_id
                WHERE a.country = p.country
            """)
            same_country_books = cursor.fetchall()

        return render_template('lab4_reports.html',
                               cat_stats=cat_stats,
                               prolific_authors=prolific_authors,
                               price_summary=price_summary,
                               unreturned_loans=unreturned_loans,
                               inactive_members=inactive_members,
                               unborrowed_books=unborrowed_books,
                               top_books=top_books,
                               top_member=top_member,
                               all_authors_stats=all_authors_stats,
                               same_country_books=same_country_books)
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)