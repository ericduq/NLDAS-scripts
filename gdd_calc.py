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
STARTMO=1
ENDMO=1
STARTDAY=1
ENDDAY=1
STARTHR=0
ENDHR=23

### Construct command sequence
dt = datetime.datetime(STARTYR,STARTMO,STARTDAY,STARTHR)
end = datetime.datetime(ENDYR,ENDMO,ENDDAY,ENDHR)
step = datetime.timedelta(hours=1)

result=list()
hour24=[]
dt_start=dt
while dt<=end:
    

    print '--- Examining ' + str(dt.year) + str(dt.month) + str(dt.month) + str(dt.hour) + '---'

    inputfile=nldas.grib_filepath(dt,DATADIR)
    f = open(inputfile)
    
    mcount=grib_count_in_file(f)
    gid_list=[grib_new_from_file(f) for i in xrange(mcount)]

    for i in xrange(mcount):
	
        gid=gid_list[i]
        avg=grib_get(gid,'average')
        if i==14: # The 14th field should always be surface temperatures
           result.append(avg)

        if i==14: # The 14th field should always be surface temperatures
           hourtemp=grib_get_values(gid)
           #hourtemp[hourtemp==9999]=np.nan
           hour24.append(hourtemp)
           print len(hour24)

    f.close()
    grib_release(gid)
    dt +=step
    
date=pd.date_range(dt_start,periods=24,freq='H')
hour24=pd.DataFrame([hour24],index=date)
#hourtemp=hourtemp.applymap(lambda x: np.nan if x==9999 else x)
#hourtemp=pd.DataFrame([hourtemp],index=date)
print result








