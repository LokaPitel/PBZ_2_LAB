# Employee data management
def add_to_employee(cursor, p_id, surname, name, fathername, birthday_date, old, sex):
    cursor.execute("""INSERT INTO employee (p_id, surname, name, fathername, birthday_date, old, sex) 
                      VALUES (%s, %s, %s, %s, %s, %s, %s)""", (p_id, surname, name, fathername, birthday_date, old, sex))


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
                          departament = %s
                      WHERE p_id = %s AND date_of_start = %s""", (role, departament, p_id, date_of_start))


def edit_of_history_pk(cursor, old_p_id, old_date_of_start, p_id, date_of_start):
    cursor.execute("""UPDATE employee_history
                      SET p_id = %s,
                          date_of_start = %s
                      WHERE p_id = %s AND date_of_start = %s""", (p_id, date_of_start, old_p_id, old_date_of_start))


def delete_from_history_by_id(cursor, p_id):
    cursor.execute("""DELETE FROM employee_history
                      WHERE p_id = %s""", (p_id,))


def delete_from_history(cursor, p_id, date_of_start):
    cursor.execute("""DELETE FROM employee_history
                      WHERE p_id = %s AND date_of_start = %s""", (p_id, date_of_start))


def delete_employee(cursor, p_id):
    cursor.execute("""INSERT INTO deleted_employee
                      VALUES (%s)""", (p_id,))


def edit_of_deleted_employee(cursor, old_p_id, new_p_id):
    cursor.execute("""UPDATE deleted_employee
                      SET p_id = %s
                      WHERE p_id = %s""", (new_p_id, old_p_id))


def undelete_employee(cursor, p_id):
    cursor.execute("""DELETE FROM deleted_employee
                      WHERE p_id = %s""", (p_id,))

