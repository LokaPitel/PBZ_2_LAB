import mysql.connector
from equipment import *
from employee import *
from repair import *


def add_equipment_procedure(cursor, name, model, manufacturing_date, departament, date_of_start):
    cursor.execute("""
        SELECT e_id
        FROM equipment
        ORDER BY e_id DESC
        LIMIT 1
    """)

    result = cursor.fetchone()

    if (result == None):
        e_id = 1

    else:
        e_id = int(result[0]) + 1

    add_to_equipment(cursor, e_id, name, model, manufacturing_date)
    add_to_ownership(cursor, e_id, departament, date_of_start)

def add_employee_procedure(cursor, surname, name, fathername, birthday_date, old, sex,
                                   role, departament, date_of_start):
    cursor.execute("""
        SELECT p_id
        FROM employee
        ORDER BY p_id DESC
        LIMIT 1
    """)

    result = cursor.fetchone()

    if (result == None):
        p_id = 1

    else:
        p_id = int(result[0]) + 1

    add_to_employee(cursor, p_id, surname, name, fathername, birthday_date, old, sex)
    add_to_history(cursor, p_id, role, departament, date_of_start)

def get_count_of_equipment_by_departament(cursor, departament, name, last_year):
    cursor.execute("""
        SELECT COUNT(DISTINCT e.e_id)
        FROM equipment as e, equipment_ownership as eo
        WHERE e.e_id = eo.e_id AND eo.departament = %s AND e.name = %s
        AND eo.date_of_start BETWEEN DATE_SUB(%s, INTERVAL 3 YEAR) AND DATE(%s)""", (departament, name, last_year, last_year))

    return cursor.fetchone()[0]

def get_list_of_departament_employees(cursor, departament):
    cursor.execute("""
        SELECT surname, name, fathername, birthday_date
        FROM employee as e, employee_history as eh
        WHERE e.p_id = eh.p_id AND eh.departament = %s""", (departament, ))

    return cursor.fetchall()

def get_list_of_sex_old_employees(cursor, sex, old):
    cursor.execute("""
        SELECT surname, name, fathername, birthday_date
        FROM employee
        WHERE sex = %s AND old = %s""", (sex, old))

    return cursor.fetchall()

def get_the_repairiest_departament(cursor):
    cursor.execute("""
        SELECT e.e_id, eo.departament
        FROM equipment as e, equipment_ownership as eo
        WHERE e.e_id = eo.e_id AND 
    """)

if __name__ == '__main__':
    try:
        db = mysql.connector.connect(
            host = 'localhost',
            user = 'root',
            password = 'peta_loka',
            database = 'repair'
        )

        cursor = db.cursor(buffered=True)

        #add_equipment_procedure(cursor, "Freezer", "Athlon 40", "2016-06-5", "HR", "2022-11-27")
        #add_employee_procedure(cursor, "Apple", "Sam", "Jackson", "1998-02-17", 24, "M", "HR specialist", "HR", "2022-12-5")

        #edit_of_employee(cursor, 1, "White", "John", "Johnson", "1994-02-17", 28, "M")

        #edit_of_employee(cursor, 3, "Apple", "Sam", "Jackson", "1998-02-17", 24, "F")

        #print(get_list_of_sex_old_employees(cursor, "M", 24))

        print(get_count_of_equipment_by_departament(cursor, "HR", "Freezer", "2023-1-1"))

        db.commit()
        

    except mysql.connector.Error as err:
        print(err)
