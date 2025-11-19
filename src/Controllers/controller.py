from src.Models.model import getModelAll
import pysd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import urllib3
import os
import mpld3
from decouple import config

def controller():
    carpeta_destino = 'static/vensim'  # Ruta de la carpeta donde deseas guardar el archivo
    # FORZAR uso del modelo Forrester - NO usar otros archivos
    nombre_archivo = 'taller5_forrester.mdl'
    ruta_archivo = os.path.join(carpeta_destino, nombre_archivo)
    
    nivel = {}
    response = getModelAll()
    if not (isinstance(response, list) and 'message' in response[0]):
        # CONVERSION DE LO OBTENIDO DE LA BD
        response_format = [{"idModel": str(item[0]), "title": item[1], "nameLabelX": item[2], 
                            "nameLabelY": item[3], "position": item[4], "nameNivel": item[5], 
                            "nameColor": item[6]} for item in response]
        
        # Verificar que el archivo taller5_forrester.mdl existe
        if not os.path.exists(ruta_archivo):
            error_message = [{'message': f'El archivo vensim requerido ({nombre_archivo}) no existe en {carpeta_destino}. Por favor, verifica que el archivo esté en la carpeta correcta.'}]
            return error_message
        #----------------------------------

        try:
            # Leer el modelo Forrester
            model = pysd.read_vensim(ruta_archivo)
            # Ejecutar el modelo una sola vez para todas las variables
            stocks = model.run()
            
            print(f"DEBUG: Usando archivo: {nombre_archivo}")
            print(f"DEBUG: Variables disponibles en modelo: {list(stocks.columns)[:10]}...")
            
            for i in response_format:
                try:
                    nivel_buscado = i['nameNivel']
                    print(f"DEBUG: Buscando nivel: {nivel_buscado}")
                    
                    # Verificar que la variable existe en el modelo
                    if nivel_buscado not in stocks.columns:
                        # Buscar nombres similares
                        similares = [col for col in stocks.columns if nivel_buscado.lower() in col.lower() or col.lower() in nivel_buscado.lower()]
                        error_msg = f'El nombre de Nivel "{nivel_buscado}" no existe en el vensim ({nombre_archivo}).'
                        if similares:
                            error_msg += f' ¿Quisiste decir: {similares[0]}?'
                        # Filtrar solo las variables INTEG (stocks) - las que tienen valores en la serie
                        variables_stock = [col for col in stocks.columns if col not in ['FINAL TIME', 'INITIAL TIME', 'SAVEPER', 'TIME STEP']]
                        error_msg += f' Variables disponibles en modelo: {", ".join(variables_stock[:15])}. Modificar BD o vensim.'
                        error_message = [{'message': error_msg}]
                        return error_message
                    
                    stock_data = stocks[nivel_buscado].head(10)
                    plt.figure(figsize=(10, 6))
                    plt.plot(stocks[nivel_buscado], label=nivel_buscado, 
                             linewidth=4.0, color=i['nameColor'])
                    plt.title(i['title'], loc='center')
                    plt.ylabel(i['nameLabelY'])
                    plt.xlabel(i['nameLabelX'])
                    plt.grid()
                    plt.legend(loc='center left', facecolor='black', 
                               framealpha=1.0, edgecolor='black', 
                               labelcolor='white')
                    plt_graph = mpld3.fig_to_html(plt.gcf())
                    plt.close()
                    nivel[nivel_buscado] = {'data': stock_data, 'graph': plt_graph,
                                             'title': i['title'], 'ylabel': i['nameLabelY'],
                                             'xlabel': i['nameLabelX']}
                except Exception as e:
                    error_message = [{'message': f'Error al procesar nivel "{i["nameNivel"]}" en vensim ({nombre_archivo}): {str(e)}. Modificar BD o vensim'}]
                    return error_message
            return nivel
        except Exception as e:
            error_message = [{'message': f'Error al leer el archivo vensim ({nombre_archivo}): {str(e)}. Verificar que el archivo existe en {carpeta_destino}/'}]
            return error_message
    else:
        error_message = response
        return error_message