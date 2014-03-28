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


# Pre-allocate and define for efficiency and accumulate values
temps=list()
gdd_accum=np.zeros([ENDC+1,103936])
celmin_arr=np.tile(range(STARTC,ENDC+1),(103936,2,1)).transpose()
celmax_arr=celmin_arr+1
gdd_total=list()


for i in xrange(53):  #clear gid 0-51 range. Only useful if a prior running results in improper shutdown and a failure to run gid release.
   try:
      grib_release(i)
   except:
      pass # do nothing

while dt<=dtend:
    
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

    gid = 15 # 15 should alawys be surface temperature for NOAH2	
    htemp=grib_get_values(gid) # ENTIRE GRID
    htemp=[np.nan if i==9999 else i-273.15 for i in htemp]
    temps.append(htemp) # append hour temperature to day temperatures
  

    if dt!=dtstart:
      tempdiff=np.diff(temps, axis=0)
      hoursperdeg=np.abs(1/tempdiff) # ! Division be zero subverted by line below
      hoursperdeg[hoursperdeg==np.inf]=1 # ! Conforms to proper gdd calculation; note: nan's should only mean grid cells with originally missing info
      hoursperdeg = np.tile(hoursperdeg,(ENDC-STARTC+1,1,1))

      nptemps=np.tile(temps,(ENDC-STARTC+1,1,1)) # Convert temps to array and duplicate per celsius bini
      mincond=nptemps<celmin_arr
      maxcond=nptemps>celmax_arr
      nptemps[mincond]=0
      nptemps=nptemps+celmin_arr*mincond
      nptemps[maxcond]=0
      nptemps=nptemps+celmax_arr*maxcond
 
      bintempdiff = np.abs(np.diff(nptemps, axis=1) )

      gdd = (bintempdiff * hoursperdeg)/24
      gdd_accum=gdd_accum+np.squeeze(gdd)

      temps.pop(0)

    for i in xrange(mcount):
       grib_release(gid_list[i])
    f.close()

    if DOWNLOAD==1:
       # Remove file from local drive
       command="rm "+inputfile
       rcode=subprocess.call(command.split())
    
    dt +=step

print '--- Finished with GDD calculation ---'
if SAVE==1:
   print '--- Saving GDD in ' + CONSTDIR 
   savefile= CONSTDIR + '/gdd_binned.txt'
   np.savetxt(savefile, gdd_accum, delimiter=",")
   print '--- Saved gdd_binned.txt ! ---'
print "Started at " + str(begintime)
print "Ended at " + str(datetime.datetime.now())


print '--- Basic GDD calculation from ' + dtstart.strftime('%c') + ' to ' + dtend.strftime('%c') + ' for Point of Rocks, MD ---'
# Basic GDD is ( max + min  ) / 2 - base
# WHen taking the cumulative sum below, the celsius value is taken to be midpint (e.g., 15.5) to match basic GDD
BASET=10
MAXT=30
GID=53275 # Point of Rocks
scale1=xrange(1,gdd_accum[BASET:(MAXT+1),:].shape[0]+1)
scale1=[i-.5 for i in scale1] # adjust by .5 to match basic gdd calculation
scale2=gdd_accum[(MAXT+1):,:].shape[0]*[MAXT-BASET+.5] # adjust by .5 to match basic gdd calculation
gdd_basic=[(gdd_accum[BASET:,i]*(scale1+scale2)).sum() for i in xrange(gdd_accum.shape[1])]
print "   Point of Rocks, MD GDD(10,30) is ", gdd_basic[GID]



