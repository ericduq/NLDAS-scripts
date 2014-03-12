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
ENDMO=4
STARTDAY=1
ENDDAY=1
STARTHR=0
ENDHR=23
BASETEMP=10 # Basic GDD calculation
MAXTEMP=30
LAT=39.27583 # Point of Rocks, MD
LON=-77.53944
DOWNLOAD=0


### Construct command sequence
dt = datetime.datetime(STARTYR,STARTMO,STARTDAY,STARTHR)
end = datetime.datetime(ENDYR,ENDMO,ENDDAY,ENDHR)
step = datetime.timedelta(hours=1)

print '--- Starting calculation ---'
dtemps=list()
gdd_total=list()
while dt<=end:
    
    htemp=list()
    
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
    #htemp=grib_get_values(gid) # ENTIRE GRID
    point=grib_find_nearest(gid,LAT,LON,is_lsm = False,npoints = 1) # SINGLE LAT-LON
    htemp=point[0]['value']
    print htemp
    htemp=np.nan if htemp==9999 else htemp-273.15 # Convert missing to Nan and K degrees to C
    print htemp
    
    dtemps.append(htemp) # append hour temperature to day temperatures
    if dt.hour==23:
       dtemps=np.array(dtemps)
       dtemps[dtemps<BASETEMP]=BASETEMP
       dtemps[dtemps>MAXTEMP]=MAXTEMP
       print '--- Calculating GDD ----'
       gdd_day=(np.nanmax(dtemps,axis=0)+np.nanmin(dtemps,axis=0))/2 - BASETEMP
       gdd_total.append(gdd_day.tolist())
       a=dtemps
       dtemps=list()
    
    for i in xrange(mcount):
       grib_release(gid_list[i])
    f.close()

    if DOWNLOAD==1:
       # Remove file from local drive
       command="rm "+inputfile
       rcode=subprocess.call(command.split())
    
    dt +=step

print gdd_total
print sum(gdd_total)
