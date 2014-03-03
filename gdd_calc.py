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
DATADIR="../NLDAS-data/originals"
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
LAT=39.27583 # Point of Rocks, MD
LON=-77.53944

### Construct command sequence
dt = datetime.datetime(STARTYR,STARTMO,STARTDAY,STARTHR)
end = datetime.datetime(ENDYR,ENDMO,ENDDAY,ENDHR)
step = datetime.timedelta(hours=1)

sft=list() # surface tempeature
dt_start=dt
print '--- Importing temperature data ---'
while dt<=end:
    
    
    # Convert dt to strings
    yy=str(dt.year)
    mm='{:02.0f}'.format(dt.month)
    dd='{:02.0f}'.format(dt.day)
    hhhh='{:02.0f}'.format(dt.hour) + "00"
    ddoy='{:03.0f}'.format(int(dt.strftime('%j')))

    print '--- Examining ' + yy + mm + dd + hhhh + ' ---'
    
    # Download grib file to local drive
    command="wget -q -P " + DATADIR +"/ " + "ftp://hydro1.sci.gsfc.nasa.gov/data/s4pa/NLDAS/NLDAS_NOAH0125_H.002/" + yy + "/" + ddoy + "/NLDAS_NOAH0125_H.A" + yy + mm + dd + "." + hhhh + ".002.grb"
    rcode=subprocess.call(command.split())

    # Open file and extract 
    inputfile=nldas.grib_filepath(dt,DATADIR)
    f = open(inputfile)    
    mcount=grib_count_in_file(f)
    gid_list=[grib_new_from_file(f) for i in xrange(mcount)]

    #for i in xrange(mcount):
    gid = 15 # 14 should alawys be surface temperature for NOAH2	
    hourtemp=grib_get_values(gid) # ENTIRE GRID
    point=grib_find_nearest(gid,LAT,LON,is_lsm = False,npoints = 1) # SINGLE LAT-LON
    hourtemp=point[0]['value']
    
    print hourtemp
    sft.append(hourtemp)
    
    for i in xrange(mcount):
       grib_release(gid_list[i])
    f.close()

    # Remove file from local drive
    command="rm "+inputfile
    rcode=subprocess.call(command.split())
    
    dt +=step

sft=np.array(sft)

print '--- Converting 9999 to missing (nan) and Celsius---'
sft[sft==9999]=np.nan
sft=sft-273.15
#hour24=[[np.nan if i==9999 else i-273.15 for i in j] for j in hour24]


print '--- Censoring data to interval between basetemp and maxtemp? ---'
sft[sft<BASETEMP]=BASETEMP
sft[sft>MAXTEMP]=MAXTEMP
#hour24=[[BASETEMP if i<BASETEMP else i for i in j] for j in hour24]
#hour24=[[MAXTEMP if i>MAXTEMP else i for i in j] for j in hour24]

print '--- Calculating GDD ----'
#hour24=np.array(hour24)
gdd=(np.nanmax(sft,axis=0)+np.nanmin(sft,axis=0))/2 - BASETEMP
print gdd


#print '--- Converting to dataframe ---'
#date=pd.date_range(dt_start,periods=24,freq='H')
#hour24=pd.DataFrame(hour24,index=date)
#hourtemp=hourtemp.applymap(lambda x: np.nan if x==9999 else x)
#gdd=hour24.max(axis=0)-hour24.min(axis=1)







