create table student(
	stu_id int not null,
	stu_name varchar(20) not null,
	email varchar not null,
	pass varchar not null
);

--QUERY
ALTER TABLE student ADD PRIMARY KEY (stu_id);

create table teacher(
	t_id int primary key,
	t_name varchar(20) not null,
	email varchar not null,
	pass varchar not null
);


drop table result;
select * from student;
select * from teacher;

create table result(
	stu_id int not null,
	stu_name varchar not null,
	t_marks int not null,
	o_marks int not null,
	c_hours float not null,
	gpa float ,
	course_name varchar not null		
);

--truncate result;


--QUERY

ALTER TABLE result ADD FOREIGN KEY (stu_id) REFERENCES student(stu_id);

create table course(
	stu_id int not null,
	foreign key (stu_id)
		references student(stu_id),
	course_name varchar,
	c_hours float not null
	);

select * from result;
--SELECT *  from course;

delete from result where stu_id = 2021648;

create table new_account(     -- TABLE FOR NEW-ACCOUNT
	stu_id int not null,
	foreign key (stu_id)
		references student(stu_id)

);


--delete from result;
select * from result;

CREATE OR REPLACE FUNCTION after_student_insert()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO new_account(stu_id)
    VALUES (NEW.stu_id);
	
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

--drop function after_student_insert();

--TRIGGER TO INSERT NEW STUDENT INTO NEW_ACCOUNT TABLE



CREATE TRIGGER after_student_insert_trigger
AFTER INSERT ON student
FOR EACH ROW
EXECUTE FUNCTION after_student_insert();

select * from new_account;

--drop TRIGGER after_student_insert_trigger on student;




CREATE OR REPLACE FUNCTION get_student_info(student_id INT)
RETURNS TABLE (
    stu_id INT,
    stu_name VARCHAR(20),
    email VARCHAR,
    t_marks INT,
    o_marks INT,
    c_hours FLOAT,
    gpa FLOAT,
    course_name VARCHAR
)
AS $$
BEGIN
    RETURN QUERY
	SELECT s.stu_id, s.stu_name, s.email, r.t_marks, r.o_marks, r.c_hours, r.gpa, r.course_name
    FROM student s
    JOIN result r ON s.stu_id = r.stu_id
    WHERE s.stu_id = student_id;
	
	
    RETURN;
END;
$$ LANGUAGE plpgsql;

--drop function get_student_info;


SELECT * FROM get_student_info();

-- VIEW FOR STUDENT RESULT
CREATE VIEW student_result_view AS
SELECT s.stu_id, s.stu_name, r.t_marks,r.o_marks,r.c_hours,r.gpa,r.course_name
FROM student as  s
full outer JOIN result as r
using (stu_id);

select * from student_result_view;

drop view student_result_view;

create table teacher_account(     -- TABLE FOR NEW-ACCOUNT--TEACHER
	t_id int not null,
	foreign key (t_id)
		references teacher(t_id)

);

CREATE OR REPLACE FUNCTION after_teacher_insert()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO teacher_account(t_id)
    VALUES (NEW.t_id);
	
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER after_teacher_insert_trigger
AFTER INSERT ON teacher
FOR EACH ROW
EXECUTE FUNCTION after_teacher_insert();

CREATE OR REPLACE FUNCTION calculate_cgpa()
  RETURNS TABLE (stu_id INT, stu_name VARCHAR(20), cgpa FLOAT)
AS $$
BEGIN
  RETURN QUERY
  SELECT r.stu_id, r.stu_name,
         (SUM(r.gpa * r.c_hours)) / SUM(r.c_hours) AS cgpa
  FROM result as r
  GROUP BY r.stu_id, r.stu_name;
END;
$$
LANGUAGE plpgsql;

drop function calculate_cgpa;


SELECT * FROM calculate_cgpa();



select count(*) as number_of_course,stu_id,sum(c_hours) as Total_credit_hours
from course
group by stu_id;





