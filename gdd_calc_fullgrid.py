import nldas_defs as nldas
import datetime
import subprocess
import pandas as pd
import numpy as np
import sys
sys.path.append("/etc/local/grib_api/lib/python2.7/site-packages/grib_api")
from gribapi import *
import subprocess

### Globals
DATADIR="/mnt/NLDAS-data/originals"
STARTYR=2012
ENDYR=2012
STARTMO=4
ENDMO=8
STARTDAY=1
ENDDAY=31
STARTHR=0
ENDHR=23
BASETEMP=10 # Basic GDD calculation
MAXTEMP=30
DOWNLOAD=0

### Construct command sequence
dt = datetime.datetime(STARTYR,STARTMO,STARTDAY,STARTHR)
end = datetime.datetime(ENDYR,ENDMO,ENDDAY,ENDHR)
step = datetime.timedelta(hours=1)
dtstart=dt

print '--- Starting calculation ---'
temps=list()
gdd_accum=np.zeros([1,103936])
gdd_total=list()
while dt<=end:
    
    # Convert dt to strings
    yy=str(dt.year)
    mm='{:02.0f}'.format(dt.month)
    dd='{:02.0f}'.format(dt.day)
    hhhh='{:02.0f}'.format(dt.hour) + "00"
    ddoy='{:03.0f}'.format(int(dt.strftime('%j')))

    print '--- Examining ' + yy + mm + dd + hhhh + ' ---'
    
    if DOWNLOAD==1:
       # Download grib file to local drive
       command="wget -q -P " + DATADIR +"/ " + "ftp://hydro1.sci.gsfc.nasa.gov/data/s4pa/NLDAS/NLDAS_NOAH0125_H.002/" + yy + "/" + ddoy + "/NLDAS_NOAH0125_H.A" + yy + mm + dd + "." + hhhh + ".002.grb"
       rcode=subprocess.call(command.split())

    # Open file and extract 
    inputfile=nldas.grib_filepath(dt,DATADIR)
    f = open(inputfile)    
    mcount=grib_count_in_file(f)
    gid_list=[grib_new_from_file(f) for i in xrange(mcount)]

    #for i in xrange(mcount):
    gid = 15 # 15 should alawys be surface temperature for NOAH2	
    htemp=grib_get_values(gid) # ENTIRE GRID
    htemp=[np.nan if i==9999 else i-273.15 for i in htemp]
    temps.append(htemp) # append hour temperature to day temperatures

    if dt!=dtstart:
       nptemps=np.array(temps)
       nptemps[nptemps<BASETEMP]=BASETEMP
       nptemps[nptemps>MAXTEMP]=MAXTEMP
       gdd=(nptemps.mean(axis=0)-BASETEMP)/24
       gdd_accum=gdd_accum+gdd
       temps.pop(0)
       #print gdd_accum[0][7000:7500]

    for i in xrange(mcount):
       grib_release(gid_list[i])
    f.close()

    if DOWNLOAD==1:
       # Remove file from local drive
       command="rm "+inputfile
       rcode=subprocess.call(command.split())
    
    dt +=step

#temps=np.array(temps)
#temps[temps==9999]=np.nan
#temps=temps-273.15
#temps[temps<BASETEMP]=BASETEMP
#temps[temps>MAXTEMP]=MAXTEMP

print '--- Calculating GDD ----'


#gdd_day=(np.nanmax(temps,axis=0)+np.nanmin(temps,axis=0))/2 - BASETEMP
#gdd_total.append(gdd_day.tolist())
#print gdd_total
#print sum(gdd_total)


#print '--- Converting to dataframe ---'
#date=pd.date_range(dt_start,periods=24,freq='H')
#hour24=pd.DataFrame(hour24,index=date)







