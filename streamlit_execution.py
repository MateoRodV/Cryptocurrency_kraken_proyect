import pandas as pd
import krakenex
from pykrakenapi import KrakenAPI
import streamlit as st
from functions_model import obtener_pares_divisas
from functions_model import obtener_cotizacion_historica
from functions_model import insumo_graph
from functions_model import generacion_graph

# Flujo principal
if __name__ == "__main__":

    # Inicializar Kraken API
    api = krakenex.API()
    k = KrakenAPI(api)
    # Streamlit App
    st.title("Cotización histórica de pares de divisas - Kraken")
    # Obtener los pares de divisas
    df_pares_divisas, pares_divisas = obtener_pares_divisas(k)
    # Crear un menú dropdown en Streamlit para seleccionar un par de divisas
    par_seleccionado = st.selectbox(
        'Selecciona el par de divisas',
        pares_divisas
    )
    # Mostrar el par seleccionado
    st.write(f"Has seleccionado: {par_seleccionado}")
    # Elegir el tamaño de la ventana para la media móvil y desviación estándar
    ventana_ma = st.slider("Selecciona el número de períodos para la media móvil (MA) y la desviación estándar", min_value=5, max_value=100, value=20, step=1)

    # Botón para obtener las cotizaciones
    if st.button("Obtener Cotización Histórica"):

        #Obtener las cotizaciones históricas del par seleccionado
        df_cotizaciones = obtener_cotizacion_historica(par_seleccionado, df_pares_divisas, k)
        #Realizar los cálculos necesarios sobre el df
        df_insumo = insumo_graph(df_cotizaciones, ventana_ma)
        fig = generacion_graph(df_insumo)
        # Mostrar el gráfico en Streamlit
        st.plotly_chart(fig)
        # Mostrar las primeras filas de las cotizaciones con la media móvil, la desviación estándar, la señal de compra y la señal de venta
        st.write(f"Cotizaciones históricas con Media Móvil (MA) de {ventana_ma} períodos, Desviación Estándar x2, Señal de Compra y Señal de Venta:")
        st.dataframe(df_insumo[['close', 'MA_', 'STDx2_', f'Banda_Superior', f'Banda_Inferior', 'Señal_Compra', 'Señal_Venta']])
