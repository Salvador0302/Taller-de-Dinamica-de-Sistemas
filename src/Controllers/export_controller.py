"""
Controlador para exportar datos de simulaciones en múltiples formatos
"""
import pandas as pd
import plotly.graph_objects as go
from io import BytesIO
import base64
from datetime import datetime
import json


def export_to_excel(simulation_data, filename=None):
    """
    Exporta datos de simulación a Excel con formato profesional
    
    Args:
        simulation_data: Diccionario con datos de simulación
        filename: Nombre del archivo (opcional)
    
    Returns:
        BytesIO: Buffer con archivo Excel
    """
    if filename is None:
        filename = f"simulacion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        workbook = writer.book
        
        # Formatos
        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': '#3B82F6',
            'font_color': 'white',
            'border': 1
        })
        
        cell_format = workbook.add_format({
            'border': 1,
            'align': 'center'
        })
        
        # Hoja de resumen
        summary_data = []
        for var_name, var_data in simulation_data.items():
            if isinstance(var_data, dict) and 'data' in var_data:
                values = list(var_data['data'].values())
                summary_data.append({
                    'Variable': var_name,
                    'Valor Inicial': values[0] if values else 0,
                    'Valor Final': values[-1] if values else 0,
                    'Promedio': sum(values) / len(values) if values else 0,
                    'Máximo': max(values) if values else 0,
                    'Mínimo': min(values) if values else 0
                })
        
        if summary_data:
            df_summary = pd.DataFrame(summary_data)
            df_summary.to_excel(writer, sheet_name='Resumen', index=False)
            
            worksheet = writer.sheets['Resumen']
            for col_num, col_name in enumerate(df_summary.columns):
                worksheet.write(0, col_num, col_name, header_format)
                worksheet.set_column(col_num, col_num, 20)
        
        # Hojas individuales por variable
        for var_name, var_data in simulation_data.items():
            if isinstance(var_data, dict) and 'data' in var_data:
                df = pd.DataFrame(list(var_data['data'].items()), 
                                columns=['Tiempo', var_name])
                
                sheet_name = var_name[:31]  # Excel limita a 31 caracteres
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                
                worksheet = writer.sheets[sheet_name]
                for col_num, col_name in enumerate(df.columns):
                    worksheet.write(0, col_num, col_name, header_format)
                    worksheet.set_column(col_num, col_num, 15)
    
    output.seek(0)
    return output


def export_to_csv(simulation_data, filename=None):
    """
    Exporta datos de simulación a CSV
    
    Args:
        simulation_data: Diccionario con datos de simulación
        filename: Nombre del archivo (opcional)
    
    Returns:
        str: Contenido CSV
    """
    if filename is None:
        filename = f"simulacion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    # Combinar todos los datos en un DataFrame
    all_data = {}
    for var_name, var_data in simulation_data.items():
        if isinstance(var_data, dict) and 'data' in var_data:
            all_data[var_name] = list(var_data['data'].values())
    
    if all_data:
        df = pd.DataFrame(all_data)
        return df.to_csv(index=False)
    
    return ""


def export_comparison_to_excel(scenarios_data, filename=None):
    """
    Exporta comparación de múltiples escenarios a Excel
    
    Args:
        scenarios_data: Lista de diccionarios con datos de escenarios
        filename: Nombre del archivo (opcional)
    
    Returns:
        BytesIO: Buffer con archivo Excel
    """
    if filename is None:
        filename = f"comparacion_escenarios_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        workbook = writer.book
        
        # Formatos
        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': '#8B5CF6',
            'font_color': 'white',
            'border': 1
        })
        
        # Hoja de comparación
        for var_name in scenarios_data[0]['data'].keys():
            comparison_data = {'Tiempo': list(scenarios_data[0]['data'][var_name]['data'].keys())}
            
            for i, scenario in enumerate(scenarios_data):
                scenario_name = scenario.get('name', f'Escenario {i+1}')
                if var_name in scenario['data']:
                    comparison_data[scenario_name] = list(scenario['data'][var_name]['data'].values())
            
            df = pd.DataFrame(comparison_data)
            sheet_name = var_name[:31]
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            worksheet = writer.sheets[sheet_name]
            for col_num, col_name in enumerate(df.columns):
                worksheet.write(0, col_num, col_name, header_format)
                worksheet.set_column(col_num, col_num, 15)
    
    output.seek(0)
    return output


def generate_pdf_report(simulation_data, parameters=None, filename=None):
    """
    Genera un reporte PDF con gráficos y estadísticas
    
    Args:
        simulation_data: Diccionario con datos de simulación
        parameters: Parámetros usados en la simulación (opcional)
        filename: Nombre del archivo (opcional)
    
    Returns:
        BytesIO: Buffer con archivo PDF
    """
    try:
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
        
        if filename is None:
            filename = f"reporte_simulacion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Título
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#3B82F6'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        story.append(Paragraph("Reporte de Simulación VENSIM", title_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Fecha
        date_style = ParagraphStyle(
            'DateStyle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.grey,
            alignment=TA_CENTER
        )
        story.append(Paragraph(f"Generado el {datetime.now().strftime('%d/%m/%Y %H:%M')}", date_style))
        story.append(Spacer(1, 0.5*inch))
        
        # Parámetros si están disponibles
        if parameters:
            story.append(Paragraph("Parámetros de Simulación", styles['Heading2']))
            param_data = [[k.replace('_', ' ').title(), f"{v:.4f}"] for k, v in parameters.items()]
            param_table = Table(param_data, colWidths=[3*inch, 2*inch])
            param_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F1F5F9')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey)
            ]))
            story.append(param_table)
            story.append(PageBreak())
        
        # Resumen estadístico
        story.append(Paragraph("Resumen Estadístico", styles['Heading2']))
        story.append(Spacer(1, 0.2*inch))
        
        summary_data = [['Variable', 'Inicial', 'Final', 'Promedio', 'Max', 'Min']]
        for var_name, var_data in simulation_data.items():
            if isinstance(var_data, dict) and 'data' in var_data:
                values = list(var_data['data'].values())
                if values:
                    summary_data.append([
                        var_name,
                        f"{values[0]:,.0f}",
                        f"{values[-1]:,.0f}",
                        f"{sum(values)/len(values):,.0f}",
                        f"{max(values):,.0f}",
                        f"{min(values):,.0f}"
                    ])
        
        summary_table = Table(summary_data, colWidths=[2*inch, 1*inch, 1*inch, 1*inch, 1*inch, 1*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3B82F6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(summary_table)
        
        doc.build(story)
        buffer.seek(0)
        return buffer
        
    except ImportError:
        # Si reportlab no está disponible, retornar None
        return None


def export_plotly_to_image(fig, format='png', width=1200, height=800):
    """
    Exporta un gráfico Plotly a imagen
    
    Args:
        fig: Figura de Plotly
        format: Formato de imagen ('png', 'jpg', 'svg')
        width: Ancho en píxeles
        height: Alto en píxeles
    
    Returns:
        bytes: Imagen en bytes
    """
    try:
        img_bytes = fig.to_image(format=format, width=width, height=height, scale=2)
        return img_bytes
    except Exception as e:
        print(f"Error exportando imagen: {e}")
        return None
