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
            fruit_data = response.json()
            return fruit_data
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
        order = fruit_data.get('order', 'N/A')
        genus = fruit_data.get('genus', 'N/A')
        nutrients = fruit_data.get('nutritions', {})

        # Create DataFrame in the specified format
        data = {
            'Metric': ['Calories', 'Fat', 'Sugar', 'Protein', 'Carbohydrates', 'Fiber'],
            'Value': [
                nutrients.get('calories', 'N/A'),
                nutrients.get('fat', 'N/A'),
                nutrients.get('sugar', 'N/A'),
                nutrients.get('protein', 'N/A'),
                nutrients.get('carbohydrates', 'N/A'),
                nutrients.get('fiber', 'N/A')
            ]
        }
        df_nutrients = pd.DataFrame(data)
        
        # Create a DataFrame with the required format
        df_final = pd.DataFrame({
            'Name': [name],
            'ID': [id_],
            'Family': [family],
            'Order': [order],
            'Genus': [genus],
            'Calories': [nutrients.get('calories', 'N/A')],
            'Fat': [nutrients.get('fat', 'N/A')],
            'Sugar': [nutrients.get('sugar', 'N/A')],
            'Protein': [nutrients.get('protein', 'N/A')],
            'Carbohydrates': [nutrients.get('carbohydrates', 'N/A')],
            'Fiber': [nutrients.get('fiber', 'N/A')]
        })
        
        # Set proper column order
        df_final = df_final[['Name', 'ID', 'Family', 'Order', 'Genus', 'Calories', 'Fat', 'Sugar', 'Protein', 'Carbohydrates', 'Fiber']]
        
        return df_final
    except Exception as e:
        st.error(f"Error creating nutrient DataFrame: {e}")
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
            
            # Fetch and format nutrient data for each selected fruit
            for ingredient in ingredients_list:
                fruit_data = get_fruit_data(ingredient)
                if fruit_data:
                    df_nutrients = create_nutrient_df(fruit_data)
                    
                    # Displaying the nutrient information for each fruit
                    st.write(f"{fruit_data.get('name')} Nutrition Information")
                    st.dataframe(df_nutrients, use_container_width=True)

        except Exception as e:
            st.error(f"Error executing query: {e}")
        st.stop()
