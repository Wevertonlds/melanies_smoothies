import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd

# Título do app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Conexão com Snowflake
session = st.connection("snowflake").session()

# Pega FRUIT_NAME e SEARCH_ON do banco
my_dataframe = session.table("smoothies.public.fruit_options").select('FRUIT_NAME', 'SEARCH_ON')
pd_df = my_dataframe.to_pandas()

# Input do nome
name_on_order = st.text_input("Name on Smoothie:", value="Your Name")
st.write(f"The name on your Smoothie will be: {name_on_order}")

# Multiselect com até 5 frutas (só mostra FRUIT_NAME bonitinho)
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    pd_df['FRUIT_NAME'].tolist(),
    max_selections=5
)

# Variável para montar os ingredientes
ingredients_string = ""

if ingredients_list:
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "

        # Pega o SEARCH_ON correto
        search_on_row = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON']
        search_on = search_on_row.iloc[0] if not search_on_row.empty else None

        # Mostra no app (debug bonitinho)
        st.write(f"The search value for **{fruit_chosen}** is `{search_on}`.")

        st.subheader(f"{fruit_chosen} Nutrition Information")

        # Só chama a API se tiver SEARCH_ON válido
        if search_on and pd.notna(search_on):
            smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
            if smoothiefroot_response.status_code == 200:
                sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
            else:
                st.error(f"Sorry, no data for {fruit_chosen} right now.")
        else:
            st.error(f"Sorry, **{fruit_chosen}** is not available in SmoothieFroot yet. Mel is talking to Melanie about it! 😅")

    # Botão de submit
    my_insert_stmt = f"""INSERT INTO smoothies.public.orders (NAME_ON_ORDER, ingredients) 
                        VALUES ('{name_on_order}', '{ingredients_string.strip()}')"""

    if st.button("Submit Order"):
        try:
            session.sql(my_insert_stmt).collect()
            st.success(f"Your smoothie is ordered, {name_on_order}! 🎉", icon="✅")
        except Exception as e:
            st.error(f"Error: {e}")

else:
    st.info("Please select at least one fruit to start building your smoothie! 🍓")
