# libraries
from haversine import haversine
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from PIL import Image
from datetime import datetime
import folium
from streamlit_folium import folium_static

# import dataset
df = pd.read_csv( 'train.csv' )

# 1. convertendo a coluna Age de texto para número
linhas_selecionadas = (df['Delivery_person_Age'] != 'NaN ')
df = df.loc[linhas_selecionadas, :].copy()

df['Delivery_person_Age'] = df['Delivery_person_Age'].astype(int)


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

# ========================================================================================
# Barra lateral
# ========================================================================================

st.header('Marketplace - Visão Entregadores')

st.sidebar.image(image='ADCPython.png', width=120)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")
st.sidebar.markdown('## Selecione uma data limite')


date_slider = st.sidebar.slider(
    'Até qual valor?',
     value=datetime(2022, 4, 13),
     min_value=datetime(2022, 2, 11),
     max_value=datetime(2022, 4, 6),
     format= "DD/MM/YYYY"
)
st.sidebar.markdown("""---""")
traffic_option = st.sidebar.multiselect(
    'Quais as condições do trânsito',
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low', 'Medium', 'High', 'Jam']
)

st.sidebar.markdown("""---""")
clima_option = st.sidebar.multiselect(
    'Quais as condições climáticas',
    ['conditions Cloudy', 'conditions Fog', 'conditions Sandstorms', 'conditions Stormy', 'conditions Sunny', 'conditions Windy'],
    default=['conditions Cloudy', 'conditions Fog', 'conditions Sandstorms', 'conditions Stormy', 'conditions Sunny', 'conditions Windy']
)
st.sidebar.markdown("""---""")
st.sidebar.markdown('### Powered by Comunidade DS')

# Filtro de data
linhas_selecionadas = df['Order_Date'] < date_slider
df = df.loc[linhas_selecionadas, :]


# Filtro de transito
linhas_selecionadas = df['Road_traffic_density'].isin(traffic_option)
df = df.loc[linhas_selecionadas, :]

# Filtro de clima
linhas_selecionadas = df['Weatherconditions'].isin(clima_option)
df = df.loc[linhas_selecionadas, :]

# ========================================================================================
# Layout streamlit
# ========================================================================================

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_', '_'])

with tab1:
    with st.container():
        st.title('Overall Metrics')
        col1, col2, col3, col4 = st.columns(4, gap='large')

        with col1:
            maior_idade = df.loc[:, 'Delivery_person_Age'].max()
            col1.metric('Maior idade', maior_idade)

        with col2:
            menor_idade = df.loc[:, 'Delivery_person_Age'].min()
            col2.metric('Menor idade', menor_idade)
        with col3:
            melhor_condicao = df.loc[:, 'Vehicle_condition'].max()
            col3.metric('Melhor condição', melhor_condicao)

        with col4:
            pior_condicao = df.loc[:, 'Vehicle_condition'].min()
            col4.metric('Pior condição', pior_condicao)

    with st.container():
        st.markdown("""---""")
        st.title('Avaliações')

        col1, col2 = st.columns(2)
        with col1:
            st.markdown('##### Avaliações médias por entregador')
            df_avg_ratings_per_deliver = df.loc[:, ['Delivery_person_Ratings', 'Delivery_person_ID']].groupby('Delivery_person_ID').mean().reset_index()
            st.dataframe(df_avg_ratings_per_deliver)

        with col2:
            st.markdown('##### Avaliação média por trânsito')
            df_avg_std_rating_by_traffic = (df.loc[:, ['Delivery_person_Ratings', 'Road_traffic_density']].groupby('Road_traffic_density').agg({'Delivery_person_Ratings' : ['mean', 'std']}))

            # Mudança de nomes das colunas
            df_avg_std_rating_by_traffic.columns = ['Delivery_mean', 'Delivery_std']

            # reset do index
            df_avg_std_rating_by_traffic = df_avg_std_rating_by_traffic.reset_index()

            st.dataframe(df_avg_std_rating_by_traffic)

            st.markdown('##### Avaliação média por clima')
            df_avg_std_rating_by_weather = (df.loc[:, ['Delivery_person_Ratings', 'Weatherconditions']].groupby('Weatherconditions').agg({'Delivery_person_Ratings':['mean', 'std']}))
            
            # Mudança de nomes das colunas
            df_avg_std_rating_by_weather.columns = ['Delivery_mean', 'Delivery_std']

            # reset do index
            df_avg_std_rating_by_weather = df_avg_std_rating_by_weather.reset_index()

            st.dataframe(df_avg_std_rating_by_weather)

    with st.container():
        st.markdown("""---""")
        st.title('Velocidade de entrega')

        col1, col2 = st.columns(2)

        with col1:
            st.markdown('##### Top entregadores mais rápidos')

            df2 = df.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']].groupby(['City', 'Delivery_person_ID']).mean().sort_values(['City', 'Time_taken(min)'], ascending=True).reset_index()

            df_aux1 = df2.loc[df2['City'] == 'Metropolitian', :].head(10)
            df_aux2 = df2.loc[df2['City'] == 'Urban', :].head(10)
            df_aux3 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)

            df3 = pd.concat([df_aux1, df_aux2, df_aux3]).reset_index(drop=True)
            st.dataframe(df3)

        with col2:
            st.markdown('##### Top entregadores mais lentos')

            df4 = df.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']].groupby(['City', 'Delivery_person_ID']).mean().sort_values(['City', 'Time_taken(min)'], ascending=False).reset_index()

            df_aux4 = df2.loc[df2['City'] == 'Metropolitian', :].head(10)
            df_aux5 = df2.loc[df2['City'] == 'Urban', :].head(10)
            df_aux6 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)

            df5 = pd.concat([df_aux4, df_aux5, df_aux6]).reset_index(drop=True)
            st.dataframe(df5)
