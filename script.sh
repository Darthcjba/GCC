
python CrearBasedeDatos.py
if [ $? -eq 0 ];then
    echo "Creando migraciones..."
    python manage.py makemigrations
    echo "Migrando base de datos..."
    python manage.py migrate
    echo "Poblando base de datos..."
    python manage.py loaddata initial
    echo "Ejecutando pruebas..."
    #python -Wi manage.py test
else
    echo "Lo sentimos, no se pudo realizar la poblacion."
fi