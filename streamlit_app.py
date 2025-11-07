import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd  # Importando pandas como pd

# App title
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Snowflake connection
cnx = st.connection("snowflake")
session = cnx.session()

# Fetch available fruits with SEARCH_ON into a pandas DataFrame
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
pd_df = my_dataframe.to_pandas()  # Criando a versão pd_df a partir de my_dataframe

# Text input for the name
name_on_order = st.text_input("Name on Smoothie:", value="Your Name")
st.write(f"The name on your Smoothie will be: {name_on_order}")

# Multiselect widget for choosing fruits with max 5 selections
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    pd_df['FRUIT_NAME'].tolist(),  # Usando FRUIT_NAME de pd_df para exibição
    max_selections=5,
    default=["Tangerine", "Kiwi", "Lime", "Mango", "Strawberries"]  # Default selection
)

# Display selected fruits if the list is not empty
if ingredients_list:
    ingredients_string = ""
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "
        st.subheader(fruit_chosen + " Nutrition Information")
        # Usando loc e iloc para pegar o valor de SEARCH_ON
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit_chosen, ' is ', search_on, '.')
        smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
        try:
            sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
        except:
            st.error("Sorry, that fruit is not in our database.")

    # SQL statement for insertion after building ingredients_string
    my_insert_stmt = f"""INSERT INTO smoothies.public.orders (NAME_ON_ORDER, ingredients) VALUES ('{name_on_order}', '{ingredients_string}')"""
    if st.button("Submit Order"):
        try:
            session.sql(my_insert_stmt).collect()
            st.success(f'Your smoothie is ordered, {name_on_order}!', icon="✅")
        except Exception as e:
            st.error(f"Error inserting into the database: {e}")
else:
    st.write("You can only select up to 5 options. Remove an option first." if len(ingredients_list) > 5 else "")
