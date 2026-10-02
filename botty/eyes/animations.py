"""
Botty EMO-style eye animation states.
scaleY/scaleX = pupil deformation, squint = drooping eyelid,
arch = happy arching. look_x/look_y = pupil direction.
Soporta 30+ expresiones incluyendo pupil_dilation, eyelid_droop,
y color_shift para animaciones avanzadas.
"""

from enum import Enum


class EyeExpression(Enum):
    IDLE = "idle"
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    SURPRISED = "surprised"
    SLEEPY = "sleepy"
    TALKING = "talking"
    LISTENING = "listening"
    THINKING = "thinking"
    BLINK = "blink"
    WAKING_UP = "waking_up"
    SHUT_DOWN = "shut_down"
    SEARCHING = "searching"
    LOVING = "loving"
    CONFUSED = "confused"
    DRIVE = "drive"
    DEVELOPER = "developer"
    EXCITED = "excited"
    CURIOUS = "curious"
    BORED = "bored"
    FEAR = "fear"
    DISGUST = "disgust"
    JOY = "joy"
    GRATEFUL = "grateful"
    SASSY = "sassy"
    SUSPICIOUS = "suspicious"
    DIZZY = "dizzy"
    NERDY = "nerdy"
    SMUG = "smug"
    DREAMY = "dreamy"


class EyeState:
    def __init__(self, scaleY=1.0, scaleX=1.0, look_x=0.0, look_y=0.0,
                 squint=0.0, arch=0.0, eye_color=None, duration=1.0,
                 pupil_dilation=1.0, eyelid_droop=0.0, color_shift=0.0):
        self.scaleY = scaleY
        self.scaleX = scaleX
        self.look_x = look_x
        self.look_y = look_y
        self.squint = squint
        self.arch = arch
        self.eye_color = eye_color
        self.duration = duration
        self.pupil_dilation = pupil_dilation
        self.eyelid_droop = eyelid_droop
        self.color_shift = color_shift


EXPRESSIONS = {
    EyeExpression.IDLE: EyeState(
        scaleY=1.0, scaleX=1.0, squint=0.0, arch=0.0,
        eye_color=(60, 140, 230),
    ),
    EyeExpression.HAPPY: EyeState(
        scaleY=0.5, scaleX=1.1, squint=0.6, arch=0.8,
        eye_color=(70, 200, 120),
    ),
    EyeExpression.SAD: EyeState(
        scaleY=0.7, scaleX=0.95, squint=0.2, arch=-0.3,
        look_y=0.2, eye_color=(100, 140, 200),
    ),
    EyeExpression.ANGRY: EyeState(
        scaleY=0.7, scaleX=1.0, squint=0.4, arch=0.0,
        eye_color=(220, 80, 60),
    ),
    EyeExpression.SURPRISED: EyeState(
        scaleY=1.4, scaleX=0.85, squint=0.0, arch=0.0,
        eye_color=(80, 160, 240), pupil_dilation=1.4,
    ),
    EyeExpression.SLEEPY: EyeState(
        scaleY=0.3, scaleX=1.0, squint=0.8, arch=0.0,
        eye_color=(90, 120, 180), look_y=0.1, eyelid_droop=0.6,
    ),
    EyeExpression.TALKING: EyeState(
        scaleY=1.0, scaleX=1.0, squint=0.0, arch=0.0,
        eye_color=(60, 140, 230),
    ),
    EyeExpression.LISTENING: EyeState(
        scaleY=1.0, scaleX=1.0, squint=0.0, arch=0.0,
        eye_color=(50, 130, 220),
    ),
    EyeExpression.THINKING: EyeState(
        scaleY=0.9, scaleX=1.0, squint=0.2, arch=0.0,
        look_x=0.3, look_y=-0.35, eye_color=(100, 140, 220),
    ),
    EyeExpression.BLINK: EyeState(
        scaleY=0.05, scaleX=1.0, squint=0.0, arch=0.0,
        eye_color=(60, 140, 230), duration=0.1,
    ),
    EyeExpression.WAKING_UP: EyeState(
        scaleY=0.8, scaleX=1.0, squint=0.0, arch=0.0,
        eye_color=(50, 120, 210),
    ),
    EyeExpression.SHUT_DOWN: EyeState(
        scaleY=0.05, scaleX=1.0, squint=0.0, arch=0.0,
        eye_color=(40, 80, 140), duration=0.5,
    ),
    EyeExpression.SEARCHING: EyeState(
        scaleY=1.0, scaleX=1.0, squint=0.0, arch=0.0,
        look_x=0.5, eye_color=(60, 140, 230),
    ),
    EyeExpression.LOVING: EyeState(
        scaleY=0.8, scaleX=1.05, squint=0.3, arch=0.5,
        eye_color=(220, 100, 160), pupil_dilation=1.2,
    ),
    EyeExpression.CONFUSED: EyeState(
        scaleY=0.9, scaleX=0.95, squint=0.15, arch=0.0,
        look_x=-0.2, look_y=-0.1, eye_color=(140, 100, 200),
    ),
    EyeExpression.DRIVE: EyeState(
        scaleY=1.0, scaleX=1.0, squint=0.0, arch=0.0,
        eye_color=(70, 200, 220),
    ),
    EyeExpression.DEVELOPER: EyeState(
        scaleY=1.2, scaleX=0.9, squint=0.0, arch=0.0,
        eye_color=(255, 50, 50),
    ),
    EyeExpression.EXCITED: EyeState(
        scaleY=0.6, scaleX=1.15, squint=0.3, arch=0.6,
        eye_color=(255, 200, 50), pupil_dilation=1.3,
    ),
    EyeExpression.CURIOUS: EyeState(
        scaleY=0.9, scaleX=0.95, squint=0.1, arch=0.0,
        look_x=0.4, look_y=-0.3, eye_color=(100, 180, 255),
        pupil_dilation=0.9,
    ),
    EyeExpression.BORED: EyeState(
        scaleY=0.6, scaleX=0.9, squint=0.3, arch=0.0,
        look_y=0.3, eye_color=(130, 140, 170), eyelid_droop=0.3,
    ),
    EyeExpression.FEAR: EyeState(
        scaleY=0.2, scaleX=0.5, squint=0.0, arch=0.0,
        eye_color=(200, 200, 50), pupil_dilation=1.5,
    ),
    EyeExpression.DISGUST: EyeState(
        scaleY=0.7, scaleX=0.9, squint=0.5, arch=-0.2,
        look_x=-0.1, look_y=0.1, eye_color=(100, 180, 100),
    ),
    EyeExpression.JOY: EyeState(
        scaleY=0.45, scaleX=1.2, squint=0.5, arch=0.9,
        eye_color=(50, 220, 100), pupil_dilation=1.1,
    ),
    EyeExpression.GRATEFUL: EyeState(
        scaleY=0.7, scaleX=1.0, squint=0.2, arch=0.4,
        eye_color=(100, 180, 255), pupil_dilation=0.8,
    ),
    EyeExpression.SASSY: EyeState(
        scaleY=0.8, scaleX=1.0, squint=0.1, arch=0.3,
        look_x=0.5, look_y=-0.2, eye_color=(200, 100, 255),
    ),
    EyeExpression.SUSPICIOUS: EyeState(
        scaleY=0.7, scaleX=0.9, squint=0.6, arch=0.0,
        look_x=-0.3, look_y=0.0, eye_color=(180, 180, 100),
    ),
    EyeExpression.DIZZY: EyeState(
        scaleY=0.8, scaleX=0.8, squint=0.1, arch=0.0,
        eye_color=(150, 100, 200), pupil_dilation=0.7,
    ),
    EyeExpression.NERDY: EyeState(
        scaleY=0.9, scaleX=1.0, squint=0.0, arch=0.0,
        look_x=0.1, look_y=-0.2, eye_color=(100, 150, 200),
    ),
    EyeExpression.SMUG: EyeState(
        scaleY=0.6, scaleX=1.05, squint=0.5, arch=0.3,
        look_x=-0.2, look_y=-0.15, eye_color=(200, 150, 100),
    ),
    EyeExpression.DREAMY: EyeState(
        scaleY=0.7, scaleX=1.0, squint=0.1, arch=0.1,
        look_x=0.2, look_y=-0.3, eye_color=(150, 100, 200),
        pupil_dilation=1.1,
    ),
}
