import math
import random
import pygame

from .animations import EyeExpression, EyeState, EXPRESSIONS


def _color_for(surface, rgb, alpha=255):
    return (*rgb, alpha) if surface.get_flags() & pygame.SRCALPHA else rgb


def _round_rect(surface, color, rect, radius):
    x, y, w, h = rect
    if not (surface.get_flags() & pygame.SRCALPHA) and len(color) == 4:
        color = color[:3]
    r = min(radius, abs(w) // 2, abs(h) // 2)
    if r <= 0:
        pygame.draw.rect(surface, color, rect)
    else:
        pygame.draw.rect(surface, color, rect, border_radius=r)


class EmoEye:
    def __init__(self, cx, cy, w, h):
        self.cx = cx
        self.cy = cy
        self.w = w
        self.h = h
        self.scaleY = 1.0
        self.scaleX = 1.0
        self.look_x = 0.0
        self.look_y = 0.0
        self.squint = 0.0
        self.arch = 0.0
        self.eye_color = (60, 140, 230)
        self.pupil_dilation = 1.0
        self.eyelid_droop = 0.0
        self.color_shift = 0.0
        self._target = EyeState()
        self._speed = 10.0
        self._time = 0.0

    def animate_to(self, state, speed=10.0):
        self._target = state
        self._speed = speed

    def update(self, dt):
        self._time += dt
        lerp = min(1.0, self._speed * dt)
        t = self._target
        self.scaleY += (t.scaleY - self.scaleY) * lerp
        self.scaleX += (t.scaleX - self.scaleX) * lerp
        self.look_x += (t.look_x - self.look_x) * lerp
        self.look_y += (t.look_y - self.look_y) * lerp
        self.squint += (t.squint - self.squint) * lerp
        self.arch += (t.arch - self.arch) * lerp
        self.pupil_dilation += (t.pupil_dilation - self.pupil_dilation) * lerp
        self.eyelid_droop += (t.eyelid_droop - self.eyelid_droop) * lerp
        self.color_shift += (t.color_shift - self.color_shift) * lerp
        if t.eye_color:
            self.eye_color = tuple(
                int(a + (b - a) * lerp) for a, b in zip(self.eye_color, t.eye_color)
            )

    def draw(self, surface):
        cx, cy = self.cx, self.cy
        w = max(2, int(self.w * self.scaleX))
        h = max(2, int(self.h * self.scaleY))
        cc = self.eye_color

        glow = pygame.Surface((w + 16, h + 16), pygame.SRCALPHA)
        _round_rect(glow, (*cc, 25), (4, 4, w + 8, h + 8), 12)
        surface.blit(glow, (cx - w // 2 - 8, cy - h // 2 - 8))

        if w > 4 and h > 4:
            rect = (cx - w // 2, cy - h // 2, w, h)
            _round_rect(surface, cc, rect, 11)
            inset = tuple(int(c * 0.7) for c in cc)
            _round_rect(surface, inset,
                        (cx - w // 2 + 3, cy - h // 2 + 3, w - 6, h - 6), 8)
            hl_w = max(4, w // 4)
            hl_h = max(2, h // 8)
            if hl_w > 2 and hl_h > 1:
                _round_rect(surface, (255, 255, 255),
                            (cx - w // 2 + 5, cy - h // 2 + 5, hl_w, hl_h), 3)

        if self.squint > 0.05:
            sq_h = int(h * self.squint * 0.65)
            if sq_h > 0:
                col = tuple(max(0, int(c * 0.35)) for c in cc)
                sq = pygame.Surface((w + 4, sq_h + 4), pygame.SRCALPHA)
                _round_rect(sq, (*col, 230), (2, 2, w, sq_h), 6)
                surface.blit(sq, (cx - w // 2 - 2, cy - h // 2 - 2))

        if self.eyelid_droop > 0.05:
            drop_h = int(h * self.eyelid_droop * 0.5)
            if drop_h > 0:
                dcol = tuple(max(0, int(c * 0.15)) for c in cc)
                dp = pygame.Surface((w + 4, drop_h + 4), pygame.SRCALPHA)
                _round_rect(dp, (*dcol, 200), (2, 2, w, drop_h), 6)
                surface.blit(dp, (cx - w // 2 - 2, cy - h // 2 - 2))

        if w > 6 and h > 6:
            max_off_x = w * 0.12
            max_off_y = h * 0.10
            px = int(self.look_x * max_off_x)
            py = int(self.look_y * max_off_y)
            dil = self.pupil_dilation
            pw = max(3, int((w - 10) * 0.5 * dil))
            ph = max(3, int((h - 12) * 0.5 * (1 - self.squint * 0.4) * dil))
            _round_rect(surface, (1, 8, 18),
                        (cx + px - pw // 2, cy + py - ph // 2 + 2, pw, ph), 5)
            rr = max(1, pw // 6)
            pygame.draw.circle(surface, _color_for(surface, (255, 255, 255), 80),
                               (cx + px - pw // 4 + 1, cy + py - ph // 4 + 3), rr)


class AmbientParticles:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.particles = []
        self._color = (70, 130, 220)
        for _ in range(8):
            self._spawn()

    def _spawn(self):
        self.particles.append({
            "x": random.uniform(0, self.width),
            "y": random.uniform(0, self.height),
            "vx": random.uniform(-3, 3),
            "vy": random.uniform(-3, 3),
            "size": random.uniform(1.0, 2.5),
            "alpha": random.uniform(15, 45),
            "phase": random.uniform(0, 6.28),
        })

    def set_color(self, color):
        self._color = color

    def update(self, dt):
        for p in self.particles:
            p["phase"] += dt * random.uniform(0.5, 1.5)
            p["x"] += p["vx"] * dt + math.sin(p["phase"]) * 2 * dt
            p["y"] += p["vy"] * dt + math.cos(p["phase"] * 0.7) * 2 * dt
            p["alpha"] += random.uniform(-5, 5) * dt
            p["alpha"] = max(10, min(60, p["alpha"]))
            if not (0 <= p["x"] <= self.width):
                p["vx"] *= -1
            if not (0 <= p["y"] <= self.height):
                p["vy"] *= -1

    def draw(self, surface):
        is_srcalpha = surface.get_flags() & pygame.SRCALPHA
        cc = tuple(min(255, max(0, int(c * 1.3))) for c in self._color[:3])
        for p in self.particles:
            size = int(p["size"])
            if size < 1:
                continue
            if is_srcalpha:
                alpha = max(1, min(255, int(p["alpha"])))
                pygame.draw.circle(surface, (*cc, alpha),
                                   (int(p["x"]), int(p["y"])), size)
            else:
                pygame.draw.circle(surface, cc,
                                   (int(p["x"]), int(p["y"])), size)


class EyeRenderer:
    def __init__(self, width=480, height=320):
        self.width = width
        self.height = height
        self._expression = EyeExpression.IDLE
        self._blink_timer = 0.0
        self._blink_interval = 3.5
        self._blink_duration = 0.12
        self._is_blinking = False
        self._total_time = 0.0
        self._look_target_x = 0.0
        self._look_target_y = 0.0
        self._look_switch_timer = 0.0

        ew = self.width // 7
        eh = int(ew * 1.3)
        gap = int(ew * 0.6)
        cx1 = self.width // 2 - gap // 2 - ew // 2
        cx2 = self.width // 2 + gap // 2 + ew // 2
        cy = self.height // 2
        self.left_eye = EmoEye(cx1, cy, ew, eh)
        self.right_eye = EmoEye(cx2, cy, ew, eh)
        self.particles = AmbientParticles(width, height)
        self._bg_color = (18, 18, 22)

    def set_expression(self, expression, speed=10.0):
        self._expression = expression
        state = EXPRESSIONS[expression]
        self.left_eye.animate_to(state, speed)
        self.right_eye.animate_to(state, speed)

    def get_expression(self):
        return self._expression

    def set_look_target(self, x, y):
        self._look_target_x = max(-1.0, min(1.0, x))
        self._look_target_y = max(-1.0, min(1.0, y))

    def trigger_blink(self):
        self._is_blinking = True
        blink = EXPRESSIONS[EyeExpression.BLINK]
        self.left_eye.animate_to(blink, 40)
        self.right_eye.animate_to(blink, 40)

    def update(self, dt):
        self._total_time += dt
        self._look_switch_timer += dt
        if self._look_switch_timer > random.uniform(2.0, 5.0):
            self._look_switch_timer = 0.0
            self.set_look_target(
                random.uniform(-0.4, 0.4),
                random.uniform(-0.3, 0.3),
            )
            state = EXPRESSIONS[EyeExpression.IDLE]
            state.look_x = self._look_target_x
            state.look_y = self._look_target_y
            self.left_eye.animate_to(state, 3)
            self.right_eye.animate_to(state, 3)

        if self._is_blinking:
            self._blink_timer += dt
            if self._blink_timer >= self._blink_duration * 1.2:
                self._is_blinking = False
                self._blink_timer = 0.0
                self.set_expression(self._expression)
        else:
            self._blink_timer += dt
            if self._blink_timer >= self._blink_interval:
                self.trigger_blink()

        self.left_eye.update(dt)
        self.right_eye.update(dt)
        self.particles.update(dt)

    def render(self, surface):
        surface.fill(self._bg_color)
        self.particles.draw(surface)
        self.left_eye.draw(surface)
        self.right_eye.draw(surface)
