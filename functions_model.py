
import pandas as pd
import plotly.graph_objects as go
import nbformat

def obtener_pares_divisas(k):
    try:
        #Genera el df con todo lo que devuelve la API
        df_pares = k.get_tradable_asset_pairs()
        #Genera una lista de las cotizaciones bajo el nombre wsname que es más legible
        pares_divisas = df_pares['wsname'].tolist()
        return df_pares, pares_divisas
    except Exception as e:
        print(f"Error al obtener los pares de divisas: {e}")
        return None, []

# Función para obtener la cotización histórica con PyKrakenAPI
def obtener_cotizacion_historica(par, df, k):
    try:
        #Convierte el par recibido en el par que recibe la API para consultar
        par_consulta = df[df['wsname'] == par]['altname'].values[0]
        print(f"Par consulta definido como {par_consulta}")
        #Extrae el dataframe con la data OHLC que viene de la API imputandole parámetros definidos
        df, _ = k.get_ohlc_data(par_consulta, interval=1440, since=None)
        return df
    except Exception as e:
        print(f"Error al obtener la cotización histórica: {e}")
        return pd.DataFrame()

#Función para hacer el cálculo de bandas y señales
def insumo_graph(df, ventana_ma):
    try:
        #Ordenar el archivo bajo el idex (fecha de cotización)
        df = df.sort_index(ascending=True)
        #Seleccionar solo la fecha y el precio de cierre de la jornada para mayor practicidad
        df = df[['close']]  
        df = df.dropna() 
        # Calcular la media móvil (Moving Average - MA) sobre la columna 'close'
        df[f'MA_'] = df['close'].rolling(window=ventana_ma, min_periods=1).mean()
        # Calcular la desviación estándar (std) multiplicada por 2 sobre la columna 'close'
        df[f'STDx2_'] = df['close'].rolling(window=ventana_ma, min_periods=1).std() * 2
        # Calcular las bandas superiores e inferiores
        df['Banda_Superior'] = df[f'MA_'] + df[f'STDx2_']
        df['Banda_Inferior'] = df[f'MA_'] - df[f'STDx2_']
        # Crear la señal de compra (booleano): cuando la cotización esté por debajo de la banda inferior (MA - 2*STD)
        df['Señal_Compra'] = df['close'] < df['Banda_Inferior']
        # Crear la señal de venta (booleano): cuando la cotización esté por encima de la banda superior (MA + 2*STD)
        df['Señal_Venta'] = df['close'] > df['Banda_Superior']
        return df
    except Exception as e:
        print(f"Error al calcular las bandas y señales: {e}")
        return pd.DataFrame()


#Función para generar la gráfica que representa la selección
def generacion_graph(df):

        try:
            # Crear el gráfico con Plotly
            fig = go.Figure()

            # Agregar las cotizaciones (precio de cierre)
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['close'],
                mode='lines',
                name='Cotización (Close)',
                line=dict(color='blue')
            ))

            # Agregar la media móvil
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['MA_'],
                mode='lines',
                name='Media Móvil (MA)',
                line=dict(color='orange')
            ))

            # Agregar la banda superior
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['Banda_Superior'],
                mode='lines',
                name='Banda Superior (MA + 2STD)',
                line=dict(color='grey', dash='dash')
            ))

            # Agregar la banda inferior
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['Banda_Inferior'],
                mode='lines',
                name='Banda Inferior (MA - 2STD)',
                line=dict(color='grey', dash='dash')
            ))

            # Agregar los puntos de compra (Señal de Compra)
            fig.add_trace(go.Scatter(
                x=df[df['Señal_Compra']].index,  # Solo en los puntos donde la señal de compra es True
                y=df[df['Señal_Compra']]['close'],
                mode='markers',
                name='Señal de Compra',
                marker=dict(color='green', size=10, symbol='triangle-up')
            ))

            # Agregar los puntos de venta (Señal de Venta)
            fig.add_trace(go.Scatter(
                x=df[df['Señal_Venta']].index,  # Solo en los puntos donde la señal de venta es True
                y=df[df['Señal_Venta']]['close'],
                mode='markers',
                name='Señal de Venta',
                marker=dict(color='red', size=10, symbol='triangle-down')
            ))

            # Títulos y ajustes del gráfico
            fig.update_layout(
                title="Cotizaciones, Media Móvil y Señales de Compra/Venta",
                xaxis_title="Fecha",
                yaxis_title="Precio",
                legend_title="Leyenda"
            )

            return fig 
        except Exception as e:
            print(f"Error al generar la gráfica: {e}")
            return None
