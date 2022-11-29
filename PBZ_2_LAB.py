from email.headerregistry import DateHeader
from sqlite3 import Cursor, connect
import sys
from PySide6.QtCore import Slot, QSize
from PySide6.QtWidgets import QApplication, QMainWindow, QDialog, QDialogButtonBox, QFormLayout, QHBoxLayout, QDateEdit, QLineEdit, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QWidget, QTabWidget, QLabel

import mysql.connector

from equipment import *
from employee import *
from repair import *


def add_equipment_procedure(cursor, name, model, manufacturing_date, departament, date_of_start):
    try:
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

    except mysql.connect.Error as err:
        print(err)

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
        SELECT t1.departament, COUNT(t1.e_id) as repair_count

        FROM

        equipment_repair as er,

        (SELECT eo1.e_id, eo1.departament, eo1.date_of_start as start, eo2.date_of_start as end
        FROM equipment_ownership as eo1, equipment_ownership as eo2
        WHERE eo1.e_id = eo2.e_id AND eo1.date_of_start < eo2.date_of_start
    
        GROUP BY eo1.date_of_start
        HAVING MAX(eo2.date_of_start)

        UNION

        SELECT eo1.e_id, eo1.departament, eo1.date_of_start as start, DATE_ADD(eo1.date_of_start, INTERVAL 1000 YEAR) as end
        FROM equipment_ownership as eo1, equipment_ownership as eo2
        WHERE eo1.e_id = eo2.e_id AND eo1.date_of_start = eo2.date_of_start
    
        GROUP BY eo1.e_id
        HAVING COUNT(eo1.e_id) = 1
        ) as t1

        WHERE er.e_id = t1.e_id AND repair_date BETWEEN start AND end
        GROUP BY departament
    """)

    result = cursor.fetchall()

    return max(result, key = lambda x: x[1])

def createTableWidget(cursor, table_name):
    table = QTableWidget()

    cursor.execute(f"SELECT * FROM {table_name}")

    result = cursor.fetchall()

    table.setRowCount(len(result))

    if (len(result) == 0):
        table.setColumnCount(1)

    else:
        table.setColumnCount(len(result[0]))
        
    cursor.execute(f"DESCRIBE {table_name}")

    heading_list = []

    for row in cursor.fetchall():
        heading_list.append(row[0])

    table.setColumnCount(len(heading_list))

    table.setHorizontalHeaderLabels(heading_list)
    table.adjustSize()

    for r_index, row in enumerate(result):
        for c_index, col in enumerate(row):
            table.setItem(r_index, c_index, QTableWidgetItem(str(col)))
       
    return table


#### EQUIPMENT ################

class ShowEquipment(QDialog):
    def __init__(self, db, parent=None,):
        super().__init__(parent)

        self.setWindowTitle("Equipment table")

        table = createTableWidget(db.cursor(buffered=True), "Equipment")

        layout = QVBoxLayout()
        layout.addWidget(table)

        self.setLayout(layout)


class AddEquipmentDialog(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Add new field to Equipment")

        self.db = db;

        dialog_layout = QVBoxLayout()
        
        layout = QFormLayout()

        self.name = QLineEdit()
        self.model = QLineEdit()
        self.date = QDateEdit()
        self.departament = QLineEdit()
        self.date_of_start = QDateEdit()

        self.date.setDisplayFormat('yyyy-MM-dd')
        self.date_of_start.setDisplayFormat('yyyy-MM-dd')

        button_layout = QHBoxLayout()

        apply_button = QPushButton("Apply")
        apply_button.clicked.connect(self.save_to_db)
        apply_button.show()

        button_layout.addWidget(apply_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.close_dialog)
        cancel_button.show()

        button_layout.addWidget(cancel_button)

        layout.addRow("Name: ", self.name)
        layout.addRow("Model: ", self.model)
        layout.addRow("Manufacturing date: ", self.date)
        layout.addRow("Departament: ", self.departament)
        layout.addRow("Date of start: ", self.date_of_start)
        
        dialog_layout.addLayout(layout)
        dialog_layout.addLayout(button_layout)

        self.setLayout(dialog_layout)

    def save_to_db(self):
        try:
            add_equipment_procedure(self.db.cursor(buffered=True), self.name.text(), self.model.text(), self.date.text(), self.departament.text(), self.date_of_start.text())
            self.db.commit()

            self.close()
        except mysql.connector.Error as err:
            print(err)

    def close_dialog(self):
        self.close()


class EditEquipmentDialog(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)

        self.db = db

        self.setWindowTitle("Edit field in Equipment")

        dialog_layout = QVBoxLayout()
        layout = QFormLayout()

        self.e_id = QLineEdit()
        self.name = QLineEdit()
        self.model = QLineEdit()
        self.date = QDateEdit()

        self.date.setDisplayFormat('yyyy-MM-dd')

        button_layout = QHBoxLayout()

        apply_button = QPushButton("Apply")
        apply_button.clicked.connect(self.save_to_db)
        apply_button.show()

        button_layout.addWidget(apply_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.close_dialog)
        cancel_button.show()

        button_layout.addWidget(cancel_button)

        layout.addRow("Id: ", self.e_id)
        layout.addRow("Name: ", self.name)
        layout.addRow("Model: ", self.model)
        layout.addRow("Manufacturing date: ", self.date)
        
        dialog_layout.addLayout(layout)
        dialog_layout.addLayout(button_layout)

        self.setLayout(dialog_layout)

    def save_to_db(self):
        try:
            edit_of_equipment(self.db.cursor(buffered=True), self.e_id.text(), self.name.text(), self.model.text(), self.date.text())
            self.db.commit()
            self.close()

        except mysql.connector.Error as err:
            print(err)

    def close_dialog(self):
        self.close()


class DeleteEquipmentDialog(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)

        self.db = db

        self.setWindowTitle("Delete from equipment")

        dialog_layout = QVBoxLayout()
        layout = QFormLayout()

        self.e_id = QLineEdit()

        button_layout = QHBoxLayout()

        apply_button = QPushButton("Apply")
        apply_button.clicked.connect(self.save_to_db)
        apply_button.show()

        button_layout.addWidget(apply_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.close_dialog)
        cancel_button.show()

        button_layout.addWidget(cancel_button)

        layout.addRow("Id: ", self.e_id)
        dialog_layout.addLayout(layout)
        dialog_layout.addLayout(button_layout)

        self.setLayout(dialog_layout)

    def save_to_db(self):
        try:
            delete_from_equipment(self.db.cursor(buffered=True), self.e_id.text())
            delete_from_ownership_by_id(self.db.cursor(buffered=True), self.e_id.text())
            delete_from_repair_by_id(self.db.cursor(buffered=True), self.e_id.text())
            self.db.commit()
            self.close()

        except mysql.connector.Error as err:
            print(err)

    def close_dialog(self):
        self.close()


#### EMPLOYE ###################

class ShowEmployee(QDialog):
    def __init__(self, db, parent=None,):
        super().__init__(parent)

        self.setWindowTitle("Employee table")

        table = createTableWidget(db.cursor(buffered=True), "employee")

        layout = QVBoxLayout()
        layout.addWidget(table)

        self.setLayout(layout)


class AddEmployeeDialog(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Add new field to Employee")

        self.db = db;

        dialog_layout = QVBoxLayout()
        
        layout = QFormLayout()

        self.surname = QLineEdit()
        self.name = QLineEdit()
        self.fathername = QLineEdit()
        self.birthday_date = QDateEdit()
        self.old = QLineEdit()
        self.sex = QLineEdit()
        self.role = QLineEdit()
        self.departament = QLineEdit()
        self.date_of_start = QDateEdit()

        self.birthday_date.setDisplayFormat('yyyy-MM-dd')
        self.date_of_start.setDisplayFormat('yyyy-MM-dd')

        button_layout = QHBoxLayout()

        apply_button = QPushButton("Apply")
        apply_button.clicked.connect(self.save_to_db)
        apply_button.show()

        button_layout.addWidget(apply_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.close_dialog)
        cancel_button.show()

        button_layout.addWidget(cancel_button)

        layout.addRow("Surname: ", self.surname)
        layout.addRow("Name: ", self.name)
        layout.addRow("Fathername: ", self.fathername)
        layout.addRow("Birthday date: ", self.birthday_date)
        layout.addRow("Old: ", self.old)
        layout.addRow("Sex: ", self.sex)
        layout.addRow("Role: ", self.role)
        layout.addRow("Departament: ", self.departament)
        layout.addRow("Date of start: ", self.date_of_start)
        
        dialog_layout.addLayout(layout)
        dialog_layout.addLayout(button_layout)

        self.setLayout(dialog_layout)

    def save_to_db(self):
        try:
            add_employee_procedure(self.db.cursor(buffered=True), self.surname.text(), self.name.text(), self.fathername.text(),
                                   self.birthday_date.text(), self.old.text(), self.sex.text(), self.role.text(),
                                   self.departament.text(), self.date_of_start.text())
            self.db.commit()

            self.close()
        except mysql.connector.Error as err:
            print(err)

    def close_dialog(self):
        self.close()


class EditEmployeeDialog(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Edit field of Employee")

        self.db = db;

        dialog_layout = QVBoxLayout()
        
        layout = QFormLayout()

        self.p_id = QLineEdit()
        self.surname = QLineEdit()
        self.name = QLineEdit()
        self.fathername = QLineEdit()
        self.birthday_date = QDateEdit()
        self.old = QLineEdit()
        self.sex = QLineEdit()
        self.role = QLineEdit()
 
        self.birthday_date.setDisplayFormat('yyyy-MM-dd')

        button_layout = QHBoxLayout()

        apply_button = QPushButton("Apply")
        apply_button.clicked.connect(self.save_to_db)
        apply_button.show()

        button_layout.addWidget(apply_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.close_dialog)
        cancel_button.show()

        button_layout.addWidget(cancel_button)

        layout.addRow("Id: ", self.p_id)
        layout.addRow("Surname: ", self.surname)
        layout.addRow("Name: ", self.name)
        layout.addRow("Fathername: ", self.fathername)
        layout.addRow("Birthday date: ", self.birthday_date)
        layout.addRow("Old: ", self.old)
        layout.addRow("Sex: ", self.sex)
        layout.addRow("Role: ", self.role)
        
        dialog_layout.addLayout(layout)
        dialog_layout.addLayout(button_layout)

        self.setLayout(dialog_layout)


    def save_to_db(self):
        try:
            edit_of_employee(self.db.cursor(buffered=True), self.p_id.text(),
                             self.surname.text(), self.name.text(), self.fathername.text(),
                                   self.birthday_date.text(), self.old.text(), self.sex.text())
            self.db.commit()

            self.close()
        except mysql.connector.Error as err:
            print(err)

    def close_dialog(self):
        self.close()


class DeleteEmployeeDialog(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)

        self.db = db
        self.setWindowTitle("Delete from employee")

        dialog_layout = QVBoxLayout()
        layout = QFormLayout()

        self.p_id = QLineEdit()

        button_layout = QHBoxLayout()

        apply_button = QPushButton("Apply")
        apply_button.clicked.connect(self.save_to_db)
        apply_button.show()

        button_layout.addWidget(apply_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.close_dialog)
        cancel_button.show()

        button_layout.addWidget(cancel_button)

        layout.addRow("Id: ", self.p_id)
        dialog_layout.addLayout(layout)
        dialog_layout.addLayout(button_layout)

        self.setLayout(dialog_layout)

    def save_to_db(self):
        try:
            delete_from_employee(self.db.cursor(buffered=True), self.p_id.text())
            delete_from_history_by_id(self.db.cursor(buffered=True), self.p_id.text())
            delete_from_repair_by_pid(self.db.cursor(buffered=True), self.p_id.text())
            self.db.commit()
            self.close()

        except mysql.connector.Error as err:
            print(err)

    def close_dialog(self):
        self.close()

#### EMPLOYEE HISTORY #########

class ShowEmployeeHistory(QDialog):
    def __init__(self, db, parent=None,):
        super().__init__(parent)

        self.setWindowTitle("Employee history table")

        table = createTableWidget(db.cursor(buffered=True), "employee_history")

        layout = QVBoxLayout()
        layout.addWidget(table)

        self.setLayout(layout)


class AddEmployeeHistoryDialog(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Add new field to Employee history")

        self.db = db;

        dialog_layout = QVBoxLayout()
        
        layout = QFormLayout()

        self.p_id = QLineEdit()
        self.role = QLineEdit()
        self.departament = QLineEdit()
        self.date_of_start = QDateEdit()

        self.date_of_start.setDisplayFormat('yyyy-MM-dd')

        button_layout = QHBoxLayout()

        apply_button = QPushButton("Apply")
        apply_button.clicked.connect(self.save_to_db)
        apply_button.show()

        button_layout.addWidget(apply_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.close_dialog)
        cancel_button.show()

        button_layout.addWidget(cancel_button)

        layout.addRow("Id: ", self.p_id)
        layout.addRow("Role: ", self.role)
        layout.addRow("Departament: ", self.departament)
        layout.addRow("Date of start: ", self.date_of_start)
        
        dialog_layout.addLayout(layout)
        dialog_layout.addLayout(button_layout)

        self.setLayout(dialog_layout)

    def save_to_db(self):
        try:
            add_to_history(self.db.cursor(buffered=True), self.p_id.text(), self.role.text(), self.departament.text(),
                           self.date_of_start.text())

            self.db.commit()

            self.close()
        except mysql.connector.Error as err:
            print(err)

    def close_dialog(self):
        self.close()


class EditEmployeeHistoryDialog(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Edit field of Employee history")

        self.db = db;

        dialog_layout = QVBoxLayout()
        
        layout = QFormLayout()

        self.p_id = QLineEdit()
        self.role = QLineEdit()
        self.departament = QLineEdit()
        self.date_of_start = QDateEdit()

        self.date_of_start.setDisplayFormat('yyyy-MM-dd')

        button_layout = QHBoxLayout()

        apply_button = QPushButton("Apply")
        apply_button.clicked.connect(self.save_to_db)
        apply_button.show()

        button_layout.addWidget(apply_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.close_dialog)
        cancel_button.show()

        button_layout.addWidget(cancel_button)

        layout.addRow("Id: ", self.p_id)
        layout.addRow("Role: ", self.role)
        layout.addRow("Departament: ", self.departament)
        layout.addRow("Date of start: ", self.date_of_start)
        
        dialog_layout.addLayout(layout)
        dialog_layout.addLayout(button_layout)

        self.setLayout(dialog_layout)

    def save_to_db(self):
        try:
            edit_of_history(self.db.cursor(buffered=True), self.p_id.text(), self.role.text(), self.departament.text(),
                           self.date_of_start.text())

            self.db.commit()
            self.close()

        except mysql.connector.Error as err:
            print(err)

    def close_dialog(self):
        self.close()


class DeleteEmployeeHistoryDialog(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Delete field of Employee history")

        self.db = db;

        dialog_layout = QVBoxLayout()
        
        layout = QFormLayout()

        self.p_id = QLineEdit()
        self.date_of_start = QDateEdit()

        self.date_of_start.setDisplayFormat('yyyy-MM-dd')

        button_layout = QHBoxLayout()

        apply_button = QPushButton("Apply")
        apply_button.clicked.connect(self.save_to_db)
        apply_button.show()

        button_layout.addWidget(apply_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.close_dialog)
        cancel_button.show()

        button_layout.addWidget(cancel_button)

        layout.addRow("Id: ", self.p_id)
        layout.addRow("Date of start: ", self.date_of_start)
        
        dialog_layout.addLayout(layout)
        dialog_layout.addLayout(button_layout)

        self.setLayout(dialog_layout)

    def save_to_db(self):
        try:
            delete_from_history(self.db.cursor(buffered=True), self.p_id.text(), self.date_of_start.text())

            self.db.commit()
            self.close()

        except mysql.connector.Error as err:
            print(err)

    def close_dialog(self):
        self.close()


#### EQUIPMENT OWNERSHIP ######

class ShowEquipmentOwnership(QDialog):
    def __init__(self, db, parent=None,):
        super().__init__(parent)

        self.setWindowTitle("Equipment ownership table")

        table = createTableWidget(db.cursor(buffered=True), "equipment_ownership")

        layout = QVBoxLayout()
        layout.addWidget(table)

        self.setLayout(layout)


class AddEquipmentOwnership(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Add new field to Equipment ownership")

        self.db = db;

        dialog_layout = QVBoxLayout()
        
        layout = QFormLayout()

        self.e_id = QLineEdit()
        self.departament = QLineEdit()
        self.date_of_start = QDateEdit()

        self.date_of_start.setDisplayFormat('yyyy-MM-dd')

        button_layout = QHBoxLayout()

        apply_button = QPushButton("Apply")
        apply_button.clicked.connect(self.save_to_db)
        apply_button.show()

        button_layout.addWidget(apply_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.close_dialog)
        cancel_button.show()

        button_layout.addWidget(cancel_button)

        layout.addRow("Id: ", self.e_id)
        layout.addRow("Departament: ", self.departament)
        layout.addRow("Date of start: ", self.date_of_start)
        
        dialog_layout.addLayout(layout)
        dialog_layout.addLayout(button_layout)

        self.setLayout(dialog_layout)

    def save_to_db(self):
        try:
            add_to_ownership(self.db.cursor(buffered=True), self.e_id.text(), self.departament.text(),
                           self.date_of_start.text())

            self.db.commit()

            self.close()
        except mysql.connector.Error as err:
            print(err)

    def close_dialog(self):
        self.close()


class EditEquipmentOwnership(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Add new field to Equipment ownership")

        self.db = db;

        dialog_layout = QVBoxLayout()
        
        layout = QFormLayout()

        self.e_id = QLineEdit()
        self.departament = QLineEdit()
        self.date_of_start = QDateEdit()

        self.date_of_start.setDisplayFormat('yyyy-MM-dd')

        button_layout = QHBoxLayout()

        apply_button = QPushButton("Apply")
        apply_button.clicked.connect(self.save_to_db)
        apply_button.show()

        button_layout.addWidget(apply_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.close_dialog)
        cancel_button.show()

        button_layout.addWidget(cancel_button)

        layout.addRow("Id: ", self.e_id)
        layout.addRow("Departament: ", self.departament)
        layout.addRow("Date of start: ", self.date_of_start)
        
        dialog_layout.addLayout(layout)
        dialog_layout.addLayout(button_layout)

        self.setLayout(dialog_layout)

    def save_to_db(self):
        try:
            edit_of_ownership(self.db.cursor(buffered=True), self.e_id.text(), self.departament.text(),
                           self.date_of_start.text())

            self.db.commit()
            self.close()

        except mysql.connector.Error as err:
            print(err)

    def close_dialog(self):
        self.close()


class DeleteEquipmentOwnership(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Edit field of Equipment ownership")

        self.db = db;

        dialog_layout = QVBoxLayout()
        
        layout = QFormLayout()

        self.e_id = QLineEdit()
        self.date_of_start = QDateEdit()

        self.date_of_start.setDisplayFormat('yyyy-MM-dd')

        button_layout = QHBoxLayout()

        apply_button = QPushButton("Apply")
        apply_button.clicked.connect(self.save_to_db)
        apply_button.show()

        button_layout.addWidget(apply_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.close_dialog)
        cancel_button.show()

        button_layout.addWidget(cancel_button)

        layout.addRow("Id: ", self.e_id)
        layout.addRow("Date of start: ", self.date_of_start)
        
        dialog_layout.addLayout(layout)
        dialog_layout.addLayout(button_layout)

        self.setLayout(dialog_layout)

    def save_to_db(self):
        try:
            delete_from_ownership(self.db.cursor(buffered=True), self.e_id.text(), self.date_of_start.text())

            self.db.commit()
            self.close()

        except mysql.connector.Error as err:
            print(err)

    def close_dialog(self):
        self.close()

#### EQUIPMENT REPAIR ##########

class ShowEquipmentRepair(QDialog):
    def __init__(self, db, parent=None,):
        super().__init__(parent)

        self.setWindowTitle("Equipment repair table")

        table = createTableWidget(db.cursor(buffered=True), "equipment_repair")

        layout = QVBoxLayout()
        layout.addWidget(table)

        self.setLayout(layout)


class AddEquipmentRepair(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Add new field to Equipment repair")

        self.db = db

        dialog_layout = QVBoxLayout()
        
        layout = QFormLayout()

        self.e_id = QLineEdit()
        self.repair_date = QDateEdit()
        self.repair_type = QLineEdit()
        self.repair_time = QLineEdit()
        self.querier_id = QLineEdit()
        self.applying_id = QLineEdit()
        self.repairing_id = QLineEdit()
        #self.r_id = QLineEdit()

        self.repair_date.setDisplayFormat('yyyy-MM-dd')

        button_layout = QHBoxLayout()

        apply_button = QPushButton("Apply")
        apply_button.clicked.connect(self.save_to_db)
        apply_button.show()

        button_layout.addWidget(apply_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.close_dialog)
        cancel_button.show()

        button_layout.addWidget(cancel_button)

        layout.addRow("Id: ", self.e_id)
        layout.addRow("Repair date: ", self.repair_date)
        layout.addRow("Repair type: ", self.repair_type)
        layout.addRow("Repair time: ", self.repair_time)
        layout.addRow("Querier id: ", self.querier_id)
        layout.addRow("Applying id: ", self.applying_id)
        layout.addRow("Repairing id: ", self.repairing_id)
        #layout.addRow("Document id: ", self.repairing_id)
        
        dialog_layout.addLayout(layout)
        dialog_layout.addLayout(button_layout)

        self.setLayout(dialog_layout)

    def save_to_db(self):
        try:
            add_to_repair(self.db.cursor(buffered=True), self.e_id.text(), self.repair_date.text(), self.repair_type.text(),
                          self.repair_time.text(), self.querier_id.text(), self.applying_id.text(), self.repairing_id.text(), 0)

            self.db.commit()

            self.close()
        except mysql.connector.Error as err:
            print(err)

    def close_dialog(self):
        self.close()


class EditEquipmentRepair(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Edit field of Equipment repair")

        self.db = db

        dialog_layout = QVBoxLayout()
        
        layout = QFormLayout()

        self.e_id = QLineEdit()
        self.repair_date = QDateEdit()
        self.repair_type = QLineEdit()
        self.repair_time = QLineEdit()
        self.querier_id = QLineEdit()
        self.applying_id = QLineEdit()
        self.repairing_id = QLineEdit()
        self.r_id = QLineEdit()

        self.repair_date.setDisplayFormat('yyyy-MM-dd')

        button_layout = QHBoxLayout()

        apply_button = QPushButton("Apply")
        apply_button.clicked.connect(self.save_to_db)
        apply_button.show()

        button_layout.addWidget(apply_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.close_dialog)
        cancel_button.show()

        button_layout.addWidget(cancel_button)

        layout.addRow("Id: ", self.e_id)
        layout.addRow("Repair date: ", self.repair_date)
        layout.addRow("Repair type: ", self.repair_type)
        layout.addRow("Repair time: ", self.repair_time)
        layout.addRow("Querier id: ", self.querier_id)
        layout.addRow("Applying id: ", self.applying_id)
        layout.addRow("Repairing id: ", self.repairing_id)
        layout.addRow("Document id: ", self.r_id)
        
        dialog_layout.addLayout(layout)
        dialog_layout.addLayout(button_layout)

        self.setLayout(dialog_layout)

    def save_to_db(self):
        try:
            edit_of_repair(self.db.cursor(buffered=True), self.e_id.text(), self.repair_date.text(), self.repair_type.text(),
                           self.repair_time.text(), self.querier_id.text(), self.applying_id.text(), self.repairing_id.text(),
                           self.r_id.text())

            self.db.commit()

            self.close()
        except mysql.connector.Error as err:
            print(err)

    def close_dialog(self):
        self.close()


class DeleteEquipmentRepair(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Delete field of Equipment repair")

        self.db = db;

        dialog_layout = QVBoxLayout()
        
        layout = QFormLayout()

        self.e_id = QLineEdit()
        self.repair_date = QDateEdit()

        self.repair_date.setDisplayFormat('yyyy-MM-dd')

        button_layout = QHBoxLayout()

        apply_button = QPushButton("Apply")
        apply_button.clicked.connect(self.save_to_db)
        apply_button.show()

        button_layout.addWidget(apply_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.close_dialog)
        cancel_button.show()

        button_layout.addWidget(cancel_button)

        layout.addRow("Id: ", self.e_id)
        layout.addRow("Repair date: ", self.repair_date)
        
        dialog_layout.addLayout(layout)
        dialog_layout.addLayout(button_layout)

        self.setLayout(dialog_layout)

    def save_to_db(self):
        try:
            delete_from_repair(self.db.cursor(buffered=True), self.e_id.text(), self.repair_date.text())

            self.db.commit()
            self.close()

        except mysql.connector.Error as err:
            print(err)

    def close_dialog(self):
        self.close()

#### REPAIR DOCUMENT ###########

class ShowRepairDocument(QDialog):
    def __init__(self, db, parent=None,):
        super().__init__(parent)

        self.setWindowTitle("Repair document table")

        table = createTableWidget(db.cursor(buffered=True), "repair_document")

        layout = QVBoxLayout()
        layout.addWidget(table)

        self.setLayout(layout)


class AddRepairDocument(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Add new field to Repair document")

        self.db = db

        dialog_layout = QVBoxLayout()
        
        layout = QFormLayout()

        self.r_id = QLineEdit()
        self.part_name = QLineEdit()
        self.date_of_buy = QDateEdit()
        self.price = QLineEdit()

        self.date_of_buy.setDisplayFormat('yyyy-MM-dd')

        button_layout = QHBoxLayout()

        apply_button = QPushButton("Apply")
        apply_button.clicked.connect(self.save_to_db)
        apply_button.show()

        button_layout.addWidget(apply_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.close_dialog)
        cancel_button.show()

        button_layout.addWidget(cancel_button)

        layout.addRow("Id: ", self.r_id)
        layout.addRow("Part name: ", self.part_name)
        layout.addRow("Date of buy: ", self.date_of_buy)
        layout.addRow("Price: ", self.price)
        
        dialog_layout.addLayout(layout)
        dialog_layout.addLayout(button_layout)

        self.setLayout(dialog_layout)

    def save_to_db(self):
        try:
            add_to_document(self.db.cursor(buffered=True), self.r_id.text(), self.part_name.text(), self.date_of_buy.text(),
                            self.price.text())

            self.db.commit()

            self.close()
        except mysql.connector.Error as err:
            print(err)

    def close_dialog(self):
        self.close()


class EditRepairDocument(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Edit field of Repair document")

        self.db = db

        dialog_layout = QVBoxLayout()
        
        layout = QFormLayout()

        self.e_id = QLineEdit()
        self.repair_date = QDateEdit()
        self.repair_type = QLineEdit()
        self.repair_time = QLineEdit()
        self.querier_id = QLineEdit()
        self.applying_id = QLineEdit()
        self.repairing_id = QLineEdit()
        self.r_id = QLineEdit()

        self.repair_date.setDisplayFormat('yyyy-MM-dd')

        button_layout = QHBoxLayout()

        apply_button = QPushButton("Apply")
        apply_button.clicked.connect(self.save_to_db)
        apply_button.show()

        button_layout.addWidget(apply_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.close_dialog)
        cancel_button.show()

        button_layout.addWidget(cancel_button)

        layout.addRow("Id: ", self.e_id)
        layout.addRow("Repair date: ", self.repair_date)
        layout.addRow("Repair type: ", self.repair_type)
        layout.addRow("Repair time: ", self.repair_time)
        layout.addRow("Querier id: ", self.querier_id)
        layout.addRow("Applying id: ", self.applying_id)
        layout.addRow("Repairing id: ", self.repairing_id)
        layout.addRow("Document id: ", self.r_id)
        
        dialog_layout.addLayout(layout)
        dialog_layout.addLayout(button_layout)

        self.setLayout(dialog_layout)

    def save_to_db(self):
        try:
            edit_of_repair(self.db.cursor(buffered=True), self.e_id.text(), self.repair_date.text(), self.repair_type.text(),
                           self.repair_time.text(), self.querier_id.text(), self.applying_id.text(), self.repairing_id.text(),
                           self.r_id.text())

            self.db.commit()

            self.close()
        except mysql.connector.Error as err:
            print(err)

    def close_dialog(self):
        self.close()


class DeleteRepairDocument(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Edit field of Repair document")

        self.db = db;

        dialog_layout = QVBoxLayout()
        
        layout = QFormLayout()

        self.e_id = QLineEdit()
        self.repair_date = QDateEdit()

        self.repair_date.setDisplayFormat('yyyy-MM-dd')

        button_layout = QHBoxLayout()

        apply_button = QPushButton("Apply")
        apply_button.clicked.connect(self.save_to_db)
        apply_button.show()

        button_layout.addWidget(apply_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.close_dialog)
        cancel_button.show()

        button_layout.addWidget(cancel_button)

        layout.addRow("Id: ", self.e_id)
        layout.addRow("Repair date: ", self.repair_date)
        
        dialog_layout.addLayout(layout)
        dialog_layout.addLayout(button_layout)

        self.setLayout(dialog_layout)

    def save_to_db(self):
        try:
            delete_from_repair(self.db.cursor(buffered=True), self.e_id.text(), self.repair_date.text())

            self.db.commit()
            self.close()

        except mysql.connector.Error as err:
            print(err)

    def close_dialog(self):
        self.close()

################################

###############################
## FUNCTIONS ##################
###############################

class CountOfEquipment(QDialog):
    def __init__(self, db, parent=None,):
        super().__init__(parent)

        self.setWindowTitle("Count of equipment")
        self.db = db

        self.departament = QLineEdit()
        self.name = QLineEdit()
        self.last_year = QDateEdit()


        dialog_layout = QVBoxLayout()
        layout = QFormLayout()

        self.last_year.setDisplayFormat('yyyy-MM-dd')

        button_layout = QHBoxLayout()

        apply_button = QPushButton("Apply")
        apply_button.clicked.connect(self.slot_show_count)
        apply_button.show()

        button_layout.addWidget(apply_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.close_dialog)
        cancel_button.show()

        button_layout.addWidget(cancel_button)

        layout.addRow("Departament: ", self.departament)
        layout.addRow("Name: ", self.name)
        layout.addRow("Last year: ", self.last_year)

        dialog_layout.addLayout(layout)
        dialog_layout.addLayout(button_layout)

        self.setLayout(dialog_layout)


    def slot_show_count(self):
        dialog = ShowEquipmentCountOfEquipment(self.db, self.departament.text(), self.name.text(), self.last_year.text())
        dialog.exec()

    def close_dialog(self):
        self.close()

class ShowEquipmentCountOfEquipment(QDialog):
    def __init__(self, db, departament, name, last_year, parent=None,):
        super().__init__(parent)

        self.setWindowTitle("Equipment repair table")

        table = QTableWidget()

        cursor = db.cursor(buffered=True)

        cursor.execute("""
        SELECT COUNT(DISTINCT e.e_id)
        FROM equipment as e, equipment_ownership as eo
        WHERE e.e_id = eo.e_id AND eo.departament = %s AND e.name = %s
        AND eo.date_of_start BETWEEN DATE_SUB(%s, INTERVAL 3 YEAR) AND DATE(%s)""", (departament, name, last_year, last_year))

        result = cursor.fetchall()

        table.setRowCount(len(result))

        if (len(result) == 0):
            table.setColumnCount(1)

        else:
            table.setColumnCount(len(result[0]))
        
        #cursor.execute(f"DESCRIBE {}")

        heading_list = ["Count"]

        table.setColumnCount(len(heading_list))

        table.setHorizontalHeaderLabels(heading_list)
        table.adjustSize()

        for r_index, row in enumerate(result):
            for c_index, col in enumerate(row):
                table.setItem(r_index, c_index, QTableWidgetItem(str(col)))
       

        layout = QVBoxLayout()
        layout.addWidget(table)

        self.setLayout(layout)

class EmployeesByDepartament(QDialog):
    def __init__(self, db, parent=None,):
        super().__init__(parent)

        self.setWindowTitle("Count of equipment")
        self.db = db

        self.departament = QLineEdit()

        dialog_layout = QVBoxLayout()
        layout = QFormLayout()

        #self.last_year.setDisplayFormat('yyyy-MM-dd')

        button_layout = QHBoxLayout()

        apply_button = QPushButton("Apply")
        apply_button.clicked.connect(self.slot_show_count)
        apply_button.show()

        button_layout.addWidget(apply_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.close_dialog)
        cancel_button.show()

        button_layout.addWidget(cancel_button)

        layout.addRow("Departament: ", self.departament)

        dialog_layout.addLayout(layout)
        dialog_layout.addLayout(button_layout)

        self.setLayout(dialog_layout)


    def slot_show_count(self):
        dialog = ShowEmployeeByDepartament(self.db, self.departament.text())
        dialog.exec()

    def close_dialog(self):
        self.close()

class ShowEmployeeByDepartament(QDialog):
    def __init__(self, db, departament, parent=None,):
        super().__init__(parent)

        self.setWindowTitle("Equipment repair table")

        table = QTableWidget()

        cursor = db.cursor(buffered=True)

        cursor.execute("""
        SELECT surname, name, fathername, birthday_date
        FROM employee as e, employee_history as eh
        WHERE e.p_id = eh.p_id AND eh.departament = %s""", (departament, ))

        result = cursor.fetchall()

        table.setRowCount(len(result))

        if (len(result) == 0):
            table.setColumnCount(1)

        else:
            table.setColumnCount(len(result[0]))
        
        #cursor.execute(f"DESCRIBE {}")

        heading_list = ["Surname", "Name", "Fathername", "Birthday date"]

        table.setColumnCount(len(heading_list))

        table.setHorizontalHeaderLabels(heading_list)
        table.adjustSize()

        for r_index, row in enumerate(result):
            for c_index, col in enumerate(row):
                table.setItem(r_index, c_index, QTableWidgetItem(str(col)))
       

        layout = QVBoxLayout()
        layout.addWidget(table)

        self.setLayout(layout)

class EmployeesBySexAndOld(QDialog):
    def __init__(self, db, parent=None,):
        super().__init__(parent)

        self.setWindowTitle("Count of equipment")
        self.db = db

        self.sex = QLineEdit()
        self.old = QLineEdit()

        dialog_layout = QVBoxLayout()
        layout = QFormLayout()

        #self.last_year.setDisplayFormat('yyyy-MM-dd')

        button_layout = QHBoxLayout()

        apply_button = QPushButton("Apply")
        apply_button.clicked.connect(self.slot_show_count)
        apply_button.show()

        button_layout.addWidget(apply_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.close_dialog)
        cancel_button.show()

        button_layout.addWidget(cancel_button)

        layout.addRow("Sex: ", self.sex)
        layout.addRow("Old: ", self.old)

        dialog_layout.addLayout(layout)
        dialog_layout.addLayout(button_layout)

        self.setLayout(dialog_layout)


    def slot_show_count(self):
        dialog = ShowEmployeeBySexAndOld(self.db, self.sex.text(), self.old.text())
        dialog.exec()

    def close_dialog(self):
        self.close()

class ShowEmployeeBySexAndOld(QDialog):
    def __init__(self, db, sex, old, parent=None,):
        super().__init__(parent)

        self.setWindowTitle("Equipment repair table")

        table = QTableWidget()

        cursor = db.cursor(buffered=True)

        cursor.execute("""
        SELECT surname, name, fathername, birthday_date
        FROM employee
        WHERE sex = %s AND old = %s""", (sex, old))

        result = cursor.fetchall()

        table.setRowCount(len(result))

        if (len(result) == 0):
            table.setColumnCount(1)

        else:
            table.setColumnCount(len(result[0]))
        
        #cursor.execute(f"DESCRIBE {}")

        heading_list = ["Surname", "Name", "Fathername", "Birthday date"]

        table.setColumnCount(len(heading_list))

        table.setHorizontalHeaderLabels(heading_list)
        table.adjustSize()

        for r_index, row in enumerate(result):
            for c_index, col in enumerate(row):
                table.setItem(r_index, c_index, QTableWidgetItem(str(col)))
       

        layout = QVBoxLayout()
        layout.addWidget(table)

        self.setLayout(layout)


class ShowRepairiestDepartament(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Equipment repair table")

        table = QTableWidget()

        cursor = db.cursor(buffered=True)

        cursor.execute("""
        SELECT t1.departament, COUNT(t1.e_id) as repair_count

        FROM

        equipment_repair as er,

        (SELECT eo1.e_id, eo1.departament, eo1.date_of_start as start, eo2.date_of_start as end
        FROM equipment_ownership as eo1, equipment_ownership as eo2
        WHERE eo1.e_id = eo2.e_id AND eo1.date_of_start < eo2.date_of_start
    
        GROUP BY eo1.date_of_start
        HAVING MAX(eo2.date_of_start)

        UNION

        SELECT eo1.e_id, eo1.departament, eo1.date_of_start as start, DATE_ADD(eo1.date_of_start, INTERVAL 1000 YEAR) as end
        FROM equipment_ownership as eo1, equipment_ownership as eo2
        WHERE eo1.e_id = eo2.e_id AND eo1.date_of_start = eo2.date_of_start
    
        GROUP BY eo1.e_id
        HAVING COUNT(eo1.e_id) = 1
        ) as t1

        WHERE er.e_id = t1.e_id AND repair_date BETWEEN start AND end
        GROUP BY departament
        """)

        result = cursor.fetchall()

        table.setRowCount(len(result))

        if (len(result) == 0):
            table.setColumnCount(1)

        else:
            table.setColumnCount(len(result[0]))
        
        #cursor.execute(f"DESCRIBE {}")

        heading_list = ["Departament"]

        table.setColumnCount(len(heading_list))

        table.setHorizontalHeaderLabels(heading_list)
        table.adjustSize()

        for r_index, row in enumerate(result):
            for c_index, col in enumerate(row):
                table.setItem(r_index, c_index, QTableWidgetItem(str(col)))
       

        layout = QVBoxLayout()
        layout.addWidget(table)

        self.setLayout(layout)


class StartWindow(QMainWindow):
    def __init__(self):
        super().__init__()  

        try:
            self.db = mysql.connector.connect(
                host = 'localhost',
                user = 'root',
                password = 'peta_loka',
                database = 'repair'
            )

            self.cursor = self.db.cursor(buffered=True)

        except mysql.connector.Error as err:
            print(err)

        app_functions_layout = QVBoxLayout()

        window_layout = QHBoxLayout()

        ### Equipment

        button_layout = QVBoxLayout()

        button = QPushButton("Show Equipment")
        button.clicked.connect(self.slot_show_equipment)
        button_layout.addWidget(button)

        button = QPushButton("Add Equipment")
        button.clicked.connect(self.slot_add_equipment)
        button_layout.addWidget(button)

        button = QPushButton("Edit Equipment")
        button.clicked.connect(self.slot_edit_equipment)
        button_layout.addWidget(button)

        button = QPushButton("Delete Equipment")
        button.clicked.connect(self.slot_delete_equipment)
        button_layout.addWidget(button)

        window_layout.addLayout(button_layout)

        ### Employee
        button_layout = QVBoxLayout()

        button = QPushButton("Show Employee")
        button.clicked.connect(self.slot_show_employee)
        button_layout.addWidget(button)

        button = QPushButton("Add Employee")
        button.clicked.connect(self.slot_add_employee)
        button_layout.addWidget(button)

        button = QPushButton("Edit Employee")
        button.clicked.connect(self.slot_edit_employee)
        button_layout.addWidget(button)

        button = QPushButton("Delete Employee")
        button.clicked.connect(self.slot_delete_employee)
        button_layout.addWidget(button)

        window_layout.addLayout(button_layout)

        ### Employee History
        button_layout = QVBoxLayout()

        button = QPushButton("Show Employee history")
        button.clicked.connect(self.slot_show_employee_history)
        button_layout.addWidget(button)

        button = QPushButton("Add to Employee history")
        button.clicked.connect(self.slot_add_employee_history)
        button_layout.addWidget(button)

        button = QPushButton("Edit Employee history")
        button.clicked.connect(self.slot_edit_employee_history)
        button_layout.addWidget(button)

        button = QPushButton("Delete from Employee history")
        button.clicked.connect(self.slot_delete_employee_history)
        button_layout.addWidget(button)

        window_layout.addLayout(button_layout)

        ### Equipment ownership
        button_layout = QVBoxLayout()

        button = QPushButton("Show Equipment ownership")
        button.clicked.connect(self.slot_show_equipment_ownership)
        button_layout.addWidget(button)

        button = QPushButton("Add to Equipment ownership")
        button.clicked.connect(self.slot_add_equipment_ownership)
        button_layout.addWidget(button)

        button = QPushButton("Edit Equipment ownership")
        button.clicked.connect(self.slot_edit_equipment_ownership)
        button_layout.addWidget(button)

        button = QPushButton("Delete from Equipment ownership")
        button.clicked.connect(self.slot_delete_equipment_ownership)
        button_layout.addWidget(button)

        window_layout.addLayout(button_layout)

        ### Equipment repair
        button_layout = QVBoxLayout()

        button = QPushButton("Show Equipment repair")
        button.clicked.connect(self.slot_show_equipment_repair)
        button_layout.addWidget(button)

        button = QPushButton("Add to Equipment repair")
        button.clicked.connect(self.slot_add_equipment_repair)
        button_layout.addWidget(button)

        button = QPushButton("Edit Equipment repair")
        button.clicked.connect(self.slot_edit_equipment_repair)
        button_layout.addWidget(button)

        button = QPushButton("Delete from Equipment repair")
        button.clicked.connect(self.slot_delete_equipment_repair)
        button_layout.addWidget(button)

        window_layout.addLayout(button_layout)

        ### Repair document
        button_layout = QVBoxLayout()

        button = QPushButton("Show Repair document")
        button.clicked.connect(self.slot_show_repair_document)
        button_layout.addWidget(button)

        button = QPushButton("Add to Repair document")
        button.clicked.connect(self.slot_add_repair_document)
        button_layout.addWidget(button)

        button = QPushButton("Edit Repair document")
        button.clicked.connect(self.slot_edit_repair_document)
        button_layout.addWidget(button)

        button = QPushButton("Delete from Repair document")
        button.clicked.connect(self.slot_delete_repair_document)
        button_layout.addWidget(button)

        window_layout.addLayout(button_layout)

        ### Functions
        button_layout = QVBoxLayout()

        button = QPushButton("Count of equipment by departament(3 years)")
        button.clicked.connect(self.slot_show_equipment_count)
        button_layout.addWidget(button)

        button = QPushButton("Get employees by departament")
        button.clicked.connect(self.slot_show_employee_by_departament)
        button_layout.addWidget(button)

        button = QPushButton("Get employees by old and sex")
        button.clicked.connect(self.slot_show_employee_by_sex_and_old)
        button_layout.addWidget(button)

        button = QPushButton("Get the most repairiest departament")
        button.clicked.connect(self.slot_show_repairiest_departament)
        button_layout.addWidget(button)

        app_functions_layout.addLayout(window_layout)
        app_functions_layout.addLayout(button_layout)

        widget = QWidget()
        widget.setLayout(app_functions_layout)


        self.setCentralWidget(widget)

        self.setWindowTitle("P _ B _ Z")
        self.setFixedSize(QSize(1200, 600))

    def slot_show_equipment(self):
        dialog = ShowEquipment(self.db)
        dialog.setMinimumSize(QSize(600, 600))
        dialog.exec()

    def slot_add_equipment(self):
        dialog = AddEquipmentDialog(self.db)
        dialog.setMinimumSize(QSize(600, 600))
        dialog.exec()
        
    def slot_edit_equipment(self):
        dialog = EditEquipmentDialog(self.db)
        dialog.setMinimumSize(QSize(600, 600))
        dialog.exec()

    def slot_delete_equipment(self):
        dialog = DeleteEquipmentDialog(self.db)
        dialog.setMinimumSize(QSize(600, 600))
        dialog.exec()

    def slot_show_employee(self):
        dialog = ShowEmployee(self.db)
        dialog.setMinimumSize(QSize(600, 600))
        dialog.exec()

    def slot_add_employee(self):
        dialog = AddEmployeeDialog(self.db)
        dialog.setMinimumSize(QSize(600, 600))
        dialog.exec()

    def slot_edit_employee(self):
        dialog = EditEmployeeDialog(self.db)
        dialog.setMinimumSize(QSize(600, 600))
        dialog.exec()

    def slot_delete_employee(self):
        dialog = DeleteEmployeeDialog(self.db)
        dialog.setMinimumSize(QSize(600, 600))
        dialog.exec()

    def slot_show_employee_history(self):
        dialog = ShowEmployeeHistory(self.db)
        dialog.setMinimumSize(QSize(600, 600))
        dialog.exec()

    def slot_add_employee_history(self):
        dialog = AddEmployeeHistoryDialog(self.db)
        dialog.setMinimumSize(QSize(600, 600))
        dialog.exec()

    def slot_edit_employee_history(self):
        dialog = EditEmployeeHistoryDialog(self.db)
        dialog.setMinimumSize(QSize(600, 600))
        dialog.exec()

    def slot_delete_employee_history(self):
        dialog = DeleteEmployeeHistoryDialog(self.db)
        dialog.setMinimumSize(QSize(600, 600))
        dialog.exec()

    def slot_show_equipment_ownership(self):
        dialog = ShowEquipmentOwnership(self.db)
        dialog.setMinimumSize(QSize(600, 600))
        dialog.exec()

    def slot_add_equipment_ownership(self):
        dialog = AddEquipmentOwnership(self.db)
        dialog.setMinimumSize(QSize(600, 600))
        dialog.exec()

    def slot_edit_equipment_ownership(self):
        dialog = EditEquipmentOwnership(self.db)
        dialog.setMinimumSize(QSize(600, 600))
        dialog.exec()

    def slot_delete_equipment_ownership(self):
        dialog = DeleteEquipmentOwnership(self.db)
        dialog.setMinimumSize(QSize(600, 600))
        dialog.exec()

    def slot_show_equipment_repair(self):
        dialog = ShowEquipmentRepair(self.db)
        dialog.setMinimumSize(QSize(600, 600))
        dialog.exec()

    def slot_add_equipment_repair(self):
        dialog = AddEquipmentRepair(self.db)
        dialog.setMinimumSize(QSize(600, 600))
        dialog.exec()

    def slot_edit_equipment_repair(self):
        dialog = EditEquipmentRepair(self.db)
        dialog.setMinimumSize(QSize(600, 600))
        dialog.exec()

    def slot_delete_equipment_repair(self):
        dialog = DeleteEquipmentRepair(self.db)
        dialog.setMinimumSize(QSize(600, 600))
        dialog.exec()

    def slot_show_repair_document(self):
        dialog = ShowRepairDocument(self.db)
        dialog.setMinimumSize(QSize(600, 600))
        dialog.exec()

    def slot_add_repair_document(self):
        dialog = AddRepairDocument(self.db)
        dialog.setMinimumSize(QSize(600, 600))
        dialog.exec()

    def slot_edit_repair_document(self):
        dialog = EditRepairDocument(self.db)
        dialog.setMinimumSize(QSize(600, 600))
        dialog.exec()

    def slot_delete_repair_document(self):
        dialog = DeleteRepairDocument(self.db)
        dialog.setMinimumSize(QSize(600, 600))
        dialog.exec()

    def slot_show_equipment_count(self):
        dialog = CountOfEquipment(self.db)
        dialog.setMinimumSize(QSize(600, 600))
        dialog.exec()

    def slot_show_employee_by_departament(self):
        dialog = EmployeesByDepartament(self.db)
        dialog.setMinimumSize(QSize(600, 600))
        dialog.exec()

    def slot_show_employee_by_sex_and_old(self):
        dialog = EmployeesBySexAndOld(self.db)
        dialog.setMinimumSize(QSize(600, 600))
        dialog.exec()

    def slot_show_repairiest_departament(self):
        dialog = ShowRepairiestDepartament(self.db)
        dialog.setMinimumSize(QSize(600, 600))
        dialog.exec()


if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        
        window = StartWindow()

        window.show()

        app.exec()
        

    except mysql.connector.Error as err:
        print(err)
