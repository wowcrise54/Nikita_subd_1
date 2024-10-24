from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length

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
