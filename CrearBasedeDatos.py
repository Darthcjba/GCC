import psycopg2
conn=None
conn = psycopg2.connect(database="postgres",user="postgres", password="postgres", host="127.0.0.1", port="5432")
conn.set_isolation_level(0)
cursor= conn.cursor()
try:
    cursor.execute('DROP DATABASE  projectium')
except:
    print("CREANDO BASE DE DATOS")
cursor.execute('CREATE DATABASE projectium')
cursor.close()
conn.close()
