# coding: utf-8
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()



class Course(db.Model):
    __tablename__ = 'course'

    stu_id = db.Column(db.ForeignKey('student.stu_id'), nullable=False)
    course_name = db.Column(db.String, primary_key=True)
    c_hours = db.Column('c_hours', db.Integer, nullable=False)

    stu = db.relationship('Student', primaryjoin='Course.stu_id == Student.stu_id', backref='courses')
    
t_result = db.Table(
    'result',
    db.Column('stu_id', db.ForeignKey('student.stu_id'), nullable=False),
    db.Column('stu_name', db.String, nullable=False),
    db.Column('t_marks', db.Integer, nullable=False),
    db.Column('o_marks', db.Integer, nullable=False),
    db.Column('c_hours', db.Integer, nullable=False),
    db.Column('gpa', db.Float(53)),
    db.Column('course_name', db.ForeignKey('course.course_name'), nullable=False)
)



class Student(db.Model):
    __tablename__ = 'student'

    stu_id = db.Column(db.Integer, primary_key=True)
    stu_name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String, nullable=False)
    password = db.Column('pass', db.String, nullable=False)



class Teacher(db.Model):
    __tablename__ = 'teacher'

    t_id = db.Column(db.Integer, primary_key=True)
    t_name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String, nullable=False)
    _pass = db.Column('pass', db.String, nullable=False)
