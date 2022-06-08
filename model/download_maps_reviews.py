'''
This code searches Google Maps for restaurants in NYC DOHMH dataset and
downloads matching restaurant details and reviews.

The script is called from the command line via

    python3 download_maps_reviews.py <nreviews>

where <nreviews> is the number of reviews to download. ***Note
that the Google Maps API is not 100% free. Take care not download more than
you want to pay for beyond the monthly free allowance!***

In order to run this code, you will need a working Google Maps API key stored
in ../API_keys/API_key_GoogleMaps_build.txt.

This code also requires the NY DOHMH dataset to be downloaded first and stored
in ./data/raw_data/DOHMH_New_York_City_Restaurant_Inspection_Results.csv.
'''
import googlemaps
import pandas as pd
import argparse
# import requests
import dill

# -----------------------------------------------------------------------------
# PARSE INPUT
# -----------------------------------------------------------------------------
parser = argparse.ArgumentParser(
    prog = 'ProgramName',
    description = 'What the program does',
    epilog = 'Text at the bottom of help',
)
parser.add_argument('num_establishments', type=int)
args = parser.parse_args()

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
                                'Latitude', 'Longitude']
)

# Sort restaurants by length of inspection history - let's get the restaurants
# with the most data first
rest_df = df.groupby([
    'CAMIS', 'DBA', 'BORO', 'CUISINE DESCRIPTION',
    'Latitude', 'Longitude'],
    as_index=False).size()
rest_df = rest_df.sort_values('size', ascending=False, ignore_index=True)

print(f'\nTotal inspected establishments: {len(rest_df)}')

# -----------------------------------------------------------------------------
# Get list of restaurants to search for
# -----------------------------------------------------------------------------
# CAMIS IDs in existing Maps data - don't re-search these
import glob
maps_data_files = sorted(glob.glob('data/raw_data/gmaps_restaurant_data_*.pkd'))
known_CAMIS = []
for file in maps_data_files:
    f = open(file, 'rb')
    maps_data = dill.load(f)
    known_CAMIS.extend(pd.json_normalize(maps_data)['CAMIS'].to_list())
nknown = len(known_CAMIS)
print(f'Previously downloaded Maps establishments: {nknown}')

# Limit to establishments whose data we don't already have
rest_df = rest_df[~rest_df['CAMIS'].isin(known_CAMIS)]
# Limit number of establishments to designated number
rest_df = rest_df.iloc[:args.num_establishments]

# -----------------------------------------------------------------------------
# Loop through restaurants and retrieve details from Google Maps
# -----------------------------------------------------------------------------
print(f'Searching for {args.num_establishments} additional establishments\n')
datalist = []; #old_j = 0
for j, row in rest_df.iterrows():
    # print(row)
    # print('\n')

    # Restaurant details from df
    rcamis = row['CAMIS']
    rname = row['DBA']
    rlat = row['Latitude']
    rlon = row['Longitude']
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
    # if ((j-nknown) / args.num_establishments)*100 % 5 == 0:
    print(f'Progress: {((j-nknown+1)/args.num_establishments)*100} %', end='\r')

    # Dump to file
    fname = f'./data/raw_data/gmaps_restaurant_data_{len(known_CAMIS)}-{len(known_CAMIS)+args.num_establishments-1}.pkd'
    dill.dump(datalist, open(fname, 'wb'))
