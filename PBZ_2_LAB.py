import mysql.connector
from equipment import *
from employee import *

if __name__ == '__main__':
    try:
        db = mysql.connector.connect(
            host = 'localhost',
            user = 'root',
            password = 'peta_loka',
            database = 'repair'
        )

        cursor = db.cursor();

      # edit_of_employee(cursor, 1, "Black", "John", "Stevenson", "1998-05-1", 24, "M")
        #add_to_history(cursor, 1, "HR specialist", "HR", "2022-01-5")

        delete_equipment(cursor, 1)

        db.commit()
        

    except mysql.connector.Error as err:
        print(err)
