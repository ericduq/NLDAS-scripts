# This files is to be executed after downloading NLDAS-scripts git repo

# Make a software installation one directory higher than git repo
mkdir software

# Install Python and Java packages
sudo apt-get install python-numpy python-scipy python-matplotlib ipython ipython-notebook python-pandas python-sympy python-nose
sudo apt-get install jasper libjasper-runtime libjasper-dev
sudo apt-get install python-pyproj

# GRIB_API Installation
cd software
wget https://software.ecmwf.int/wiki/download/attachments/3473437/grib_api-1.11.0.tar.gz?api=v2
mv grib_api-1.11.0.tar.gz?api=v2 grib_api-1.11.0.tar.gz
gunzip grib_api-1.11.0.tar.gz
tar xf grib_api-1.11.0.tar
cd /usr/local
sudo mkdir grib_api
cd ./software/grib_api-1.11.0
/configure --prefix=./etc/local/grib_api --enable-python
make
make check
sudo make install

#Setup paths for downloading GRIB
cd /mnt
mkdir /NLDAS-data
mkdir /NLDAS-data/originals
mkdir /NLDAS-data/constructed
chown -R ubuntu NLDAS-data
chgrp -R ubuntu NLDAS-data
exit

#sudo apt-get install python-pip
#pip install --update pandas
sudo easy_install -U pandas

# Download GRIB files
cd /home/ubuntu/NLDAS-scripts/setup/
python dnl_commands.py

# Make GRIB files Hadoop ready   - this stage might best be embedded in the previous stage so that the GRIB files don't have to be stored
python export_files_for_hadoop.py

# Upload files to HDFS
cd /mnt/NLDAS-data/constructed
hdfs dfs -rm NLDAS-data/tdata/*.*
hdfs dfs -copyFromLocal temp*.txt NLDAS-data/tdata

# Run pig or python script to generate calculation
pig gdd.pig


