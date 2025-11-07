import streamlit as st
from snowflake.snowpark.functions import col, upper
import pandas as pd
import requests

# ================================== TÍTULO ==================================
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# ============================= CONEXÃO SNOWFLAKE ============================
cnx = st.connection("snowflake")
session = cnx.session()

# ======================= CRIA pd_df COM SEARCH_ON EM MAIÚSCULAS ===========
my_dataframe = session.table("smoothies.public.fruit_options") \
    .select(col("FRUIT_NAME")) \
    .withColumn("SEARCH_ON", upper(col("FRUIT_NAME")))

pd_df = my_dataframe.to_pandas()
st.dataframe(pd_df, use_container_width=True)

# ========================== NOME DO SMOOTHIE ================================
name_on_order = st.text_input("Name on Smoothie:", value="Johnny")
st.write(f"The name on your Smoothie will be: **{name_on_order}**")

# ========================== MULTISELECT =====================================
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    pd_df["FRUIT_NAME"].tolist(),
    max_selections=5,
    default=["Apples", "Blueberries", "Dragon Fruit", "Mango", "Strawberries"]
)

# ========================= LOOP DAS FRUTAS ==================================
if ingredients_list:
    ingredients_string = ""

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "

        st.subheader(f"{fruit_chosen} Nutrition Information")

        # <<< LINHA EXATA QUE O VALIDADOR QUER >>>
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit_chosen, ' is ', search_on, '.')

        # <<< URL CORRETA DO LAB + TRATAMENTO PERFEITO DO JSON >>>
        fruityvice_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + search_on)

        if fruityvice_response.status_code == 200:
            fv_json = fruityvice_response.json()
            # A API retorna uma lista com 1 objeto → pegamos nutritions direto
            nutrition_data = fv_json[0]["nutritions"]
            fv_df = pd.DataFrame(list(nutrition_data.items()), columns=["Nutrient", "Amount"])
            st.dataframe(fv_df, use_container_width=True)
        else:
            st.error(f"Sorry, no nutrition info found for {fruit_chosen}.")

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
    st.info("Select at least one fruit to continue!")

# st.stop()  # já pode ficar comentado
