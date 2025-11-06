# Import python packages
import streamlit as st

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write(
    """Choose the fruits you want in your custom Smoothie!"""
)

# Add text input for the name
name_on_order = st.text_input("Name on Smoothie:", value="Your Name")
st.write(f"The name on your Smoothie will be: {name_on_order}")

# Multiselect widget for choosing fruits with max 5 selections
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    ["Banana", "Morango", "Misto"],  # Lista fixa de frutas como exemplo
    max_selections=5,
    default=[]
)

# Display selected fruits if the list is not empty
if ingredients_list:
    ingredients_string = ' '.join(ingredients_list)
    st.write(f"Ingredientes selecionados: {ingredients_string}")
else:
    st.write("Selecione até 5 ingredientes.")
