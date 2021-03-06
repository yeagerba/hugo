# Hugo
#### A webapp for predicting restaurant health inspection results using Google Maps data

Created for The Data Incubator capstone project, fulfilling requirements:
1. Clear business objective
  - The webapp allows users to obtain information about the sanitary conditions at food establishments which may not be posted in an easily-accesible format online or in the business.
2. Data ingestion
  - Data was downloaded from the New York City Department of Health and Mental Hygiene as well as from the Google Maps API.
3. Visualizations
  - Several visualizations illustrating model fits to the data are plotted in the model development Jupyter notebook `model/Food Safety Model Development.ipynb`.
4. (a) Machine learning
  - The predictive model uses natural language processing, regression, and cross validation
4. (c) Interactive website
  - The web app allows users to search for a restaurant through Google Maps. Data from the Maps API is then given to the predictive model to provide an estimate of the restaurant's health inspection performance.
5. A deliverable
  - The Jupyter notebook `model/Food Safety Model Development.ipynb` details data processing and development of the model.

### Notes:
- The web app requires a working Google Maps API key, stored in `API_keys/API_key_GoogleMaps.txt`.
- To run the webapp navigate to the 'webapp/' directory and run `streamlit run hugo.py`
- Data used for model training is located in `model/data/raw_data.zip` and must be unzipped before running the model development Jupyter notebook.
