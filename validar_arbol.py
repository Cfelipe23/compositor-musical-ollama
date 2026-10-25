
import json

with open("arbol_musical.json", "r", encoding="utf-8") as archivo:
    arbol = json.load(archivo)

print("El archivo JSON es válido.")
print("Pregunta inicial:", arbol["pregunta"])
print("Géneros disponibles:")

for genero in arbol["hijos"]:
    print("-", genero["valor"])

print("Preguntas finales:", len(arbol["preguntas_finales"]))
