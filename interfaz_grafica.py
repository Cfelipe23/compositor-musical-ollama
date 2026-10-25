"""Interfaz de escritorio para el asistente de composicion musical."""

import queue
import threading

import customtkinter as ctk

from decide_musica import decidir_guia, generar_propuesta_musical
from router_musical import (
    construir_respuestas,
    cargar_arbol,
    obtener_paso_arbol,
)


FONDO = "#0B0D12"
PANEL = "#141821"
PANEL_SECUNDARIO = "#1B202B"
ACENTO = "#28E0B5"
ACENTO_HOVER = "#18B995"
TEXTO = "#F3F5F8"
TEXTO_SECUNDARIO = "#A2AAB8"
ERROR = "#FF7777"


class AsistenteMusicalApp(ctk.CTk):
    """Presenta el cuestionario musical y los resultados reales del sistema."""

    def __init__(self):
        super().__init__()

        self.title("Arbol Musical | Asistente de composicion")
        self.geometry("1040x780")
        self.minsize(780, 640)
        self.configure(fg_color=FONDO)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self._result_queue = queue.Queue()
        self._processing = False
        self._active_mode = ""
        self._stage = ""
        self._active_question = None
        self._question_index = 0
        self._final_questions = []
        self._camino = []
        self._respuestas_finales = {}
        self._guia_sugerida = ""
        self._load_error = None

        try:
            self._arbol = cargar_arbol()
        except Exception as error:
            self._arbol = None
            self._load_error = error

        self._build_layout()

        if self._load_error is not None:
            self._set_status("No se pudo cargar el arbol musical", error=True)
            self._add_message(
                "assistant",
                "No fue posible iniciar el cuestionario.\n\n"
                f"Detalle: {self._load_error}"
            )
            self._send_button.configure(state="disabled")
        else:
            self._add_message(
                "assistant",
                "Define tu proxima composicion con el arbol musical. "
                "Empezaremos por el genero."
            )
            self._show_tree_step()

    def _build_layout(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(
            self,
            fg_color=PANEL,
            corner_radius=0,
            height=86
        )
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(1, weight=1)
        header.grid_propagate(False)

        brand = ctk.CTkFrame(header, fg_color="transparent")
        brand.grid(row=0, column=0, sticky="w", padx=(30, 18), pady=18)
        ctk.CTkLabel(
            brand,
            text="♫",
            font=ctk.CTkFont(family="Segoe UI Symbol", size=31, weight="bold"),
            text_color=ACENTO
        ).pack(side="left", padx=(0, 12))

        title_block = ctk.CTkFrame(brand, fg_color="transparent")
        title_block.pack(side="left")
        ctk.CTkLabel(
            title_block,
            text="ARBOL MUSICAL",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=TEXTO
        ).pack(anchor="w")
        ctk.CTkLabel(
            title_block,
            text="ASISTENTE DE COMPOSICION",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=TEXTO_SECUNDARIO
        ).pack(anchor="w", pady=(2, 0))

        self._status_label = ctk.CTkLabel(
            header,
            text="●  Listo para crear",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=ACENTO
        )
        self._status_label.grid(row=0, column=2, sticky="e", padx=30)

        main = ctk.CTkFrame(self, fg_color=FONDO)
        main.grid(row=1, column=0, sticky="nsew", padx=30, pady=(24, 16))
        main.grid_columnconfigure(0, weight=1)
        main.grid_rowconfigure(0, weight=1)

        self._conversation = ctk.CTkScrollableFrame(
            main,
            fg_color=FONDO,
            corner_radius=0
        )
        self._conversation.grid(row=0, column=0, sticky="nsew")
        self._conversation.grid_columnconfigure(0, weight=1)

        composer = ctk.CTkFrame(
            self,
            fg_color=PANEL,
            corner_radius=18,
            border_width=1,
            border_color="#252B37"
        )
        composer.grid(row=2, column=0, sticky="ew", padx=30, pady=(0, 22))
        composer.grid_columnconfigure(0, weight=1)

        self._question_label = ctk.CTkLabel(
            composer,
            text="",
            anchor="w",
            justify="left",
            wraplength=850,
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=TEXTO
        )
        self._question_label.grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="ew",
            padx=20,
            pady=(16, 12)
        )

        self._option_menu = ctk.CTkOptionMenu(
            composer,
            values=["Selecciona una opcion"],
            height=44,
            fg_color=PANEL_SECUNDARIO,
            button_color=ACENTO,
            button_hover_color=ACENTO_HOVER,
            text_color=TEXTO,
            dropdown_fg_color=PANEL_SECUNDARIO,
            dropdown_text_color=TEXTO,
            font=ctk.CTkFont(size=13)
        )
        self._option_menu.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=(20, 10),
            pady=(0, 18)
        )

        self._answer_entry = ctk.CTkEntry(
            composer,
            height=44,
            placeholder_text="Escribe tu frase o idea...",
            fg_color=PANEL_SECUNDARIO,
            border_color="#303847",
            text_color=TEXTO,
            placeholder_text_color=TEXTO_SECUNDARIO,
            font=ctk.CTkFont(size=13)
        )
        self._answer_entry.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=(20, 10),
            pady=(0, 18)
        )
        self._answer_entry.grid_remove()

        self._send_button = ctk.CTkButton(
            composer,
            text="Continuar  ›",
            command=self._on_submit,
            width=150,
            height=44,
            corner_radius=12,
            fg_color=ACENTO,
            hover_color=ACENTO_HOVER,
            text_color=FONDO,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self._send_button.grid(
            row=1,
            column=1,
            sticky="e",
            padx=(0, 20),
            pady=(0, 18)
        )

        self._progress = ctk.CTkProgressBar(
            composer,
            mode="indeterminate",
            height=4,
            progress_color=ACENTO,
            fg_color=PANEL_SECUNDARIO
        )
        self._progress.grid(
            row=2,
            column=0,
            columnspan=2,
            sticky="ew",
            padx=20,
            pady=(0, 14)
        )
        self._progress.grid_remove()

    def _add_message(self, role, text, is_error=False):
        is_user = role == "user"
        row = len(self._conversation.winfo_children())
        bubble_color = "#183D3B" if is_user else PANEL
        label_color = ACENTO if is_user else "#9B8CFF"
        label_text = "TU" if is_user else "ASISTENTE MUSICAL"
        if is_error:
            label_color = ERROR

        bubble = ctk.CTkFrame(
            self._conversation,
            fg_color=bubble_color,
            corner_radius=16,
            border_width=1,
            border_color="#27313D" if not is_user else "#24524D"
        )
        bubble.grid(
            row=row,
            column=0,
            sticky="e" if is_user else "w",
            padx=(120, 4) if is_user else (4, 120),
            pady=7
        )
        ctk.CTkLabel(
            bubble,
            text=label_text,
            anchor="w",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=label_color
        ).pack(anchor="w", padx=16, pady=(12, 3))
        ctk.CTkLabel(
            bubble,
            text=text,
            anchor="w",
            justify="left",
            wraplength=680,
            font=ctk.CTkFont(size=13),
            text_color=TEXTO,
            padx=16,
            pady=0
        ).pack(anchor="w", fill="x", pady=(0, 13))

        self.after(
            50,
            lambda: self._conversation._parent_canvas.yview_moveto(1.0)
        )

    def _set_status(self, text, error=False):
        self._status_label.configure(
            text=f"●  {text}",
            text_color=ERROR if error else ACENTO
        )

    def _present_question(self, prompt, options=None, free_text=False):
        self._active_question = prompt
        self._question_label.grid()
        self._question_label.configure(text=prompt)
        self._option_menu.grid_remove()
        self._answer_entry.grid_remove()

        if free_text:
            self._active_mode = "text"
            self._answer_entry.delete(0, "end")
            self._answer_entry.grid()
            self._answer_entry.focus_set()
        else:
            self._active_mode = "choice"
            values = list(options or [])
            self._option_menu.configure(
                values=["Selecciona una opcion"] + values
            )
            self._option_menu.set("Selecciona una opcion")
            self._option_menu.grid()

        self._send_button.configure(
            text="Continuar  ›",
            command=self._on_submit,
            state="normal"
        )

    def _show_tree_step(self):
        self._stage = "tree"
        try:
            paso = obtener_paso_arbol(self._arbol, self._camino)
        except Exception as error:
            self._show_error(f"No se pudo recorrer el arbol musical: {error}")
            return

        if paso["pregunta"] is None:
            self._guia_sugerida = paso["guia"]
            self._final_questions = self._arbol.get(
                "preguntas_finales",
                []
            )
            self._question_index = 0
            self._add_message(
                "assistant",
                "Estilo definido. Ahora personaliza la cancion con "
                "tus preferencias."
            )
            self._show_final_question()
            return

        options = [hijo["valor"] for hijo in paso["opciones"]]
        self._add_message(
            "assistant",
            f"{paso['pregunta']}\n\n" + "\n".join(
                f"• {option}" for option in options
            )
        )
        self._present_question(paso["pregunta"], options=options)
        self._set_status("Elige tu estilo")

    def _show_final_question(self):
        self._stage = "final"
        if self._question_index >= len(self._final_questions):
            self._run_music_pipeline()
            return

        pregunta = self._final_questions[self._question_index]
        opciones = pregunta.get("opciones")
        texto_libre = pregunta.get("tipo") == "texto_libre"
        self._add_message("assistant", pregunta["pregunta"])
        self._present_question(
            pregunta["pregunta"],
            options=opciones,
            free_text=texto_libre
        )
        self._set_status("Personaliza tu cancion")

    def _on_submit(self):
        if self._processing:
            return

        if self._active_mode == "retry":
            self._run_music_pipeline()
            return
        if self._active_mode == "done":
            self._new_composition()
            return

        if self._active_mode == "text":
            answer = self._answer_entry.get().strip()
        else:
            answer = self._option_menu.get().strip()
            if answer == "Selecciona una opcion":
                answer = ""

        if not answer:
            self._set_status("Completa tu respuesta para continuar", error=True)
            return

        self._add_message("user", answer)

        if self._active_question is None:
            self._show_error("No hay una pregunta activa para esta respuesta.")
            return

        if self._stage == "tree":
            self._camino.append(answer)
            self._active_question = None
            self._show_tree_step()
            return

        pregunta = self._final_questions[self._question_index]
        self._respuestas_finales[pregunta["id"]] = answer
        self._question_index += 1
        self._show_final_question()

    def _run_music_pipeline(self):
        if self._processing:
            return

        self._processing = True
        self._active_mode = "processing"
        self._active_question = None
        self._send_button.grid_remove()
        self._option_menu.grid_remove()
        self._answer_entry.grid_remove()
        self._question_label.configure(
            text="Consultando Ollama y preparando tu propuesta musical..."
        )
        self._progress.grid()
        self._progress.start()
        self._set_status("Procesando con el modelo local")

        respuestas = construir_respuestas(
            list(self._camino),
            dict(self._respuestas_finales)
        )
        guia_sugerida = self._guia_sugerida

        def worker():
            try:
                resultado = decidir_guia(
                    respuestas=respuestas,
                    guia_sugerida=guia_sugerida
                )
            except Exception as error:
                self._result_queue.put(("error", error))
                return

            try:
                propuesta = generar_propuesta_musical(
                    respuestas=respuestas,
                    guia=resultado
                )
            except Exception as error:
                self._result_queue.put(
                    ("partial", (resultado, error))
                )
                return

            self._result_queue.put(
                ("success", (respuestas, resultado, propuesta))
            )

        threading.Thread(target=worker, daemon=True).start()
        self.after(100, self._check_worker_result)

    def _check_worker_result(self):
        try:
            state, payload = self._result_queue.get_nowait()
        except queue.Empty:
            self.after(100, self._check_worker_result)
            return

        self._processing = False
        self._progress.stop()
        self._progress.grid_remove()

        if state == "error":
            self._show_error(
                f"No se pudo completar la recomendacion musical: {payload}"
            )
            self._set_retry_action()
            return

        if state == "partial":
            resultado, error = payload
            self._add_message(
                "assistant",
                self._format_guide(resultado)
            )
            self._show_error(
                "La guia se obtuvo correctamente, pero Ollama no pudo "
                f"generar la propuesta: {error}"
            )
            self._set_retry_action()
            return

        _, _, propuesta = payload
        for widget in self._conversation.winfo_children():
            widget.destroy()
        self._add_message(
            "assistant",
            self._format_result(propuesta)
        )
        self._set_status("Propuesta lista")
        self._active_mode = "done"
        self._question_label.grid_remove()
        self._send_button.configure(
            text="Nueva composicion",
            command=self._on_submit,
            state="normal"
        )
        self._send_button.grid()

    def _format_guide(self, resultado):
        return (
            "GUIA MUSICAL RECOMENDADA\n"
            f"{resultado['nombre']}\n\n"
            f"Motivo: {resultado['razon']}\n\n"
            f"Instrucciones: {resultado['instrucciones']}\n\n"
            f"Descripcion: {resultado['descripcion']}\n\n"
            f"Origen: {resultado['fuente']}"
        )

    def _format_result(self, propuesta):
        sections = [
            "=" * 60,
            "PROPUESTA DE CANCION GENERADA POR IA",
            "=" * 60,
            "",
            "TITULO",
            propuesta["titulo"],
            "",
            "CONCEPTO DE LA CANCION",
            propuesta["concepto"],
            "",
            "DIRECCION MUSICAL",
            propuesta["direccion_musical"],
            "",
            "ESTRUCTURA MUSICAL",
            ""
        ]
        structure = []
        for section in propuesta["estructura"]:
            if isinstance(section, dict):
                name = section.get("seccion", "Seccion")
                guidance = section.get("indicaciones", "")
                structure.append(f"{name.upper()}\n{guidance}")
            else:
                structure.append(str(section).upper())
        sections.extend(("\n\n".join(structure), "", "-" * 60))
        sections.extend(("", "LETRA PROPUESTA", "-" * 60, ""))

        lyrics = propuesta["letra"]
        lyric_names = {
            "verso_1": "VERSO 1",
            "preestribillo": "PREESTRIBILLO",
            "estribillo": "ESTRIBILLO",
            "verso_2": "VERSO 2",
            "puente": "PUENTE",
            "estribillo_final": "ESTRIBILLO FINAL"
        }
        lyric_sections = [
            f"{name}\n{lyrics[key]}"
            for key, name in lyric_names.items()
            if lyrics.get(key)
        ]
        if lyric_sections:
            sections.append("\n\n".join(lyric_sections))

        recommendations = propuesta.get("recomendaciones", [])
        if recommendations:
            sections.extend(("", "-" * 60, "RECOMENDACIONES", "-" * 60))
            sections.extend(f"- {item}" for item in recommendations)

        sections.extend(("", "=" * 60))
        return "\n".join(sections)

    def _show_error(self, message):
        self._add_message("assistant", message, is_error=True)
        self._set_status("Ocurrio un error", error=True)

    def _set_retry_action(self):
        self._active_mode = "retry"
        self._question_label.configure(
            text="Puedes volver a intentar generar la recomendacion."
        )
        self._send_button.configure(
            text="Reintentar",
            command=self._on_submit,
            state="normal"
        )
        self._send_button.grid()

    def _new_composition(self):
        for widget in self._conversation.winfo_children():
            widget.destroy()
        self._camino = []
        self._respuestas_finales = {}
        self._guia_sugerida = ""
        self._question_index = 0
        self._final_questions = []
        self._active_question = None
        self._question_label.grid()
        self._add_message(
            "assistant",
            "Empecemos una nueva composicion. Elige un genero musical."
        )
        self._show_tree_step()


def main():
    app = AsistenteMusicalApp()
    app.mainloop()


if __name__ == "__main__":
    main()
