import calendar
import pandas as pd
import streamlit as st
import plotly.express as px
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import os


# Cargar el DataFrame
st.title('Datos Crímenes en México')
dfcrimen = pd.read_csv("etc/Delitos_Final.csv")

# Eliminar columna Unnamed
if "Unnamed: 0" in dfcrimen.columns:
    dfcrimen.drop(columns=["Unnamed: 0"], inplace=True)
print(dfcrimen.dtypes)


st.sidebar.header('Filtros gráfica de línea')
#Filtros de para gráfica de línea
# Filtro de Entidad
entidad_opciones = ['Todos'] + sorted(dfcrimen['Entidad'].unique().tolist())
entidad_seleccionada = st.sidebar.selectbox('Selecciona la Entidad', entidad_opciones)

# Filtro de Tipo de Delito
tipo_delito_opciones = ['Todos'] + sorted(dfcrimen['Tipo de delito'].unique().tolist())
tipo_delito_seleccionado = st.sidebar.multiselect('Selecciona Tipo(s) de Delito', tipo_delito_opciones, default='Todos')

# Filtro Tipo de Delito
if 'Todos' not in tipo_delito_seleccionado and tipo_delito_seleccionado:
    subtipo_delito_opciones = sorted(
        dfcrimen[dfcrimen['Tipo de delito'].isin(tipo_delito_seleccionado)]['Subtipo de delito'].unique().tolist()
    )
else:
    subtipo_delito_opciones = sorted(dfcrimen['Subtipo de delito'].unique().tolist())
subtipo_delito_opciones = ['Todos'] + subtipo_delito_opciones
subtipo_delito_seleccionado = st.sidebar.multiselect('Selecciona Subtipo(s) de Delito', subtipo_delito_opciones, default='Todos')

# Filtro de Sexo
sexo_opciones = ['Todos', 'Hombre', 'Mujer', 'No identificado']
sexo_seleccionado = st.sidebar.selectbox('Selecciona el Sexo', sexo_opciones)

# Filtrado según la selección
df_filtrado = dfcrimen.copy()

if entidad_seleccionada != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['Entidad'] == entidad_seleccionada]

if 'Todos' not in tipo_delito_seleccionado:
    df_filtrado = df_filtrado[df_filtrado['Tipo de delito'].isin(tipo_delito_seleccionado)]

if 'Todos' not in subtipo_delito_seleccionado:
    df_filtrado = df_filtrado[df_filtrado['Subtipo de delito'].isin(subtipo_delito_seleccionado)]

if sexo_seleccionado != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['Sexo'] == sexo_seleccionado]

# Calcular totales por año
df_totales = df_filtrado.groupby('Año')['Total_Delitos'].sum().reset_index()

# Mostrar gráfica de línea
st.subheader('Nivel de Crimen por Año')
fig_linea = px.line(
    df_totales,
    x='Año',
    y='Total_Delitos',
    title='Nivel de Crimen por Año en México',
    labels={'Año': 'Año', 'Total_Delitos': 'Total de Delitos'},
    markers=True,
    height=600,  # Incrementa el tamaño de la gráfica
    width=800  # Incrementa el ancho de la gráfica
)
st.plotly_chart(fig_linea)


# Filtros en gráfica de barras
st.sidebar.header("Filtros para gráfica de barras")

# Filtro de años
año_opciones = ['Todos'] + sorted(dfcrimen['Año'].unique().tolist())
año_seleccionado = st.sidebar.selectbox('Selecciona el Año', año_opciones, key='anio_filtro')

# Filtro de tipo de delito
tipo_delito_opciones = ['Todos'] + sorted(dfcrimen['Tipo de delito'].unique().tolist())
tipo_delito_seleccionado = st.sidebar.selectbox('Selecciona el Tipo de Delito', tipo_delito_opciones, key='delito_filtro')

# Filtrar DataFrame por años y tipo de delito
df_filtrado = dfcrimen.copy()

if año_seleccionado != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['Año'] == año_seleccionado]

if tipo_delito_seleccionado != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['Tipo de delito'] == tipo_delito_seleccionado]

# Agrupar por entidad y sumar el total de delitos
df_entidades = df_filtrado.groupby('Entidad')['Total_Delitos'].sum().reset_index()

# Ordenar en orden descendente
df_entidades = df_entidades.sort_values(by='Total_Delitos', ascending=False)

# Mostrar la entidad con más delitos
if not df_entidades.empty:
    entidad_con_mas_delitos = df_entidades.iloc[0]
    st.write(f"""
    **Del análisis:**
    - Año seleccionado: **{año_seleccionado}**
    - Tipo de delito seleccionado: **{tipo_delito_seleccionado}**

    La entidad con más registros de este delito es **{entidad_con_mas_delitos['Entidad']}** con **{entidad_con_mas_delitos['Total_Delitos']}** delitos reportados.
    """)
else:
    st.write("No hay datos para los filtros seleccionados.")

# Mostrar la entidad con menos delitos
if not df_entidades.empty:
    entidad_con_menos_delitos = df_entidades.iloc[31]
    st.write(f"""
    
    La entidad con menos registros de este delito es **{entidad_con_menos_delitos['Entidad']}** con **{entidad_con_menos_delitos['Total_Delitos']}** delitos reportados.
    """)
else:
    st.write("No hay datos para los filtros seleccionados.")


# Gráfica
st.subheader('Total de Delitos por Entidad para los Filtros Seleccionados')
if not df_entidades.empty:
    fig = px.bar(
        df_entidades,
        x='Total_Delitos',
        y='Entidad',
        orientation='h',
        title=f'Total de Delitos por Entidad ({año_seleccionado}, {tipo_delito_seleccionado})',
        labels={'Total_Delitos': 'Total de Delitos', 'Entidad': 'Entidad'},
        text_auto=True,
        height = 700,
        width = 900
    )
    st.plotly_chart(fig)

# Lista de meses en orden
meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
         'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

#Filtros meses
st.sidebar.header('Filtros para Distribución Mensual')
entidad_opciones = ['Todos'] + sorted(dfcrimen['Entidad'].unique().tolist())
entidad_seleccionada = st.sidebar.selectbox('Selecciona la Entidad', entidad_opciones, key='filtro_entidad')

anio_opciones = ['Todos'] + sorted(dfcrimen['Año'].unique().tolist())
anio_seleccionado = st.sidebar.selectbox('Selecciona el Año', anio_opciones, key='filtro_anio')

tipo_delito_opciones = ['Todos'] + sorted(dfcrimen['Tipo de delito'].unique().tolist())
tipo_delito_seleccionado = st.sidebar.selectbox('Selecciona el Tipo de Delito', tipo_delito_opciones, key='filtro_tipo_delito')


df_filtrado_mes = dfcrimen.copy()
if entidad_seleccionada != 'Todos':
    df_filtrado_mes = df_filtrado_mes[df_filtrado_mes['Entidad'] == entidad_seleccionada]
if anio_seleccionado != 'Todos':
    df_filtrado_mes = df_filtrado_mes[df_filtrado_mes['Año'] == anio_seleccionado]
if tipo_delito_seleccionado != 'Todos':
    df_filtrado_mes = df_filtrado_mes[df_filtrado_mes['Tipo de delito'] == tipo_delito_seleccionado]

# Sumar los delitos por mes para los datos filtrados
meses_presentes = [mes for mes in meses if mes in df_filtrado_mes.columns]
df_mes = df_filtrado_mes[meses_presentes].sum().reset_index()
df_mes.columns = ['Mes', 'Total_Delitos']

# Asegurar que los meses estén en orden
df_mes['Mes'] = pd.Categorical(df_mes['Mes'], categories=meses, ordered=True)
df_mes = df_mes.sort_values(by='Mes')

# Gráfica de meses
st.subheader('Distribución Mensual de los Delitos')
if not df_mes.empty:
    titulo = 'Distribución Mensual de los Delitos'
    if entidad_seleccionada != 'Todos':
        titulo += f' en {entidad_seleccionada}'
    if anio_seleccionado != 'Todos':
        titulo += f' para el Año {anio_seleccionado}'
    if tipo_delito_seleccionado != 'Todos':
        titulo += f' del Tipo {tipo_delito_seleccionado}'

    fig_mes = px.bar(
        df_mes,
        x='Mes',
        y='Total_Delitos',
        title=titulo,
        labels={'Total_Delitos': 'Total de Delitos', 'Mes': 'Mes'},
        text_auto=True
    )
    st.plotly_chart(fig_mes)
else:
    st.warning('No hay datos para los filtros seleccionados.')


st.title("Crímenes por Entidad")

# Filtro de año para el mapa
anios_disponibles = sorted(dfcrimen['Año'].unique())
anio_seleccionado = st.selectbox("Selecciona el Año", anios_disponibles)

# Cargar el archivo shapefile
try:
    mex = gpd.read_file("etc/mexican-states/mexican-states.dbf")
except Exception as e:
    ({e})

# Filtrar los datos de crímenes por el año seleccionado
dfcrimen_filtrado = dfcrimen[dfcrimen['Año'] == anio_seleccionado]

# Agrupar los crímenes por entidad
df_crimen_agg = dfcrimen_filtrado.groupby('Entidad')['Total_Delitos'].sum().reset_index()

# Fusión de los datos de crímenes con el shapefile
df_merged = pd.merge(mex, df_crimen_agg, left_on='name', right_on='Entidad', how='left')

# Crear un mapa con plotly
fig = px.choropleth(df_merged,
                    geojson=df_merged['geometry'],
                    locations=df_merged.index,
                    color="Total_Delitos",
                    hover_name="name",
                    hover_data=["Total_Delitos"],
                    color_continuous_scale="Viridis",
                    title=f"Total de Delitos por Estado en {anio_seleccionado}",
                    labels={"Total_Delitos": "Total de Delitos"}
)

fig.update_geos(fitbounds="locations", visible=False)
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

st.subheader(f"Mapa de Crímenes en México - Año {anio_seleccionado}")
st.write("Pasa el cursor sobre un estado para ver los detalles.")
st.plotly_chart(fig)

