# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col

# Título do app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Conexão com Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Buscar frutas disponíveis
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))

# Input para nome do pedido
name_on_order = st.text_input("Name on Smoothie:", value="Your Name")
st.write(f"The name on your smoothie will be: {name_on_order}")

# Multiselect para escolher até 5 frutas
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    [row[0] for row in my_dataframe.collect()],
    max_selections=5,
    default=[]
)

# Se houver frutas selecionadas, monta a string e insere no banco
if ingredients_list:
    ingredients_string = ' '.join(ingredients_list)
    my_insert_stmt = """
        INSERT INTO smoothies.public.orders (NAME_ON_ORDER, ingredients)
        VALUES (:1, :2)
    """
    if st.button("Submit Order"):
        try:
            session.sql(my_insert_stmt, params=[name_on_order, ingredients_string]).collect()
            st.success(f'Your smoothie is ordered, {name_on_order}!', icon="✅")
        except Exception as e:
            st.error(f"Error inserting into the database: {e}")
else:
    st.write("Please select at least one ingredient to submit your order.")

# Nova seção para exibir informação nutricional do SmoothieFroot
import requests
smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
st.text(smoothiefroot_response)
