import pysd

m = pysd.read_vensim('static/vensim/taller5_forrester.mdl')
deps = m.get_dependencies()

print("Tipo:", type(deps))
print("\nAtributos disponibles:")
for attr in dir(deps):
    if not attr.startswith('_'):
        print(f"  - {attr}")

print("\nc_vars (control variables):", deps.c_vars)
print("\nd_deps (dynamic dependencies):", type(deps.d_deps))
if deps.d_deps:
    print("  Keys:", list(deps.d_deps.keys())[:5])
    
print("\ns_deps (stateful dependencies):", type(deps.s_deps))
if deps.s_deps:
    print("  Keys:", list(deps.s_deps.keys())[:5])

# Obtener variables del modelo
print("\n\nVariables del modelo:")
print(list(m.components.keys())[:10])
