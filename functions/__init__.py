import sqlite3
import json

# def add_to_database(table, data, columns):
#     '''Adds Values To Database Column'''
#     values = ""
#     i = 1
#     while i <= len(data):
#         if i == len(data):
#             values += "?"
#         else:
#             values += "?, "
#         i += 1
#     values = "(" + values + ")"
#     conn = sqlite3.connect("database.db")
#     c = conn.cursor()
#     c.execute(f"INSERT INTO {table}{columns} VALUES{values}", data)
#     conn.commit()
#     conn.close()

def get_from_database(table, id=None):
    '''Returns Values From Database Column'''
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute(f"SELECT * FROM {table}")
    data = c.fetchall()
    conn.commit()
    conn.close()
    if id == None:
        return data
    for item in data:
        if item[0] == id:
            return item
    return None

def update_in_database(table, row, new):    #new = (new_info, id)
    '''Updates Row In Database Column'''
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute(f"UPDATE {table} SET {row} = ? WHERE id = ?", new)
    conn.commit()
    conn.close()

# def remove_from_database(table, id, *args):
#     '''Removes Value From Database Column'''
#     conn = sqlite3.connect("database.db")
#     c = conn.cursor()
#     if table == "courts":
#         c.execute(f"CREATE TABLE IF NOT EXISTS backup(id INTEGER NOT NULL PRIMARY KEY, name UNIQUE, data, open_close)")
#     elif table == "accounts":
#         app = MDApp.get_running_app()
#         if app.logged_in_user[1] == id:
#             app.logout()
#         c.execute("CREATE TABLE IF NOT EXISTS backup(id INTEGER NOT NULL PRIMARY KEY, username UNIQUE, password, admin DEFAULT False)")
#     c.execute(f"SELECT * FROM {table}")
#     old_data = c.fetchall()
#     for i in old_data:
#         if not i[0] == id:
#             if table == "courts":
#                 c.execute("INSERT INTO backup(name, data, open_close) VALUES(?, ?, ?)", (i[1], i[2], i[3]))
#             elif table == "accounts":
#                 c.execute("INSERT INTO backup(username, password, admin) VALUES(?, ?, ?)", (i[1], i[2], True if i[3] == 1 else False))
#     c.execute(f"DROP TABLE IF EXISTS {table}")
#     c.execute(f"ALTER TABLE backup RENAME TO {table}")
#     conn.commit()
#     conn.close()
