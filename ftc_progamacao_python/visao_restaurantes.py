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
import numpy as np

# import dataset
df = pd.read_csv( 'train.csv' )

# 1. convertendo a coluna Age de texto para número
linhas_selecionadas = (df['Delivery_person_Age'] != 'NaN ')
df = df.loc[linhas_selecionadas, :].copy()
df['Delivery_person_Age'] = df['Delivery_person_Age'].astype(int)

linhas_selecionadas = (df['Road_traffic_density'] != 'NaN ')
df = df.loc[linhas_selecionadas, :].copy()

linhas_selecionadas = (df['City'] != 'NaN ')
df = df.loc[linhas_selecionadas, :].copy()

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

st.header('Marketplace - Visão Restaurantes')

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
        col1, col2, col3, col4, col5, col6 = st.columns(6)

        with col1:
            delivery_unique = len(df.loc[:, 'Delivery_person_ID'].unique())
            col1.metric('Entregadores', delivery_unique)

        with col2:
            cols = ['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_latitude', 'Restaurant_longitude']
            df['Distance'] = df.loc[:, cols].apply(lambda x: 
                                                   haversine((x['Restaurant_latitude'], x['Restaurant_longitude']),
                                                            (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1)
            avg_distance = np.round( df['Distance'].mean(), 2)
            col2.metric('A distancia média das entregas', avg_distance)


        with col3:
            df_aux = df.loc[:, ['Time_taken(min)', 'Festival']].groupby('Festival').agg({'Time_taken(min)': ['mean', 'std']})
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            df_aux = np.round(df_aux.loc[df_aux['Festival'] == 'Yes', 'avg_time'], 2)

            col3.metric('Tempo médio', df_aux)


        with col4:
            df_aux = df.loc[:, ['Time_taken(min)', 'Festival']].groupby('Festival').agg({'Time_taken(min)': ['mean', 'std']})
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            df_aux = np.round(df_aux.loc[df_aux['Festival'] == 'Yes', 'std_time'], 2)

            col4.metric('STD entrega', df_aux)

        with col5:
            df_aux = df.loc[:, ['Time_taken(min)', 'Festival']].groupby('Festival').agg({'Time_taken(min)': ['mean', 'std']})
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            df_aux = np.round(df_aux.loc[df_aux['Festival'] == 'No', 'avg_time'], 2)

            col5.metric('Tempo médio', df_aux)

        with col6:
            df_aux = df.loc[:, ['Time_taken(min)', 'Festival']].groupby('Festival').agg({'Time_taken(min)': ['mean', 'std']})
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            df_aux = np.round(df_aux.loc[df_aux['Festival'] == 'No', 'std_time'], 2)

            col5.metric('STD entrega', df_aux)


    with st.container():
            cols = ['City', 'Time_taken(min)']
            df_aux = df.loc[:, cols].groupby('City').agg({'Time_taken(min)': ['mean', 'std']})
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            fig = go.Figure()
            fig.add_trace(go.Bar(name = 'Control',
                                 x=df_aux['City'],
                                 y=df_aux['avg_time'],
                                 error_y=dict(type='data', array=df_aux['std_time'])))
            fig.update_layout(barmode='group')
            st.plotly_chart(fig)

    with st.container():
        st.title('Distribuição do tempo')

        col1, col2 = st.columns(2)

        with col1:
            cols = ['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_latitude', 'Restaurant_longitude']
            df['distance'] = df.loc[:, cols].apply(lambda x:
                                               haversine( (x['Restaurant_latitude'], x['Restaurant_longitude']),
                                                          (x['Delivery_location_latitude'], x['Delivery_location_longitude']) ), axis=1)
            avg_distance = df.loc[:, ['City', 'distance']].groupby('City').mean().reset_index()
            fig = go.Figure(data = [go.Pie(labels=avg_distance['City'], values=avg_distance['distance'], pull=[0, 0.1, 0])])
            st.plotly_chart(fig)

        with col2:
            cols = ['City', 'Time_taken(min)', 'Road_traffic_density']
            df_aux = df.loc[:, cols].groupby(['City', 'Road_traffic_density']).agg({'Time_taken(min)': ['mean', 'std']})
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values='avg_time',
                              color='std_time', color_continuous_scale='RdBu',
                              color_continuous_midpoint=np.average(df_aux['std_time']))
            st.plotly_chart(fig)

    with st.container():
        st.title('Distribuição da distância')
        df_aux = (df.loc[:, ['City', 'Time_taken(min)', 'Type_of_order']]
                    .groupby(['City', 'Type_of_order'])
                    .agg({'Time_taken(min)': ['mean', 'std']}))
        df_aux.columns = ['avg_time', 'std_time']
        df_aux = df_aux.reset_index()
        st.dataframe(df_aux)