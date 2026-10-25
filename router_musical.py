
# router_musical.py
# Interfaz de consola para recorrer el arbol musical
# y obtener una recomendacion personalizada.

import json
from pathlib import Path

from decide_musica import decidir_guia, generar_propuesta_musical

# --------------------------------------------------
# CONFIGURACION
# --------------------------------------------------

CARPETA_PROYECTO = Path(__file__).resolve().parent

ARBOL_FILE = CARPETA_PROYECTO / "arbol_musical.json"


# --------------------------------------------------
# 1. CARGAR EL ARBOL
# --------------------------------------------------

def cargar_arbol(path=ARBOL_FILE):
    """Carga el arbol musical desde un archivo JSON."""

    with open(path, "r", encoding="utf-8") as archivo:
        return json.load(archivo)


def obtener_paso_arbol(arbol, camino):
    """Devuelve la pregunta y las opciones correspondientes al camino."""

    nodo = arbol

    for valor in camino:
        nodo = next(
            (
                hijo
                for hijo in nodo.get("hijos", [])
                if hijo.get("valor") == valor
            ),
            None
        )

        if nodo is None:
            raise ValueError(
                "El camino seleccionado no existe en el arbol musical."
            )

    hijos = nodo.get("hijos", [])

    if not hijos:
        guia = nodo.get("guia")

        if not guia:
            raise ValueError(
                "Se llego a un nodo sin hijos ni guia."
            )

        return {
            "pregunta": None,
            "opciones": [],
            "guia": guia
        }

    pregunta = nodo.get("pregunta")

    if not pregunta:
        raise ValueError(
            "El nodo con opciones no contiene una pregunta."
        )

    return {
        "pregunta": pregunta,
        "opciones": hijos,
        "guia": None
    }


# --------------------------------------------------
# 2. MOSTRAR OPCIONES
# --------------------------------------------------

def mostrar_opciones(opciones):
    """Muestra las opciones numeradas y permite elegir."""

    if not opciones:
        raise ValueError("No hay opciones disponibles.")

    while True:
        print()

        for numero, opcion in enumerate(opciones, start=1):
            print(f"{numero}. {opcion['valor']}")

        respuesta = input(
            "\nSelecciona una opcion escribiendo su numero: "
        ).strip()

        try:
            seleccion = int(respuesta)

            if 1 <= seleccion <= len(opciones):
                return opciones[seleccion - 1]

            print(
                f"Elige un numero entre 1 y {len(opciones)}."
            )

        except ValueError:
            print("Entrada no valida. Escribe un numero.")


# --------------------------------------------------
# 3. RECORRER EL ARBOL DE DECISIONES
# --------------------------------------------------

def recorrer_arbol(nodo, camino):
    """
    Recorre el arbol de manera interactiva.

    Cada nodo presenta su pregunta y sus opciones.
    Cuando llega a una hoja, devuelve la guia sugerida.
    """

    pregunta = nodo.get("pregunta")

    if pregunta:
        print("\n" + "=" * 55)
        print(pregunta)
        print("=" * 55)

    hijos = nodo.get("hijos", [])

    # Si el nodo no tiene hijos, es una hoja.
    if not hijos:
        guia = nodo.get("guia")

        if not guia:
            raise ValueError(
                "Se llego a un nodo sin hijos ni guia."
            )

        return guia

    opcion = mostrar_opciones(hijos)

    camino.append(opcion["valor"])

    return recorrer_arbol(opcion, camino)


# --------------------------------------------------
# 4. REALIZAR LAS PREGUNTAS FINALES
# --------------------------------------------------

def realizar_preguntas_finales(arbol):
    """
    Solicita emocion, hook, estructura, voz e instrumento.
    Las opciones se leen directamente del JSON.
    """

    respuestas = {}

    preguntas = arbol.get("preguntas_finales", [])

    print("\n" + "=" * 55)
    print("PERSONALIZA TU CANCION")
    print("=" * 55)

    for pregunta in preguntas:
        identificador = pregunta["id"]
        texto = pregunta["pregunta"]

        print("\n" + texto)

        # Pregunta de respuesta libre, como el hook.
        if pregunta.get("tipo") == "texto_libre":
            while True:
                respuesta = input(
                    "Escribe tu respuesta: "
                ).strip()

                if respuesta:
                    respuestas[identificador] = respuesta
                    break

                print("La respuesta no puede estar vacia.")

        # Pregunta con opciones definidas en el JSON.
        else:
            opciones = pregunta.get("opciones", [])

            if not opciones:
                raise ValueError(
                    "La pregunta no tiene opciones: " + identificador
                )

            while True:
                for numero, opcion in enumerate(
                    opciones, start=1
                ):
                    print(f"{numero}. {opcion}")

                entrada = input(
                    "Selecciona una opcion: "
                ).strip()

                try:
                    numero = int(entrada)

                    if 1 <= numero <= len(opciones):
                        respuestas[identificador] = (
                            opciones[numero - 1]
                        )
                        break

                    print(
                        f"Elige un numero entre 1 y "
                        f"{len(opciones)}."
                    )

                except ValueError:
                    print("Entrada no valida. Escribe un numero.")

    return respuestas


# --------------------------------------------------
# 5. MOSTRAR EL PERFIL MUSICAL
# --------------------------------------------------

def mostrar_perfil(camino, respuestas, resultado):
    """Presenta la seleccion y la propuesta musical."""

    print("\n" + "=" * 60)
    print("RESULTADO DE TU COMPOSICION MUSICAL")
    print("=" * 60)

    print("\nESTILO SELECCIONADO")

    for nivel, valor in enumerate(camino, start=1):
        print(f"{nivel}. {valor}")

    print("\nGUIA MUSICAL RECOMENDADA")
    print("Nombre:", resultado["nombre"])
    print("Motivo:", resultado["razon"])

    print("\nINSTRUCCIONES DE LA GUIA")
    print(resultado["instrucciones"])

    print("\nTU PERFIL MUSICAL PERSONALIZADO")
    print("Genero:", camino[0] if camino else "No definido")
    print("Subgenero:", camino[1] if len(camino) > 1 else "No definido")
    print("Enfoque:", camino[2] if len(camino) > 2 else "No definido")
    print("Emocion central:", respuestas.get("emocion", "No definida"))
    print("Hook:", respuestas.get("hook", "No definido"))
    print("Estructura:", respuestas.get("estructura", "No definida"))
    print("Voz:", respuestas.get("voz", "No definida"))
    print("Instrumento:", respuestas.get("instrumento", "No definido"))

    print("\nPROPUESTA INICIAL PARA COMPONER")

    print(
        f"Crea una cancion de {camino[0]} "
        f"con el enfoque {camino[-1] if len(camino) > 2 else camino[0]}, "
        f"centrada en la emocion de "
        f"{respuestas.get('emocion', 'una emocion por definir')}."
    )

    print(
        f"Utiliza como hook la idea: "
        f"'{respuestas.get('hook', '')}'."
    )

    print(
        f"Organiza la cancion con esta estructura: "
        f"{respuestas.get('estructura', 'por definir')}."
    )

    print(
        f"Adapta la interpretacion a "
        f"{respuestas.get('voz', 'una voz por definir')} "
        f"y destaca el sonido de "
        f"{respuestas.get('instrumento', 'un instrumento por definir')}."
    )

    print("\nDESCRIPCION DE LA GUIA")
    print(resultado["descripcion"])

    print("\nOrigen de la recomendacion:", resultado["fuente"])
    print("=" * 60)


def mostrar_propuesta_musical(propuesta):
    print("\n" + "=" * 60)
    print("PROPUESTA DE CANCION GENERADA POR IA")
    print("=" * 60)

    print("\nTITULO")
    print(propuesta["titulo"])

    print("\nCONCEPTO DE LA CANCION")
    print(propuesta["concepto"])

    print("\nDIRECCION MUSICAL")
    print(propuesta["direccion_musical"])

    print("\nESTRUCTURA MUSICAL")
    for seccion in propuesta["estructura"]:
        if isinstance(seccion, dict):
            nombre = seccion.get("seccion", "Seccion")
            indicaciones = seccion.get("indicaciones", "")
            print(f"\n{nombre.upper()}")
            print(indicaciones)
        else:
            print(seccion)

    print("\n" + "-" * 60)
    print("LETRA PROPUESTA")
    print("-" * 60)

    letra = propuesta["letra"]

    nombres_secciones = {
        "verso_1": "VERSO 1",
        "preestribillo": "PREESTRIBILLO",
        "estribillo": "ESTRIBILLO",
        "verso_2": "VERSO 2",
        "puente": "PUENTE",
        "estribillo_final": "ESTRIBILLO FINAL"
    }

    for clave, titulo in nombres_secciones.items():
        contenido = letra.get(clave, "")

        if contenido and contenido.strip():
            print(f"\n{titulo}")
            print(contenido)

    print("\n" + "-" * 60)
    print("RECOMENDACIONES MUSICALES")
    print("-" * 60)

    for recomendacion in propuesta["recomendaciones"]:
        print(f"- {recomendacion}")

    print("\n" + "=" * 60)


def construir_respuestas(camino, respuestas_finales):
    """Construye el perfil que consumen las funciones de decision."""

    return {
        "camino": camino,
        "genero": camino[0] if len(camino) > 0 else "",
        "subgenero": camino[1] if len(camino) > 1 else "",
        "enfoque": camino[2] if len(camino) > 2 else "",
        **respuestas_finales
    }


# --------------------------------------------------
# 6. FUNCION PRINCIPAL
# --------------------------------------------------


def main():
    print("=" * 60)
    print("ASISTENTE DE COMPOSICION MUSICAL")
    print("=" * 60)
    print("Responde las preguntas para definir tu estilo musical.")

    try:
        arbol = cargar_arbol()

        # 1. Recorrer el arbol de decisiones.
        camino = []
        guia_sugerida = recorrer_arbol(arbol, camino)

        # 2. Recopilar las preferencias musicales.
        respuestas_finales = realizar_preguntas_finales(arbol)

        respuestas = construir_respuestas(camino, respuestas_finales)

        # 3. Seleccionar y validar la guia musical.
        print("\nBuscando la guia musical mas adecuada...")

        resultado = decidir_guia(
            respuestas=respuestas,
            guia_sugerida=guia_sugerida
        )

        # 4. Mostrar el perfil y la guia seleccionada.
        mostrar_perfil(camino, respuestas_finales, resultado)

        # 5. Generar la propuesta creativa con Ollama.
        print("\nGenerando tu propuesta musical con inteligencia artificial...")
        print("Esto puede tardar unos momentos.\n")

        propuesta = generar_propuesta_musical(
            respuestas=respuestas,
            guia=resultado
        )

        # 6. Mostrar la propuesta generada.
        mostrar_propuesta_musical(propuesta)

    except FileNotFoundError as error:
        print("\nERROR: No se encontro un archivo necesario.")
        print(error)
        print("Verifica que los archivos esten en la carpeta del proyecto.")

    except json.JSONDecodeError as error:
        print("\nERROR: Hay un problema con un archivo JSON.")
        print(error)

    except Exception as error:
        print("\nERROR durante la ejecucion:")
        print(error)


if __name__ == "__main__":
    main()
