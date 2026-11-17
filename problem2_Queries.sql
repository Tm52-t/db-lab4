USE library;

-- F2.1 Search books (WHERE, LIKE, BETWEEN, ORDER BY)
SELECT b.book_id, b.title, b.price, b.publish_year, c.name AS category_name
FROM BOOK b
JOIN CATEGORY c ON b.category_id = c.category_id
WHERE b.title LIKE '%Crime%' 
  AND b.price BETWEEN 15 AND 20 
  AND b.category_id = 1
ORDER BY b.price ASC;

-- F2.2 Catalogue (JOIN)
SELECT b.book_id, b.title, b.price, b.publish_year, 
       a.name AS author_name, p.name AS publisher_name, c.name AS category_name
FROM BOOK b
JOIN AUTHOR a ON b.author_id = a.author_id
JOIN PUBLISHER p ON b.publisher_id = p.publisher_id
JOIN CATEGORY c ON b.category_id = c.category_id
ORDER BY b.book_id ASC;

-- F2.3 Reports (GROUP BY, HAVING, Aggregations)
-- (a) Number of books and average price of each category
SELECT c.name AS category_name, COUNT(b.book_id) AS total_books, AVG(b.price) AS avg_price
FROM CATEGORY c
LEFT JOIN BOOK b ON c.category_id = b.category_id
GROUP BY c.category_id, c.name;

-- (b) Authors who wrote at least 2 books
SELECT a.name AS author_name, COUNT(b.book_id) AS book_count
FROM AUTHOR a
JOIN BOOK b ON a.author_id = b.author_id
GROUP BY a.author_id, a.name
HAVING COUNT(b.book_id) >= 2;

-- (c) Total, smallest and largest price of the whole library
SELECT SUM(price) AS total_price, MIN(price) AS min_price, MAX(price) AS max_price
FROM BOOK;

-- F2.4 Loans (JOIN, LEFT JOIN)
-- (a) Loans not returned yet
SELECT l.loan_id, b.title AS book_title, m.name AS member_name, l.loan_date
FROM LOAN l
JOIN BOOK b ON l.book_id = b.book_id
JOIN MEMBER m ON l.member_id = m.member_id
WHERE l.return_date IS NULL;

-- (b) Members who never borrowed a book
SELECT m.member_id, m.name, m.email, m.join_date
FROM MEMBER m
LEFT JOIN LOAN l ON m.member_id = l.member_id
WHERE l.loan_id IS NULL;

-- (c) Books that were never borrowed
SELECT b.book_id, b.title, b.price, b.publish_year
FROM BOOK b
LEFT JOIN LOAN l ON b.book_id = l.book_id
WHERE l.loan_id IS NULL;

-- F2.5 Most borrowed (GROUP BY, ORDER BY, LIMIT)
-- Top 3 books with the most loans
SELECT b.title AS book_title, COUNT(l.loan_id) AS times_borrowed
FROM BOOK b
JOIN LOAN l ON b.book_id = l.book_id
GROUP BY b.book_id, b.title
ORDER BY times_borrowed DESC
LIMIT 3;

-- Member with the most loans
SELECT m.name AS member_name, COUNT(l.loan_id) AS total_loans
FROM MEMBER m
JOIN LOAN l ON m.member_id = l.member_id
GROUP BY m.member_id, m.name
ORDER BY total_loans DESC
LIMIT 1;

-- F2.6 Authors and books (LEFT JOIN, JOIN)
-- (a) Every author with number of books (including 0)
SELECT a.name AS author_name, a.country, COUNT(b.book_id) AS book_count
FROM AUTHOR a
LEFT JOIN BOOK b ON a.author_id = b.author_id
GROUP BY a.author_id, a.name, a.country;

-- (b) Books whose author and publisher come from the same country
SELECT b.title AS book_title, a.name AS author_name, p.name AS publisher_name, a.country
FROM BOOK b
JOIN AUTHOR a ON b.author_id = a.author_id
JOIN PUBLISHER p ON b.publisher_id = p.publisher_id
WHERE a.country = p.country;