import streamlit as st
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col
import requests
import pandas as pd  # Import pandas

# Streamlit App title
st.title("My Parents New Healthy Diner")
st.write("Choose the Fruits You want in your Smoothie!")

# Input for the name on the smoothie
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on the Smoothie will be:", name_on_order)

# Load Snowflake secrets and establish a session (as before)
# -- Existing Snowflake connection code here --

# Fetching available fruit options from the database
try:
    my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON')).collect()

    # Convert Snowflake data to Pandas DataFrame
    pd_df = pd.DataFrame([row.as_dict() for row in my_dataframe])  # Converts Snowflake data to Pandas DataFrame
    fruit_options = pd_df['FRUIT_NAME'].tolist()  # Get list of fruit names

except Exception as e:
    st.error(f"Error fetching data: {e}")
    st.stop()

# Multiselect for ingredients
ingredients_list = st.multiselect(
    'Choose your ingredients (up to 5):', 
    fruit_options
)

# Custom max selection check
def max_selection(ingredients):
    if len(ingredients) > 5:
        st.error("You have selected more than 5 ingredients! Please deselect some to proceed.")
        return False
    return True

if ingredients_list:
    if not max_selection(ingredients_list):
        st.warning("Please reduce the number of ingredients to 5 or less.")
else:
    st.write("Please select up to 5 ingredients for your smoothie.")

# Fetch the SEARCH_ON value for the selected fruit
for fruit_chosen in ingredients_list:
    search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
    st.write(f"The search value for {fruit_chosen} is {search_on}.")
