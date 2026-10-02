import random
import re
import threading

import pygame

from botty.config import Config
from botty.eyes.renderer import EyeRenderer, EyeExpression
from botty.audio.tts import Speaker
from botty.ai.brain import Brain
from botty.actions import try_open_app, try_web_search, try_read_desktop, try_read_screen, try_weather


class Botty:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((Config.DISPLAY_WIDTH, Config.DISPLAY_HEIGHT))
        pygame.display.set_caption("Botty")
        self.clock = pygame.time.Clock()
        self.renderer = EyeRenderer(Config.DISPLAY_WIDTH, Config.DISPLAY_HEIGHT)
        self.speaker = Speaker()
        self.brain = Brain()
        self.running = True
        self._typing_mode = False
        self._input_text = ""
        self._chat_in_progress = False
        self._thinking_frame = 0
        self._listening_active = False
        self._touch_reactions = [
            "Hey!", "Oye!", "Que pasa?", "Mira eso!",
            "Hola!", "Eso fue divertido!", "Jeje!", "Ajá!",
            "Dime!", "Cuentame!", "Vale!", "Claro!", "Ahá!"
        ]

    def init(self):
        print("=" * 40)
        print("  Botty")
        print("=" * 40)
        self._boot_animation()
        self.speaker.init()
        self.brain.init()
        print("  ESC: salir | ENTER: escribir | V: voz (alternativo) | CLICK: interactuar")
        self._listening_active = True
        threading.Thread(target=self._continuous_listen, daemon=True).start()
        self.speaker.say("Hola! Soy Botty.")

    def _boot_animation(self):
        self.renderer.set_expression(EyeExpression.SHUT_DOWN)
        for i in range(30):
            dt = self.clock.tick(Config.FPS) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return
            self.renderer.update(dt)
            if i == 15:
                self.renderer.set_expression(EyeExpression.WAKING_UP, speed=4)
            self.renderer.render(self.screen)
            pygame.display.flip()
        self.renderer.set_expression(EyeExpression.IDLE)
        for _ in range(10):
            dt = self.clock.tick(Config.FPS) / 1000.0
            self.renderer.update(dt)
            self.renderer.render(self.screen)
            pygame.display.flip()

    def run(self):
        while self.running:
            dt = self.clock.tick(Config.FPS) / 1000.0
            self.running = self._handle_events()
            self.renderer.update(dt)
            if self._chat_in_progress:
                self._thinking_frame += 1
            self._render_ui()
            pygame.display.flip()

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_RETURN:
                    if self._typing_mode:
                        if self._input_text.strip():
                            self._handle_chat(self._input_text.strip())
                        self._typing_mode = False
                        self._input_text = ""
                    else:
                        self._typing_mode = True
                        self._input_text = ""
                elif event.key == pygame.K_v:
                    threading.Thread(target=self._listen_voice, daemon=True).start()
                elif event.key == pygame.K_BACKSPACE:
                    if self._typing_mode:
                        self._input_text = self._input_text[:-1]
            elif event.type == pygame.TEXTINPUT:
                if self._typing_mode:
                    self._input_text += event.text
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._on_click()
        return True

    def _on_click(self):
        self.speaker.stop()
        expr = random.choice([
            EyeExpression.HAPPY, EyeExpression.SURPRISED,
            EyeExpression.LOVING, EyeExpression.EXCITED,
        ])
        self.renderer.set_expression(expr, speed=8)
        if not self.speaker.is_speaking():
            msg = random.choice(self._touch_reactions)
            print(f"  [Click] {msg}")
            self.speaker.say(msg, block=False)

    def _continuous_listen(self):
        try:
            import speech_recognition as sr
            r = sr.Recognizer()
            r.pause_threshold = 0.8
            r.energy_threshold = 1000
            with sr.Microphone() as source:
                r.adjust_for_ambient_noise(source, duration=0.5)
                print("  [Voz] Siempre escuchando... di \"Boti\" + comando")
                while self._listening_active and self.running:
                    try:
                        audio = r.listen(source, timeout=1, phrase_time_limit=3)
                        text = r.recognize_google(audio, language="es-ES").lower()
                        if "boti" in text:
                            print(f"  [Voz] Dijiste: {text}")
                            text = re.sub(r".*?boti\s*", "", text, flags=re.I).strip()
                            if not text:
                                text = "hola"
                            self._handle_chat(text, voice=True)
                    except sr.WaitTimeoutError:
                        continue
                    except sr.UnknownValueError:
                        continue
        except ImportError:
            print("  [Voz] speech_recognition no instalado")
        except Exception as e:
            print(f"  [Voz] Error: {e}")

    def _listen_voice(self):
        self.speaker.stop()
        try:
            import speech_recognition as sr
            r = sr.Recognizer()
            with sr.Microphone() as source:
                r.adjust_for_ambient_noise(source, duration=0.3)
                print("  [Voz] Escuchando... (pulsa V para enviar)")
                audio = r.listen(source, timeout=5, phrase_time_limit=5)
            text = r.recognize_google(audio, language="es-ES")
            print(f"  [Voz] Dijiste: {text}")
            self._handle_chat(text, voice=True)
        except ImportError:
            print("  [Voz] speech_recognition no instalado")
        except sr.WaitTimeoutError:
            print("  [Voz] No se detecto voz")
        except sr.UnknownValueError:
            print("  [Voz] No se entendio el audio")
            self.speaker.say("No te entendi")
        except Exception as e:
            print(f"  [Voz] Error: {e}")

    def _handle_chat(self, text, voice=False):
        if self._chat_in_progress:
            if voice:
                self.speaker.say("Estoy ocupado")
            return
        self.speaker.stop()
        self._chat_in_progress = True

        if voice and not text.strip().lower().startswith("boti"):
            text = f"boti {text}"

        text = re.sub(r"^boti\s+", "", text, flags=re.I).strip()

        self.renderer.set_expression(EyeExpression.THINKING, speed=6)

        def _do_reply(text=text):
            try:
                cmd_reply = try_weather(text) or try_web_search(text) or try_read_screen(text) or try_read_desktop(text) or try_open_app(text)
                if cmd_reply:
                    reply = cmd_reply
                    print(f"  [Accion] {reply}")
                else:
                    print(f"  [Chat] Tu: {text}")
                    reply = self.brain.think(text)
                    if not reply:
                        reply = "..."
                    print(f"  [Chat] Botty: {reply}")
                self.renderer.set_expression(EyeExpression.TALKING, speed=6)
                self.speaker.say(reply)
            except Exception as e:
                print(f"  [Chat] Error: {e}")
            finally:
                self.renderer.set_expression(EyeExpression.IDLE)
                self._chat_in_progress = False
        threading.Thread(target=_do_reply, daemon=True).start()

    def _render_ui(self):
        self.renderer.render(self.screen)

        try:
            font = pygame.font.Font(None, 30)
            wip = font.render("W.I.P. — WORK IN PROGRESS", True, (120, 120, 140))
            tx = (self.renderer.width - wip.get_width()) // 2
            self.screen.blit(wip, (tx, 6))
        except Exception:
            pass

        if self._chat_in_progress:
            try:
                dots = "." * ((self._thinking_frame // 15) % 4)
                font = pygame.font.Font(None, 24)
                label = font.render(f"Pensando{dots}", True, (140, 140, 160))
                tx = (self.renderer.width - label.get_width()) // 2
                self.screen.blit(label, (tx, self.renderer.height - 30))
            except Exception:
                pass

        if self._typing_mode:
            try:
                font = pygame.font.Font(None, 20)
                hint = font.render("Escribe y presiona ENTER:", True, (180, 180, 190))
                tx = (self.renderer.width - hint.get_width()) // 2
                self.screen.blit(hint, (tx, self.renderer.height - 65))

                bg_rect = pygame.Rect(30, self.renderer.height - 50,
                                      self.renderer.width - 60, 28)
                pygame.draw.rect(self.screen, (30, 30, 35), bg_rect)
                pygame.draw.rect(self.screen, (80, 80, 100), bg_rect, 1)

                txt = font.render(self._input_text + "|", True, (220, 220, 230))
                self.screen.blit(txt, (38, self.renderer.height - 47))
            except Exception:
                pass


def main():
    botty = Botty()
    botty.init()
    botty.run()
    pygame.quit()
    print("  Hasta luego!")
