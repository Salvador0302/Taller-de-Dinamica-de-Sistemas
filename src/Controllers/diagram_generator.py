"""
Generador de diagramas de Forrester y causales a partir de modelos Vensim usando PySD
"""
import pysd
import networkx as nx
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Circle, FancyArrowPatch
import base64
from io import BytesIO


def extract_model_structure(model_path):
    """
    Extrae la estructura del modelo Vensim: variables, tipos y dependencias
    
    Returns:
        dict: {
            'stocks': list,  # Variables INTEG (niveles)
            'flows': list,   # Variables que modifican stocks
            'auxiliaries': list,  # Variables auxiliares
            'constants': list,  # Constantes
            'dependencies': dict  # {variable: [dependencies]}
        }
    """
    try:
        model = pysd.read_vensim(model_path)
        
        # Obtener todas las variables del modelo
        doc_data = model.get_dependencies()
        
        stocks = []
        flows = []
        auxiliaries = []
        constants = []
        dependencies = {}
        
        # Analizar cada variable
        for var_name, deps in doc_data.items():
            # Limpiar nombre
            clean_name = var_name.replace('_', ' ').title()
            
            dependencies[clean_name] = [d.replace('_', ' ').title() for d in deps]
            
            # Clasificar según tipo
            # Los stocks son las variables INTEG
            if 'integ' in var_name.lower():
                stocks.append(clean_name)
            # Las constantes son las que empiezan con 'tasa'
            elif var_name.startswith('tasa_'):
                constants.append(clean_name)
            # Los flujos son variables que afectan directamente a stocks
            elif any(stock_name.replace(' ', '_').lower() in var_name.lower() 
                    for stock_name in stocks):
                flows.append(clean_name)
            else:
                auxiliaries.append(clean_name)
        
        return {
            'stocks': stocks,
            'flows': flows,
            'auxiliaries': auxiliaries,
            'constants': constants,
            'dependencies': dependencies
        }
    except Exception as e:
        print(f"Error extrayendo estructura: {str(e)}")
        return None


def generate_forrester_diagram(model_path):
    """
    Genera un diagrama de Forrester (Stock-Flow) del modelo Vensim
    
    Returns:
        str: Imagen en base64
    """
    try:
        model = pysd.read_vensim(model_path)
        
        # Crear grafo dirigido
        G = nx.DiGraph()
        
        # Variables principales del modelo (basado en el .mdl)
        stocks = [
            'Poblacion Inmigrante',
            'Inmigrantes Desempleados',
            'Delincuentes En La Calle',
            'Policias En Servicio'
        ]
        
        flows = [
            'Inmigrantes Que Llegan',
            'Inmigrantes Que Se Van',
            'Nuevos Inmigrantes Desempleados',
            'Inmigrantes Que Obtienen Empleo',
            'Nuevos Delicuentes',
            'Delincuentes Arrestados',
            'Delincuentes Muertos',
            'Policias Asignados',
            'Policias Retirados'
        ]
        
        auxiliaries = [
            'Inmigrantes',
            'Fondos Municipales',
            'Programas De Integracion',
            'Delitos Resueltos',
            'Discrepancia'
        ]
        
        constants = [
            'Tasa De Inmigrantes',
            'Tasa De Emigrantes',
            'Tasa De Desempleo',
            'Tasa De Inmigrantes Empleados',
            'Tasa De Nuevos Delincuentes',
            'Tasa De Muertes',
            'Tasa De Delincuentes Arrestados',
            'Tasa De Policias Contratados',
            'Tasa De Policias Retirados',
            'Objetivo'
        ]
        
        # Agregar nodos
        for stock in stocks:
            G.add_node(stock, node_type='stock')
        for flow in flows:
            G.add_node(flow, node_type='flow')
        for aux in auxiliaries:
            G.add_node(aux, node_type='auxiliary')
        for const in constants:
            G.add_node(const, node_type='constant')
        
        # Relaciones principales del modelo
        relationships = [
            # Población Inmigrante
            ('Inmigrantes Que Llegan', 'Poblacion Inmigrante'),
            ('Poblacion Inmigrante', 'Inmigrantes Que Se Van'),
            ('Poblacion Inmigrante', 'Inmigrantes Que Llegan'),
            ('Tasa De Inmigrantes', 'Inmigrantes Que Llegan'),
            ('Poblacion Inmigrante', 'Inmigrantes Que Se Van'),
            ('Tasa De Emigrantes', 'Inmigrantes Que Se Van'),
            
            # Inmigrantes
            ('Inmigrantes Que Llegan', 'Inmigrantes'),
            ('Inmigrantes', 'Nuevos Inmigrantes Desempleados'),
            ('Tasa De Desempleo', 'Nuevos Inmigrantes Desempleados'),
            
            # Inmigrantes Desempleados
            ('Nuevos Inmigrantes Desempleados', 'Inmigrantes Desempleados'),
            ('Inmigrantes Desempleados', 'Inmigrantes Que Obtienen Empleo'),
            ('Programas De Integracion', 'Inmigrantes Que Obtienen Empleo'),
            ('Tasa De Inmigrantes Empleados', 'Inmigrantes Que Obtienen Empleo'),
            
            # Delincuentes
            ('Inmigrantes Desempleados', 'Nuevos Delicuentes'),
            ('Tasa De Nuevos Delincuentes', 'Nuevos Delicuentes'),
            ('Nuevos Delicuentes', 'Delincuentes En La Calle'),
            ('Delincuentes En La Calle', 'Delincuentes Arrestados'),
            ('Delincuentes En La Calle', 'Delincuentes Muertos'),
            ('Tasa De Muertes', 'Delincuentes Muertos'),
            
            # Policías
            ('Delincuentes En La Calle', 'Fondos Municipales'),
            ('Fondos Municipales', 'Programas De Integracion'),
            ('Policias En Servicio', 'Delitos Resueltos'),
            ('Delitos Resueltos', 'Delincuentes Arrestados'),
            ('Tasa De Delincuentes Arrestados', 'Delincuentes Arrestados'),
            
            ('Objetivo', 'Discrepancia'),
            ('Policias En Servicio', 'Discrepancia'),
            ('Discrepancia', 'Policias Asignados'),
            ('Tasa De Policias Contratados', 'Policias Asignados'),
            ('Policias Asignados', 'Policias En Servicio'),
            ('Policias En Servicio', 'Policias Retirados'),
            ('Tasa De Policias Retirados', 'Policias Retirados'),
        ]
        
        # Agregar edges
        for source, target in relationships:
            if source in G.nodes and target in G.nodes:
                G.add_edge(source, target)
        
        # Crear figura con fondo oscuro
        fig, ax = plt.subplots(figsize=(18, 14))
        fig.patch.set_facecolor('#020617')
        ax.set_facecolor('#020617')
        
        # Layout jerárquico mejorado
        pos = nx.spring_layout(G, k=2.5, iterations=60, seed=42)
        
        # Colores según tipo
        node_colors = []
        for node in G.nodes():
            ntype = G.nodes[node].get('node_type', 'auxiliary')
            if ntype == 'stock':
                node_colors.append('#3b82f6')  # Azul para stocks
            elif ntype == 'flow':
                node_colors.append('#10b981')  # Verde para flujos
            elif ntype == 'constant':
                node_colors.append('#f59e0b')  # Naranja para constantes
            else:
                node_colors.append('#8b5cf6')  # Púrpura para auxiliares
        
        # Dibujar nodos
        nx.draw_networkx_nodes(
            G, pos, 
            node_color=node_colors,
            node_size=2500,
            alpha=0.9,
            ax=ax
        )
        
        # Dibujar edges
        nx.draw_networkx_edges(
            G, pos,
            edge_color='#64748b',
            arrows=True,
            arrowsize=18,
            arrowstyle='->',
            width=1.5,
            alpha=0.6,
            connectionstyle='arc3,rad=0.1',
            ax=ax
        )
        
        # Etiquetas
        nx.draw_networkx_labels(
            G, pos,
            font_size=7,
            font_color='white',
            font_weight='bold',
            ax=ax
        )
        
        # Leyenda
        legend_elements = [
            mpatches.Patch(color='#3b82f6', label='Stocks (Niveles)'),
            mpatches.Patch(color='#10b981', label='Flows (Flujos)'),
            mpatches.Patch(color='#8b5cf6', label='Auxiliares'),
            mpatches.Patch(color='#f59e0b', label='Constantes/Parámetros')
        ]
        legend = ax.legend(
            handles=legend_elements,
            loc='upper left',
            facecolor='#1e293b',
            edgecolor='#475569',
            fontsize=11
        )
        for text in legend.get_texts():
            text.set_color('white')
        
        ax.set_title(
            'Diagrama de Forrester - Modelo de Sistema Dinámico\nFlujos, Niveles y Relaciones',
            color='white',
            fontsize=18,
            fontweight='bold',
            pad=20
        )
        ax.axis('off')
        
        plt.tight_layout()
        
        # Convertir a base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=150, facecolor='#020617', edgecolor='none')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode()
        plt.close(fig)
        
        return f"data:image/png;base64,{image_base64}"
        
    except Exception as e:
        print(f"Error generando diagrama de Forrester: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def generate_causal_diagram(model_path):
    """
    Genera un diagrama de lazos causales del modelo Vensim
    
    Returns:
        str: Imagen en base64
    """
    try:
        model = pysd.read_vensim(model_path)
        deps = model.get_dependencies()
        
        # Crear grafo dirigido
        G = nx.DiGraph()
        
        # Simplificar: solo variables principales (stocks y sus influencias directas)
        main_vars = [
            'Poblacion Inmigrante',
            'Inmigrantes Desempleados',
            'Delincuentes En La Calle',
            'Policias En Servicio',
            'Fondos Municipales',
            'Programas De Integracion',
            'Discrepancia'
        ]
        
        # Agregar nodos principales
        for var in main_vars:
            G.add_node(var)
        
        # Agregar relaciones causales importantes
        causal_links = {
            'Poblacion Inmigrante': [('Inmigrantes Desempleados', '+')],
            'Inmigrantes Desempleados': [('Delincuentes En La Calle', '+'), ('Programas De Integracion', '-')],
            'Delincuentes En La Calle': [('Fondos Municipales', '+'), ('Policias En Servicio', '-')],
            'Fondos Municipales': [('Programas De Integracion', '+')],
            'Programas De Integracion': [('Inmigrantes Desempleados', '-')],
            'Policias En Servicio': [('Delincuentes En La Calle', '-'), ('Discrepancia', '-')],
            'Discrepancia': [('Policias En Servicio', '+')]
        }
        
        # Agregar edges con polaridad
        edge_labels = {}
        for source, targets in causal_links.items():
            for target, polarity in targets:
                if source in G.nodes and target in G.nodes:
                    G.add_edge(source, target, polarity=polarity)
                    edge_labels[(source, target)] = polarity
        
        # Crear figura
        fig, ax = plt.subplots(figsize=(14, 10))
        fig.patch.set_facecolor('#020617')
        ax.set_facecolor('#020617')
        
        # Layout circular para mostrar bucles
        pos = nx.spring_layout(G, k=3, iterations=50, seed=42)
        
        # Dibujar nodos
        nx.draw_networkx_nodes(
            G, pos,
            node_color='#6366f1',
            node_size=4000,
            alpha=0.9,
            ax=ax
        )
        
        # Dibujar edges con colores según polaridad
        for edge in G.edges(data=True):
            source, target, data = edge
            polarity = data.get('polarity', '+')
            color = '#10b981' if polarity == '+' else '#ef4444'
            
            nx.draw_networkx_edges(
                G, pos,
                edgelist=[(source, target)],
                edge_color=color,
                arrows=True,
                arrowsize=25,
                arrowstyle='->',
                width=3,
                alpha=0.8,
                connectionstyle='arc3,rad=0.1',
                ax=ax
            )
        
        # Etiquetas de nodos
        nx.draw_networkx_labels(
            G, pos,
            font_size=9,
            font_color='white',
            font_weight='bold',
            ax=ax
        )
        
        # Etiquetas de edges (polaridad)
        nx.draw_networkx_edge_labels(
            G, pos,
            edge_labels=edge_labels,
            font_size=14,
            font_color='white',
            font_weight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#1e293b', edgecolor='none', alpha=0.8),
            ax=ax
        )
        
        # Leyenda
        legend_elements = [
            mpatches.Patch(color='#10b981', label='Relación Positiva (+)'),
            mpatches.Patch(color='#ef4444', label='Relación Negativa (-)'),
            mpatches.Patch(color='#6366f1', label='Variable del Sistema')
        ]
        legend = ax.legend(
            handles=legend_elements,
            loc='upper left',
            facecolor='#1e293b',
            edgecolor='#475569',
            fontsize=10
        )
        for text in legend.get_texts():
            text.set_color('white')
        
        ax.set_title(
            'Diagrama de Lazos Causales - Retroalimentación del Sistema',
            color='white',
            fontsize=16,
            fontweight='bold',
            pad=20
        )
        ax.axis('off')
        
        plt.tight_layout()
        
        # Convertir a base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=150, facecolor='#020617', edgecolor='none')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode()
        plt.close(fig)
        
        return f"data:image/png;base64,{image_base64}"
        
    except Exception as e:
        print(f"Error generando diagrama causal: {str(e)}")
        import traceback
        traceback.print_exc()
        return None
