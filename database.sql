CREATE TABLE IF NOT EXISTS urls (
    id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    name VARCHAR(255) UNIQUE NOT NULL,
    created_at DATE
);

CREATE TABLE IF NOT EXISTS url_checks (
    id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    url_id INT REFERENCES urls (id),
    status_code INT,
    h1 TEXT,
    title TEXT,
    description TEXT,
    created_at DATE
);
