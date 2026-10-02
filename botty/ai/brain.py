import json
import os
import re
from pathlib import Path

from botty.config import Config


MEMORY_FILE = Path(__file__).parent.parent / "memory.json"


class Brain:
    def __init__(self):
        self._llm = None
        self._available = False
        self._history = []
        self._max_turns = 6
        self._memories = self._load_memories()

    def _load_memories(self):
        if MEMORY_FILE.exists():
            try:
                data = json.loads(MEMORY_FILE.read_text(encoding="utf-8"))
                return data.get("memorias", [])
            except Exception:
                pass
        return []

    def _save_memories(self):
        MEMORY_FILE.write_text(json.dumps({"memorias": self._memories},
                                          ensure_ascii=False, indent=2),
                               encoding="utf-8")

    def _extract_memory(self, text, reply):
        patterns = [
            (r"(recuerda|acuerdate|no olvides|guarda|memoriza)\s+(?:que\s+)?(.+)", None),
            (r"mi (nombre|correo|telefono|edad|cumpleaños|usuario)\s+(?:es\s+)?(.+)", lambda m: f"{m.group(1)}: {m.group(2)}"),
            (r"(?:me\s+)?llamo\s+(.+)", lambda m: f"nombre: {m.group(1)}"),
            (r"soy\s+(.+?)(?:\s+y\s+|\s*$)", lambda m: f"nombre: {m.group(1)}"),
            (r"yo\s+soy\s+(.+?)(?:\s+y\s+|\s*$)", lambda m: f"nombre: {m.group(1)}"),
        ]
        for pattern, fmt in patterns:
            m = re.search(pattern, text, re.I)
            if m:
                if fmt:
                    fact = fmt(m).strip().rstrip(".!")
                else:
                    fact = m.group(2).strip().rstrip(".!")
                if not fact or len(fact) < 3:
                    continue
                key = fact.split(":")[0].lower() if ":" in fact else None
                if key:
                    self._memories = [x for x in self._memories if not x.lower().startswith(key)]
                if fact not in self._memories:
                    self._memories.append(fact)
                    self._save_memories()
                    print(f"  [Memoria] guardado: {fact}")
                return True
        return False

    def init(self):
        model = self._find_model()
        if not model:
            print("  [IA] No se encontró modelo GGUF en models/")
            if self._memories:
                print(f"  [Memoria] {len(self._memories)} recuerdos cargados")
            return
        try:
            from llama_cpp import Llama
            print(f"  [IA] Cargando modelo...")
            self._llm = Llama(
                model_path=str(model),
                n_ctx=2048,
                n_gpu_layers=0,
                verbose=False,
            )
            self._available = True
            print(f"  [IA] Pickle Brain listo")
            if self._memories:
                print(f"  [Memoria] {len(self._memories)} recuerdos cargados")
        except Exception as e:
            print(f"  [IA] Error cargando modelo: {e}")

    def _find_model(self):
        models_dir = Path(__file__).parent.parent / "models"
        if not models_dir.exists():
            return None
        ggufs = list(models_dir.glob("*.gguf"))
        return ggufs[0] if ggufs else None

    def think(self, user_input):
        if not self._available or self._llm is None:
            if self._memories:
                return "Tengo memoria pero el modelo no está cargado."
            return "El modelo de IA no está cargado."

        system = (
            "Eres Pickle Brain, un asistente de escritorio con personalidad curiosa, creativa y servicial. "
            "Respondes en español de forma natural, evitando repetir frases. Tus respuestas son "
            "cortas y directas, de máximo 3 oraciones.\n\n"
            "Puedes leer texto de la pantalla usando OCR cuando te lo pidan explícitamente "
            "(ej: \"que ves\", \"lee la pantalla\"). NO inventes información visual. "
            "Si no usan OCR, no sabes lo que hay en la pantalla."
        )
        if self._memories:
            facts = "; ".join(self._memories)
            system += f"\n\nRecuerda esto sobre el usuario: {facts}"

        messages = [{"role": "system", "content": system}]

        for turn in self._history[-self._max_turns:]:
            messages.append({"role": "user", "content": turn[0]})
            messages.append({"role": "assistant", "content": turn[1]})

        messages.append({"role": "user", "content": user_input})

        try:
            resp = self._llm.create_chat_completion(
                messages=messages,
                max_tokens=150,
                temperature=0.65,
            )
            msg = resp.get("choices", [{}])[0].get("message", {})
            reply = msg.get("content", "").strip() or "..."

            self._extract_memory(user_input, reply)

            self._history.append((user_input, reply))
            if len(self._history) > self._max_turns * 2:
                self._history = self._history[-self._max_turns:]

            return reply
        except Exception as e:
            return f"Error: {e}"
