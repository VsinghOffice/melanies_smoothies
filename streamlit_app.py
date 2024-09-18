import streamlit as st
import requests
import pandas as pd  # Importing pandas as pd
from snowflake.snowpark.functions import col

# Write directly to the app
st.title("My Parents New Healthy Diner")
st.write("Choose the fruits you want in your custom Smoothie!.")

# Input for the name on the smoothie
name_on_order = st.text_input('Name on smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# Get session and fetch data
cnx = st.connection("snowflake")
session = cnx.session()

# Fetch available fruits and their corresponding SEARCH_ON values
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON')).to_pandas()


# Modify the status to 'FILLED' for the orders you need to mark as filled
# This would need to be managed separately or added as a feature to your Streamlit app if necessary.


# Create a pd_df DataFrame from my_dataframe
pd_df = pd.DataFrame(my_dataframe)

# Ingredient selection
fruit_options = pd_df['FRUIT_NAME'].tolist()  # Display fruits to the user
ingredients_list = st.multiselect("Choose up to 5 ingredients:", fruit_options, max_selections=5)

# API endpoint for Fruityvice
api_url = "https://fruityvice.com/api/fruit/"

if ingredients_list:
    ingredients_string = ' '.join(ingredients_list)
    st.write("Your selected ingredients:", ingredients_string)

    for fruit_chosen in ingredients_list:
        # Get the SEARCH_ON term for the selected fruit using loc and iloc
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit_chosen, ' is ', search_on, '.')

        # Display subheader for the fruit
        st.subheader(f"{fruit_chosen} Nutrition Information")

        # Fetch the data from Fruityvice using the SEARCH_ON value
        try:
            fruityvice_response = requests.get(api_url + search_on.lower())
            if fruityvice_response.status_code == 200:
                # Display the fruit data in a table format
                fv_df = st.dataframe(data=fruityvice_response.json(), use_container_width=True)
            else:
                # If data not found, display a message
                st.write(f"No data found for {fruit_chosen}")
        except Exception as e:
            st.write(f"Error fetching data for {fruit_chosen}: {e}")

    # SQL insert statement
    my_insert_stmt = f"INSERT INTO smoothies.public.orders (ingredients, name_on_order, status) VALUES ('{ingredients_string}', '{name_on_order}', 'UNFILLED')"

    # Button with a unique key to avoid the DuplicateWidgetID issue
    time_to_insert = st.button('Submit Order', key='submit_order')

    # Insert when the button is clicked
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")


# import streamlit as st
# import requests
# from snowflake.snowpark.functions import col

# # Write directly to the app
# st.title("My Parents New Healthy Diner")
# st.write("Choose the fruits you want in your custom Smoothie!.")

# # Input for the name on the smoothie
# name_on_order = st.text_input('Name on smoothie:')
# st.write('The name on your Smoothie will be:', name_on_order)

# # Get session and fetch data
# cnx = st.connection("snowflake")
# session = cnx.session()

# # Fetch available fruits and their corresponding SEARCH_ON values
# fruit_df = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON')).to_pandas()

# # Ingredient selection
# fruit_options = fruit_df['FRUIT_NAME'].tolist()  # Display fruits to the user
# ingredients_list = st.multiselect("Choose up to 5 ingredients:", fruit_options, max_selections=5)

# # API endpoint for Fruityvice
# api_url = "https://fruityvice.com/api/fruit/"

# if ingredients_list:
#     ingredients_string = ' '.join(ingredients_list)
#     st.write("Your selected ingredients:", ingredients_string)

#     for fruit_chosen in ingredients_list:
#         # Get the SEARCH_ON term for the selected fruit
#         search_on = fruit_df.loc[fruit_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]

#         # Display subheader for the fruit
#         st.subheader(f"{fruit_chosen} Nutrition Information")

#         # Fetch the data from Fruityvice using the SEARCH_ON value
#         try:
#             fruityvice_response = requests.get(api_url + search_on.lower())
#             if fruityvice_response.status_code == 200:
#                 # Display the fruit data in a table format
#                 fv_df = st.dataframe(data=fruityvice_response.json(), use_container_width=True)
#             else:
#                 # If data not found, display a message
#                 st.write(f"No data found for {fruit_chosen}")
#         except Exception as e:
#             st.write(f"Error fetching data for {fruit_chosen}: {e}")

#     # SQL insert statement
#     my_insert_stmt = f"INSERT INTO smoothies.public.orders (ingredients, name_on_order) VALUES ('{ingredients_string}', '{name_on_order}')"

#     # Button with a unique key to avoid the DuplicateWidgetID issue
#     time_to_insert = st.button('Submit Order', key='submit_order')

#     # Insert when the button is clicked
#     if time_to_insert:
#         session.sql(my_insert_stmt).collect()
#         st.success('Your Smoothie is ordered!', icon="✅")
