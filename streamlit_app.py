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

# Debugging secrets
st.write("Secrets configuration:")
st.write(st.secrets)

# Create a Snowflake session using Streamlit secrets
try:
    session = Session.builder.configs({
        "account": st.secrets["connections.snowflake"]["account"],
        "user": st.secrets["connections.snowflake"]["user"],
        "password": st.secrets["connections.snowflake"]["password"],
        "role": st.secrets["connections.snowflake"]["role"],
        "warehouse": st.secrets["connections.snowflake"]["warehouse"],
        "database": st.secrets["connections.snowflake"]["database"],
        "schema": st.secrets["connections.snowflake"]["schema"],
        "client_session_keep_alive": st.secrets["connections.snowflake"].get("client_session_keep_alive", True)
    }).create()
except KeyError as e:
    st.error(f"Connection error: {e}")
    st.stop()
except Exception as e:
    st.error(f"Unexpected error: {e}")
    st.stop()

# Fetching available fruit options from the database
try:
    my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME')).collect()
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

if ingredients_list:
    if not max_selection(ingredients_list):
        st.warning("Please reduce the number of ingredients to 5 or less.")
else:
    st.write("Please select up to 5 ingredients for your smoothie.")

def get_repeated_fruit_data(num_repeats):
    try:
        fruityvice_response = requests.get("https://fruityvice.com/api/fruit/watermelon")
        fruit_data = fruityvice_response.json()
        repeated_data = [fruit_data] * num_repeats
        df = pd.DataFrame(repeated_data)
        return df
    except Exception as e:
        st.error(f"Error fetching or processing fruit data: {e}")
        return pd.DataFrame()

if ingredients_list and max_selection(ingredients_list):
    ingredients_string = ' '.join(ingredients_list)
    my_insert_stmt = f"""INSERT INTO smoothies.public.orders(name_on_order, ingredients)
                         VALUES ('{name_on_order}', '{ingredients_string}')"""

    submitted = st.button('Submit Order')
    
    if submitted:
        try:
            session.sql(my_insert_stmt).collect()
            st.success('Your Smoothie is ordered!', icon="✅")
            st.write("SQL Query executed:")
            st.write(my_insert_stmt)
            
            num_ingredients = len(ingredients_list)
            df_repeated = get_repeated_fruit_data(num_ingredients)
            st.dataframe(data=df_repeated, use_container_width=True)
        except Exception as e:
            st.error(f"Error executing query: {e}")
        st.stop()
