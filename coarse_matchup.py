#!/usr/bin/env python

import os, sys, csv
from SOAPpy.WSDL import Proxy
from datetime import datetime, timedelta

# NOAA data file for LAX
NOAA_file = os.path.join("data", "NOAA", "36258.csv")

def main():

    # get proxy
    wsdl = sys.argv[1]
    proxy = Proxy(wsdl)

    # read in NOAA data
    f = open(NOAA_file)
    reader = csv.DictReader(f)
    for row in reader:

        # get ISO 8601 datetime from NOAA data
        yy = int(row['DATE'][0:4])
        mm = int(row['DATE'][4:6])
        dd = int(row['DATE'][6:8])
        hh = int(row['DATE'][9:11])
        mn = int(row['DATE'][12:14])
        dt = datetime(year=yy, month=mm, day=dd, hour=mm, minute=mm)
    
        # get start and end date surrounding NOAA date
        start_dt = dt - timedelta(seconds=10)
        end_dt = dt + timedelta(seconds=10)
        print start_dt, end_dt
    
        # get matching AIRS metadata info
        results = proxy.geoRegionQuery("AIRS", None, None, "2010-01-01T00:00:00Z",
                                       "2010-01-01T00:01:00Z", -180, 180, -90, 90,
                                       "Large")
    
        print results 
        print row
        break

    # cleanup
    f.close()

if __name__ == "__main__":
    main()
