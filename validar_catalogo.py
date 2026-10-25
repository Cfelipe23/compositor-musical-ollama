
import json

with open("catalogo_musical.json", "r", encoding="utf-8") as archivo:
    catalogo = json.load(archivo)

guias = catalogo["guias"]
nombres = [guia["nombre"] for guia in guias]

print("El catálogo JSON es válido.")
print("Total de guías:", len(guias))
print("Identificadores duplicados:", len(nombres) - len(set(nombres)))

for guia in guias:
    print("-", guia["nombre"])
