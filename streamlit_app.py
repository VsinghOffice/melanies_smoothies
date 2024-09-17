import streamlit as st
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col
import pandas as pd  # Import pandas
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
    # Fetching fruit options including the new SEARCH_ON column
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

# Submit button for order
if ingredients_list and max_selection(ingredients_list):
    ingredients_string = ', '.join(ingredients_list)
    my_insert_stmt = f"""
    INSERT INTO smoothies.public.orders(name_on_order, ingredients)
    VALUES ('{name_on_order}', '{ingredients_string}')
    """

    submitted = st.button('Submit Order')
    
    if submitted:
        try:
            session.sql(my_insert_stmt).collect()
            st.success('Your Smoothie is ordered!', icon="✅")
            st.write("SQL Query executed:")
            st.write(my_insert_stmt)
            
            # Fetch and format nutrient data for each selected fruit (optional, assuming we have an API)
            for ingredient in ingredients_list:
                fruit_data = get_fruit_data(ingredient)  # Optional API call
                if fruit_data:
                    df_fruit_info, df_nutrients = create_nutrient_df(fruit_data)  # Assuming API integration
                    
                    # Displaying the fruit information
                    st.write(f"{fruit_data.get('name')} Nutrition Information")
                    
                    # Display fruit info
                    st.write("Fruit Information:")
                    st.dataframe(df_fruit_info, use_container_width=True)
                    
                    # Display nutrients
                    st.write("Nutritional Information:")
                    st.dataframe(df_nutrients.set_index('Metric').T, use_container_width=True)

        except Exception as e:
            st.error(f"Error executing query: {e}")
        st.stop()

# Function to create orders (for DORA check)
def create_order(name, fruits, filled=False):
    ingredients_string = ', '.join(fruits)
    fill_status = 'FILLED' if filled else 'UNFILLED'
    
    insert_stmt = f"""
    INSERT INTO smoothies.public.orders(name_on_order, ingredients, status)
    VALUES ('{name}', '{ingredients_string}', '{fill_status}')
    """
    
    try:
        session.sql(insert_stmt).collect()
        st.success(f"Order created for {name} with fruits: {ingredients_string}. Status: {fill_status}", icon="✅")
    except Exception as e:
        st.error(f"Error executing query: {e}")

# Orders for DORA Check
create_order("Kevin", ["Apples", "Lime", "Ximenia"])  # Kevin's order, not filled
create_order("Divya", ["Dragon Fruit", "Guava", "Figs", "Jackfruit", "Blueberries"], filled=True)  # Divya's order, filled
create_order("Xi", ["Vanilla Fruit", "Nectarine"], filled=True)  # Xi's order, filled
