# Functions to manage equipment data
def add_to_equipment(cursor, name, model, manufacturing_date):
    cursor.execute("""INSERT INTO equipment (name, model, manufacturing_date) 
                      VALUES (%s, %s, %s)""", (name, model, manufacturing_date))


def edit_of_equipment(cursor, e_id, name, model, manufacturing_date):
    cursor.execute("""UPDATE equipment 
                      SET name = %s,
                          model = %s,
                          manufacturing_date = %s
                      WHERE e_id = %s""", (name, model, manufacturing_date, e_id))


def delete_from_equipment(cursor, e_id):
    cursor.execute("""DELETE FROM equipment
                      WHERE e_id = %s""", (e_id,))


def add_to_ownership(cursor, e_id, departament, date_of_start):
    cursor.execute("""INSERT INTO equipment_ownership (e_id, departament, date_of_start) 
                      VALUES (%s, %s, %s)""", (e_id, departament, date_of_start))


def edit_of_ownership(cursor, e_id, departament, date_of_start):
    cursor.execute("""UPDATE equipment_ownership
                      SET departament = %s
                      WHERE e_id = %s AND date_of_start = %s""", (departament, e_id, date_of_start))


def delete_from_ownership(cursor, e_id):
    cursor.execute("""DELETE FROM equipment_ownership
                      WHERE e_id = %s""", (e_id,))


def delete_equipment(cursor, e_id):
    cursor.execute("""INSERT INTO deleted_equipment
                      VALUES (%s)""", (e_id,))


def undelete_equipment(cursor, e_id):
    cursor.execute("""DELETE FROM deleted_equipment
                      WHERE e_id = %s""", (e_id,))