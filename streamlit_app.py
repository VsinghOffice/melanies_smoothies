import streamlit as st
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col
import pandas as pd
import requests

# Streamlit App title
st.title("My Parents New Healthy Diner")
st.write("Choose the Fruits You want in your Smoothie!")

# Input for the name on the smoothie
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on the Smoothie will be:", name_on_order)

# Load Snowflake secrets
try:
    snowflake_secrets = st.secrets["connections"]["snowflake"]

    # Ensure all required keys are present
    required_keys = ["account", "user", "password", "role", "warehouse", "database", "schema", "client_session_keep_alive"]
    for key in required_keys:
        if key not in snowflake_secrets:
            st.error(f"Missing secret key: {key}")
            st.stop()

    # Create Snowflake session
    session = Session.builder.configs({
        "account": snowflake_secrets["account"],
        "user": snowflake_secrets["user"],
        "password": snowflake_secrets["password"],
        "role": snowflake_secrets["role"],
        "warehouse": snowflake_secrets["warehouse"],
        "database": snowflake_secrets["database"],
        "schema": snowflake_secrets["schema"],
        "client_session_keep_alive": snowflake_secrets.get("client_session_keep_alive", True)
    }).create()

except KeyError as e:
    st.error(f"Connection error: Missing secret key: {e}")
    st.stop()
except AttributeError as e:
    st.error(f"Attribute error: {e}")
    st.stop()
except Exception as e:
    st.error(f"Unexpected error: {e}")
    st.stop()

# Fetching available fruit options from the database
try:
    my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME')).collect()
    fruit_options = [row['FRUIT_NAME'] for row in my_dataframe]
    
    # Convert to Pandas dataframe
    pd_df = pd.DataFrame([row.as_dict() for row in my_dataframe])
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

def get_fruit_data(fruit_name):
    try:
        response = requests.get(f"https://fruityvice.com/api/fruit/{fruit_name.lower()}")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to fetch data for {fruit_name}. Status code: {response.status_code}")
            return {}
    except Exception as e:
        st.error(f"Error fetching or processing fruit data: {e}")
        return {}

def create_nutrient_df(fruit_data):
    try:
        # Extract fruit info
        name = fruit_data.get('name', 'Unknown')
        id_ = fruit_data.get('id', 'N/A')
        family = fruit_data.get('family', 'N/A')
        genus = fruit_data.get('genus', 'N/A')
        nutrients = fruit_data.get('nutritions', {})

        # Create a DataFrame with fruit info and nutrients
        df_fruit_info = pd.DataFrame({
            'Name': [name],
            'ID': [id_],
            'Family': [family],
            'Genus': [genus]
        })

        df_nutrients = pd.DataFrame({
            'Metric': ['Calories', 'Fat', 'Sugar', 'Protein', 'Carbohydrates'],
            'Value': [
                nutrients.get('calories', 'N/A'),
                nutrients.get('fat', 'N/A'),
                nutrients.get('sugar', 'N/A'),
                nutrients.get('protein', 'N/A'),
                nutrients.get('carbohydrates', 'N/A')
            ]
        })
        
        return df_fruit_info, df_nutrients
    except Exception as e:
        st.error(f"Error creating nutrient DataFrame: {e}")
        return pd.DataFrame(), pd.DataFrame()

# Add column SEARCH_ON in DataFrame
if "SEARCH_ON" not in pd_df.columns:
    pd_df["SEARCH_ON"] = pd_df["FRUIT_NAME"]

# For selected fruits
if ingredients_list and max_selection(ingredients_list):
    ingredients_string = ', '.join(ingredients_list)
    my_insert_stmt = f"""INSERT INTO smoothies.public.orders(name_on_order, ingredients, STATUS)
                         VALUES ('{name_on_order}', '{ingredients_string}', 'UNFILLED')"""

    submitted = st.button('Submit Order')
    
    if submitted:
        try:
            session.sql(my_insert_stmt).collect()
            st.success('Your Smoothie is ordered!', icon="✅")
            st.write("SQL Query executed:")
            st.write(my_insert_stmt)
            
            # Fetch and format nutrient data for each selected fruit
            for ingredient in ingredients_list:
                search_on = pd_df.loc[pd_df['FRUIT_NAME'] == ingredient, 'SEARCH_ON'].iloc[0]
                st.write(f"The search value for {ingredient} is {search_on}.")
                fruit_data = get_fruit_data(search_on)
                if fruit_data:
                    df_fruit_info, df_nutrients = create_nutrient_df(fruit_data)
                    
                    # Displaying the fruit information
                    st.write(f"{fruit_data.get('name')} Nutrition Information")
                    
                    # Display fruit info
                    st.dataframe(df_fruit_info, use_container_width=True)
                    
                    # Display nutrients in formatted table
                    st.write("Nutritional Information:")
                    st.dataframe(df_nutrients.set_index('Metric').T, use_container_width=True)

        except Exception as e:
            st.error(f"Error executing query: {e}")
        st.stop()
import hashlib

def hash_ingredients(ingredients):
    # Hash the ingredients string using SHA256
    return int(hashlib.sha256(ingredients.encode('utf-8')).hexdigest(), 16)

# Examples of ingredients
print(hash_ingredients("Apples, Lime, Ximenia"))
print(hash_ingredients("Dragon Fruit, Guava, Figs, Jackfruit, Blueberries"))
print(hash_ingredients("Vanilla Fruit, Nectarine"))
