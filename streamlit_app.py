import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd

st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

session = st.connection("snowflake").session()

# Pega os dados com SEARCH_ON
my_dataframe = session.table("smoothies.public.fruit_options").select('FRUIT_NAME', 'SEARCH_ON')
pd_df = my_dataframe.to_pandas()

name_on_order = st.text_input("Name on Smoothie:", value="Your Name")
st.write(f"The name on your Smoothie will be: {name_on_order}")

ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    pd_df['FRUIT_NAME'].tolist(),
    max_selections=5
)

ingredients_string = ""

if ingredients_list:
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "

        # ←←← EXATAMENTE O CÓDIGO DO PRINT ←←←
        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write(f"The search value for {fruit_chosen} is {search_on}.")

        st.subheader(fruit_chosen + " Nutrition Information")
        smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

    # Submit
    my_insert_stmt = f"""INSERT INTO smoothies.public.orders (NAME_ON_ORDER, ingredients) 
                        VALUES ('{name_on_order}', '{ingredients_string.strip()}')"""

    if st.button("Submit Order"):
        session.sql(my_insert_stmt).collect()
        st.success(f"Your smoothie is ordered, {name_on_order}! 🎉", icon="✅")
