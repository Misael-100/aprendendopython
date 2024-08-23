# libraries
from haversine import haversine
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from datetime import date, time, datetime, timedelta

# import dataset
df = pd.read_csv( 'train.csv' )

# 1. convertendo a coluna Age de texto para número
linhas_selecionadas = (df['Delivery_person_Age'] != 'NaN ')
df = df.loc[linhas_selecionadas, :].copy()

df['Delivery_person_Age'] = df['Delivery_person_Age'].astype(int)
df.shape

# 2. convertendo a coluna Rating de texto para número decimal
df['Delivery_person_Ratings'] = df['Delivery_person_Ratings'].astype(float)

# 3. convertendo a coluna order_Date de texto para data
df['Order_Date'] = pd.to_datetime(df['Order_Date'], format = '%d-%m-%Y')

# 4. convertendo multiple_deliveries de texto para número inteiro
linhas_selecionadas = (df['multiple_deliveries'] != 'NaN ')
df = df.loc[linhas_selecionadas, :].copy()
df['multiple_deliveries'] = df['multiple_deliveries'].astype(int)

# 5. removendo os espaços dentro de strings/texto/object
#df = df.reset_index(drop=True)
#for i in range(42805):
 # df.loc[i, 'ID'] = df.loc[i, 'ID'].strip()

# 6. removendo os espaços dentro de strings/texto/object
df.loc[:, 'ID'] = df.loc[:, 'ID'].str.strip()
df.loc[:, 'Road_traffic_density'] = df.loc[:, 'Road_traffic_density'].str.strip()
df.loc[:, 'Type_of_order'] = df.loc[:, 'Type_of_order'].str.strip()
df.loc[:, 'Type_of_vehicle'] = df.loc[:, 'Type_of_vehicle'].str.strip()
df.loc[:, 'City'] = df.loc[:, 'City'].str.strip()
df.loc[:, 'Festival'] = df.loc[:, 'Festival'].str.strip()

# 7. Limpando a coluna de time taken
df['Time_taken(min)'] = df['Time_taken(min)'].apply(lambda x: x.split( '(min) ' )[1] )
df['Time_taken(min)'] = df['Time_taken(min)'].astype(int)

# visao-empresa

# colunas
cols = ['ID', 'Order_Date']

# selecao de linhas
df_aux = df.loc[:, cols].groupby('Order_Date').count().reset_index()

# desenhar o gráfico

px.bar( df_aux, x= 'Order_Date', y= 'ID' )

# ========================================================================================
# layout no steamlit
# ========================================================================================

st.header('Marketplace - Visão Cliente')

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")
st.sidebar.markdown('## Selecione uma data limite')

st.sidebar.slider(
    'Até qual valor?',
     value=pd.datetime(2022, 4, 13),
     min_value=pd.datetime()
)