"""
Script de prueba para verificar la generación de diagramas
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.Controllers.diagram_generator import generate_forrester_diagram, generate_causal_diagram

model_path = 'static/vensim/taller5_forrester.mdl'

print("=" * 60)
print("PRUEBA DE GENERACIÓN DE DIAGRAMAS")
print("=" * 60)

print("\n1. Generando diagrama de Forrester...")
try:
    forrester = generate_forrester_diagram(model_path)
    if forrester:
        print("✓ Diagrama de Forrester generado exitosamente")
        print(f"  Longitud de imagen base64: {len(forrester)} caracteres")
    else:
        print("✗ Error: No se generó el diagrama de Forrester")
except Exception as e:
    print(f"✗ Error generando Forrester: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n2. Generando diagrama causal...")
try:
    causal = generate_causal_diagram(model_path)
    if causal:
        print("✓ Diagrama causal generado exitosamente")
        print(f"  Longitud de imagen base64: {len(causal)} caracteres")
    else:
        print("✗ Error: No se generó el diagrama causal")
except Exception as e:
    print(f"✗ Error generando causal: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("Prueba completada")
print("=" * 60)
