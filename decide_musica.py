
# decide_musica.py
# Selecciona una guia musical del catalogo usando Ollama.

import json
from pathlib import Path

import ollama


# --------------------------------------------------
# CONFIGURACION
# --------------------------------------------------

CARPETA_PROYECTO = Path(__file__).resolve().parent

CATALOGO_FILE = CARPETA_PROYECTO / "catalogo_musical.json"

# Nombre del modelo derivado que crearemos con Ollama.
MODELO = "arbol-musical"


# --------------------------------------------------
# 1. CARGAR EL CATALOGO
# --------------------------------------------------

def cargar_catalogo(path=CATALOGO_FILE):
    """
    Carga las guias musicales desde el archivo JSON.
    """

    with open(path, "r", encoding="utf-8") as archivo:
        catalogo = json.load(archivo)

    if "guias" not in catalogo:
        raise ValueError(
            "El catalogo no contiene la clave 'guias'."
        )

    nombres = [
        guia["nombre"]
        for guia in catalogo["guias"]
    ]

    if len(nombres) != len(set(nombres)):
        raise ValueError(
            "Hay identificadores duplicados en el catalogo."
        )

    return catalogo


# --------------------------------------------------
# 2. PREPARAR LAS GUIAS PARA EL MODELO
# --------------------------------------------------

def preparar_guias(catalogo):
    """
    Extrae los datos necesarios para que Ollama
    conozca las guias que puede seleccionar.
    """

    guias_disponibles = []

    for guia in catalogo["guias"]:
        guias_disponibles.append({
            "nombre": guia["nombre"],
            "descripcion": guia["descripcion"],
            "instrucciones": guia["instrucciones"],
            "tags": guia.get("tags", [])
        })

    return guias_disponibles


# --------------------------------------------------
# 3. SOLICITAR LA RECOMENDACION A OLLAMA
# --------------------------------------------------

def consultar_ollama(respuestas, guia_sugerida, catalogo):
    """
    Envía las respuestas del usuario y el catalogo
    al modelo de Ollama.

    Devuelve el nombre de la guia elegida y la razon.
    """

    guias = preparar_guias(catalogo)

    prompt = f"""
Debes seleccionar la guia musical mas adecuada.

RESPUESTAS DEL USUARIO:
{json.dumps(respuestas, ensure_ascii=False, indent=2)}

GUIA SUGERIDA POR EL ARBOL:
{guia_sugerida}

CATALOGO DE GUIAS DISPONIBLES:
{json.dumps(guias, ensure_ascii=False, indent=2)}

REGLAS:
1. Selecciona una sola guia del catalogo.
2. No inventes identificadores.
3. Si la guia sugerida existe en el catalogo y es
   coherente con las respuestas, seleccionala.
4. Considera el genero, subgenero, enfoque y las
   preferencias expresadas por el usuario.
5. Explica brevemente la seleccion en español.
6. Devuelve exclusivamente un objeto JSON valido.

FORMATO OBLIGATORIO:
{{
    "nombre": "identificador_exacto_de_la_guia",
    "razon": "Explicacion breve en español"
}}
"""

    respuesta = ollama.chat(
        model=MODELO,
        messages=[
            {
                "role": "system",
                "content": (
                    "Eres un experto en composicion musical. "
                    "Seleccionas guias exclusivamente del "
                    "catalogo proporcionado. Respondes en JSON."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        format="json",
        options={
            "temperature": 0
        }
    )

    contenido = respuesta["message"]["content"]

    resultado = json.loads(contenido)

    if not isinstance(resultado, dict):
        raise ValueError(
            "Ollama no devolvio un objeto JSON."
        )

    nombre = resultado.get("nombre")
    razon = resultado.get("razon")

    if not isinstance(nombre, str) or not nombre:
        raise ValueError(
            "La respuesta de Ollama no contiene un nombre valido."
        )

    if not isinstance(razon, str):
        razon = "Guia seleccionada para el perfil musical."

    return {
        "nombre": nombre,
        "razon": razon
    }


# --------------------------------------------------
# 4. VALIDAR LA GUIA SELECCIONADA
# --------------------------------------------------

def buscar_guia(nombre, catalogo):
    """
    Busca una guia por su identificador exacto.
    """

    for guia in catalogo["guias"]:
        if guia["nombre"] == nombre:
            return guia

    return None


# --------------------------------------------------
# 5. FUNCION PRINCIPAL DE DECISION
# --------------------------------------------------

def decidir_guia(
    respuestas,
    guia_sugerida,
    catalogo_path=CATALOGO_FILE
):
    """
    Selecciona una guia musical y devuelve sus datos.

    Si Ollama falla o propone una guia inexistente,
    utiliza la guia sugerida por el arbol, siempre
    que esa guia exista en el catalogo.
    """

    catalogo = cargar_catalogo(catalogo_path)

    guia_base = buscar_guia(
        guia_sugerida,
        catalogo
    )

    if guia_base is None:
        raise ValueError(
            "La guia sugerida por el arbol no existe "
            "en el catalogo: " + str(guia_sugerida)
        )

   
    try:
        seleccion = consultar_ollama(
            respuestas,
            guia_sugerida,
            catalogo
        )

        guia_elegida = buscar_guia(
            seleccion["nombre"],
            catalogo
        )

        if guia_elegida is None:
            raise ValueError(
                "Ollama selecciono una guia inexistente."
            )

        if guia_elegida["nombre"] != guia_sugerida:
            guia_elegida = guia_base
            razon = (
                "Se conservo la guia del arbol de decisiones "
                "porque la guia propuesta por Ollama era diferente."
            )
            fuente = "arbol_validado"
        else:
            razon = seleccion["razon"]
            fuente = "ollama"

    except Exception as error:
        guia_elegida = guia_base
        razon = (
            "Se utilizo la guia sugerida por el arbol como respaldo. "
            "Detalle: " + str(error)
        )
        fuente = "arbol"


    return {
        "nombre": guia_elegida["nombre"],
        "razon": razon,
        "descripcion": guia_elegida["descripcion"],
        "instrucciones": guia_elegida["instrucciones"],
        "tags": guia_elegida.get("tags", []),
        "fuente": fuente
    }


def generar_propuesta_musical(respuestas, guia):
    """
    Genera una propuesta de cancion personalizada usando Ollama.

    Parametros:
        respuestas: preferencias musicales del usuario.
        guia: guia musical validada por decidir_guia().

    Retorna:
        Un diccionario con el titulo, concepto, direccion musical,
        estructura y letra propuesta.
    """

    
    prompt = f"""
Compón una propuesta de canción ORIGINAL y coherente con el perfil
musical del usuario. Escribe como un compositor cuidadoso, no como
un generador de frases repetidas.

PERFIL MUSICAL:
{json.dumps(respuestas, ensure_ascii=False, indent=2)}

GUIA MUSICAL VALIDADA:
{json.dumps(guia, ensure_ascii=False, indent=2)}

REGLAS OBLIGATORIAS:

1. Respeta exactamente el género, subgénero y enfoque seleccionados.
2. La emoción indicada debe notarse en la letra.
3. Conserva el hook escrito por el usuario y úsalo literalmente al
   menos una vez en el estribillo, salvo que sea una instrucción
   imposible de interpretar como letra.
4. No sustituyas el hook por el título. El título puede ser diferente.
5. Sigue las instrucciones de la guía musical validada.
6. Prioriza el instrumento elegido. Puedes añadir otros instrumentos
   únicamente si complementan el estilo.
7. Respeta la estructura elegida y evita incluir secciones duplicadas.
8. Cada sección de la letra debe aportar una idea nueva.
9. No copies versos enteros de una sección a otra, excepto el hook
   y las repeticiones naturales del estribillo.
10. Evita frases genéricas, contradicciones, palabras pegadas y
    construcciones gramaticales incorrectas.
11. No inventes citas, títulos de canciones existentes ni nombres
    de artistas como recomendaciones.
12. Todas las recomendaciones deben ser consejos prácticos de
    composición, interpretación o instrumentación.
13. Escribe una letra original. No imites a artistas concretos.
14. Usa español natural y revisa la coherencia antes de responder.

EXTENSION ORIENTATIVA:
- Verso 1: entre 4 y 6 líneas.
- Preestribillo: entre 2 y 4 líneas.
- Estribillo: entre 4 y 6 líneas.
- Verso 2: entre 4 y 6 líneas.
- Puente: entre 2 y 4 líneas.
- Estribillo final: entre 4 y 6 líneas.

FORMATO DE RESPUESTA:
Devuelve exclusivamente un objeto JSON válido con estas claves:

{{
    "titulo": "Título original",
    "concepto": "Resumen del mensaje de la canción",
    "direccion_musical": "Descripción coherente del sonido",
    "estructura": [
        {{
            "seccion": "Intro",
            "indicaciones": "Indicaciones musicales concretas"
        }}
    ],
    "letra": {{
        "verso_1": "Verso original",
        "preestribillo": "Preestribillo original",
        "estribillo": "Estribillo original",
        "verso_2": "Segundo verso original",
        "puente": "Puente original",
        "estribillo_final": "Estribillo final"
    }},
    "recomendaciones": [
        "Consejo concreto de composición"
    ]
}}

Todos los textos deben estar en español.
No incluyas explicaciones fuera del JSON.
No añadas secciones que no correspondan al formato solicitado.
"""


    respuesta = ollama.chat(
        model=MODELO,
        messages=[
            {
                "role": "system",
                "content": (
                    "Eres un compositor musical creativo y profesional. "
                    "Generas propuestas originales y personalizadas. "
                    "Respetas el perfil del usuario y las instrucciones "
                    "de la guia validada. Respondes en JSON valido."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        format="json",
        options={"temperature": 0.4,
                 "num_predict": 1200}
    )

    contenido = respuesta["message"]["content"]
    propuesta = json.loads(contenido)

    if not isinstance(propuesta, dict):
        raise ValueError(
            "El modelo no devolvio una propuesta en formato objeto JSON."
        )

    campos_obligatorios = [
        "titulo",
        "concepto",
        "direccion_musical",
        "estructura",
        "letra",
        "recomendaciones"
    ]

    for campo in campos_obligatorios:
        if campo not in propuesta:
            raise ValueError(
                f"La propuesta generada no contiene el campo: {campo}"
            )

    if not isinstance(propuesta["estructura"], list):
        raise ValueError("La estructura musical debe ser una lista.")

    if not isinstance(propuesta["letra"], dict):
        raise ValueError("La letra debe ser un objeto JSON.")

    return propuesta

# --------------------------------------------------
# 6. PRUEBA INDEPENDIENTE DEL MODULO
# --------------------------------------------------

if __name__ == "__main__":

    respuestas_demo = {
        "genero": "Rock pop",
        "subgenero": "Rock pop en español",
        "enfoque": "Romantico/emocional",
        "emocion": "Nostalgia",
        "hook": "Volver a encontrarte",
        "estructura": (
            "Verso - estribillo - verso - estribillo "
            "- puente - estribillo"
        ),
        "voz": "Voz media",
        "instrumento": "Guitarra electrica"
    }

    guia_demo = "estribillo_amplio_cantable"

    print("Consultando el sistema de recomendacion...\n")

    resultado = decidir_guia(
        respuestas=respuestas_demo,
        guia_sugerida=guia_demo
    )

    print("GUIA MUSICAL SELECCIONADA")
    print("-------------------------")
    print("Nombre:", resultado["nombre"])
    print("Razon:", resultado["razon"])
    print("Descripcion:", resultado["descripcion"])
    print("Instrucciones:", resultado["instrucciones"])
    print("Etiquetas:", ", ".join(resultado["tags"]))
    print("Fuente:", resultado["fuente"])
