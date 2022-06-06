'''
This code pulls Google Maps review data using the Google Maps API
and saves to file
'''

import googlemaps
import pandas as pd
import requests
from pprint import pprint
import dill

# datafile = './data/GMaps_data_1_10_test.pkd'

# -----------------------------------------------------------------------------
# OPEN GMAPS API SESSION
# -----------------------------------------------------------------------------
# Read API key from file
with open('../API_keys/API_key_GoogleMaps.txt', 'r') as f:
    APIkey = f.read().strip()

# Authenticate/open API session
gmaps = googlemaps.Client(key = APIkey)

# -----------------------------------------------------------------------------
# Get DOHMH restaurant names and info
# -----------------------------------------------------------------------------
df = pd.read_csv('data/raw_data/DOHMH_New_York_City_Restaurant_Inspection_Results.csv',
                    # index_col = 'CAMIS',
                    usecols = ['CAMIS', 'DBA', 'BORO', 'CUISINE DESCRIPTION',
                                # 'INSPECTION DATE',
                                # 'VIOLATION CODE',
                                # 'VIOLATION DESCRIPTION', 'CRITICAL FLAG',
                                # 'SCORE',
                                # 'GRADE',
                                'Latitude', 'Longitude']
)

by_rest = df.groupby([
    'CAMIS', 'DBA', 'BORO', 'CUISINE DESCRIPTION',
    'Latitude', 'Longitude'],
    as_index=False).size()
by_rest = by_rest.sort_values('size', ascending=False, ignore_index=True)

print(f'Total restaurants: {len(by_rest)}')

# -----------------------------------------------------------------------------
# Loop through restaurants and retrieve details from Google Maps
# -----------------------------------------------------------------------------
datalist = []; old_j = 0
for j in range(18000,20000):

    # Restaurant details from df
    rcamis = by_rest.loc[j, 'CAMIS']
    rname = by_rest.loc[j, 'DBA']
    rlat = by_rest.loc[j, 'Latitude']
    rlon = by_rest.loc[j, 'Longitude']
    loc_string = 'point:'+str(rlat)+','+str(rlon)

    # Search restaurant on Maps using name and lat/lon
    rest = gmaps.find_place(
        rname,
        input_type='textquery',
        location_bias=loc_string
        )

    # If no results, store CAMIS and continue
    if len(rest['candidates']) == 0:
        print('**************************************************************')
        print(f'WARNING: Returned no search results for {rname}.')
        print('**************************************************************')
        restdata = {'CAMIS':rcamis}
        continue

    # Get top result details
    restdata = gmaps.place(
        rest['candidates'][0]['place_id'],
        fields = ['name', 'opening_hours', 'type',
            'price_level', 'rating', 'review']
        )

    # Check for errors during query
    if restdata['status'] != 'OK':
        print('***************************************')
        print('WARNING: Status not ''OK''')
        print(restdata['status'])
        print('***************************************')

    # Add CAMIS to restaurant entry dictionary for easy matching
    # with DOHMH data later
    restdata['CAMIS'] = rcamis
    datalist.append(restdata)

    # Status update
    if (j % 100) == 0:
        print(f'Searched {j}/{len(by_rest)} restaurants.')

    # Dump to file
    if (j+1) % 1000 == 0:
        print(f'Dumping entries {old_j}-{j} to file.')
        dill.dump(datalist, open(f'./data/raw_data/gmaps_restaurant_data_{j:05d}.pkd', 'wb'))

        old_j = j
        datalist = []
