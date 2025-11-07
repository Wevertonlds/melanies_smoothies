import streamlit as st
from snowflake.snowpark.functions import col
import requests

# App title
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Snowflake connection
cnx = st.connection("snowflake")
session = cnx.session()

# Fetch available fruits
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))

# Text input for the name
name_on_order = st.text_input("Name on Smoothie:", value="Your Name")
st.write(f"The name on your Smoothie will be: {name_on_order}")

# Multiselect widget for choosing fruits with max 5 selections
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    [row[0] for row in my_dataframe.collect()],  # Extract FRUIT_NAME as strings
    max_selections=5,
    default=[]  # No default selection to start
)

# Display selected fruits if the list is not empty
if ingredients_list:
    ingredients_string = ' '.join(ingredients_list)  # Join fruits with a space
    # SQL statement for insertion
    my_insert_stmt = f"""INSERT INTO smoothies.public.orders (NAME_ON_ORDER, ingredients) VALUES ('{name_on_order}', '{ingredients_string}')"""
    # Trigger insert and success message on button click
    if st.button("Submit Order"):
        try:
            session.sql(my_insert_stmt).collect()
            st.success(f'Your smoothie is ordered, {name_on_order}!', icon="✅")
            # Iterate over chosen fruits and call the API
            for fruit_chosen in ingredients_list:
                smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{fruit_chosen}")
                if smoothiefroot_response.status_code == 200:
                    st.subheader(f"{fruit_chosen} Nutrition Information")
                    sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
                else:
                    st.error(f"Sorry, that fruit is not in our database.")
        except Exception as e:
            st.error(f"Error inserting into the database: {e}")
else:
    st.write("You can only select up to 5 options. Remove an option first." if len(ingredients_list) > 5 else "")
