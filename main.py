import json
import time

import psycopg2
import pyodbc

import paths_manager


paths_info = {
    'MONITOR.BDPRODUCTOS': ['Base de Datos', '5 - Bases de Datos/PRODUCTOS.accdb', 'FILE'],
}

paths = paths_manager.get_paths(paths_info)
source_access_db = paths["MONITOR.BDPRODUCTOS"]

conn_A = pyodbc.connect(r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};'fr'DBQ={source_access_db};')
cursor_A = conn_A.cursor()

conn_B = psycopg2.connect(database="postgres",
                        user="postgres",
                        host='localhost',
                        password="root",
                        port=5432)

cursor_B = conn_B.cursor()

table_queries = {}
with open('tables.json', "r") as x:
    table_queries = json.load(x)

i = 0
for table_name, data in table_queries.items():
    query_to_create_table = data[0]
    src_table = data[1]
    query_to_retrieve_rows = data[2]
    print(f"##### {table_name} ######################################")
    cursor_B.execute(f'DROP TABLE IF EXISTS {table_name}')
    cursor_B.execute(query_to_create_table)
    conn_B.commit()
    cursor_A.execute(query_to_retrieve_rows)

    num_of_params = query_to_retrieve_rows.count(', ') + 1
    placeholders = ', '.join(['%s'] * num_of_params)
    rows = cursor_A.fetchall()
    for row in rows:
        print(f'INSERT INTO {table_name} VALUES ({placeholders})', row)
        row = list(row)
        cursor_B.execute(f'INSERT INTO {table_name} VALUES ({placeholders})', row)

    i += 1

# Make the changes to the database persistent
conn_B.commit()
# Close cursor and communication with the database
cursor_B.close()
conn_B.close()
