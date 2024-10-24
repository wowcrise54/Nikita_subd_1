import os


class Config:
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:Tusson112@localhost/employees"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "default_secret_key"
