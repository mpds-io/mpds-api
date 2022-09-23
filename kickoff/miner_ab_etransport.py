#!/usr/bin/env python3

import io

import requests
from mpds_client import MPDSDataRetrieval, MPDSDataTypes

from etransport_raw import analyze_raw # this is given in the supplied file "etransport_raw.py"

# the raw simulation data on the MPDS are in 7z format
# so we need the latest dev version of pylzma
# pip install git+https://github.com/fancycode/pylzma
# then py7zlib is available

from py7zlib import Archive7z


mpds_api = MPDSDataRetrieval(dtype=MPDSDataTypes.AB_INITIO)

for entry in mpds_api.get_data({'props': 'electrical conductivity'}, fields={}):

    archive_url = entry['sample']['measurement'][0]['raw_data'] # this is the raw data archive field in the MPDS JSON P-entries

    p = requests.get(archive_url)
    if p.status_code != 200:
        logging.critical('ARCHIVE %s IS UNAVAILABLE' % archive_url)
        continue

    print('Analyzing the raw data for %s' % entry['sample']['material']['entry'])

    archive = Archive7z(io.BytesIO(p.content))
    for virtual_path in archive.files:

        if virtual_path.filename != 'TRANSPORT/SIGMA.DAT': # raw simulation output log file
            continue

        # this is how we extract data from the 7z-archive
        member = archive.getmember(virtual_path.filename)
        rawdata = io.StringIO(member.read().decode('ascii'))
        result = analyze_raw(rawdata)
        rawdata.seek(0)

        print(entry['sample']['material']['phase'], result)
