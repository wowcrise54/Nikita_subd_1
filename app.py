from flask import Flask, render_template, redirect, url_for, request
from config import Config
from models import db, Department, Employee, Position, Project, EmployeeProject
from forms import DepartmentForm, EmployeeForm
from flask_migrate import Migrate
import requests

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
migrate = Migrate(app, db)

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
    # Запрос для получения информации о сотруднике, его департаменте и должности
    employee = db.session.query(Employee).filter_by(employee_id=employee_id).first()
    department = db.session.query(Department).filter_by(department_id=employee.department_id).first()
    position = db.session.query(Position).filter_by(position_id=employee.position_id).first()

    # Запрос для получения всех проектов, в которых задействован сотрудник
    projects = db.session.query(Project, EmployeeProject).join(EmployeeProject).filter(EmployeeProject.employee_id == employee_id).all()

    # Отправляем данные в шаблон
    return render_template('employee_detail.html', employee=employee, department=department, position=position, projects=projects)

@app.route('/department/<int:department_id>/assign_manager', methods=['GET', 'POST'])
def assign_manager(department_id):
    department = Department.query.get_or_404(department_id)
    employees = Employee.query.all()  # Получаем список всех сотрудников
    
    if request.method == 'POST':
        manager_id = request.form.get('manager_id')
        department.manager_id = manager_id  # Назначаем нового начальника отдела
        db.session.commit()  # Сохраняем изменения в базе данных
        return redirect(url_for('department_detail', department_id=department_id))
    
    return render_template('assign_manager.html', department=department, employees=employees)

@app.route('/department/<int:department_id>')
def department_detail(department_id):
    department = Department.query.get_or_404(department_id)
    return render_template('department_details.html', department=department)

if __name__ == '__main__':
    app.run(debug=True)
