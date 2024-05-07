# Mariline Catalina Delgado Martínez
# Analítica de Datos
# Abril 2024
#%% Librerías
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

#%% FASE DE CARGAR LOS DATOS
db = pd.read_excel("online_retail_II.xlsx", sheet_name = "Year 2009-2010")
# Calcular el número de filas que representan el 10% de los datos para un menor tiempo de procesamiento
n_filas = int(len(db) * 0.1)
# Tomar un porcentaje de los datos
db = db.sample(n=n_filas)

#%% FASE DE PROCESO Y ALISTAMIENTO DEL CONJUNTO DE DATOS FINAL
db = db.drop_duplicates() # Eliminar los datos duplicados, debido a que estos aportan ventas que no son reales
db = db.dropna() # Eliminar datos faltantes 
db['Customer ID'] = db['Customer ID'].astype(str) # Transformar a STR
db = db.drop(columns=['Invoice','Description']) # Eliminar las columnas con información irrelevante 

# Datos Inválidos
db = db[db["Price"] >= 0] #No existen precios negativos
db = db[db["Quantity"] >= 0] #No existen cantidades negaticas

# Base de datos con columna objetivo
XY = db[['Country', 'Quantity']]
XY['Sales']= db['Price']*db['Quantity']  # Columna objetivo
XY['StockCode'] = db['StockCode'].astype(str)
XY['Customer ID'] = db['Customer ID'].astype(str)

#%%Separar año, mes y día de Invoice Date
XY['Day'] = db['InvoiceDate'].dt.to_period('d').astype(str)
XY['Day'] = pd.to_datetime(XY['Day'])
minimo = XY['Day'].min()
maximo = XY['Day'].max()

# %% Creación de datos en streamlit
import streamlit as st

# Configuración de la página
st.set_page_config(layout="wide")
st.title('Dashboard Online Retail')

# Sidebar para selección de variables y fechas
st.sidebar.header('Configuraciones de Gráficos')
variable = st.sidebar.selectbox('Selecciona la variable a visualizar:', options=['StockCode','Customer ID', 'Country'])
start_date = st.sidebar.date_input('Fecha de inicio:', value=minimo)
end_date = st.sidebar.date_input('Fecha de fin:', value=maximo)

# Convertir a datetime64 y normalizar
start_date = pd.to_datetime(start_date).normalize()
end_date = pd.to_datetime(end_date).normalize()

# Filtrar datos por fechas
filtered_data = XY[(XY['Day'] >= start_date) & (XY['Day'] <= end_date)]

# Se indica el total de ventas por cada variable: cliente, país, producto
# El producto tiene una excepción, ya que se muestra la cantidad total vendida
# y el valor de la venta de ese producto

if variable == 'StockCode':
    # para el caso en el que la variable selecionada sea el producto
    data = filtered_data.groupby(variable).agg({'Quantity':'sum','Sales':'sum'})
    data = data.reset_index().sort_values('Quantity',ascending = False).head(10)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(data['StockCode'], data['Quantity'], color='blue', label='Cantidad vendida')
    ax.set_ylabel('Cantidad', color='blue')
    ax.tick_params(axis='y', labelcolor='blue')

    ax2 = ax.twinx()
    ax2.plot(data['StockCode'], data['Sales'], color='red', linestyle='-', marker='o', label='Ventas')
    ax2.set_ylabel('Ventas', color='red')
    ax2.tick_params(axis='y', labelcolor='red')

    ax.set_title('Cantidad y Ventas de Productos')
    ax.set_xlabel('Código del Producto')
    plt.xticks(rotation=90, ha='right')
    ax.legend(loc='upper left')
    ax2.legend(loc='upper right')
    st.pyplot(fig)
    
else:
    data = filtered_data.groupby(variable)['Sales'].sum()
    data = data.sort_values(ascending = False).head(10).reset_index()

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(data[variable], data['Sales'])
    ax.set_title(f'Gráfico de Ventas por {variable} ')
    ax.set_xlabel(variable)
    ax.set_ylabel('Ventas')
    st.pyplot(fig)