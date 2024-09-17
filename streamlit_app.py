# Import python packages
import streamlit as st
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col

# Streamlit App title
st.title("My Parents New Healthy Diner")
st.write("Choose the Fruits You want in your Smoothie!")

# Input for the name on the smoothie
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on the Smoothie will be:", name_on_order)

# Get the Snowflake connection
try:
    cnx = st.connection("Snowflake")
    # Create a Snowflake session using Streamlit's connection
    session = cnx.session()
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
        except Exception as e:
            st.error(f"Error executing query: {e}")
        st.stop()
