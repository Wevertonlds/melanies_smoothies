import streamlit as st
from snowflake.snowpark.functions import col, upper
import pandas as pd  # <-- já importado como pd
import requests

# ================================== TÍTULO ==================================
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_staw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# ============================= CONEXÃO SNOWFLAKE ============================
cnx = st.connection("snowflake")
session = cnx.session()

# ======================= DATAFRAME COM SEARCH_ON ===========================
my_dataframe = session.table("smoothies.public.fruit_options") \
    .select(col("FRUIT_NAME")) \
    .withColumn("SEARCH_ON", upper(col("FRUIT_NAME")))

# ============================ CONVERTE PARA PANDAS =========================
pd_df = my_dataframe.to_pandas()  # <-- obrigatório

# ========================= EXIBE pd_df (desafio anterior) ==================
st.dataframe(pd_df, use_container_width=True)

# ========================== NOME DO SMOOTHIE ================================
name_on_order = st.text_input("Name on Smoothie:", value="Your Name")
st.write(f"The name on your Smoothie will be: **{name_on_order}**")

# ========================== MULTISELECT =====================================
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    pd_df["FRUIT_NAME"].tolist(),
    max_selections=5,
    default=["Tangerine", "Kiwi", "Lime", "Mango", "Strawberries"]
)

# ========================= LOOP DAS FRUTAS ESCOLHIDAS =======================
if ingredients_list:
    ingredients_string = ""

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "

        st.subheader(f"{fruit_chosen} Nutrition Information")

        # <<< AQUI É A LINHA "ESTRANHA" QUE O DESAFIO PEDE >>>
        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit_chosen, ' is ', search_on, '.')

        # <<< API com o SEARCH_ON correto >>>
        fruityvice_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + search_on)
        
        if fruityvice_response.status_code == 200:
            fv_df = pd.DataFrame(fruityvice_response.json()[0]["nutritions"].items(), columns=["Nutrient", "Amount"])
            st.dataframe(fv_df, use_container_width=True)
        else:
            st.error(f"No data found for {fruit_chosen}")

    # =========================== INSERT SEGURO ==============================
    ingredients_string = ingredients_string.strip()

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
    st.info("Select at least one fruit to see the magic happen!")

# st.stop()  # <-- já pode ficar comentado
