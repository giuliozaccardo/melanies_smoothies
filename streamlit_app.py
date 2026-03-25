# Import python packages.
import streamlit as st
from snowflake.snowpark.functions import col
import pandas as pd
import requests

# --- PARTE 1: ORDERING APP ---
st.title(":cup_with_straw: Customize Your Smoothie!:cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!.")

name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

cnx = st.connection("snowflake")
session = cnx.session()

# MODIFICA QUI: Dobbiamo selezionare ENTRAMBE le colonne per poterle usare dopo
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))

# Convertiamo in Pandas
pd_df = my_dataframe.to_pandas()

ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    pd_df['FRUIT_NAME'],
    max_selections=5
)

if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        
        # Cerchiamo il valore SEARCH_ON corrispondente
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit_chosen, ' is ', search_on, '.')
        
        st.subheader(fruit_chosen + ' Nutrition Information')
        
        # Chiamata API usando search_on
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + search_on)
        st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

    # Preparazione inserimento SQL
    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
            values ('""" + ingredients_string + """', '""" + name_on_order + """')"""
    
    if st.button('Submit Order'):
        session.sql(my_insert_stmt).collect()
        st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")


