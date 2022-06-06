import streamlit as st
import googlemaps
import pandas as pd
import numpy as np


# -----------------------------------------------------------------------------
# SETUP
# -----------------------------------------------------------------------------
# Read API key from file
with open('../API_key_GoogleMaps.txt', 'r') as f:
    APIkey = f.read().strip()

# Authenticate/open API session
gmaps = googlemaps.Client(key = APIkey)

# -----------------------------------------------------------------------------
# MAIN WEBAPP CODE
# -----------------------------------------------------------------------------
st.write("# Remote Restaurant Inspector")
st.write('''Before trying a new restaurant, see what others are saying about
their food safety practices.''')
st.write('---')
# st.write('''''')

search_text = st.text_input('', placeholder='Search Google Maps')

if st.button('Search'):
    # st.write(f'Searching Google Maps for {search_text}...')

    rest = gmaps.find_place(search_text, input_type='textquery')
    restdata = gmaps.place(rest['candidates'][0]['place_id'],
        fields = ['name', 'address_component', 'geometry/location'])
    address_str = restdata['result']['address_components'][0]['short_name'] + \
        ' ' + \
        restdata['result']['address_components'][1]['short_name'] + \
        ', ' + \
        restdata['result']['address_components'][2]['short_name'] + \
        ', ' + \
        restdata['result']['address_components'][3]['short_name'] + \
        ' ' + \
        restdata['result']['address_components'][5]['short_name']

    st.write('### ' + restdata['result']['name'])
    st.write(address_str)


    lat = restdata['result']['geometry']['location']['lat']
    lon = restdata['result']['geometry']['location']['lng']
    df = pd.DataFrame(np.array([[lat, lon]]), columns = ['lat', 'lon'])

    st.map(df, zoom=12, use_container_width=True)



    st.write('### Food safety practices (estimated): POOR')
    st.write("""This restarant's food safety practices are MUCH POORER than
                usual for restaurants of a similar price.""")
    # st.write('## POOR', color='r')

    st.write('#### What diners are saying:')
    st.write('"...shattered glass on a bottom of the wine glass..."')
    st.write('"Dirty, shabby..."')
    st.write('"major NYC HEALTH DEPARTMENT VIOLATOR"')

    # This will handle multiple results and allow user to choose one:
    # if len(rest['candidates']) == 0:
    #     st.write('No results')
    # else:
    #     st.write('Results:')
    #     candidates = rest['candidates'][:5]
    #     st.write(len(candidates))
    #     for j in range(len(rest['candidates'])):
    #         st.write(j)
    #         restdata = gmaps.place(rest['candidates'][j]['place_id'],
    #             fields = ['name', 'geometry/location'])
    #         st.write(restdata['result']['name'])
