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
CONSTDIR="/mnt/NLDAS-data/constructed"
STARTYR=2012
ENDYR=2012
STARTMO=6
ENDMO=6
STARTDAY=1
ENDDAY=1
STARTHR=0
ENDHR=23
STARTC=0 # starting celsius bin
ENDC=45# ending celsius bin (inclusive)
#MAXTEMP=30
DOWNLOAD=0
SAVE=0

# Record time for caclulations
begintime=datetime.datetime.now()

### Construct command sequence
dtstart = datetime.datetime(STARTYR,STARTMO,STARTDAY,STARTHR)
dtend = datetime.datetime(ENDYR,ENDMO,ENDDAY,ENDHR)
step = datetime.timedelta(hours=1)
dt=dtstart

print '--- Starting GDD calculation ---'
temps=list()
gdd_accum=np.zeros([ENDC+1,103936])
gdd_total=list()

#for i in xrange(53):  #clear gid 0-51 range. Only useful if a prior running results in improper shutdown and a failure to run gid release.
#   try:
#      grib_release(i)
#   except:
#      pass # do nothing

while dt<=dtend:
    
    # Convert dt to strings
    yy=str(dt.year)
    mm='{:02.0f}'.format(dt.month)
    dd='{:02.0f}'.format(dt.day)
    hhhh='{:02.0f}'.format(dt.hour) + "00"
    ddoy='{:03.0f}'.format(int(dt.strftime('%j')))

    print '--- Examining ' + yy + mm + dd + hhhh + ' ---'


    inputfile=nldas.grib_filepath(dt,DATADIR) 
    f = open(inputfile)
    mcount=grib_count_in_file(f)
    gid_list=[grib_new_from_file(f) for i in xrange(mcount)]

    gid = 15 # 15 should alawys be surface temperature for NOAH2
    htemp=grib_get_values(gid) # ENTIRE GRID

    htemp=['' if i==9999 else i-273.15 for i in htemp]

    print htemp[100:150]

    # Prepare temperature text files for hadoop
    text_file=open(CONSTDIR+"/temp"+yy+mm+dd+hhhh+".txt", "w")
    text_file.write
    for t in xrange(1,len(htemp)):
      #print '%s\t%s\t%s' % (t,yy+mm+dd+hhhh,htemp[t])
      text_file.write('%s\t%s\t%s\n' % (t,yy+mm+dd+hhhh,htemp[t]))
    text_file.close()

    for i in xrange(mcount):
       grib_release(gid_list[i])
    f.close()


    dt+=step 

