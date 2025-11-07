import streamlit as st
from snowflake.snowpark.functions import col, upper
import pandas as pd
import requests

# ================================== TÍTULO ==================================
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_staw:")
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
    default=["Blueberries", "Jackfruit", "Raspberries", "Kiwi", "Dragon Fruit"]
)

# ========================= LOOP DAS FRUTAS ==================================
if ingredients_list:
    ingredients_string = ""

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "

        st.subheader(f"{fruit_chosen} Nutrition Information")

        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit_chosen, ' is ', search_on, '.')

        smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

    # =========================== INSERT CORRETO (SEM %s) =====================
    ingredients_string = ingredients_string.strip()

    # <<< MÉTODO QUE O LAB ACEITA 100% >>>
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (NAME_ON_ORDER, INGREDIENTS)
        VALUES ('{name_on_order}', '{ingredients_string}')
    """

    if st.button("Submit Order"):
        try:
            session.sql(my_insert_stmt).collect()
            st.success(f"Your Smoothie is ordered, {name_on_order}! 🎉", icon="✅")
        except Exception as e:
            st.error(f"Error: {e}")

else:
    st.info("Select at least one fruit!")

# st.stop()  # já pode ficar comentado
