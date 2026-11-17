USE library;

-- 1. Authors (4 authors: 2 from Russia, 1 from Egypt, 1 with 0 books)
INSERT INTO AUTHOR (name, country) VALUES 
('Fyodor Dostoevsky', 'Russia'),
('Leo Tolstoy', 'Russia'),
('Ahmed Khaled Towfik', 'Egypt'),
('Haruki Murakami', 'Japan'); -- Author with 0 books

-- 2. Publishers (3 publishers: 1 from Russia to match Dostoevsky/Tolstoy)
INSERT INTO PUBLISHER (name, country) VALUES 
('Eksmo Publishing', 'Russia'),
('Dar El Shorouk', 'Egypt'),
('Penguin Classics', 'UK');

-- 3. Categories (3 categories)
INSERT INTO CATEGORY (name) VALUES 
('Classic Literature'),
('Sci-Fi & Horror'),
('Philosophy');

-- 4. Books (10 books: Dostoevsky has >= 2, prices include 15-20, Book 10 never borrowed)
INSERT INTO BOOK (title, price, publish_year, author_id, publisher_id, category_id) VALUES 
('Crime and Punishment', 18.50, 1866, 1, 1, 1),      -- Price 15-20, Author & Pub from Russia
('The Brothers Karamazov', 25.00, 1880, 1, 1, 3),    -- Dostoevsky book 2
('Notes from Underground', 14.00, 1864, 1, 3, 3),    -- Dostoevsky book 3
('War and Peace', 30.00, 1869, 2, 1, 1),             -- Tolstoy (Russia) + Eksmo (Russia)
('Anna Karenina', 22.00, 1878, 2, 3, 1),
('Utopia', 16.00, 2008, 3, 2, 2),                    -- Price 15-20
('Ma Waraa Al Tabiaa', 12.50, 1993, 3, 2, 2),
('The Idiot', 19.99, 1869, 1, 3, 1),                 -- Price 15-20
('The Death of Ivan Ilyich', 15.00, 1886, 2, 3, 3),  -- Price 15-20
('Snakes and Ladders', 17.50, 2005, 3, 2, 2);        -- Book 10: Never borrowed

-- 5. Members (5 members: Member 5 has 0 loans)
INSERT INTO MEMBER (name, email, join_date) VALUES 
('Taha Mohamed', 'taha@anu.edu.eg', '2026-01-10'),
('Noor Elhawary', 'noor@anu.edu.eg', '2026-01-15'),
('Omar Khaled', 'omar@anu.edu.eg', '2026-02-01'),
('Sara Ahmed', 'sara@anu.edu.eg', '2026-02-10'),
('Ali Mahmoud', 'ali@anu.edu.eg', '2026-03-01');      -- Member with 0 loans

-- 6. Loans (12 loans: includes unreturned loans where return_date IS NULL)
INSERT INTO LOAN (book_id, member_id, loan_date, return_date) VALUES 
(1, 1, '2026-09-01', '2026-09-10'),
(1, 2, '2026-09-15', '2026-09-25'),
(1, 3, '2026-10-01', NULL),         -- Unreturned loan (Book 1 borrowed 3 times)
(2, 1, '2026-09-05', '2026-09-12'),
(2, 4, '2026-10-05', NULL),         -- Unreturned loan (Book 2 borrowed 2 times)
(4, 1, '2026-09-10', '2026-09-20'), -- Member 1 has 3 loans so far
(6, 1, '2026-10-10', NULL),         -- Unreturned loan (Member 1 has 4 loans -> Most loans)
(6, 2, '2026-09-20', '2026-09-28'), -- Book 6 borrowed 2 times
(3, 2, '2026-10-12', NULL),         -- Unreturned loan
(5, 3, '2026-09-18', '2026-09-29'),
(7, 4, '2026-10-02', '2026-10-09'),
(8, 1, '2026-10-15', NULL);         -- Member 1 has 5 loans