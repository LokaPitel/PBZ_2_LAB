# Employee data management
def add_to_employee(cursor, surname, name, fathername, birthday_date, old, sex):
    cursor.execute("""INSERT INTO employee (surname, name, fathername, birthday_date, old, sex) 
                      VALUES (%s, %s, %s, %s, %s, %s)""", (surname, name, fathername, birthday_date, old, sex))


def edit_of_employee(cursor, p_id, surname, name, fathername, birthday_date, old, sex):
    cursor.execute("""UPDATE employee 
                      SET surname = %s,
                          name = %s,
                          fathername = %s,
                          birthday_date = %s,
                          old = %s,
                          sex = %s
                      WHERE p_id = %s""", (surname, name, fathername, birthday_date, old, sex, p_id))


def delete_from_employee(cursor, p_id):
    cursor.execute("""DELETE FROM employee
                      WHERE p_id = %s""", (p_id,))


def add_to_history(cursor, p_id, role, departament, date_of_start):
    cursor.execute("""INSERT INTO employee_history (p_id, role, departament, date_of_start) 
                      VALUES (%s, %s, %s, %s)""", (p_id, role, departament, date_of_start))


def edit_of_history(cursor, p_id, role, departament, date_of_start):
    cursor.execute("""UPDATE employee_history 
                      SET role = %s,
                          departament = %s,
                      WHERE p_id = %s AND date_of_start = %s""", (role, departament, p_id, date_of_start))


def delete_from_history(cursor, p_id, date_of_start):
    cursor.execute("""DELETE FROM employee_history
                      WHERE p_id = %s AND date_of_start = %s""", (p_id, date_of_start))


def delete_employee(cursor, p_id):
    cursor.execute("""INSERT INTO deleted_employee
                      VALUES (%s)""", (p_id,))


def undelete_employee(cursor, p_id):
    cursor.execute("""DELETE FROM deleted_employee
                      WHERE p_id = %s""", (p_id,))

