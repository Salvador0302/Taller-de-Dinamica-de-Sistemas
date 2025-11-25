from src.Models.model import getModelAll
import pysd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import urllib3
import os
import mpld3
from decouple import config
import base64
from io import BytesIO


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

                    # FIGURA: compacta, con más altura y más margen inferior
                    fig, ax = plt.subplots(figsize=(7, 4.8))

                    ax.plot(
                        full_data,
                        label=nivel_buscado,
                        linewidth=3.0,
                        color=i['nameColor']
                    )

                    ax.set_facecolor('#020617')

                    # números de ejes en blanco
                    ax.tick_params(axis='both', colors='white')
                    for spine in ax.spines.values():
                        spine.set_color('#64748b')

                    # Ajustar límites del eje Y para evitar desbordamiento
                    y_min = full_data.min()
                    y_max = full_data.max()
                    y_range = y_max - y_min
                    margin = y_range * 0.1 if y_range != 0 else 1  # 10% de margen
                    ax.set_ylim(y_min - margin, y_max + margin)

                    # etiquetas de ejes en blanco
                    ax.set_ylabel(i['nameLabelY'], color='white')
                    ax.set_xlabel(i['nameLabelX'], color='white', labelpad=12)

                    ax.grid(color='#1f2937', alpha=0.6)

                    legend = ax.legend(
                        loc='center left',
                        facecolor='#020617',
                        framealpha=0.95,
                        edgecolor='#4b5563'
                    )
                    # color de texto de la leyenda
                    for text in legend.get_texts():
                        text.set_color('white')

                    # Margenes manuales: más espacio abajo para ticks + label del eje X
                    fig.subplots_adjust(
                        left=0.12,
                        right=0.97,
                        top=0.95,
                        bottom=0.30   # <- margen inferior más grande
                    )

                    # Agregar plugins interactivos de mpld3
                    plugins_list = [
                        mpld3.plugins.Reset(),
                        mpld3.plugins.BoxZoom(button=True),
                        mpld3.plugins.MousePosition(fontsize=12)
                    ]
                    
                    for plugin in plugins_list:
                        mpld3.plugins.connect(fig, plugin)

                    plt_graph = mpld3.fig_to_html(fig)
                    plt.close(fig)

                    # Convertir datos a formato serializable
                    data_dict = {str(k): float(v) for k, v in stock_data.items()}

                    nivel[nivel_buscado] = {
                        'data': data_dict,
                        'graph': plt_graph,
                        'title': i['title'],
                        'ylabel': i['nameLabelY'],
                        'xlabel': i['nameLabelX'],
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
