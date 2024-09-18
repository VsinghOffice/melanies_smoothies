import pandas as pd
import streamlit as st
import requests
from snowflake.snowpark.functions import col

# Write directly to the app
st.title("My Parents New Healthy Diner")
st.write(
    """Choose the fruits you want in your custom Smoothie!."""
)

name_on_order = st.text_input('Name on smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# Get session and fetch data
cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
pd_df = my_dataframe.to_pandas()

# Check if the necessary column exists
if 'SEARCH_ON' not in pd_df.columns:
    st.error("The 'SEARCH_ON' column is missing from the data.")
else:
    # Ingredient selection
    ingredients_list = st.multiselect("Choose up to 5 ingredients:", pd_df['FRUIT_NAME'].tolist(), max_selections=5)

    if ingredients_list:
        ingredients_string = ' '.join(ingredients_list)
        st.write("Your selected ingredients:", ingredients_string)

        for fruit_chosen in ingredients_list:
            # Ensure fruit is in DataFrame before accessing
            if fruit_chosen in pd_df['FRUIT_NAME'].values:
                search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
                st.write('The search value for', fruit_chosen, 'is', search_on, '.')
                st.subheader(fruit_chosen + ' Nutrition Information')
                
                # Fetch nutrition information
                api_url = f"https://fruityvice.com/api/fruit/{fruit_chosen.lower()}"
                fruityvice_response = requests.get(api_url)
                
                # Check if the response is valid
                if fruityvice_response.status_code == 200:
                    try:
                        fv_data = fruityvice_response.json()
                        st.dataframe(pd.DataFrame(fv_data), use_container_width=True)
                    except ValueError as e:
                        st.error(f"Failed to parse the nutrition information: {e}")
                else:
                    st.error(f"Failed to fetch nutrition information for {fruit_chosen}. Status code: {fruityvice_response.status_code}. Response: {fruityvice_response.text}")
            else:
                st.warning(f"{fruit_chosen} is not available in the database.")

        # SQL insert statement
        my_insert_stmt = f"INSERT INTO smoothies.public.orders (ingredients, name_on_order) VALUES ('{ingredients_string}', '{name_on_order}')"
        
        # Button with a unique key to avoid the DuplicateWidgetID issue
        time_to_insert = st.button('Submit Order', key='submit_order')

        # Insert when the button is clicked
        if time_to_insert:
            try:
                session.sql(my_insert_stmt).collect()
                st.success('Your Smoothie is ordered!', icon="✅")
            except Exception as e:
                st.error(f"Failed to place the order: {e}")


# import pandas as pd
# import streamlit as st
# import requests
# from snowflake.snowpark.functions import col

# # Write directly to the app
# st.title("My Parents New Healthy Diner")
# st.write(
#     """Choose the fruits you want in your custom Smoothie!."""
# )

# name_on_order = st.text_input('Name on smoothie:')
# st.write('The name on your Smoothie will be:', name_on_order)

# # Get session and fetch data
# cnx = st.connection("snowflake")
# session = cnx.session()
# my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
# pd_df = my_dataframe.to_pandas()

# # Check if the necessary column exists
# if 'SEARCH_ON' not in pd_df.columns:
#     st.error("The 'SEARCH_ON' column is missing from the data.")
# else:
#     # Ingredient selection
#     ingredients_list = st.multiselect("Choose up to 5 ingredients:", pd_df['FRUIT_NAME'].tolist(), max_selections=5)

#     if ingredients_list:
#         ingredients_string = ' '.join(ingredients_list)
#         st.write("Your selected ingredients:", ingredients_string)

#         for fruit_chosen in ingredients_list:
#             # Ensure fruit is in DataFrame before accessing
#             if fruit_chosen in pd_df['FRUIT_NAME'].values:
#                 search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
#                 st.write('The search value for', fruit_chosen, 'is', search_on, '.')
#                 st.subheader(fruit_chosen + ' Nutrition Information')
                
#                 # Fetch nutrition information
#                 fruityvice_response = requests.get(f"https://fruityvice.com/api/fruit/{fruit_chosen}")
                
#                 # Check if the response is valid
#                 if fruityvice_response.status_code == 200:
#                     fv_data = fruityvice_response.json()
#                     st.dataframe(pd.DataFrame(fv_data), use_container_width=True)
#                 else:
#                     st.error(f"Failed to fetch nutrition information for {fruit_chosen}.")
#             else:
#                 st.warning(f"{fruit_chosen} is not available in the database.")

#         # SQL insert statement
#         my_insert_stmt = f"INSERT INTO smoothies.public.orders (ingredients, name_on_order) VALUES ('{ingredients_string}', '{name_on_order}')"
        
#         # Button with a unique key to avoid the DuplicateWidgetID issue
#         time_to_insert = st.button('Submit Order', key='submit_order')

#         # Insert when the button is clicked
#         if time_to_insert:
#             try:
#                 session.sql(my_insert_stmt).collect()
#                 st.success('Your Smoothie is ordered!', icon="✅")
#             except Exception as e:
#                 st.error(f"Failed to place the order: {e}")

# import streamlit as st
# from snowflake.snowpark.context import get_active_session
# from snowflake.snowpark.functions import col, when_matched
# import pandas as pd
 
# # Title of the app
# st.title(":cup_with_straw: Pending Smoothie Orders :cup_with_straw:")
# st.write("""Orders that need to be filled.""")
 
# # Get the Snowflake session
# session = get_active_session()
 
# # Fetch data for unfilled orders (ORDER_FILLED = FALSE)
# my_dataframe = session.table("smoothies.public.orders").filter(col("ORDER_FILLED") == False).select(col('NAME_ON_ORDER'), col('INGREDIENTS')).to_pandas()
 
# # Create a new column for checkboxes to fulfill orders
# my_dataframe["Fulfilled"] = False  # Add a column for checkboxes with a default value of False
 
# # Display the dataframe with checkboxes in the 'Fulfilled' column
# for index, row in my_dataframe.iterrows():
#     fulfilled = st.checkbox(f"Fulfill Order for {row['NAME_ON_ORDER']}", key=index)
#     my_dataframe.at[index, "Fulfilled"] = fulfilled  # Update the dataframe based on checkbox input
 
# # Add a submit button
# if st.button('Submit'):
#     st.success("Submit button clicked.", icon="👍")
#     # Filter the orders that are fulfilled
#     fulfilled_orders = my_dataframe[my_dataframe['Fulfilled'] == True]
#     if not fulfilled_orders.empty:
#         # Convert the filtered DataFrame to Snowpark DataFrame for the fulfilled orders
#         fulfilled_snowpark_df = session.create_dataframe(fulfilled_orders[['NAME_ON_ORDER']])
 
#         # Create the original dataset
#         original_dataset = session.table("smoothies.public.orders")
 
#         try:
#             # Perform the merge operation to update the ORDER_FILLED status
#             original_dataset.merge(
#                 fulfilled_snowpark_df,
#                 (original_dataset['NAME_ON_ORDER'] == fulfilled_snowpark_df['NAME_ON_ORDER']),
#                 [when_matched().update({'ORDER_FILLED': True})]
#             )._internal_object()  # Trigger the execution of the merge operation
#             st.success("Order(s) Updated!", icon="👍")
#         except Exception as e:
#             st.write(f'Something went wrong: {e}')
#     else:
#         st.warning("No orders were selected for fulfillment.")
 
# # Display the dataframe for reference (without checkboxes)
# st.dataframe(my_dataframe[['NAME_ON_ORDER', 'INGREDIENTS']])
