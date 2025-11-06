# Import python packages
import streamlit as st
import snowflake.connector  # Substitui Snowpark para conexão manual

# Função para conectar ao Snowflake (placeholder para credenciais)
def connect_to_snowflake():
    try:
        conn = snowflake.connector.connect(
            user='seu_usuario',  # Substitua com seu usuário
            password='sua_senha',  # Substitua com sua senha
            account='sua_conta',  # Ex.: kbgnbtt/agb64374
            warehouse='COMPUTE_WH',  # Ajuste conforme seu warehouse
            database='SMOOTHIES',
            schema='PUBLIC'
        )
        return conn
    except Exception as e:
        st.error(f"Erro de conexão: {e}")
        return None

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write(
    """Choose the fruits you want in your custom Smoothie!"""
)

# Conexão manual (substitui get_active_session)
conn = connect_to_snowflake()
if conn:
    # Fetch fruit names manually (substitui my_dataframe)
    cursor = conn.cursor()
    cursor.execute("SELECT FRUIT_NAME FROM smoothies.public.fruit_options")
    fruit_options = [row[0] for row in cursor.fetchall()]
    cursor.close()

    # Add text input for the name
    name_on_order = st.text_input("Name on Smoothie:", value="Your Name")
    st.write(f"The name on your Smoothie will be: {name_on_order}")

    # Multiselect widget for choosing fruits with max 5 selections
    ingredients_list = st.multiselect(
        "Choose up to 5 ingredients:",
        fruit_options,
        max_selections=5,
        default=[]
    )

    # Display selected fruits if the list is not empty
    if ingredients_list:
        ingredients_string = ' '.join(ingredients_list)
        my_insert_stmt = f"""INSERT INTO smoothies.public.orders (NAME_ON_ORDER, ingredients) VALUES ('{name_on_order}', '{ingredients_string}')"""
        if st.button("Submit Order"):
            try:
                cursor = conn.cursor()
                cursor.execute(my_insert_stmt)
                conn.commit()
                st.success(f'Your smoothie is ordered, {name_on_order}!', icon="✅")
                cursor.close()
            except Exception as e:
                st.error(f"Error inserting into the database: {e}")
                conn.rollback()
    else:
        st.write("You can only select up to 5 options. Remove an option first." if len(ingredients_list) > 5 else "")
else:
    st.write("Conexão com Snowflake falhou. Verifique as credenciais.")

# Fechar conexão ao final (bom hábito)
if 'conn' in locals() and conn is not None:
    conn.close()
