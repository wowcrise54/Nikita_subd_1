from flask import Flask, render_template, redirect, url_for
from config import Config
from models import db, Department, Employee, Position
from forms import DepartmentForm, EmployeeForm
from flask_migrate import Migrate

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

if __name__ == '__main__':
    app.run(debug=True)