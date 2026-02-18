"""Simulation-wide constants and configuration values.

All tunable parameters live here so they can be adjusted in one place
and imported by any layer without circular dependencies.
"""

# --- Display ---
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 450
FPS = 60
STATUS_BAR_HEIGHT = 30

# The playable area excludes the status bar at the bottom.
PLAY_AREA_HEIGHT = WINDOW_HEIGHT - STATUS_BAR_HEIGHT

# --- Ball defaults ---
MIN_RADIUS = 12
MAX_RADIUS = 30
MIN_SPEED = 0.5
MAX_SPEED = 3.0

# Mass is proportional to area: mass = MASS_DENSITY * pi * r^2
MASS_DENSITY = 1.0

# --- Physics ---
SURFACE_FRICTION = 0.9999         # multiplied each frame (no-gravity mode)
GRAVITY_ACCEL = 0.15              # px / frame^2 downward
BOUNCE_RESTITUTION = 0.85         # energy retained on ground bounce (gravity mode)
FLOOR_FRICTION = 0.99             # velocity multiplier while rolling on floor
AIR_RESISTANCE = 0.9995           # per-frame drag in gravity mode
LEFT_WALL_BOOST = 1.12            # velocity multiplier on left-wall bounce
MAX_SPEED_CAP = 5.0               # absolute speed limit (wall boost won't exceed this)
SHOCKWAVE_STRENGTH = 800.0        # impulse magnitude at distance = 0
SHOCKWAVE_RADIUS = 400.0          # px – beyond this radius the wave has no effect

# --- Colours (RGB) ---
COLOR_BG_SPACE = (10, 10, 15)
COLOR_BG_SKY = (135, 206, 235)
COLOR_GRASS = (34, 139, 34)
COLOR_GRASS_DARK = (0, 100, 0)
COLOR_GROUND = (34, 100, 34)
COLOR_BALL_LEFT = (75, 46, 131)   # #4B2E83
COLOR_BALL_OTHER = (183, 165, 122)  # #B7A57A
COLOR_STATUS_BG = (30, 30, 30)
COLOR_STATUS_TEXT = (200, 200, 200)
COLOR_WALL_GLOW = (255, 165, 0)   # orange glow for left-wall boost
COLOR_SHOCKWAVE = (255, 255, 255)
COLOR_SLINGSHOT_LINE = (255, 255, 100)
COLOR_PANEL_BG = (40, 40, 50, 220)
COLOR_PANEL_TEXT = (230, 230, 230)
COLOR_BUTTON_BG = (60, 60, 80)
COLOR_BUTTON_TEXT = (220, 220, 220)
COLOR_BUTTON_HOVER = (80, 80, 110)
COLOR_ENERGY_BAR = (0, 200, 100)
