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

def clean_code (df):
    """ Está função tem a responsabilidade de limpar o dataframe
        Tipos de limpeza:
        1. Remoção dos dados NaN
        2. Mudança do tipo da coluna de dados
        3. Remoção dos espaços das variáveis de texto
        4. Formatação da coluna de datas
        5. Limpeza da coluna de tempo (Remoção do texto da variável numérica)

        Input: Dataframe
        Output: Dataframe
    """
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

    return df


# ========================================================================================
# Barra lateral
# ========================================================================================

st.header('Marketplace - Visão Cliente')

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
st.sidebar.markdown('### Powered by Comunidade DS')

# Filtro de data
linhas_selecionadas = df['Order_Date'] < date_slider
df = df.loc[linhas_selecionadas, :]


# Filtro de transito
linhas_selecionadas = df['Road_traffic_density'].isin(traffic_option)
df = df.loc[linhas_selecionadas, :]
# ========================================================================================
# Layout streamlit
# ========================================================================================

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
    with st.container():
        # Order Matric
        st.markdown('# Orders by Day')
        # colunas
        cols = ['ID', 'Order_Date']

        # selecao de linhas
        df_aux = df.loc[:, cols].groupby('Order_Date').count().reset_index()

        # desenhar o gráfico
        fig = px.bar( df_aux, x= 'Order_Date', y= 'ID' )
        st.plotly_chart(fig, use_container_width=True)
    
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.header('Traffic Order Share')
            df_aux = df.loc[:, ['ID', 'Road_traffic_density']].groupby('Road_traffic_density').count().reset_index()

            df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN', :]
            df_aux['entregas_perc'] = df_aux['ID'] / df_aux['ID'].sum()

            fig2 = px.pie(df_aux, values='entregas_perc', names='Road_traffic_density')
            st.plotly_chart(fig2, use_container_width=True)

        with col2:
            st.header('Traffic Order City')
            df_aux = df.loc[:, ['ID', 'City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).count().reset_index()
            df_aux = df_aux.loc[df_aux['City'] != 'NaN', :]
            df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN', :]

            fig3 = px.scatter(df_aux, x='City', y='Road_traffic_density', size='ID', color='City')
            st.plotly_chart(fig3, use_container_width=True)

with tab2:
    with st.container():
        st.header('Order by week')
        # criar a coluna de semana
        df['week_of_year'] = df['Order_Date'].dt.strftime( '%U' )

        df_aux = df.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()

        fig4 = px.line(df_aux, x='week_of_year', y='ID')
        st.plotly_chart(fig4, use_container_width=True)

    with st.container():
        # Quantidade de pedidos por semana / Número único de entregadores por semana
        st.header('Order share by week')
        df_aux1 = df.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
        df_aux2 = df.loc[:, ['Delivery_person_ID', 'week_of_year']].groupby('week_of_year').nunique().reset_index()

        df_aux = pd.merge( df_aux1, df_aux2, how='inner' )
        df_aux['order_by_delivery'] = df_aux['ID'] / df_aux['Delivery_person_ID']

        fig5 = px.line(df_aux, x='week_of_year', y='order_by_delivery')
        st.plotly_chart(fig5, use_container_width=True)


with tab3:
    st.header('Country Maps')
    df_aux = df.loc[:, ['City', 'Road_traffic_density', 'Restaurant_latitude', 'Restaurant_longitude']].groupby(['City', 'Road_traffic_density']).median().reset_index()
    df_aux = df_aux.loc[df_aux['City'] != 'NaN', :]
    df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN', :]


    map = folium.Map()

    for index, location_info in df_aux.iterrows():
        folium.Marker([location_info['Restaurant_latitude'], location_info['Restaurant_longitude']]).add_to(map)

    folium_static(map, width=1024, height=600)
