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
import requests
from snowflake.snowpark.functions import col
 
# Write directly to the app
st.title("My Parents New Healthy Diner")
st.write(
    """Choose the fruits you want in your custom Smoothie!.
    """
)
 
name_on_order = st.text_input('Name on smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)
 
# Get session and fetch data
cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
 
# Ingredient selection
ingredients_list = st.multiselect("Choose up to 5 ingredients:", my_dataframe, max_selections = 5)
 
if ingredients_list:
    ingredients_string = ' '.join(ingredients_list)
    st.write("Your selected ingredients:", ingredients_string)
 
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ''
        st.subheader(fruit_chosen + 'Nutrition Information')
        fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + fruit_chosen)
        fv_df = st.dataframe(data=fruityvice_response.json(), use_container_width=True)
 
    # SQL insert statement
    my_insert_stmt = f"INSERT INTO smoothies.public.orders (ingredients, name_on_order) VALUES ('{ingredients_string}','{name_on_order}')"
    # Button with a unique key to avoid the DuplicateWidgetID issue
    time_to_insert = st.button('Submit Order', key='submit_order')
 
    # Insert when the button is clicked
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")
