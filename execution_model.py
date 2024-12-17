import pandas as pd
import krakenex
from pykrakenapi import KrakenAPI
from functions_model import obtener_pares_divisas
from functions_model import obtener_cotizacion_historica
from functions_model import insumo_graph
from functions_model import generacion_graph

# Flujo principal
if __name__ == "__main__":

    try:
        # Inicializar Kraken API
        api = krakenex.API()
        k = KrakenAPI(api)
        #Obtener los pares de divisas 
        df_pares, pares_divisas = obtener_pares_divisas(k)
        #Solicitar en py el par de divisas al usuario (a través de streamlite se generará la lista desplegable)
        val = False
        while val == False:
            par_divisa = input("Ingrese el par de divisas (eg. XBT/USD): ")
            if par_divisa in pares_divisas:
                val = True
                print(f"Par de divisas encontrado y definido como: {par_divisa}")
            else:
                val = False
                print("Par de divisas no encontrado")
        #Obtener las cotizaciones históricas del par seleccionado
        df_cotizaciones = obtener_cotizacion_historica(par_divisa, df_pares, k)
        #Realizar los cálculos necesarios sobre el df
        df_insumo = insumo_graph(df_cotizaciones, ventana_ma=20)
        #Llamar a la función que define la gráfica
        fig = generacion_graph(df_insumo)
        #Mostrar la gráfica
        fig.show()
    except Exception as e:
        print(f"Error en el flujo principal: {e}")