import nldas_defs as nldas
import datetime
import subprocess
import pandas as pd
import numpy as np
import sys
sys.path.append("/etc/local/grib_api/lib/python2.7/site-packages/grib_api")
from gribapi import *

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
    

    print '--- Examining ' + str(dt.year) + str(dt.month) + str(dt.month) + str(dt.hour) + '---'

    inputfile=nldas.grib_filepath(dt,DATADIR)
    f = open(inputfile)
    
    mcount=grib_count_in_file(f)
    gid_list=[grib_new_from_file(f) for i in xrange(mcount)]

    #for i in xrange(mcount):
    for i in [14]: # only care about surface temperature for gdd
	
        gid=gid_list[i]
        if i==14: # 14 should always be surface temperatures
           hourtemp=grib_get_values(gid)
	   point=grib_find_nearest(gid,LAT,LON,is_lsm = False,npoints = 1)
	   hourtemp=point[0]['value']
           #hourtemp[hourtemp==9999]=np.inan
           sft.append(hourtemp)

    f.close()
    grib_release(gid)
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







