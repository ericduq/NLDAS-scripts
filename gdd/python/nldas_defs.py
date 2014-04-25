import datetime

def grib_filepath(dt,datadir):
    
    # Year string    
    yy=str(dt.year)
    
    # Month string    
    mm='{:02.0f}'.format(dt.month)
    
    # Day string;
    dd='{:02.0f}'.format(dt.day)
    
    # Hour string;
    hhhh='{:02.0f}'.format(dt.hour) + "00"
    
    #Day of year string
    ddoy='{:03.0f}'.format(int(dt.strftime('%j')))

    inputfile = datadir +"/NLDAS_NOAH0125_H.A" + yy + mm + dd + "." + hhhh + ".002.grb"
    return inputfile
