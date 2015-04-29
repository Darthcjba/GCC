import psycopg2
conn=None
conn = psycopg2.connect(database="postgres",user="postgres", password="postgres", host="127.0.0.1", port="5432")
conn.set_isolation_level(0)
cursor= conn.cursor()
cursor.execute('DROP DATABASE projectium')
cursor.execute('CREATE DATABASE projectium')
cursor.close()
conn.close()
