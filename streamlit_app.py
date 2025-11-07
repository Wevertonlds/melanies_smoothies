import streamlit as st
from snowflake.snowpark.functions import col, upper
import requests
import pandas as pd

# ================================== TÍTULO ==================================
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# ============================= CONEXÃO SNOWFLAKE ============================
cnx = st.connection("snowflake")
session = cnx.session()

# ======================= CRIA O DATAFRAME COM SEARCH_ON =====================
# <-- AQUI É O DESAFIO: adiciona a coluna SEARCH_ON em maiúsculas
my_dataframe = session.table("smoothies.public.fruit_options") \
    .select(col("FRUIT_NAME")) \
    .withColumn("SEARCH_ON", upper(col("FRUIT_NAME")))

# Converte para pandas (necessário pro multiselect)
pd_df = my_dataframe.to_pandas()

# DEBUG OPCIONAL: descomente as 2 linhas abaixo pra ver o DataFrame com SEARCH_ON
# st.write("DEBUG: pd_df com a coluna SEARCH_ON criada")
# st.dataframe(pd_df)

# ========================== NOME DO SMOOTHIE ================================
name_on_order = st.text_input("Name on Smoothie:", value="Your Name")
st.write(f"The name on your Smoothie will be: **{name_on_order}**")

# ========================== MULTISELECT DE FRUTAS ==========================
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    pd_df["FRUIT_NAME"].tolist(),
    max_selections=5,
    default=["Tangerine", "Kiwi", "Lime", "Mango", "Strawberries"]
)

# ========================= EXIBE INFORMAÇÕES DAS FRUTAS =====================
if ingredients_list:
    ingredients_string = ""

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "

        st.subheader(f"{fruit_chosen} Nutrition Information")

        # Pega o valor de SEARCH_ON correspondente (em maiúsculas)
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write(f"The search value for **{fruit_chosen}** is **{search_on}**.")

        # Chama a API do SmoothieFroot
        response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")

        if response.status_code == 200:
            data = response.json()
            # A API retorna uma lista com um dicionário, então pegamos o primeiro
            nutrition_df = pd.DataFrame(data[0]["nutritions"].items(), columns=["Nutrient", "Amount"])
            st.dataframe(nutrition_df, use_container_width=True)
        else:
            st.error(f"Sorry, no nutrition info found for {fruit_chosen}.")

    # ============================ INSERT SEGURO NO BANCO ========================
    # Monta a string só das frutas (sem o espaço no final)
    ingredients_string = ingredients_string.strip()

    my_insert_stmt = """
        INSERT INTO smoothies.public.orders (NAME_ON_ORDER, INGREDIENTS)
        VALUES (%s, %s)
    """

    if st.button("Submit Order"):
        try:
            # USANDO PARÂMETROS (evita SQL injection e passa no validador do lab)
            session.sql(my_insert_stmt, params=[name_on_order, ingredients_string]).collect()
            st.success(f"Your Smoothie is ordered, {name_on_order}! 🎉", icon="✅")
        except Exception as e:
            st.error(f"Error inserting order: {e}")

else:
    st.info("Please select at least one fruit to continue.")
