from flask_sqlalchemy import SQLAlchemy
from flask import render_template
from flask import Flask, render_template, request
# from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Session
from sqlalchemy.sql import select
from xmodels import Student, t_result, Course, Teacher, db
from sqlalchemy import select
from flask import session
from sqlalchemy import text
import psycopg2

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:pgadmin@localhost:5432/srms'
# db = db(app)
db.init_app(app)


@app.route("/")
def home():
    return render_template("/home.html")


conn = psycopg2.connect(
    host='localhost',
    database='srms',
    user='postgres',
    password='pgadmin',
    port=5432
)
print('Connecting to the PostgreSQL database...')


@app.route("/student-login", methods=['GET', 'POST'])
def login1():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        student = Student.query.filter_by(
            stu_name=name, password=password).one()

        if student:
            print("logged in successfully")
            msg = "logged in successfully"
            return render_template("student-portal.html", msg=msg, name=name)

        else:
            print("Incorrect email or password")
            msg = "Incorrect email or password"

    return render_template("/student-login.html")


@app.route("/student-portal", methods=['GET', 'POST'])
def portal():
    name = session.get('stu_name', None)

    if request.method == 'POST':
        id = request.form['id']

        # Call the get_student_info function using SQLAlchemy ORM
        # result = db.session.execute(
        #     text("SELECT * FROM get_student_info({id})")
        # ).params(id=id).all()
        result = db.session.execute(
            text("SELECT * FROM get_student_info(:id)"),
            {"id": int(id)}
        ).all()
        print(result)
        if result:
            name = result[0].stu_name
            courses = []
            total_gpa = 0.0
            total_credit_hours = 0

            for row in result:
                t_marks = row.t_marks
                o_marks = row.o_marks
                gpa = row.gpa
                course = row.course_name
                c_hours = row.c_hours
                course_result = "Pass" if gpa >= 2.0 else "Fail"
                courses.append({
                    "course_name": course,
                    "t_marks": t_marks,
                    "o_marks": o_marks,
                    "gpa": gpa,
                    "course_result": course_result,
                    "credit_hours": c_hours
                })

                total_gpa += gpa * c_hours
                total_credit_hours += c_hours

            cgpa = round(total_gpa / total_credit_hours,
                         2) if total_credit_hours > 0 else 0.0

            return render_template("show_result.html", id=id, name=name, courses=courses, cgpa=cgpa)
        else:
            return render_template("student-portal.html", msg=f"No results found for {id}")

    return render_template("student-portal.html", name=name)


@app.route("/teacher-login", methods=['GET', 'POST'])  # Teacher login
def login2():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        # print(id,password)
        try:
            curr = conn.cursor()
            sql = f"select t_name,pass from teacher where t_name='{name}' and pass='{password}'"
            curr.execute(sql)
            res = curr.fetchall()
            print(res)
            conn.commit()

            # pass check
            if res:
                print("logged in successfully")

                return render_template("teach-update.html", name=name)

            else:
                print("Incorrect name or password")
                msg = "Incorrect name or password"
                return render_template("/teacher-login.html", msg=msg)

        except:
            conn.rollback()
            print("Error in login")
            msg = "An error occurred while logging in. Please try again."
            return render_template("/teacher-login.html", msg=msg)

    return render_template("/teacher-login.html")


@app.route("/teach-update", methods=['GET', 'POST'])  # Teacher_insert_marks
def result():
    if request.method == 'POST':
        id = request.form['id']
        name = request.form['name']
        t_marks = request.form['total-marks']
        o_marks = request.form['obtained-marks']
        gpa = request.form['gpa']
        course = request.form['course']
        c_hours = float(request.form['credit-hours'])
        print(id, name, t_marks, o_marks, gpa, course)

        curr = conn.cursor()
        sql = f"SELECT course_name, c_hours FROM course WHERE course_name = '{course}'"
        curr.execute(sql)
        result = curr.fetchone()

        if result is None:
            msg = "Course not registered"
            return render_template("/teach-update.html", msg=msg)

        course_name, course_credit_hours = result
        if c_hours != course_credit_hours:
            msg = f"The entered credit hours for {course_name} must be {course_credit_hours}"
            return render_template("/teach-update.html", msg=msg)

        sql = f"SELECT stu_id FROM result WHERE course_name = '{course}' AND c_hours = '{c_hours}'"
        curr.execute(sql)
        result = curr.fetchone()

        if result:
            msg = "Marks for this course have already been entered for this student ID."
            return render_template("/teach-update.html", msg=msg)
        else:
            query = "'" + id + "'" + "," + "'" + name + "'" + "," + "'" + t_marks + "'" + "," + "'" + \
                o_marks + "'" + "," + "'" + \
                    str(c_hours) + "'" + "," + "'" + \
                gpa + "'" + "," + "'" + course + "'"

            curr.execute(
                "insert into result(stu_id, stu_name, t_marks, o_marks, c_hours, gpa, course_name) values(" + query + ")")
            conn.commit()
            msg = "Data inserted successfully"

        return render_template("/teach-update.html", msg=msg)

    return render_template("teach-update.html", name=name)


@app.route("/show_result", methods=['GET'])
def show_results():

    return render_template("show_result.html")


@app.route("/course", methods=['GET', 'POST', 'DELETE'])
def course():
    if request.method == 'POST':
        id = request.form['id']
        course_name = request.form['course']
        c_hours = float(request.form['credit-hours'])

        curr = conn.cursor()

        # Check the total credit hours for the given id
        curr.execute(f"SELECT SUM(c_hours) FROM course WHERE stu_id='{id}'")
        total_credit_hours = float(curr.fetchone()[0] or 0)

        # Check if the total credit hours exceed the limit
        if total_credit_hours + c_hours > 18:
            msg = "You can't enter more than 18 credit hours."
            return render_template("course.html", msg=msg)

        sql = f"SELECT stu_id, course_name, c_hours FROM course WHERE stu_id='{id}' AND course_name='{course_name}'"
        curr.execute(sql)
        result = curr.fetchone()

        try:
            if result:
                msg = "This course is already registered."
                return render_template("course.html", msg=msg)
            else:
                query = f"'{id}', '{course_name}', '{c_hours}'"
                curr.execute(
                    "INSERT INTO course (stu_id, course_name, c_hours) VALUES (" + query + ")")
                conn.commit()
                msg = "Course registered successfully."
                return render_template("course.html", msg=msg)

        except:
            conn.rollback()
            msg = f"Student with ID '{id}' not found."
            return render_template("course.html", msg=msg)

    elif request.method == 'DELETE':
        id = request.form['id']
        course_name = request.form['unregister-course']

        curr = conn.cursor()

        # Check if the course is registered for the given student
        curr.execute(
            f"SELECT stu_id, course_name FROM course WHERE stu_id='{id}' AND course_name='{course_name}'"
        )
        result = curr.fetchone()

        try:
            if result:
                curr.execute(
                    f"DELETE FROM course WHERE stu_id='{id}' AND course_name='{course_name}'"
                    )
                conn.commit()
                msg = "Course unregistered successfully."
                return render_template("course.html", msg=msg)
            else:
                msg = "This course is not registered for the student."
                return render_template("course.html", msg=msg)

        except:
            conn.rollback()
            msg = f"Student with ID '{id}' not found."
            return render_template("course.html", msg=msg)

    return render_template("course.html")

@app.route("/student-register", methods=['GET', 'POST'])  # Student Register
def register1():
    if request.method == 'POST':
        id = request.form['id']
        full_name = request.form['full-name']
        email = request.form['email']
        password = request.form['password']
        print(id, full_name, email, password)

        query = "'" + id + "'" + "," + "'" + full_name + "'" + \
            "," + "'" + email + "'" + "," + "'" + password + "'"

        curr = conn.cursor()
        curr.execute(
            "insert into student(stu_id,stu_name,email,pass)values("+query+")")
        conn.commit()
        msg = "Account created successfully"

        return render_template("student-register.html", msg=msg)
    return render_template("student-register.html")


@app.route("/teacher-register", methods=['GET', 'POST'])  # Teacher register
def register2():
    if request.method == 'POST':
        id = request.form['id']
        full_name = request.form['full-name']
        email = request.form['email']
        password = request.form['password']

        print(id, full_name, email, password)
        query = "'" + id + "'" + "," + "'" + full_name + \
            "'"+"," + "'" + email+"'"+"," + "'" + password+"'"
        curr = conn.cursor()
        curr.execute(
            "insert into teacher(t_id,t_name,email,pass) values("+query+")")
        conn.commit()
        msg = "Account created successfully"

        return render_template("teacher-register.html", msg=msg)
    return render_template("teacher-register.html")


if __name__ == '__main__':
    app.secret_key = 'your_secret_key_here'
    # app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(debug=True)


# @app.route("/course", methods=['GET', 'POST'])  # COURSE REGISTER
# def course():
#     if request.method == 'POST':
#         id = request.form['id']
#         course_name = request.form['course']
#         c_hours = request.form['credit-hours']

#         curr = conn.cursor()
#         sql = f"SELECT stu_id, course_name,c_hours FROM course WHERE stu_id='{id}' AND course_name='{course_name}'"
#         curr.execute(sql)
#         result = curr.fetchone()

#         try:
#             if result:
#                 msg = "This course is already registered."
#                 return render_template("course.html", msg=msg)
#             else:
#                 query = "'" + id + "'" + "," + "'" + course_name + "'" + "," + "'" + c_hours + "'"
#                 curr.execute(
#                     "insert into course(stu_id,course_name,c_hours)values(" + query + ")")
#                 conn.commit()
#                 msg = "Course registered successfully"
#                 return render_template("course.html", msg=msg)

#         except:
#             conn.rollback()
#             msg = f"Student with id '{id}' not found ."
#             return render_template("course.html", msg=msg)

#     return render_template("course.html")
