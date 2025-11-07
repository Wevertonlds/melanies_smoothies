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

# ======================= CRIA pd_df COM SEARCH_ON ==========================
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
    default=["Apples", "Blueberries", "Raspberries", "Kiwi", "Dragon Fruit"]
)

# ======================== MAPEAMENTO CORRETO PARA A API =====================
# Essa é a mágica que resolve Kiwi, Raspberries, Dragon Fruit, etc.
API_NAME_MAP = {
    "APPLE": "Apple",
    "APPLES": "Apple",
    "BLUEBERRIES": "Blueberries",
    "RASPBERRIES": "Red Raspberries",
    "KIWI": "Kiwi",
    "DRAGON FRUIT": "Pitahaya",
    "MANGO": "Mango",
    "STRAWBERRIES": "Strawberry",
    "TANGERINE": "Tangerine",
    "LIME": "Lime",
    "PINEAPPLE": "Pineapple",
    "BANANA": "Banana",
    "AVOCADO": "Avocado"
    # Adicione mais se precisar
}

# ========================= LOOP DAS FRUTAS ==================================
if ingredients_list:
    ingredients_string = ""

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "

        st.subheader(f"{fruit_chosen} Nutrition Information")

        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit_chosen, ' is ', search_on, '.')

        # <<< USA O NOME CORRETO NA API >>>
        api_fruit_name = API_NAME_MAP.get(search_on, search_on)  # fallback se não tiver no mapa

        response = requests.get("https://my.smoothiefroot.com/api/fruit/" + api_fruit_name)

        if response.status_code == 200:
            try:
                data = response.json()

                # Tratamento robusto: às vezes vem lista, às vezes direto
                if isinstance(data, list):
                    nutrition = data[0].get("nutritions") or data[0].get("nutrition")
                else:
                    nutrition = data.get("nutritions") or data.get("nutrition")

                if nutrition:
                    fv_df = pd.DataFrame(list(nutrition.items()), columns=["Nutrient", "Amount"])
                    st.dataframe(fv_df, use_container_width=True)
                else:
                    st.warning(f"Nutrition data not available for {fruit_chosen}.")
            except Exception as e:
                st.error(f"Error parsing data for {fruit_chosen}: {e}")
        else:
            st.error(f"Sorry, no info found for {fruit_chosen} (tried '{api_fruit_name}')")

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
    st.info("Select fruits to see nutrition info!")
