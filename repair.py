# Management of repair data
def add_to_repair(cursor, e_id, repair_date, repair_type, repair_time, querier_id, applying_id, repairing_id, r_id):
     cursor.execute("""INSERT INTO equipment_repair (e_id, repair_date, repair_type, repair_time, querier_id, applying_id, repairing_id, r_id) 
                      VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                     (e_id, repair_date, repair_type, repair_time, querier_id, applying_id, repairing_id, r_id))

def edit_of_repair(cursor, e_id, repair_date, repair_type, repair_time, querier_id, applying_id, repairing_id, r_id):
    cursor.execute("""UPDATE equipment_repair
                      SET repair_type = %s,
                          repair_time = %s,
                          querier_id = %s,
                          applying_id = %s,
                          repairing_id = %s,
                          r_id = %s
                      WHERE e_id = %s AND repair_date = %s""",
                     (repair_type, repair_time, querier_id, applying_id, repairing_id, r_id, e_id, repair_date))

def edit_of_repair_pk(cursor, old_e_id, old_repair_date, p_id, repair_date):
    cursor.execute("""UPDATE equipment_repair
                      SET e_id = %s,
                          repair_date = %s
                      WHERE e_id = %s AND repair_date = %s""", (p_id, repair_date, old_e_id, old_repair_date))


def delete_from_repair_by_id(cursor, e_id):
    cursor.execute("""DELETE FROM equipment_repair
                      WHERE e_id = %s""", (e_id,))

def delete_from_repair_by_pid(cursor, p_id):
    cursor.execute("""DELETE FROM equipment_repair
                      WHERE querier_id = %s OR applying_id = %s OR repairing_id = %s""", (p_id, p_id, p_id))

def delete_from_repair(cursor, e_id, part_name, repair_date):
    cursor.execute("""DELETE FROM equipment_repair
                      WHERE e_id = %s AND part_name = %s AND repair_date = %s""", (e_id, part_name, repair_date))


def add_to_document(cursor, r_id, part_name, date_of_buy, price):
    cursor.execute("""INSERT INTO repair_document (r_id, part_name, date_of_buy, price) 
                      VALUES (%s, %s, %s, %s)""",
                     (r_id, part_name, date_of_buy, price))

def edit_of_document(cursor, r_id, part_name, date_of_buy, price):
    cursor.execute("""UPDATE repair_document
                      SET price = %s
                      WHERE r_id = %s AND part_name = %s AND date_of_buy = %s""",
                     (price, r_id, part_name, date_of_buy))


def edit_of_document_pk(cursor, old_r_id, old_part_name, old_date_of_buy, r_id, part_name, date_of_buy):
    cursor.execute("""UPDATE repair_document
                      SET r_id = %s,
                          part_name = %s,
                          date_of_buy = %s
                      WHERE r_id = %s AND part_name = %s AND date_of_buy = %s""", 
                      (r_id, part_name, date_of_buy, old_r_id, old_part_name, old_date_of_buy))


def delete_from_document(cursor, r_id, part_name, date_of_buy):
    cursor.execute("""DELETE FROM repair_document
                      WHERE r_id = %s AND part_name = %s AND date_of_buy = %s""", (r_id, part_name, date_of_buy))
