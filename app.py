from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length
import requests
import os
from sqlalchemy import func

# Configuration
class Config:
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:Tusson112@localhost/employee_otdel"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "default_secret_key"


# Flask app and config
app = Flask(__name__)
app.config.from_object(Config)

# Database setup
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# Models
class Department(db.Model):
    __tablename__ = 'departments'
    department_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    manager_id = db.Column(db.Integer, db.ForeignKey('employees.employee_id'), unique=True)
    manager = db.relationship('Employee', backref='managed_department', foreign_keys=[manager_id])


class Position(db.Model):
    __tablename__ = 'positions'
    position_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False, unique=True)
    salary = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.Text)
    requirements = db.Column(db.Text)


class Employee(db.Model):
    __tablename__ = 'employees'
    employee_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    middle_name = db.Column(db.String(50))
    date_of_birth = db.Column(db.Date)
    email = db.Column(db.String(100), nullable=False, unique=True)
    phone = db.Column(db.String(20), nullable=False, unique=True)
    hire_date = db.Column(db.Date, nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.department_id'), nullable=False)
    position_id = db.Column(db.Integer, db.ForeignKey('positions.position_id'), nullable=False)
    position = db.relationship('Position', backref='employees')


class Project(db.Model):
    __tablename__ = 'projects'
    project_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)


class EmployeeProject(db.Model):
    __tablename__ = 'employee_projects'
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.employee_id'), primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.project_id'), primary_key=True)
    role = db.Column(db.String(100))


# Forms
class DepartmentForm(FlaskForm):
    name = StringField('Название департамента', validators=[DataRequired(), Length(max=100)])
    manager_id = SelectField('Менеджер', coerce=int)
    submit = SubmitField('Сохранить')


class EmployeeForm(FlaskForm):
    first_name = StringField('Имя', validators=[DataRequired()])
    last_name = StringField('Фамилия', validators=[DataRequired()])
    middle_name = StringField('Отчество')
    date_of_birth = DateField('Дата рождения', format='%Y-%m-%d')
    email = StringField('Электронная почта', validators=[DataRequired()])
    phone = StringField('Телефон', validators=[DataRequired()])
    hire_date = DateField('Дата найма', format='%Y-%m-%d')
    department_id = SelectField('Департамент', coerce=int)
    position_id = SelectField('Должность', coerce=int)
    submit = SubmitField('Сохранить')


# Routes
@app.route('/')
def index():
    departments = Department.query.all()
    employees = Employee.query.all()
    return render_template('index.html', departments=departments, employees=employees)


@app.route('/department/new', methods=['GET', 'POST'])
def new_department():
    form = DepartmentForm()
    form.manager_id.choices = [(e.employee_id, f'{e.first_name} {e.last_name}') for e in Employee.query.all()]
    if form.validate_on_submit():
        department = Department(name=form.name.data, manager_id=form.manager_id.data)
        db.session.add(department)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('department.html', form=form)


@app.route('/employee/new', methods=['GET', 'POST'])
def new_employee():
    form = EmployeeForm()
    form.department_id.choices = [(d.department_id, d.name) for d in Department.query.all()]
    form.position_id.choices = [(p.position_id, p.title) for p in Position.query.all()]
    if form.validate_on_submit():
        employee = Employee(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            middle_name=form.middle_name.data,
            date_of_birth=form.date_of_birth.data,
            email=form.email.data,
            phone=form.phone.data,
            hire_date=form.hire_date.data,
            department_id=form.department_id.data,
            position_id=form.position_id.data
        )
        db.session.add(employee)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('employee.html', form=form)


@app.route('/employee/<int:employee_id>')
def employee_detail(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    department = Department.query.get(employee.department_id)
    position = Position.query.get(employee.position_id)
    projects = db.session.query(Project, EmployeeProject).join(EmployeeProject).filter(EmployeeProject.employee_id == employee_id).all()

    return render_template('employee_detail.html', employee=employee, department=department, position=position, projects=projects)


@app.route('/department/<int:department_id>')
def department_details(department_id):
    department = Department.query.get_or_404(department_id)
    return render_template('department_details.html', department=department)


@app.route('/department/<int:department_id>/remove_manager', methods=['POST'])
def remove_manager(department_id):
    department = Department.query.get_or_404(department_id)
    if department.manager_id:
        department.manager_id = None
        db.session.commit()
        flash('Начальник отдела был снят с должности.')
    else:
        flash('В этом отделе нет назначенного начальника.')
    return redirect(url_for('department_details', department_id=department_id))


@app.route('/employee/<int:employee_id>/transfer', methods=['GET', 'POST'])
def transfer_employee(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    departments = Department.query.all()
    if employee.managed_department:
        flash('Нельзя перевести сотрудника, так как он является начальником отдела.')
        return redirect(url_for('employee_detail', employee_id=employee_id))
    if request.method == 'POST':
        new_department_id = request.form.get('new_department_id')
        employee.department_id = new_department_id
        db.session.commit()
        flash('Сотрудник успешно переведен.')
        return redirect(url_for('employee_detail', employee_id=employee_id))
    return render_template('transfer_employee.html', employee=employee, departments=departments)


@app.route('/department/<int:department_id>/assign_manager', methods=['GET', 'POST'])
def assign_manager(department_id):
    department = Department.query.get_or_404(department_id)
    employees = Employee.query.filter(Employee.managed_department == None).all()
    if request.method == 'POST':
        manager_id = request.form.get('manager_id')
        department.manager_id = manager_id
        db.session.commit()
        return redirect(url_for('department_details', department_id=department_id))
    return render_template('assign_manager.html', department=department, employees=employees)


@app.route('/department/<int:department_id>/employees')
def department_employees(department_id):
    department = Department.query.get_or_404(department_id)
    employees = Employee.query.filter_by(department_id=department_id).all()
    return render_template('department_employees.html', department=department, employees=employees)

@app.route('/employee/<int:employee_id>/edit', methods=['GET', 'POST'])
def edit_employee(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    form = EmployeeForm(obj=employee)

    form.department_id.choices = [(d.department_id, d.name) for d in Department.query.all()]
    form.position_id.choices = [(p.position_id, p.title) for p in Position.query.all()]

    if form.validate_on_submit():
        employee.first_name = form.first_name.data
        employee.last_name = form.last_name.data
        employee.middle_name = form.middle_name.data
        employee.date_of_birth = form.date_of_birth.data
        employee.email = form.email.data
        employee.phone = form.phone.data
        employee.hire_date = form.hire_date.data
        employee.department_id = form.department_id.data
        employee.position_id = form.position_id.data

        db.session.commit()
        flash('Информация о сотруднике обновлена!')
        return redirect(url_for('employee_detail', employee_id=employee.employee_id))
    
    return render_template('employee.html', form=form)

@app.route('/employee/<int:employee_id>/delete', methods=['POST'])
def delete_employee(employee_id):
    employee = Employee.query.get_or_404(employee_id)

    # Удаление сотрудника
    db.session.delete(employee)
    db.session.commit()

    flash('Сотрудник удалён!')
    return redirect(url_for('index'))

@app.route('/summary')
def summary():
    # Общее количество сотрудников
    total_employees = db.session.query(func.count(Employee.employee_id)).scalar()
    
    # Средняя зарплата всех сотрудников
    average_salary = db.session.query(func.avg(Position.salary)).scalar()

    # Количество проектов
    total_projects = db.session.query(func.count(Project.project_id)).scalar()

    # Передача данных в шаблон
    return render_template('summary.html', total_employees=total_employees, average_salary=average_salary, total_projects=total_projects)

@app.route('/employees', methods=['GET', 'POST'])
def employees():
    search_query = request.args.get('search', '')  # Получение поискового запроса
    sort_by = request.args.get('sort_by', 'last_name')  # Сортировка по умолчанию по фамилии
    order = request.args.get('order', 'asc')  # Порядок сортировки (по умолчанию по возрастанию)
    department_id = request.args.get('department_id', None)  # Получаем выбранный департамент

    # Фильтрация и поиск
    employees = Employee.query.filter(
        (Employee.first_name.ilike(f'%{search_query}%')) |
        (Employee.last_name.ilike(f'%{search_query}%')) |
        (Employee.email.ilike(f'%{search_query}%'))
    )

    if department_id:  # Фильтрация по департаменту
        employees = employees.filter(Employee.department_id == department_id)
    # Сортировка
    if sort_by == 'first_name':
        employees = employees.order_by(Employee.first_name.asc() if order == 'asc' else Employee.first_name.desc())
    elif sort_by == 'last_name':
        employees = employees.order_by(Employee.last_name.asc() if order == 'asc' else Employee.last_name.desc())
    elif sort_by == 'email':
        employees = employees.order_by(Employee.email.asc() if order == 'asc' else Employee.email.desc())

    # Получение результата
    employees = employees.all()
    departments = Department.query.all()

    return render_template('employees.html', employees=employees, search_query=search_query, sort_by=sort_by, order=order, departments=departments, department_id=department_id)


if __name__ == '__main__':
    app.run(debug=True)
