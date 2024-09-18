# import streamlit as st

# from snowflake.snowpark.functions import col
 
# # Write directly to the app

# st.title("My Parents New Healthy Diner")

# st.write(

#     """Choose the fruits you want in your custom Smoothie!.

#     """

# )
 
# name_on_order = st.text_input('Name on smoothie:')

# st.write('The name on your Smoothie will be:', name_on_order)
 
# # Get session and fetch data

# cnx = st.connection("snowflake")

# session = cnx.session()

# my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
 
# # Ingredient selection

# ingredients_list = st.multiselect("Choose up to 5 ingredients:", my_dataframe, max_selections = 5)
 
# if ingredients_list:

#     ingredients_string = ' '.join(ingredients_list)

#     st.write("Your selected ingredients:", ingredients_string)
 
#     # SQL insert statement

#     my_insert_stmt = f"INSERT INTO smoothies.public.orders (ingredients, name_on_order) VALUES ('{ingredients_string}','{name_on_order}')"

#     # Button with a unique key to avoid the DuplicateWidgetID issue

#     time_to_insert = st.button('Submit Order', key='submit_order')
 
#     # Insert when the button is clicked

#     if time_to_insert:

#         session.sql(my_insert_stmt).collect()

#         st.success('Your Smoothie is ordered!', icon="✅")
 
 
# import requests

# fruityvice_response = requests.get("https://fruityvice.com/api/fruit/watermelon")

# #st.text(fruityvice_response.json())

# fv_df = st.dataframe(data=fruityvice_response.json(), use_container_width=True)
 
import streamlit as st
import pandas as pd
import requests
from snowflake.snowpark.functions import col

# App title
st.title("My Parents New Healthy Diner")
st.write("Choose the fruits you want in your custom Smoothie!")

# Input for the name on the smoothie
name_on_order = st.text_input('Name on smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# Get session and fetch data
cnx = st.connection("snowflake")
session = cnx.session()

# Fetching available fruit options from the database
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
ingredients_list = st.multiselect("Choose up to 5 ingredients:", my_dataframe, max_selections=5)

# API endpoint for Fruityvice
api_url = "https://fruityvice.com/api/fruit/"

# Function to get fruit data from Fruityvice API
def get_fruit_data(fruit_name):
    try:
        response = requests.get(f"{api_url}{fruit_name.lower()}")
        if response.status_code == 200:
            return response.json()  # Return the API response as JSON
        else:
            return None  # If the fruit is not found in the API
    except Exception as e:
        return None  # If there's an error, treat it as no data found

# Function to display data as a formatted table
def create_nutrient_table(fruit_name, fruit_data):
    if fruit_data:
        nutrients = fruit_data.get('nutritions', {})
        table_data = {
            'Metric': ['Calories', 'Fat', 'Sugar', 'Protein', 'Carbohydrates', 'Fiber'],
            'Value': [
                nutrients.get('calories', 'null'),
                nutrients.get('fat', 'null'),
                nutrients.get('sugar', 'null'),
                nutrients.get('protein', 'null'),
                nutrients.get('carbohydrates', 'null'),
                nutrients.get('fiber', 'null')
            ]
        }
        df_nutrients = pd.DataFrame(table_data)
        df_nutrients.set_index('Metric', inplace=True)
        
        st.write(f"{fruit_name}'s Nutrition Table")
        st.dataframe(df_nutrients.T, use_container_width=True)
    else:
        st.write(f"{fruit_name}'s Nutrition Table")
        st.write("Data not found in API.")
        st.dataframe(pd.DataFrame({
            'Metric': ['Calories', 'Fat', 'Sugar', 'Protein', 'Carbohydrates', 'Fiber'],
            'Value': ['null', 'null', 'null', 'null', 'null', 'null']
        }).set_index('Metric').T, use_container_width=True)

# Handle form submission
if ingredients_list:
    ingredients_string = ' '.join(ingredients_list)
    st.write("Your selected ingredients:", ingredients_string)

    # Insert order into the database
    my_insert_stmt = f"INSERT INTO smoothies.public.orders (ingredients, name_on_order) VALUES ('{ingredients_string}','{name_on_order}')"
    time_to_insert = st.button('Submit Order', key='submit_order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")

        # Fetch and display nutrient data for each selected fruit
        for ingredient in ingredients_list:
            fruit_data = get_fruit_data(ingredient)
            create_nutrient_table(ingredient, fruit_data)
