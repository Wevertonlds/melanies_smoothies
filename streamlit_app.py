import streamlit as st
from snowflake.snowpark.functions import col, upper
import pandas as pd  # <-- IMPORTAÇÃO OBRIGATÓRIA DO DESAFIO (como pd)

# ================================== TÍTULO ==================================
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# ============================= CONEXÃO SNOWFLAKE ============================
cnx = st.connection("snowflake")
session = cnx.session()

# ======================= DATAFRAME COM SEARCH_ON EM MAIÚSCULAS ==============
my_dataframe = session.table("smoothies.public.fruit_options") \
    .select(col("FRUIT_NAME")) \
    .withColumn("SEARCH_ON", upper(col("FRUIT_NAME")))

# ======================= CONVERTE PARA PANDAS (DESAFIO ATUAL) ===============
pd_df = my_dataframe.to_pandas()  # <-- LINHA OBRIGATÓRIA DO DESAFIO

# ======================= EXIBE O pd_df (DESAFIO ATUAL) =====================
st.dataframe(pd_df, use_container_width=True)  # <-- EXIBE COMO PANDAS DATAFRAME

# ========================== NOME DO SMOOTHIE ================================
name_on_order = st.text_input("Name on Smoothie:", value="Your Name")
st.write(f"The name on your Smoothie will be: **{name_on_order}**")

# ========================== MULTISELECT DE FRUTAS ==========================
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    pd_df["FRUIT_NAME"].tolist(),  # <-- usa pd_df como pedido
    max_selections=5,
    default=["Tangerine", "Kiwi", "Lime", "Mango", "Strawberries"]
)

# ========================= EXIBE INFORMAÇÕES DAS FRUTAS =====================
if ingredients_list:
    ingredients_string = ""

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "

        st.subheader(f"{fruit_chosen} Nutrition Information")

        # Agora usa pd_df + .loc (próximo desafio vai pedir exatamente isso)
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write(f"The search value for **{fruit_chosen}** is **{search_on}**.")

        # Chama a API
        response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
        if response.status_code == 200:
            data = response.json()
            nutrition_df = pd.DataFrame(data[0]["nutritions"].items(), columns=["Nutrient", "Amount"])
            st.dataframe(nutrition_df, use_container_width=True)
        else:
            st.error(f"No info found for {fruit_chosen}.")

    ingredients_string = ingredients_string.strip()

    # INSERT SEGURO (com parâmetros)
    my_insert_stmt = """
        INSERT INTO smoothies.public.orders (NAME_ON_ORDER, INGREDIENTS)
        VALUES (%s, %s)
    """

    if st.button("Submit Order"):
        try:
            session.sql(my_insert_stmt, params=[name_on_order, ingredients_string]).collect()
            st.success(f"Your Smoothie is ordered, {name_on_order}! 🎉", icon="✅")
        except Exception as e:
            st.error(f"Error: {e}")
else:
    st.info("Select at least one fruit!")

# st.stop()  # <-- Deixe comentado agora (só usava antes)
