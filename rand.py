from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import math
import random
import time

# =========================
# GLOBALS / GAME SETTINGS
# =========================
window_width, window_height = 1000, 800

grid_length = 600

# World bounds (simple square room)
WORLD_MIN = -grid_length + 60
WORLD_MAX =  grid_length - 60

# Timing
last_time = time.time()
delta_time = 0.0

# Camera
camera_angle = 0.0          # degrees (yaw around player)
camera_up_down = -25.0      # degrees-ish applied as height offset
fov = 120
cam_dir = [1.0, 0.0, 0.0]   # forward direction on XY plane

# Player
player_xyz = [0.0, 0.0, 0.0]
player_radius = 25.0
player_speed = 5.0
run_speed = 12.0
running = False
player_color = [0.2, 0.6, 1.0]

# Game state
lives = 5
score = 0
game_over = False
paused = False
show_help = False

# Flashlight system (fake lighting via color)
flashlight_on = True
flash_range = 150.0
flash_fov = 30.0            # degrees (cone angle)
flash_brightness = 1.5
ambient_dim = 0.2
flash_battery = 100.0       # percent

# Cheats
cheat_god = False
cheat_vision = False        # reveal everything and no battery drain (optional)

# Enemies
enemies = []
enemy_count = 4
enemy_initial_speed = 1.0
enemy_chase_speed = 2.0
enemy_damage_cooldown = 0.8
last_damage_time = 0.0

# Items / powerups
hidden_items = []
item_count = 10

# Shadow
shadows_on = True
shadow_scale = 1.0

# Powerup timers
light_boost_until = 0.0
slow_enemies_until = 0.0

# Random seed (deterministic)
seed = 423
random.seed(seed)

# =========================
# HELPERS
# =========================
def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def dist2(ax, ay, bx, by):
    dx = ax - bx
    dy = ay - by
    return dx*dx + dy*dy

def normalize2(vx, vy):
    l = math.sqrt(vx*vx + vy*vy)
    if l == 0:
        return 0.0, 0.0
    return vx/l, vy/l

def keep_inside_world(p):
    p[0] = clamp(p[0], WORLD_MIN, WORLD_MAX)
    p[1] = clamp(p[1], WORLD_MIN, WORLD_MAX)

def is_in_flashlight(obj_pos):
    """
    Visibility test: within flashlight cone + range.
    We use the player's position and cam_dir (forward) on XY plane.
    """
    if cheat_vision:
        return True
    if not flashlight_on:
        return False

    ox, oy = obj_pos[0], obj_pos[1]
    px, py = player_xyz[0], player_xyz[1]

    vx, vy = ox - px, oy - py
    if (vx*vx + vy*vy) > (flash_range * flash_range):
        return False

    fx, fy = cam_dir[0], cam_dir[1]
    vnx, vny = normalize2(vx, vy)

    dot = clamp(fx*vnx + fy*vny, -1.0, 1.0)
    theta = math.degrees(math.acos(dot))
    return theta <= (flash_fov * 0.5)

# =========================
# DRAW: 2D TEXT (HUD)
# =========================
def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, window_width, 0, window_height)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

# =========================
# DRAW: WORLD
# =========================
def draw_ground():
    # Four coloured quadrants like your snippet, plus grid lines
    glBegin(GL_QUADS)
    glColor3f(0.12, 0.12, 0.12)
    glVertex3f(-grid_length,  grid_length, 0)
    glVertex3f(0,            grid_length, 0)
    glVertex3f(0,            0,           0)
    glVertex3f(-grid_length, 0,           0)

    glColor3f(0.10, 0.10, 0.16)
    glVertex3f( grid_length, -grid_length, 0)
    glVertex3f(0,           -grid_length,  0)
    glVertex3f(0,            0,            0)
    glVertex3f( grid_length, 0,            0)

    glColor3f(0.10, 0.14, 0.10)
    glVertex3f(-grid_length, -grid_length, 0)
    glVertex3f(-grid_length, 0,            0)
    glVertex3f(0,            0,            0)
    glVertex3f(0,           -grid_length,  0)

    glColor3f(0.14, 0.10, 0.10)
    glVertex3f( grid_length,  grid_length, 0)
    glVertex3f( grid_length,  0,           0)
    glVertex3f(0,             0,           0)
    glVertex3f(0,             grid_length, 0)
    glEnd()

    # Simple grid lines
    glColor3f(0.25, 0.25, 0.25)
    glBegin(GL_LINES)
    step = 60
    for x in range(-grid_length, grid_length + 1, step):
        glVertex3f(x, -grid_length, 0.2)
        glVertex3f(x,  grid_length, 0.2)
    for y in range(-grid_length, grid_length + 1, step):
        glVertex3f(-grid_length, y, 0.2)
        glVertex3f( grid_length, y, 0.2)
    glEnd()

def draw_walls():
    # Simple boundary walls (thin vertical quads)
    h = 140
    t = 8  # thickness
    glColor3f(0.18, 0.18, 0.18)

    # Left wall
    glBegin(GL_QUADS)
    glVertex3f(WORLD_MIN, WORLD_MIN, 0)
    glVertex3f(WORLD_MIN, WORLD_MAX, 0)
    glVertex3f(WORLD_MIN, WORLD_MAX, h)
    glVertex3f(WORLD_MIN, WORLD_MIN, h)
    glEnd()

    # Right wall
    glBegin(GL_QUADS)
    glVertex3f(WORLD_MAX, WORLD_MIN, 0)
    glVertex3f(WORLD_MAX, WORLD_MAX, 0)
    glVertex3f(WORLD_MAX, WORLD_MAX, h)
    glVertex3f(WORLD_MAX, WORLD_MIN, h)
    glEnd()

    # Bottom wall
    glBegin(GL_QUADS)
    glVertex3f(WORLD_MIN, WORLD_MIN, 0)
    glVertex3f(WORLD_MAX, WORLD_MIN, 0)
    glVertex3f(WORLD_MAX, WORLD_MIN, h)
    glVertex3f(WORLD_MIN, WORLD_MIN, h)
    glEnd()

    # Top wall
    glBegin(GL_QUADS)
    glVertex3f(WORLD_MIN, WORLD_MAX, 0)
    glVertex3f(WORLD_MAX, WORLD_MAX, 0)
    glVertex3f(WORLD_MAX, WORLD_MAX, h)
    glVertex3f(WORLD_MIN, WORLD_MAX, h)
    glEnd()

def draw_shadow_circle(x, y, r):
    glColor3f(0.02, 0.02, 0.02)
    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(x, y, 0.5)
    for i in range(0, 33):
        ang = (i / 32.0) * 2.0 * math.pi
        glVertex3f(x + math.cos(ang) * r, y + math.sin(ang) * r, 0.5)
    glEnd()

def draw_player():
    # Player visible always (but can dim slightly when flashlight off for mood)
    base = 0.7 if flashlight_on else 0.45
    glColor3f(player_color[0]*base, player_color[1]*base, player_color[2]*base)

    glPushMatrix()
    glTranslatef(player_xyz[0], player_xyz[1], 25)
    glutSolidSphere(player_radius, 18, 18)
    glPopMatrix()

    if shadows_on:
        draw_shadow_circle(player_xyz[0], player_xyz[1], player_radius*1.2)

def draw_items():
    for it in hidden_items:
        if it["collected"]:
            continue

        visible = is_in_flashlight(it["pos"])
        if not visible and not cheat_vision:
            continue

        # colour by kind
        if it["kind"] == "score":
            glColor3f(1.0, 0.9, 0.2)
        elif it["kind"] == "light_boost":
            glColor3f(0.2, 1.0, 1.0)
        else:  # slow
            glColor3f(0.6, 0.2, 1.0)

        glPushMatrix()
        glTranslatef(it["pos"][0], it["pos"][1], 12)
        glutSolidCube(it["r"]*1.4)
        glPopMatrix()

        if shadows_on:
            draw_shadow_circle(it["pos"][0], it["pos"][1], it["r"]*shadow_scale)

def draw_enemies():
    for e in enemies:
        visible = is_in_flashlight(e["pos"])
        if visible:
            glColor3f(1.0, 0.25, 0.25)
        else:
            # "hidden in darkness" effect
            glColor3f(ambient_dim*0.3, ambient_dim*0.1, ambient_dim*0.1)

        glPushMatrix()
        glTranslatef(e["pos"][0], e["pos"][1], 22)
        glutSolidSphere(e["r"], 16, 16)
        glPopMatrix()

        if shadows_on:
            draw_shadow_circle(e["pos"][0], e["pos"][1], e["r"]*shadow_scale)

# =========================
# CAMERA
# =========================
def setup_camera():
    global cam_dir

    # Forward direction from angle on XY plane
    fx = math.cos(math.radians(camera_angle))
    fy = math.sin(math.radians(camera_angle))
    cam_dir = [fx, fy, 0.0]

    # Camera position behind player
    back = 220.0
    cx = player_xyz[0] - fx * back
    cy = player_xyz[1] - fy * back
    cz = 220.0 + camera_up_down  # height offset

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    aspect = window_width / float(window_height)
    gluPerspective(fov, aspect, 1.0, 2000.0)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(
        cx, cy, cz,
        player_xyz[0] + fx*40.0, player_xyz[1] + fy*40.0, 40.0,
        0, 0, 1
    )

# =========================
# SPAWN
# =========================
def spawn_enemies():
    global enemies
    enemies = []
    for _ in range(enemy_count):
        ex = random.randint(int(WORLD_MIN), int(WORLD_MAX))
        ey = random.randint(int(WORLD_MIN), int(WORLD_MAX))
        enemies.append({
            "pos": [float(ex), float(ey), 0.0],
            "r": 22.0,
            "base_speed": enemy_initial_speed,
            "state": "idle"
        })

def spawn_items():
    global hidden_items
    hidden_items = []
    for _ in range(item_count):
        ix = random.randint(int(WORLD_MIN), int(WORLD_MAX))
        iy = random.randint(int(WORLD_MIN), int(WORLD_MAX))
        kind = random.choice(["score", "light_boost", "slow"])
        hidden_items.append({
            "pos": [float(ix), float(iy), 0.0],
            "r": 14.0,
            "kind": kind,
            "collected": False
        })

# =========================
# UPDATE LOGIC
# =========================
def check_game_over():
    global game_over
    if lives <= 0 or flash_battery <= 0:
        game_over = True

def apply_timed_effects():
    global flash_range, flash_brightness
    t = time.time()

    base_range = 150.0
    base_brightness = 1.5

    if t < light_boost_until:
        flash_range = 250.0
        flash_brightness = 2.0
    else:
        flash_range = base_range
        flash_brightness = base_brightness

def update_enemies(dt):
    global lives, last_damage_time

    t = time.time()
    slow_factor = 0.45 if t < slow_enemies_until else 1.0

    for e in enemies:
        ex, ey = e["pos"][0], e["pos"][1]
        px, py = player_xyz[0], player_xyz[1]

        d2 = dist2(ex, ey, px, py)
        visible = is_in_flashlight(e["pos"])

        # Simple state
        if visible or d2 < (260.0*260.0):
            e["state"] = "chase"
        else:
            e["state"] = "idle"

        speed = e["base_speed"] * slow_factor
        if e["state"] == "chase":
            speed *= enemy_chase_speed
            vx, vy = px - ex, py - ey
            nx, ny = normalize2(vx, vy)
            e["pos"][0] += nx * speed * 60.0 * dt
            e["pos"][1] += ny * speed * 60.0 * dt
        else:
            # tiny wander
            ang = (random.random()*2.0 - 1.0) * 60.0
            e["pos"][0] += math.cos(math.radians(ang)) * speed * 10.0 * dt
            e["pos"][1] += math.sin(math.radians(ang)) * speed * 10.0 * dt

        keep_inside_world(e["pos"])

        # Damage if touching
        touch = dist2(e["pos"][0], e["pos"][1], px, py) <= (e["r"] + player_radius)**2
        if touch and (not cheat_god) and (t - last_damage_time > enemy_damage_cooldown):
            lives -= 1
            last_damage_time = t

def check_item_pickups():
    global score, light_boost_until, slow_enemies_until
    px, py = player_xyz[0], player_xyz[1]

    for it in hidden_items:
        if it["collected"]:
            continue

        if dist2(it["pos"][0], it["pos"][1], px, py) <= (it["r"] + player_radius)**2:
            it["collected"] = True
            if it["kind"] == "score":
                score += 10
            elif it["kind"] == "light_boost":
                light_boost_until = time.time() + 10.0
            elif it["kind"] == "slow":
                slow_enemies_until = time.time() + 8.0

def update_game(dt):
    global flash_battery

    check_game_over()
    if game_over:
        return

    apply_timed_effects()

    # Battery drain only if flashlight ON and not cheat vision
    if flashlight_on and not cheat_vision:
        drain_per_sec = 0.10  # tune; 0.10 means ~1000s for full drain
        flash_battery -= drain_per_sec * 100.0 * dt
        flash_battery = clamp(flash_battery, 0.0, 100.0)

    update_enemies(dt)
    check_item_pickups()
    check_game_over()

# =========================
# INPUT
# =========================
def reset_game():
    global player_xyz, lives, score, game_over, paused, flash_battery
    global cheat_god, cheat_vision, light_boost_until, slow_enemies_until

    player_xyz = [0.0, 0.0, 0.0]
    lives = 5
    score = 0
    game_over = False
    paused = False
    flash_battery = 100.0
    cheat_god = False
    cheat_vision = False
    light_boost_until = 0.0
    slow_enemies_until = 0.0

    spawn_enemies()
    spawn_items()

def keyboard(key, x, y):
    global paused, flashlight_on, show_help, running
    global cheat_god, cheat_vision, player_color
    global shadows_on, game_over

    if key == b'\x1b':  # ESC
        glutLeaveMainLoop()
        return

    if key == b'p':
        paused = not paused
        return

    if key == b'f':
        flashlight_on = not flashlight_on
        return

    if key == b'h':
        show_help = not show_help
        return

    if key == b'x':  # run toggle (safe if you can't use key-up)
        running = not running
        return

    if key == b'c':
        cheat_god = not cheat_god
        return

    if key == b'v':
        cheat_vision = not cheat_vision
        return

    if key == b'o':  # outfit colour
        player_color = [random.random(), random.random(), random.random()]
        return

    if key == b't':  # toggle shadows
        shadows_on = not shadows_on
        return

    if key == b'r':
        reset_game()
        return

    if game_over:
        return
    if paused:
        return

    # Movement based on camera forward/right
    speed = run_speed if running else player_speed
    fx, fy = cam_dir[0], cam_dir[1]
    rx, ry = -fy, fx

    if key == b'w':
        player_xyz[0] += fx * speed
        player_xyz[1] += fy * speed
    elif key == b's':
        player_xyz[0] -= fx * speed
        player_xyz[1] -= fy * speed
    elif key == b'a':
        player_xyz[0] -= rx * speed
        player_xyz[1] -= ry * speed
    elif key == b'd':
        player_xyz[0] += rx * speed
        player_xyz[1] += ry * speed

    keep_inside_world(player_xyz)

def special_keys(key, x, y):
    global camera_angle, camera_up_down

    if key == GLUT_KEY_LEFT:
        camera_angle = (camera_angle + 4.0) % 360.0
    elif key == GLUT_KEY_RIGHT:
        camera_angle = (camera_angle - 4.0) % 360.0
    elif key == GLUT_KEY_UP:
        camera_up_down += 4.0
    elif key == GLUT_KEY_DOWN:
        camera_up_down -= 4.0

def mouse(button, state, x, y):
    # Left click: small score bonus (placeholder interaction) OR toggle flashlight
    # Right click: toggle cheat vision (as an example)
    global flashlight_on, cheat_vision, score
    if state != GLUT_DOWN:
        return

    if button == GLUT_LEFT_BUTTON:
        # optional: flashlight toggle on click
        flashlight_on = not flashlight_on
    elif button == GLUT_RIGHT_BUTTON:
        cheat_vision = not cheat_vision

# =========================
# GLUT LOOP
# =========================
def idle():
    global last_time, delta_time
    now = time.time()
    delta_time = now - last_time
    last_time = now

    if not paused and not game_over:
        update_game(delta_time)

    glutPostRedisplay()

def reshape(width, height):
    global window_width, window_height
    window_width = max(1, int(width))
    window_height = max(1, int(height))
    glViewport(0, 0, window_width, window_height)

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    setup_camera()

    # Draw world
    draw_ground()
    draw_walls()

    # Draw entities
    draw_items()
    draw_enemies()
    draw_player()

    # HUD
    draw_text(10, window_height - 25, f"Score: {score}   Lives: {lives}   Battery: {int(flash_battery)}%")
    draw_text(10, window_height - 50, f"Flashlight: {'ON' if flashlight_on else 'OFF'}   Run(x): {'ON' if running else 'OFF'}   Shadows(t): {'ON' if shadows_on else 'OFF'}")

    if paused:
        draw_text(window_width//2 - 50, window_height//2, "PAUSED", GLUT_BITMAP_TIMES_ROMAN_24)

    if game_over:
        draw_text(window_width//2 - 90, window_height//2 + 30, "GAME OVER", GLUT_BITMAP_TIMES_ROMAN_24)
        draw_text(window_width//2 - 170, window_height//2, "Press 'r' to restart", GLUT_BITMAP_HELVETICA_18)

    if show_help:
        y = window_height - 80
        draw_text(10, y,     "Controls:")
        draw_text(10, y-25,  "WASD move | Arrow keys rotate/tilt camera | P pause | F flashlight | X run toggle")
        draw_text(10, y-50,  "C god mode | V vision cheat | O outfit colour | T shadows | R reset | H help | ESC exit")

    glutSwapBuffers()

# =========================
# INIT
# =========================
def init():
    glClearColor(0.02, 0.02, 0.02, 1.0)
    glEnable(GL_DEPTH_TEST)

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(window_width, window_height)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"3D Light & Shadow Game (GLUT only)")

    init()
    spawn_enemies()
    spawn_items()

    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(special_keys)
    glutMouseFunc(mouse)
    glutIdleFunc(idle)

    glutMainLoop()

if __name__ == "__main__":
    main()
