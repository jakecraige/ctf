# Student Body (375)

> Author: syyntax
> We believe Lucia is trying to target a student taught by her SOCI424
> professor. How many students were taught by that professor in either term?
> Submit the number of students as well as the professor's first and last name
> concatenated.

The challenge is asking us to find all students who took _any_ course where the
instructor was the same as who taught Lucia's SOCI424 class.

A prerequisite to this challenge is to set up a local MySQL instance and import
the data provided from "Address Book". I solved this on Kali linux and with how
my database was configured I ran the following commands to set it up, you're
environment will likely be different.

```sh
# Start MySQL and create the database
$ service mysql start
$ mysql -u root
$ MariaDB [(none)]> CREATE DATABASE hacktober;
Query OK, 1 row affected (0.000 sec)
$ MariaDB [(none)]> exit

# Import provided data into the database
$ mysql -u root hacktober < shallowgraveu.sql

# Connect so we can execute queries
$ mysql -u root hacktober
MariaDB [hacktober]> show tables;
+---------------------+
| Tables_in_hacktober |
+---------------------+
| countries           |
| courses             |
| degree_types        |
| enrollments         |
| passwords           |
| payment_statuses    |
| programs            |
| roles               |
| roles_assigned      |
| states              |
| term_courses        |
| terms               |
| users               |
+---------------------+
13 rows in set (0.001 sec)
```

Now that the database is set up we can begin. First we find the course_id for
SOCI424 since we'll need it in our later queries.

```sql
MariaDB [hacktober]> select * from courses where title='SOCI424';

+-----------+---------+-------+----------------------------------------+------------------+-----------+
| course_id | title   | level | description                            | long_description | sem_hours |
+-----------+---------+-------+----------------------------------------+------------------+-----------+
|      6775 | SOCI424 | 0     | SOCI424 - Sociology of Death and Dying |                  |         3 |
+-----------+---------+-------+----------------------------------------+------------------+-----------+
1 row in set (0.001 sec)
```

We know Lucia is user_id 49 from an earlier challenge, so now we just need to
construct some queries to look up the solution. I decided to do this all at
once using Common Table Expressions (CTE) but you could also do this a step at
a time. This just made it easier to copy and paste the whole query with
modifications to any point easily.

```sql
with lucias_term_crs_id as (
  -- We fetch the term_crs_id for the Lucia's enrollment in the SOCI424 course
  -- so that we can then look up the professor.
  select term_crs_id from enrollments 
    where user_id=49 and term_crs_id IN (
      select term_crs_id from term_courses where course_id=6775
    )
), instructor as (
  -- Using the term_crs_id of the instructor we want to find students of, we
  -- query for them in the users table.
  select * from users where user_id IN (
    select instructor from term_courses where term_crs_id IN (select * from lucias_term_crs_id)
  )
), enrollments_with_instructor as (
  -- Look up all enrollments where the course is taught by the target instructor
  select enrollments.*, course_id, instructor from enrollments
    left join term_courses on enrollments.term_crs_id = term_courses.term_crs_id
    where term_courses.instructor in (select user_id from instructor)
)
-- Count up enrollments and include professor info for simple flag construction
select count(*), first, last from enrollments_with_instructor join instructor on 1=1;

+----------+--------+-----------+
| count(*) | first  | last      |
+----------+--------+-----------+
|      122 | CLAUDE | DARRACOTT |
+----------+--------+-----------+
1 row in set (0.002 sec)
```

Formatting the flag as described in the prompt: `flag{122_ClaudeDarracott}`
