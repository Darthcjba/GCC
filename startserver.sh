#! /bin/bash
sudo cp -r /home/santiortizpy/PycharmProjects/Projectium/ /var/www
sudo service apache2 start>/dev/null
echo Se ha iniciado el sistema.
sudo phantomjs /var/www/Projectium/highchart-export/highcharts-convert.js -type png -host 127.0.0.1 -port 3003