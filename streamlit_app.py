# Import python packages
# Import python packages
import streamlit as st
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col
import requests
import pandas as pd

# Streamlit App title
st.title("My Parents New Healthy Diner")
st.write("Choose the Fruits You want in your Smoothie!")

# Input for the name on the smoothie
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on the Smoothie will be:", name_on_order)

# Create a Snowflake session using secrets
try:
    session = Session.builder.configs({
        "user": st.secrets["Snowflake"]["user"],
        "password": st.secrets["Snowflake"]["password"],
        "account": st.secrets["Snowflake"]["account"],
        "warehouse": st.secrets["Snowflake"]["warehouse"],
        "database": st.secrets["Snowflake"]["database"],
        "schema": st.secrets["Snowflake"]["schema"]
    }).create()
except KeyError as e:
    st.error(f"Connection error: {e}")
    st.stop()

# Fetching available fruit options from the database
try:
    my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME')).collect()
    # List of fruit options
    fruit_options = [row['FRUIT_NAME'] for row in my_dataframe]
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

# Check if the user has selected more than 5 ingredients
if ingredients_list:
    if not max_selection(ingredients_list):
        st.warning("Please reduce the number of ingredients to 5 or less.")
else:
    st.write("Please select up to 5 ingredients for your smoothie.")

# Function to repeat watermelon data based on the number of ingredients chosen
def get_repeated_fruit_data(num_repeats):
    try:
        # Fetch watermelon data
        fruityvice_response = requests.get("https://fruityvice.com/api/fruit/watermelon")
        fruit_data = fruityvice_response.json()
        
        # Repeat the data
        repeated_data = fruit_data * num_repeats
        
        # Convert to DataFrame
        df = pd.DataFrame(repeated_data)
        return df
    except Exception as e:
        st.error(f"Error fetching or processing fruit data: {e}")
        return pd.DataFrame()

# Allow Submit button only if the selection is valid
if ingredients_list and max_selection(ingredients_list):
    ingredients_string = ' '.join(ingredients_list)
    
    # Insert statement to store the smoothie order
    my_insert_stmt = f"""INSERT INTO smoothies.public.orders(name_on_order, ingredients)
                         VALUES ('{name_on_order}', '{ingredients_string}')"""

    # Submit button for order
    submitted = st.button('Submit Order')
    
    if submitted:
        try:
            # Execute the SQL query to insert the order
            session.sql(my_insert_stmt).collect()
            st.success('Your Smoothie is ordered!', icon="✅")
            st.write("SQL Query executed:")
            st.write(my_insert_stmt)
            
            # Display repeated watermelon data based on selected ingredients
            num_ingredients = len(ingredients_list)
            df_repeated = get_repeated_fruit_data(num_ingredients)
            st.dataframe(data=df_repeated, use_container_width=True)
        except Exception as e:
            st.error(f"Error executing query: {e}")
        st.stop()



# # Import required packages
# import streamlit as st
# from snowflake.snowpark import Session
# from snowflake.snowpark.functions import col
# import requests
# # Streamlit App title
# st.title("My Parents New Healthy Diner")
# st.write("Choose the Fruits You want in your Smoothie!")

# # Input for the name on the smoothie
# name_on_order = st.text_input("Name on Smoothie:")
# st.write("The name on the Smoothie will be:", name_on_order)

# # Get the Snowflake connection
# try:
#     cnx = st.connection("snowflake")  # Ensure connection name is lowercase
#     # Create a Snowflake session using Streamlit's connection
#     session = cnx.session()
# except KeyError as e:
#     st.error(f"Connection error: {e}")
#     st.stop()

# # Fetching available fruit options from the database
# try:
#     my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME')).collect()
#     # List of fruit options
#     fruit_options = [row['FRUIT_NAME'] for row in my_dataframe]
# except Exception as e:
#     st.error(f"Error fetching data: {e}")
#     st.stop()

# # Multiselect for ingredients
# ingredients_list = st.multiselect(
#     'Choose your ingredients (up to 5):', 
#     fruit_options
# )

# # Custom max selection check
# def max_selection(ingredients):
#     if len(ingredients) > 5:
#         st.error("You have selected more than 5 ingredients! Please deselect some to proceed.")
#         return False
#     return True

# # Check if the user has selected more than 5 ingredients
# if ingredients_list:
#     if not max_selection(ingredients_list):
#         st.warning("Please reduce the number of ingredients to 5 or less.")
# else:
#     st.write("Please select up to 5 ingredients for your smoothie.")

# # Allow Submit button only if the selection is valid
# if ingredients_list and max_selection(ingredients_list):
#     ingredients_string = ' '.join(ingredients_list)
    
#     # Insert statement to store the smoothie order
#     my_insert_stmt = f"""INSERT INTO smoothies.public.orders(name_on_order, ingredients)
#                          VALUES ('{name_on_order}', '{ingredients_string}')"""

#     # Submit button for order
#     submitted = st.button('Submit Order')
    
#     if submitted:
#         try:
#             # Execute the SQL query to insert the order
#             session.sql(my_insert_stmt).collect()
#             st.success('Your Smoothie is ordered!', icon="✅")
#             st.write("SQL Query executed:")
#             st.write(my_insert_stmt)
#         except Exception as e:
#             st.error(f"Error executing query: {e}")
#         st.stop()

# fruityvice_response = requests.get("https://fruityvice.com/api/fruit/watermelon")
# # st.text(fruityvice_response.json())
# fv_df = st.dataframe(data=fruityvice_response.json(),use_container_width=True)


