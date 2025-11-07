# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col

# Título do app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Escolha as frutas que deseja no seu Smoothie personalizado!")

# Conexão com Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Buscar frutas disponíveis
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))

# Input para nome do pedido
name_on_order = st.text_input("Nome no Smoothie:", value="Your Name")
st.write(f"O nome no seu smoothie será: {name_on_order}")

# Multiselect para escolher até 5 frutas
ingredients_list = st.multiselect(
    "Escolha até 5 ingredientes:",
    [row[0] for row in my_dataframe.collect()],
    max_selections=5,
    default=[],
    placeholder="Choose options"
)

# Se houver frutas selecionadas, monta a string e insere no banco
if ingredients_list:
    ingredients_string = ' '.join(ingredients_list)
    my_insert_stmt = """
        INSERT INTO smoothies.public.orders (NAME_ON_ORDER, ingredients)
        VALUES (:1, :2)
    """
    if st.button("Enviar Pedido"):
        try:
            session.sql(my_insert_stmt, params=[name_on_order, ingredients_string]).collect()
            st.success(f'Seu smoothie foi pedido, {name_on_order}!', icon="✅")
        except Exception as e:
            st.error(f"Erro ao inserir no banco de dados: {e}")
else:
    st.write("Por favor, selecione pelo menos um ingrediente para enviar seu pedido.")

# Nova seção para exibir informação nutricional do SmoothieFroot (apenas se ingredientes forem selecionados)
if ingredients_list:
    import requests
    smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
    st.text(smoothiefroot_response)
