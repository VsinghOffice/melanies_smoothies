import streamlit as st
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col, when_matched
import pandas as pd

# Snowflake connection configuration (Replace these values with your actual credentials)
snowflake_config = {

account = "VAMOAYB.EQ76171"
user = "VSINGH"
password = "Vsingh@17"
role = "SYSADMIN"
warehouse = "COMPUTE_WH"
database = "SMOOTHIES"
schema = "PUBLIC"
client_session_keep_alive = true
}

# Create a Snowflake session
session = Session.builder.configs(snowflake_config).create()

# Title of the app
st.title(":cup_with_straw: Pending Smoothie Orders :cup_with_straw:")
st.write("""Orders that need to be filled.""")

# Fetch data for unfilled orders (ORDER_FILLED = 'UNFILLED')
my_dataframe = session.table("smoothies.public.orders").filter(col("ORDER_FILLED") == 'UNFILLED').select(col('NAME_ON_ORDER'), col('INGREDIENTS')).to_pandas()

# Create a new column for checkboxes to fulfill orders
my_dataframe["Fulfilled"] = False  # Add a column for checkboxes with a default value of False

# Display the dataframe with checkboxes in the 'Fulfilled' column
for index, row in my_dataframe.iterrows():
    fulfilled = st.checkbox(f"Fulfill Order for {row['NAME_ON_ORDER']}", key=index)
    my_dataframe.at[index, "Fulfilled"] = fulfilled  # Update the dataframe based on checkbox input

# Add a submit button
if st.button('Submit'):
    st.success("Submit button clicked.", icon="👍")
    # Filter the orders that are fulfilled
    fulfilled_orders = my_dataframe[my_dataframe['Fulfilled'] == True]
    if not fulfilled_orders.empty:
        # Convert the filtered DataFrame to Snowpark DataFrame for the fulfilled orders
        fulfilled_snowpark_df = session.create_dataframe(fulfilled_orders[['NAME_ON_ORDER']])
        
        # Create the original dataset
        original_dataset = session.table("smoothies.public.orders")
        
        try:
            # Perform the merge operation to update the ORDER_FILLED status
            original_dataset.merge(
                fulfilled_snowpark_df,
                (original_dataset['NAME_ON_ORDER'] == fulfilled_snowpark_df['NAME_ON_ORDER']),
                [when_matched().update({'ORDER_FILLED': 'FILLED'})]
            )._internal_object()  # Trigger the execution of the merge operation
            st.success("Order(s) Updated!", icon="👍")
        except Exception as e:
            st.write(f'Something went wrong: {e}')
    else:
        st.warning("No orders were selected for fulfillment.")

# Display the dataframe for reference (without checkboxes)
st.dataframe(my_dataframe[['NAME_ON_ORDER', 'INGREDIENTS']])
