# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write(
    """Choose the fruits you want in your custom Smoothie!"""
)
# Snowflake connection setup
cnx = st.connection("snowflake")
session = cnx.session()

# Get the active Snowflake session and fetch fruit names
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
# Add text input for the name
name_on_order = st.text_input("Name on Smoothie:", value="Your Name")
st.write(f"The name on your smoothie will be: {name_on_order}")
# Multiselect widget for choosing fruits with max 5 selections
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    [row[0] for row in my_dataframe.collect()], # Extract FRUIT_NAME as strings
    max_selections=5,
    default=[] # No default selection to start
)
# Display selected fruits if the list is not empty
if ingredients_list:
    ingredients_string = ' '.join(ingredients_list) # Join fruits with a space
    # SQL statement for insertion (not displayed by default)
    my_insert_stmt = f"""INSERT INTO smoothies.public.orders (NAME_ON_ORDER, ingredients) VALUES ('{name_on_order}', '{ingredients_string}')"""
    # Trigger insert and success message on button click
    if st.button("Submit Order"):
        try:
            session.sql(my_insert_stmt).collect()
            st.success(f'Your smoothie is ordered, {name_on_order}!', icon="✅")
        except Exception as e:
            st.error(f"Error inserting into the database: {e}")
else:
    st.write("You can only select up to 5 options. Remove an option first." if len(ingredients_list) > 5 else "")
