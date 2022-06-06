import streamlit as st
import googlemaps
import pandas as pd
import numpy as np


# -----------------------------------------------------------------------------
# SETUP
# -----------------------------------------------------------------------------
# Read API key from file
with open('../API_keys/API_key_GoogleMaps.txt', 'r') as f:
    APIkey = f.read().strip()

# Authenticate/open API session
gmaps = googlemaps.Client(key = APIkey)

# Load the predictive model
from joblib import load
hugo_model = load('../model/Hugo_model.joblib')

# -----------------------------------------------------------------------------
# HELPFUL FUNCTIONS
# -----------------------------------------------------------------------------
def get_maps_data(query_string):
    rest = gmaps.find_place(
        query_string,
        input_type='textquery',
        # location_bias=loc_string
        )

    # If no results, store CAMIS and continue
    if len(rest['candidates']) == 0:
        print('**************************************************************')
        print(f'No search results for {rname}.')
        print('**************************************************************')

        st.write(f'## No results for search query {rname}')

        return None

    # Get top result details
    restdata = gmaps.place(
        rest['candidates'][0]['place_id'],
        fields = ['name', 'address_component', 'geometry/location',
            'opening_hours', 'type', 'price_level', 'rating', 'review']
        )

    return restdata

def estimate_health_inspection_results(restdata):
    # Convert to pandas dataframe
    maps_rest_data = pd.json_normalize(restdata)[
              ['result.name', 'result.price_level', 'result.rating', 'result.types']
          ].rename(columns = {
              'result.name':'name',
              'result.price_level':'price_level',
              'result.rating':'rating',
              'result.types':'types'
              })

    maps_review_data = pd.json_normalize(
            restdata,
            ['result', 'reviews']#, 'CAMIS'
        ).drop(columns=[
            'author_url',
            'profile_photo_url',
            'relative_time_description'
            ])

    # Convert restaurant types list to string for use with CountVectorizer
    def join_types(type_series):
        joinedtypes = []
        for l in type_series:
            try:
                joinedtypes.append(' '.join(l))
            except:
                joinedtypes.append([])
        return joinedtypes
    maps_rest_data['joinedtypes'] = join_types(maps_rest_data['types'].to_list())

    # Collate reviews and add to restaurant data
    def collate_reviews(review_series):
        review_corpus = []
        for review in review_series:
            review_corpus.append(review)

        review_corpus = ' '.join(review_corpus)

        return [review_corpus]

    maps_rest_data['text'] = collate_reviews(maps_review_data['text'])

    # Predict inspection score
    est_insp_score = hugo_model.predict(maps_rest_data[['rating', 'price_level', 'joinedtypes', 'text']])

    return est_insp_score


# -----------------------------------------------------------------------------
# MAIN WEBAPP CODE
# -----------------------------------------------------------------------------
st.write("# Hugo")
st.write('#### A tool to estimate restaurant health inspection performance based upon Google Maps review data')
# st.write('''Before trying a new restaurant, see what others are saying about
# their food safety practices.''')
st.write('---')
# st.write('''''')

search_text = st.text_input('', placeholder='Search Google Maps')

if st.button('Search'):
    # Search Google Maps for restaurant
    restdata = get_maps_data(search_text)

    if not restdata == None:
        # Display information about top result in the app
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

        st.write('\n\n')

        # Estimate inspection score
        est_insp_score = estimate_health_inspection_results(restdata)

        if est_insp_score <= 13:
            st.write(f'### Estimated health inspection grade: <span style="color:blue">A</span>', unsafe_allow_html=True)
            st.write('This restaurant is estimated to be in satisfactory compliance with food safety guidelines.')
        elif est_insp_score <= 27:
            st.write(f'### Estimated health inspection grade: <span style="color:green">B</span>', unsafe_allow_html=True)
            st.write('This restaurant is estimated to have recent health code violations.')
        elif est_insp_score > 27:
            st.write(f'### Estimated health inspection grade: <span style="color:red">C</span>', unsafe_allow_html=True)
            st.write('This restaurant may be in danger of shutting down due to poor food safety prctices.')

        st.write(f'Estimated NYC DOHMH inspection score: {est_insp_score[0]}')
        st.write('For more information on inspection scores, grades, and guidelines, visit the [NYC DOHMH website](https://www1.nyc.gov/site/doh/business/food-operators/letter-grading-for-restaurants.page)')
