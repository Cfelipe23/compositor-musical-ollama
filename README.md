![Python](https://img.shields.io/badge/Python-3.x-blue?style=flat&logo=python&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-Local_AI-black?style=flat)
![License](https://img.shields.io/badge/License-Academic-green?style=flat)
# Asistente de Composición Musical

## 1. Descripción del proyecto

Este proyecto desarrolla un asistente de composición musical que utiliza
un árbol de decisiones, un catálogo de guías musicales y un modelo de
inteligencia artificial ejecutado localmente mediante Ollama.

El sistema permite que el usuario seleccione un género musical,
un subgénero y un enfoque de composición. Después, responde preguntas
sobre la emoción, el hook, la estructura, la voz y los instrumentos
que desea incorporar.

Con esta información, el sistema recomienda una guía musical y presenta
una propuesta inicial para orientar la composición de una canción.

## 2. Objetivo general

Desarrollar un sistema de recomendación musical basado en árboles de
decisión e inteligencia artificial, capaz de orientar la composición
de canciones según las preferencias expresadas por el usuario.

## 3. Objetivos específicos

- Organizar los géneros y subgéneros musicales mediante un árbol de decisiones.
- Almacenar las guías de composición en un catálogo JSON.
- Recopilar las preferencias del usuario desde una interfaz gráfica o la consola.
- Utilizar Ollama para seleccionar una guía del catálogo.
- Proporcionar una guía de composición personalizada.
- Mantener una alternativa de selección cuando el modelo no esté disponible.

## 4. Tecnologías utilizadas

- Python 3.
- Ollama.
- Modelo base: llama3.2:1b.
- Archivos JSON para almacenar el árbol y el catálogo.
- Modelfile para configurar el modelo personalizado.
- Interfaz de escritorio con CustomTkinter y alternativa de consola.

## 5. Arquitectura del proyecto

### arbol_musical.json

Contiene el árbol de decisiones. Define las preguntas, las opciones
disponibles y las ramas que conducen a una guía musical.

### catalogo_musical.json

Contiene las guías musicales. Cada guía incluye un identificador,
una descripción, instrucciones y etiquetas.

### decide_musica.py

Carga el catálogo y consulta al modelo de Ollama para seleccionar
la guía más apropiada. También valida la selección y utiliza la
guía sugerida por el árbol como alternativa ante errores.

### router_musical.py

Contiene el recorrido del árbol, la recopilación de preferencias y la
presentación de resultados para la consola. También expone las funciones
compartidas que permiten a la interfaz gráfica consultar el siguiente paso
del árbol y construir el perfil musical.

### interfaz_grafica.py

Presenta el cuestionario y los resultados en una ventana de escritorio.
Utiliza las funciones de `router_musical.py` y las funciones de decisión y
generación de `decide_musica.py`; las consultas al modelo se ejecutan en
segundo plano para mantener la ventana disponible.

### Modelfile

Define el modelo personalizado arbol-musical a partir de llama3.2:1b.
Incluye las instrucciones para seleccionar guías musicales y responder
en formato JSON.

### requirements.txt

Contiene las dependencias externas de Python necesarias para ejecutar
el proyecto.

## 6. Requisitos previos

Antes de ejecutar el proyecto, se necesita:

- Python instalado.
- Ollama instalado.
- El modelo base llama3.2:1b descargado.
- Los archivos del proyecto ubicados en una misma carpeta.

## 7. Instalación

### Paso 1. Instalar las dependencias de Python

Desde la terminal, en la carpeta del proyecto, ejecutar:

    python -m pip install -r requirements.txt

### Paso 2. Descargar el modelo base

    ollama pull llama3.2:1b

### Paso 3. Crear el modelo personalizado

    ollama create arbol-musical -f Modelfile

### Paso 4. Verificar el modelo

    ollama list

Debe aparecer arbol-musical entre los modelos disponibles.

## 8. Ejecución

Desde la terminal, ejecutar:

    python interfaz_grafica.py

La aplicación presenta las preguntas del árbol de decisiones y solicita
las preferencias musicales del usuario. La versión de consola se mantiene
disponible con `python router_musical.py`.

Al finalizar, muestra la guía recomendada, la razón de la selección,
las instrucciones de composición y el perfil musical definido.

## 9. Flujo de funcionamiento

1. El usuario inicia la interfaz gráfica o la versión de consola.
2. El router carga el árbol de decisiones.
3. El usuario selecciona género, subgénero y enfoque.
4. El sistema recoge las preferencias de composición.
5. El módulo de decisión carga el catálogo musical.
6. Ollama selecciona una guía disponible.
7. El sistema valida la guía seleccionada.
8. Si ocurre un error, se utiliza la guía sugerida por el árbol.
9. El programa presenta el resultado y una propuesta inicial.

## 10. Pruebas recomendadas

- Seleccionar diferentes géneros y comprobar las ramas del árbol.
- Verificar que las opciones numéricas incorrectas se soliciten nuevamente.
- Comprobar que las respuestas de texto no estén vacías.
- Confirmar que los identificadores de las guías existan en el catálogo.
- Ejecutar el programa con Ollama disponible.
- Probar el mecanismo alternativo cuando falle la consulta al modelo.
- Comprobar que el resultado refleje las preferencias del usuario.

## 11. Limitaciones actuales

La versión actual recomienda una guía musical y solicita a Ollama una
propuesta con título, concepto, dirección musical, estructura, letra y
recomendaciones, a partir de las respuestas del usuario. La generación
requiere que Ollama esté disponible y que el modelo `arbol-musical` esté
instalado.

## 12. Posibles mejoras

- Generar letras originales a partir del perfil musical.
- Proponer títulos y estribillos personalizados.
- Recomendar tempo, tonalidad e instrumentos.
- Incorporar pruebas automatizadas.
- Ampliar el árbol y el catálogo con nuevas guías.
- Permitir guardar los resultados de cada composición.

## 13. Autoría

Proyecto académico de composición musical asistida por inteligencia artificial.
