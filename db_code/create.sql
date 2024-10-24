-- Создание таблицы positions
CREATE TABLE positions (
    position_id SERIAL PRIMARY KEY,
    title VARCHAR(100) NOT NULL UNIQUE,
    salary NUMERIC(10, 2) NOT NULL,
    description TEXT,
    requirements TEXT
);

-- Создание таблицы employees
CREATE TABLE employees (
    employee_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    middle_name VARCHAR(50),
    date_of_birth DATE,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20) UNIQUE NOT NULL,
    hire_date DATE NOT NULL,
    department_id INTEGER,
    position_id INTEGER NOT NULL,
    CONSTRAINT fk_position
        FOREIGN KEY(position_id)
        REFERENCES positions(position_id)
        ON DELETE SET NULL
);

-- Создание таблицы departments
CREATE TABLE departments (
    department_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    manager_id INTEGER UNIQUE,
    CONSTRAINT fk_manager
        FOREIGN KEY(manager_id)
        REFERENCES employees(employee_id)
        ON DELETE SET NULL
);

-- Теперь изменим employees, чтобы добавить ссылку на department_id
ALTER TABLE employees
    ADD CONSTRAINT fk_department
    FOREIGN KEY(department_id)
    REFERENCES departments(department_id)
    ON DELETE CASCADE;

-- Создание таблицы projects
CREATE TABLE projects (
    project_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    start_date DATE NOT NULL,
    end_date DATE
);

-- Создание таблицы employee_projects
CREATE TABLE employee_projects (
    employee_id INTEGER NOT NULL,
    project_id INTEGER NOT NULL,
    role VARCHAR(100),
    PRIMARY KEY (employee_id, project_id),
    CONSTRAINT fk_employee
        FOREIGN KEY(employee_id)
        REFERENCES employees(employee_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_project
        FOREIGN KEY(project_id)
        REFERENCES projects(project_id)
        ON DELETE CASCADE
);

-- Вставка данных в таблицу departments
INSERT INTO departments (name) VALUES
('IT'),
('HR'),
('Sales'),
('Marketing'),
('Finance');

-- Вставка данных в таблицу positions
INSERT INTO positions (title, salary, description, requirements) VALUES
('Software Engineer', 80000.00, 'Develop and maintain software.', 'Bachelor in CS, 3 years experience.'),
('HR Manager', 60000.00, 'Manage HR activities.', '5 years experience in HR.'),
('Sales Representative', 50000.00, 'Sell company products.', 'Strong communication skills.'),
('Marketing Specialist', 55000.00, 'Create marketing campaigns.', 'Experience in digital marketing.'),
('Financial Analyst', 70000.00, 'Analyze financial data.', 'Degree in finance.');

-- Вставка данных в таблицу employees
INSERT INTO employees (first_name, last_name, middle_name, date_of_birth, email, phone, hire_date, department_id, position_id) VALUES
('John', 'Doe', 'Michael', '1990-01-15', 'john.doe@example.com', '1234567890', '2020-05-10', 1, 1),
('Jane', 'Smith', 'Anne', '1985-06-20', 'jane.smith@example.com', '1234567891', '2019-09-01', 2, 2),
('Robert', 'Brown', 'James', '1992-03-10', 'robert.brown@example.com', '1234567892', '2021-02-15', 3, 3),
('Emily', 'Davis', 'Louise', '1987-07-25', 'emily.davis@example.com', '1234567893', '2018-11-30', 4, 4),
('Michael', 'Wilson', 'Thomas', '1995-12-05', 'michael.wilson@example.com', '1234567894', '2022-01-10', 5, 5);

-- Вставка данных в таблицу projects
INSERT INTO projects (name, description, start_date, end_date) VALUES
('Project A', 'Software development project.', '2023-01-01', '2023-06-30'),
('Project B', 'Marketing campaign.', '2022-05-15', '2022-12-31'),
('Project C', 'Sales improvement project.', '2023-07-01', '2023-12-31'),
('Project D', 'HR restructuring.', '2022-10-01', '2023-03-31');

-- Вставка данных в таблицу employee_projects
INSERT INTO employee_projects (employee_id, project_id, role) VALUES
(1, 1, 'Developer'),
(2, 2, 'HR Manager'),
(3, 3, 'Sales Lead'),
(4, 4, 'Marketing Lead'),
(5, 1, 'Financial Analyst'),
(1, 2, 'Developer');
