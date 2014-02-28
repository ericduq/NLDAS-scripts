"""
Created on Tues Feb 25 09:41:05 2014

This Python script downloads the NLDAS-2 Forcing GRIB encoded data from a NASA anonymous ftp server.
The time span for the files to be downloaded can be specified under the Globals section.
The wget download commands are executed at the end of the script.

"""
### Packages
import datetime
import subprocess # for calling external commands

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

EXECUTEDOWNLOAD=1

### Construct command sequence
dt = datetime.datetime(STARTYR,STARTMO,STARTDAY,STARTHR)
end = datetime.datetime(ENDYR,ENDMO,ENDDAY,ENDHR)
step = datetime.timedelta(hours=1)

result=list()
while dt<=end:
    
    y=str(dt.year)    
    m=str(dt.month)
    d=str(dt.day)
    h=str(dt.hour)
    doy=str(dt.strftime('%j'))

    # Year string    
    yy=str(y)
    
    # Month string    
    if len(m)==1:
        mm="0" + m
    else:
        mm=m
    
    # Day string;
    if len(d)==1:
        dd="0"+d
    else:
        dd=d
    
    # Hour string;
    if len(h)==1:
        hhhh="0" + h + "00"
    else : 
        hhhh=h+"00"
    
    #Day of year string
    if len(doy)==1:
        ddoy="00"+doy
    elif len(doy)==2:
        ddoy="0"+doy
    else: 
        ddoy=doy

    command="wget -q -P " + DATADIR +"/ " + "ftp://hydro1.sci.gsfc.nasa.gov/data/s4pa/NLDAS/NLDAS_NOAH0125_H.002/" + yy + "/" + ddoy + "/NLDAS_NOAH0125_H.A" + yy + mm + dd + "." + hhhh + ".002.grb"
    result.append(command)        
    dt += step

print "Downloading GRIB files ..."
for i in xrange(len(result)):
    print result[i].split()[-1]
    if EXECUTEDOWNLOAD==1:
	rcode=subprocess.call(result[i].split())
print "...Finished downloading GRIB files"
