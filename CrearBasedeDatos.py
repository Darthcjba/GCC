import psycopg2
import sys

conn = None
conn = psycopg2.connect(database="postgres", user="postgres", password="postgres", host="127.0.0.1", port="5432")
conn.set_isolation_level(0)
cursor = conn.cursor()
try:
    cursor.execute('DROP DATABASE  projectium')
    print "La base de datos fue eliminada."
except psycopg2.ProgrammingError:
    print "La base de datos no existe."
    sys.exit(1)
except psycopg2.OperationalError:
    print "La base de datos esta siendo utilizada. No se puede eliminar."
    sys.exit(1)
cursor.execute('CREATE DATABASE projectium')
cursor.close()
conn.close()
print "Base de Datos fue creada."
sys.exit(0)