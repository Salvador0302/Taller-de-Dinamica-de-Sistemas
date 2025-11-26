from src.Models.model import getModelAll
import pysd
import os
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json


def controller(params=None):
    carpeta_destino = 'static/vensim'  # Ruta de la carpeta donde deseas guardar el archivo
    # FORZAR uso del modelo Forrester - NO usar otros archivos
    nombre_archivo = 'taller5_forrester.mdl'
    ruta_archivo = os.path.join(carpeta_destino, nombre_archivo)

    nivel = {}
    response = getModelAll()
    if not (isinstance(response, list) and 'message' in response[0]):
        # CONVERSION DE LO OBTENIDO DE LA BD
        response_format = [
            {
                "idModel": str(item[0]),
                "title": item[1],
                "nameLabelX": item[2],
                "nameLabelY": item[3],
                "position": item[4],
                "nameNivel": item[5],
                "nameColor": item[6],
            }
            for item in response
        ]

        # Verificar que el archivo taller5_forrester.mdl existe
        if not os.path.exists(ruta_archivo):
            error_message = [{
                'message': f'El archivo vensim requerido ({nombre_archivo}) no existe en '
                           f'{carpeta_destino}. Por favor, verifica que el archivo esté en la carpeta correcta.'
            }]
            return error_message
        # ----------------------------------

        try:
            # Leer el modelo Forrester
            model = pysd.read_vensim(ruta_archivo)

            # Ejecutar el modelo con parámetros si se proporcionan
            if params:
                print(f"DEBUG: Ejecutando modelo con parámetros: {params}")
                try:
                    stocks = model.run(params=params)
                except Exception as e:
                    print(f"ERROR al ejecutar con parámetros: {str(e)}")
                    # Intentar sin parámetros como fallback
                    stocks = model.run()
            else:
                print("DEBUG: Ejecutando modelo con valores por defecto")
                stocks = model.run()

            print(f"DEBUG: Usando archivo: {nombre_archivo}")
            print(f"DEBUG: Variables disponibles en modelo: {list(stocks.columns)[:10]}...")
            print(f"DEBUG: Forma de stocks: {stocks.shape}")

            for i in response_format:
                try:
                    nivel_buscado = i['nameNivel']
                    print(f"DEBUG: Buscando nivel: {nivel_buscado}")

                    # Verificar que la variable existe en el modelo
                    if nivel_buscado not in stocks.columns:
                        # Buscar nombres similares
                        similares = [
                            col for col in stocks.columns
                            if nivel_buscado.lower() in col.lower()
                            or col.lower() in nivel_buscado.lower()
                        ]
                        error_msg = f'El nombre de Nivel "{nivel_buscado}" no existe en el vensim ({nombre_archivo}).'
                        if similares:
                            error_msg += f' ¿Quisiste decir: {similares[0]}?'
                        # Filtrar solo las variables INTEG (stocks)
                        variables_stock = [
                            col for col in stocks.columns
                            if col not in ['FINAL TIME', 'INITIAL TIME', 'SAVEPER', 'TIME STEP']
                        ]
                        error_msg += (
                            f' Variables disponibles en modelo: {", ".join(variables_stock[:15])}. '
                            f'Modificar BD o vensim.'
                        )
                        error_message = [{'message': error_msg}]
                        return error_message

                    # Datos para la tabla (primeros 10)
                    stock_data = stocks[nivel_buscado].head(10)

                    # Datos completos para el gráfico
                    full_data = stocks[nivel_buscado]

                    # Obtener datos para el gráfico
                    x_data = full_data.index.values.tolist()
                    y_data = full_data.values.tolist()
                    
                    print(f"DEBUG: Generando gráfico para {nivel_buscado}")
                    print(f"  X data (primeros 5): {x_data[:5]}")
                    print(f"  Y data (primeros 5): {y_data[:5]}")
                    print(f"  Total puntos: {len(x_data)}")

                    # CREAR GRÁFICO INTERACTIVO CON PLOTLY
                    fig = go.Figure()
                    
                    # Agregar línea principal
                    fig.add_trace(go.Scatter(
                        x=x_data,
                        y=y_data,
                        mode='lines',
                        name=nivel_buscado,
                        line=dict(
                            color=i['nameColor'],
                            width=3
                        ),
                        hovertemplate='<b>%{fullData.name}</b><br>' +
                                    i['nameLabelX'] + ': %{x:.2f}<br>' +
                                    i['nameLabelY'] + ': %{y:.2f}<br>' +
                                    '<extra></extra>'
                    ))
                    
                    # Configurar layout con tema oscuro (por defecto)
                    # El JavaScript se encargará de cambiar los colores según el tema seleccionado
                    fig.update_layout(
                        title=dict(
                            text=i['title'],
                            font=dict(size=16, color='white', family='Arial, sans-serif'),
                            x=0.5,
                            xanchor='center'
                        ),
                        xaxis=dict(
                            title=dict(
                                text=i['nameLabelX'],
                                font=dict(size=12, color='white')
                            ),
                            showgrid=True,
                            gridcolor='rgba(31, 41, 55, 0.6)',
                            gridwidth=1,
                            zeroline=True,
                            zerolinecolor='rgba(100, 116, 139, 0.5)',
                            color='white',
                            tickfont=dict(size=10, color='white'),
                            showline=True,
                            linewidth=1,
                            linecolor='rgba(100, 116, 139, 0.8)'
                        ),
                        yaxis=dict(
                            title=dict(
                                text=i['nameLabelY'],
                                font=dict(size=12, color='white')
                            ),
                            showgrid=True,
                            gridcolor='rgba(31, 41, 55, 0.6)',
                            gridwidth=1,
                            zeroline=True,
                            zerolinecolor='rgba(100, 116, 139, 0.5)',
                            color='white',
                            tickfont=dict(size=10, color='white'),
                            showline=True,
                            linewidth=1,
                            linecolor='rgba(100, 116, 139, 0.8)'
                        ),
                        plot_bgcolor='rgba(2, 6, 23, 0)',  # Transparente para heredar del contenedor
                        paper_bgcolor='rgba(2, 6, 23, 0)',  # Transparente
                        font=dict(
                            family='Arial, sans-serif',
                            color='white'
                        ),
                        hovermode='closest',
                        showlegend=True,
                        legend=dict(
                            bgcolor='rgba(2, 6, 23, 0.95)',
                            bordercolor='rgba(75, 85, 99, 0.8)',
                            borderwidth=1,
                            font=dict(size=10, color='white'),
                            x=0.02,
                            y=0.98,
                            xanchor='left',
                            yanchor='top'
                        ),
                        margin=dict(l=60, r=30, t=60, b=60),
                        height=400,
                        # Configuración de interactividad
                        dragmode='pan',
                        hoversubplots='axis'
                    )
                    
                    # Configurar interactividad: zoom, pan, reset
                    fig.update_xaxes(fixedrange=False)
                    fig.update_yaxes(fixedrange=False)
                    
                    # Convertir a JSON para pasar al frontend
                    plot_json = fig.to_json()

                    # Convertir datos a formato serializable para la tabla
                    data_dict = {str(k): float(v) for k, v in stock_data.items()}

                    nivel[nivel_buscado] = {
                        'data': data_dict,
                        'plot_json': plot_json,
                        'title': i['title'],
                        'ylabel': i['nameLabelY'],
                        'xlabel': i['nameLabelX'],
                        'color': i['nameColor']
                    }
                except Exception as e:
                    error_message = [{
                        'message': (
                            f'Error al procesar nivel "{i["nameNivel"]}" en vensim ({nombre_archivo}): {str(e)}. '
                            f'Modificar BD o vensim'
                        )
                    }]
                    return error_message
            return nivel
        except Exception as e:
            error_message = [{
                'message': (
                    f'Error al leer el archivo vensim ({nombre_archivo}): {str(e)}. '
                    f'Verificar que el archivo existe en {carpeta_destino}/'
                )
            }]
            return error_message
    else:
        error_message = response
        return error_message
