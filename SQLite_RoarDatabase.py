import sqlite3

def Query(User_ID):
    connection = sqlite3.connect('database3.db') # Connect python with SQLite
    cursor = connection.cursor()
    listt = []
    for i in cursor.execute(f"SELECT * FROM record_model WHERE User_ID='{User_ID}'"):
        listt.append(i)
    return listt
