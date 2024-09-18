import streamlit


streamlit.title('My Mom \'s New Healthy Diner!')

streamlit.header('Breakfast Favorites')
streamlit.text('🥣 Omega 3 & Blueberry Oatmeal')
streamlit.text('🥬 Kale, Spinach & Rocket Smoothie')
streamlit.text('🥚 Hard-Boiled Free-Range Egg')
streamlit.text('🥑🍞Avacado Toast')

streamlit.header('🍌🥭 Build Your Own Fruit Smoothie 🥝🍇')

import pandas
my_fruit_list = pandas.read_csv("https://uni-lab-files.s3.us-west-2.amazonaws.com/dabw/fruit_macros.txt")
my_fruit_list = my_fruit_list.set_index('Fruit')

# Let's put a pick list here so they can pick the fruit they want to include 
fruits_selected = streamlit.multiselect("Pick some fruits:", list(my_fruit_list.index),['Avocado', 'Strawberries'])
fruits_to_show = my_fruit_list.loc[fruits_selected]

# Display the table on the page.
streamlit.dataframe(fruits_to_show)

streamlit.text('🍌🥭Available Fruit🥝🍇')
streamlit.dataframe(my_fruit_list)

# import streamlit as st
# import pandas as pd
# from snowflake.snowpark import Session
# from snowflake.snowpark.functions import col
# import hashlib
# import requests  # Add this to avoid the 'requests not defined' error

# def hash_ingredients(ingredients):
#     return int(hashlib.sha256(ingredients.encode('utf-8')).hexdigest(), 16)

# # Streamlit App title
# st.title("My Parents New Healthy Diner")
# st.write("Choose the Fruits You want in your Smoothie!")

# # Input for the name on the smoothie
# name_on_order = st.text_input("Name on Smoothie:")
# st.write("The name on the Smoothie will be:", name_on_order)

# # Load Snowflake secrets
# try:
#     snowflake_secrets = st.secrets["connections"]["snowflake"]
#     session = Session.builder.configs({
#         "account": snowflake_secrets["account"],
#         "user": snowflake_secrets["user"],
#         "password": snowflake_secrets["password"],
#         "role": snowflake_secrets["role"],
#         "warehouse": snowflake_secrets["warehouse"],
#         "database": snowflake_secrets["database"],
#         "schema": snowflake_secrets["schema"],
#         "client_session_keep_alive": snowflake_secrets.get("client_session_keep_alive", True)
#     }).create()
# except Exception as e:
#     st.error(f"Connection error: {e}")
#     st.stop()

# # Fetch available fruit options from the database
# try:
#     pd_df = session.table("smoothies.public.fruit_options").to_pandas()
#     fruit_options = pd_df['FRUIT_NAME'].tolist()
# except Exception as e:
#     st.error(f"Error fetching data: {e}")
#     st.stop()

# # Multiselect for ingredients
# ingredients_list = st.multiselect('Choose your ingredients (up to 5):', fruit_options)

# # Custom max selection check
# def max_selection(ingredients):
#     if len(ingredients) > 5:
#         st.error("You have selected more than 5 ingredients! Please deselect some to proceed.")
#         return False
#     return True

# if ingredients_list:
#     if not max_selection(ingredients_list):
#         st.warning("Please reduce the number of ingredients to 5 or less.")
# else:
#     st.write("Please select up to 5 ingredients for your smoothie.")

# def get_fruit_data(fruit_name):
#     try:
#         response = requests.get(f"https://fruityvice.com/api/fruit/{fruit_name.lower()}")
#         if response.status_code == 200:
#             return response.json()
#         else:
#             st.error(f"Failed to fetch data for {fruit_name}. Status code: {response.status_code}")
#             return {}
#     except Exception as e:
#         st.error(f"Error fetching or processing fruit data: {e}")
#         return {}

# def create_nutrient_df(fruit_data):
#     try:
#         name = fruit_data.get('name', 'Unknown')
#         id_ = fruit_data.get('id', 'N/A')
#         family = fruit_data.get('family', 'N/A')
#         order = fruit_data.get('order', 'N/A')
#         genus = fruit_data.get('genus', 'N/A')
#         nutrients = fruit_data.get('nutritions', {})

#         data = {
#             'Metric': ['Calories', 'Fat', 'Sugar', 'Protein', 'Carbohydrates', 'Fiber'],
#             'Value': [
#                 nutrients.get('calories', 'N/A'),
#                 nutrients.get('fat', 'N/A'),
#                 nutrients.get('sugar', 'N/A'),
#                 nutrients.get('protein', 'N/A'),
#                 nutrients.get('carbohydrates', 'N/A'),
#                 nutrients.get('fiber', 'N/A')
#             ]
#         }
#         df_nutrients = pd.DataFrame(data)
        
#         df_fruit_info = pd.DataFrame({
#             'Name': [name],
#             'ID': [id_],
#             'Family': [family],
#             'Order': [order],
#             'Genus': [genus]
#         })
        
#         return df_fruit_info, df_nutrients
#     except Exception as e:
#         st.error(f"Error creating nutrient DataFrame: {e}")
#         return pd.DataFrame(), pd.DataFrame()

# if ingredients_list and max_selection(ingredients_list):
#     ingredients_string = ' '.join(ingredients_list)
#     my_insert_stmt = f"""INSERT INTO smoothies.public.orders(name_on_order, ingredients)
#                          VALUES ('{name_on_order}', '{ingredients_string}')"""

#     submitted = st.button('Submit Order')
    
#     if submitted:
#         try:
#             session.sql(my_insert_stmt).collect()
#             st.success('Your Smoothie is ordered!', icon="✅")
#             st.write("SQL Query executed:")
#             st.write(my_insert_stmt)
            
#             # Fetch and format nutrient data for each selected fruit
#             for ingredient in ingredients_list:
#                 search_on = pd_df.loc[pd_df['FRUIT_NAME'] == ingredient, 'SEARCH_ON'].iloc[0]
#                 fruit_data = get_fruit_data(search_on)
#                 if fruit_data:
#                     df_fruit_info, df_nutrients = create_nutrient_df(fruit_data)
                    
#                     # Displaying the fruit information
#                     st.write(f"{fruit_data.get('name')} Nutrition Information")
                    
#                     # Display fruit info
#                     st.write("Fruit Information:")
#                     st.dataframe(df_fruit_info, use_container_width=True)
                    
#                     # Display nutrients
#                     df_nutrients.set_index('Metric', inplace=True)
#                     st.write("Nutritional Information:")
#                     st.dataframe(df_nutrients.T, use_container_width=True)

#         except Exception as e:
#             st.error(f"Error executing query: {e}")
#         st.stop()
