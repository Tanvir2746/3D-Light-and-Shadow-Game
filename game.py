from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import math
import random
import time

colors = {
    "white":  (1.0, 1.0, 1.0),
    "red":    (1.0, 0.0, 0.0),
    "green":  (0.0, 1.0, 0.0),
    "blue":   (0.0, 0.0, 1.0),
    "yellow": (1.0, 1.0, 0.0),
    "cyan":   (0.0, 1.0, 1.0),
    "magenta":(1.0, 0.0, 1.0),
    "orange": (1.0, 0.5, 0.0),
    "purple": (0.5, 0.0, 0.5)
}
win_width = 1000
win_height = 800
grid_length = 2000
boundary_min = 100 - grid_length
boundary_max = grid_length - 100
last_time = time.time()
delta_time = 0.0
camera_angle = 0.0
cam_up_down = -25.0
fov = 120.0
cam_direction = [1.0, 0.0, 0.0]  
view = "third_person"            
player_xyz = [0.0, 0.0, 0.0]
player_radius = 25.0
player_speed = 5.0
run_speed = 12.0
running = False
player_color = [0.0, 0.0, 1.0]
player_yaw = 0.0
enemies = []
enemy_count = 4
enemy_init_speed = 0.5
enemy_chase_speed = 1.5
enemy_damage_cooldown = 0.8
last_damage = 0.0
lives = 5
score = 0
game_over = False
paused = False
show_instructions = False
flash_on = True
flash_range = 350.0
flash_fov = 40.0
flash_brightness = 2.5
flash_off_dim = 0.2
flash_battery = 100.0
shadows = True
shadow_len = 1.0
cheat_mode = False   
cheat_vision = False 
hidden_items = []
items = 8
in_menu = True
light_boost = 0.0
slow_enemies = 0.0
speed_boost = 0.0
collectibles = []
powerups = []
collectible_count = 5
collectible_radius = 10
structures = []

# Outfit selections (cycled with the 'u' key)
outfit_colors = [
    [1.0, 0.0, 0.0],
    [0.0, 1.0, 0.0],
    [0.0, 0.0, 1.0],
    [1.0, 1.0, 0.0],
    [1.0, 0.5, 0.0],
    [0.5, 0.0, 0.5],
    [0.0, 1.0, 1.0],
    [1.0, 0.0, 1.0]
]
current_outfit_index = 2

def draw_text(x, y, text, font=GLUT_BITMAP_TIMES_ROMAN_24):
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, win_width, 0, win_height)
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

def draw_menu():
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, win_width, 0, win_height)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glDisable(GL_DEPTH_TEST)
    glColor3f(0.02, 0.02, 0.02)
    glBegin(GL_QUADS)
    glVertex2f(0, 0)
    glVertex2f(win_width, 0)
    glVertex2f(win_width, win_height)
    glVertex2f(0, win_height)
    glEnd()
    bw, bh = 480, 140
    bx = (win_width - bw) / 2
    by = (win_height - bh) / 2
    glColor3f(0.12, 0.12, 0.12)
    glBegin(GL_QUADS)
    glVertex2f(bx, by)
    glVertex2f(bx + bw, by)
    glVertex2f(bx + bw, by + bh)
    glVertex2f(bx, by + bh)
    glEnd()
    glColor3f(1.0, 1.0, 1.0)
    glLineWidth(2.0)
    glBegin(GL_LINE_LOOP)
    glVertex2f(bx, by)
    glVertex2f(bx + bw, by)
    glVertex2f(bx + bw, by + bh)
    glVertex2f(bx, by + bh)
    glEnd()
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glEnable(GL_DEPTH_TEST)
    glColor3f(1.0, 1.0, 1.0)
    font = GLUT_BITMAP_TIMES_ROMAN_24
    label = "Press SPACE to start"
    total_w = sum(glutBitmapWidth(font, ord(ch)) for ch in label)
    start_x = int(win_width / 2) - (total_w // 2)
    y = int(win_height / 2) + 20
    draw_text(start_x, y, label, font)
    draw_text(10, 60, "Controls: WASD move | Arrow keys rotate/tilt | P pause | L-click flashlight | R-click FPV toggle")
    draw_text(10, 35, "X run | C god | V vision | O outfit | T shadows | R reset | H help")


def draw_ground():
    glBegin(GL_QUADS)
    glColor3f(0.12, 0.12, 0.12)

    glVertex3f(-grid_length, grid_length, 0)
    glVertex3f(0, grid_length, 0)
    glVertex3f(0, 0, 0)
    glVertex3f(-grid_length, 0, 0)

    glColor3f(0.10, 0.10, 0.16)
    glVertex3f(grid_length, -grid_length, 0)
    glVertex3f(0, -grid_length, 0)
    glVertex3f(0, 0, 0)
    glVertex3f(grid_length, 0, 0)

    glColor3f(0.10, 0.14, 0.10)
    glVertex3f(-grid_length, -grid_length, 0)
    glVertex3f(-grid_length, 0, 0)
    glVertex3f(0, 0, 0)
    glVertex3f(0, -grid_length, 0)

    glColor3f(0.14, 0.10, 0.10)
    glVertex3f(grid_length, grid_length, 0)
    glVertex3f(grid_length, 0, 0)
    glVertex3f(0, 0, 0)
    glVertex3f(0, grid_length, 0)
    glEnd()

    glColor3f(0.25, 0.25, 0.25)
    glBegin(GL_LINES)
    step = 100
    for x in range(-grid_length, grid_length + 1, step):
        glVertex3f(x, -grid_length, 0.2)
        glVertex3f(x,  grid_length, 0.2)
    for y in range(-grid_length, grid_length + 1, step):
        glVertex3f(-grid_length, y, 0.2)
        glVertex3f( grid_length, y, 0.2)
    glEnd()

def draw_walls():
    height = 100.0
    glColor3f(0.3, 0.3, 0.3)
    glBegin(GL_QUADS)
    glVertex3f(boundary_min, boundary_min, 0)
    glVertex3f(boundary_min, boundary_max, 0)
    glVertex3f(boundary_min, boundary_max, height)
    glVertex3f(boundary_min, boundary_min, height)

    glVertex3f(boundary_max, boundary_min, 0)
    glVertex3f(boundary_max, boundary_max, 0)
    glVertex3f(boundary_max, boundary_max, height)
    glVertex3f(boundary_max, boundary_min, height)

    glVertex3f(boundary_min, boundary_min, 0)
    glVertex3f(boundary_max, boundary_min, 0)
    glVertex3f(boundary_max, boundary_min, height)
    glVertex3f(boundary_min, boundary_min, height)

    glVertex3f(boundary_min, boundary_max, 0)
    glVertex3f(boundary_max, boundary_max, 0)
    glVertex3f(boundary_max, boundary_max, height)
    glVertex3f(boundary_min, boundary_max, height)
    glEnd()

def draw_shadow(x, y, r):
    glColor3f(0.02, 0.02, 0.02)
    glPointSize(2)
    glBegin(GL_POINTS)
    steps = 160
    for i in range(steps):
        ang = (i / steps) * 2.0 * math.pi
        for d in range(0, int(r), 2):
            px = x + math.cos(ang) * d
            py = y + math.sin(ang) * d
            glVertex3f(px, py, 0.5)
    glEnd()

def in_flash(pos):
    # Cheat vision reveals everything regardless of flashlight state
    if cheat_vision:
        return True
    if not flash_on:
        return False
    px, py = player_xyz[0], player_xyz[1]
    ox, oy = pos[0], pos[1]
    dx, dy = ox - px, oy - py
    dist = math.hypot(dx, dy)
    if dist > flash_range:
        return False
    fx, fy = cam_direction[0], cam_direction[1]
    cam_len = math.hypot(fx, fy)
    if cam_len == 0 or dist == 0:
        return True
    dot = fx * dx + fy * dy
    cosang = dot / (cam_len * dist)
    cosang = max(-1.0, min(1.0, cosang))
    ang_deg = math.degrees(math.acos(cosang))
    return ang_deg <= (flash_fov * 0.5)

def draw_player():
    if view == "first_person":
        return
    base = 0.7 if flash_on else 0.45
    glPushMatrix()
    glTranslatef(player_xyz[0], player_xyz[1], player_radius)
    glRotatef(player_yaw - 90.0, 0, 0, 1)

    # Torso
    glColor3f(player_color[0]*base, player_color[1]*base, player_color[2]*base)
    glPushMatrix()
    glScalef(player_radius * 0.6, player_radius * 0.6, player_radius * 1.6)
    glutSolidCube(1.0)
    glPopMatrix()

    # Head
    glPushMatrix()
    glTranslatef(0, 0, player_radius * 1.2)
    glutSolidSphere(player_radius * 0.6, 16, 16)
    glPopMatrix()

    # Head-mounted flashlight body and lens
    glPushMatrix()
    glTranslatef(player_radius * 0.9, 0, player_radius * 1.2)
    glRotatef(-90, 1, 0, 0)
    glPushMatrix()
    glColor3f(0.85, 0.85, 0.85)
    glScalef(player_radius * 0.25, player_radius * 0.25, player_radius * 0.6)
    glutSolidCube(1.0)
    glPopMatrix()
    glTranslatef(0, 0, player_radius * 0.35)
    glColor3f(1.0, 1.0, 0.6)
    glutSolidCone(player_radius * 0.15, player_radius * 0.25, 10, 2)
    glPopMatrix()

    # Arms
    glPushMatrix()
    glTranslatef(player_radius * 0.65, 0, player_radius * 0.45)
    glScalef(player_radius * 0.3, player_radius * 0.3, player_radius * 1.1)
    glutSolidCube(1.0)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(-player_radius * 0.65, 0, player_radius * 0.45)
    glScalef(player_radius * 0.3, player_radius * 0.3, player_radius * 1.1)
    glutSolidCube(1.0)
    glPopMatrix()

    # Legs
    glPushMatrix()
    glTranslatef(player_radius * 0.28, 0, -player_radius * 0.35)
    glScalef(player_radius * 0.35, player_radius * 0.35, player_radius * 1.25)
    glutSolidCube(1.0)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(-player_radius * 0.28, 0, -player_radius * 0.35)
    glScalef(player_radius * 0.35, player_radius * 0.35, player_radius * 1.25)
    glutSolidCube(1.0)
    glPopMatrix()

    glPopMatrix()
    if shadows:
        draw_shadow(player_xyz[0], player_xyz[1], player_radius * shadow_len)

# Collectible star (points)
def draw_collectible(x, y, z, radius):
    glPushMatrix()
    glTranslatef(x, y, z)
    glColor3f(1.0, 1.0, 0.0)
    for i in range(5):
        glPushMatrix()
        glRotatef(i * 72, 0, 0, 1)
        glTranslatef(radius, 0, 0)
        glutSolidCone(radius/3, radius, 10, 2)
        glPopMatrix()
    glColor3f(1.0, 0.8, 0.0)
    glutSolidSphere(radius/2, 10, 10)
    glPopMatrix()

# Power-up renderings
def draw_powerup(x, y, z, radius, powerup_type):
    glPushMatrix()
    glTranslatef(x, y, z)
    if powerup_type == "light_boost":
        glColor3f(0.0, 1.0, 1.0)
        glutSolidSphere(radius, 15, 15)
        glColor3f(1.0, 1.0, 1.0)
        glutSolidSphere(radius * 0.7, 12, 12)
    elif powerup_type == "slow_enemies":
        glColor3f(0.5, 0.8, 1.0)
        for i in range(6):
            glPushMatrix()
            glRotatef(i * 60, 0, 0, 1)
            glTranslatef(radius, 0, 0)
            glutSolidCone(radius/4, radius*1.5, 8, 2)
            glPopMatrix()
        glColor3f(1.0, 1.0, 1.0)
        glutSolidSphere(radius/2, 10, 10)
    elif powerup_type == "speed_boost":
        glColor3f(1.0, 0.8, 0.0)
        glBegin(GL_QUADS)
        glVertex3f(-radius, 0, 0)
        glVertex3f(0, radius, 0)
        glVertex3f(radius, 0, 0)
        glVertex3f(0, -radius, 0)
        glEnd()
    glPopMatrix()

def draw_items():
    for item in hidden_items:
        if item["collected"]:
            continue
        visible = in_flash(item["pos"])
        if (not visible) and (not cheat_vision):
            continue
        t = item["type"]
        if t == "flash_recharge":
            glColor3f(*colors["yellow"])
        elif t == "life_refill":
            glColor3f(*colors["green"])
        elif t == "light_boost":
            glColor3f(*colors["blue"])
        elif t == "slow_enemies":
            glColor3f(*colors["red"])
        else:
            glColor3f(*colors["white"])
        glPushMatrix()
        glTranslatef(item["pos"][0], item["pos"][1], 10)
        glutSolidCube(item["r"] * 1.4)
        glPopMatrix()
        if shadows:
            draw_shadow(item["pos"][0], item["pos"][1], item["r"] * shadow_len)

    for collectible in collectibles:
        if collectible.get("collected"):
            continue
        if (not in_flash(collectible["pos"])) and (not cheat_vision):
            continue
        draw_collectible(collectible["pos"][0], collectible["pos"][1], 15, collectible_radius)
        if shadows:
            draw_shadow(collectible["pos"][0], collectible["pos"][1], collectible_radius * shadow_len)

    for powerup in powerups:
        if powerup.get("collected"):
            continue
        if (not in_flash(powerup["pos"])) and (not cheat_vision):
            continue
        draw_powerup(powerup["pos"][0], powerup["pos"][1], 15, powerup["r"], powerup["type"])
        if shadows:
            draw_shadow(powerup["pos"][0], powerup["pos"][1], powerup["r"] * shadow_len)

def draw_enemies():
    for enemy in enemies:
        visible = in_flash(enemy["pos"])
        t = time.time()
        base_col = (0.4, 0.75, 0.4)  # zombie green
        if t < slow_enemies:
            if visible:
                glColor3f(0.8, 0.8, 0.8)
            else:
                glColor3f(0.5, 0.5, 0.5)
        else:
            if visible:
                glColor3f(*base_col)
            else:
                glColor3f(base_col[0]*0.35, base_col[1]*0.35, base_col[2]*0.35)

        glPushMatrix()
        glTranslatef(enemy["pos"][0], enemy["pos"][1], enemy["r"])

        # Torso
        glPushMatrix()
        glScalef(enemy["r"] * 0.7, enemy["r"] * 0.7, enemy["r"] * 1.8)
        glutSolidCube(1.0)
        glPopMatrix()

        # Head
        glPushMatrix()
        glTranslatef(0, 0, enemy["r"] * 1.2)
        glutSolidSphere(enemy["r"] * 0.7, 14, 14)
        glPopMatrix()

        # Arms forward (zombie pose)
        glPushMatrix()
        glTranslatef(enemy["r"] * 0.8, 0, enemy["r"] * 0.45)
        glRotatef(20, 0, 1, 0)
        glScalef(enemy["r"] * 0.35, enemy["r"] * 0.35, enemy["r"] * 1.35)
        glutSolidCube(1.0)
        glPopMatrix()

        glPushMatrix()
        glTranslatef(-enemy["r"] * 0.8, 0, enemy["r"] * 0.45)
        glRotatef(-20, 0, 1, 0)
        glScalef(enemy["r"] * 0.35, enemy["r"] * 0.35, enemy["r"] * 1.35)
        glutSolidCube(1.0)
        glPopMatrix()

        # Legs
        glPushMatrix()
        glTranslatef(enemy["r"] * 0.38, 0, -enemy["r"] * 0.45)
        glScalef(enemy["r"] * 0.4, enemy["r"] * 0.4, enemy["r"] * 1.4)
        glutSolidCube(1.0)
        glPopMatrix()

        glPushMatrix()
        glTranslatef(-enemy["r"] * 0.38, 0, -enemy["r"] * 0.45)
        glScalef(enemy["r"] * 0.4, enemy["r"] * 0.4, enemy["r"] * 1.4)
        glutSolidCube(1.0)
        glPopMatrix()

        glPopMatrix()
        if shadows:
            draw_shadow(enemy["pos"][0], enemy["pos"][1], enemy["r"] * shadow_len)

def setup_camera():
    global cam_direction
    fx = math.cos(math.radians(camera_angle))
    fy = math.sin(math.radians(camera_angle))
    cam_direction = [fx, fy, 0.0]
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    aspect_ratio = win_width / float(win_height)
    gluPerspective(fov, aspect_ratio, 1.0, 5000.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    if view == "first_person":
        eye_x = player_xyz[0]
        eye_y = player_xyz[1]
        eye_z = 55.0
        look_x = eye_x + fx * 120.0
        look_y = eye_y + fy * 120.0
        look_z = eye_z
        gluLookAt(eye_x, eye_y, eye_z,
                  look_x, look_y, look_z,
                  0, 0, 1)
    else:
        eye_x = player_xyz[0] - fx * 200.0
        eye_y = player_xyz[1] - fy * 200.0
        eye_z = 100.0 + cam_up_down

        gluLookAt(eye_x, eye_y, eye_z,
                  player_xyz[0], player_xyz[1], player_xyz[2],
                  0, 0, 1)

def spawn_enemies():
    global enemies
    enemies = []
    for _ in range(enemy_count):
        while True:
            enemy_x = random.randint(boundary_min, boundary_max)
            enemy_y = random.randint(boundary_min, boundary_max)
            dist = math.sqrt((enemy_x - player_xyz[0])**2 + (enemy_y - player_xyz[1])**2)
            if dist > 200:
                break
        enemies.append({
            "pos": [float(enemy_x), float(enemy_y), 0.0],
            "r": 20.0,
            "state": "idle",
            "base_speed": enemy_init_speed
        })

def spawn_items():
    global hidden_items
    hidden_items = []
    for _ in range(items):
        item_x = random.randint(boundary_min, boundary_max)
        item_y = random.randint(boundary_min, boundary_max)
        kind = random.choice(["flash_recharge", "life_refill", "light_boost", "slow_enemies"])
        hidden_items.append({
            "pos": [float(item_x), float(item_y), 0.0],
            "r": 15.0,
            "collected": False,
            "type": kind
        })

def spawn_collectibles():
    global collectibles
    collectibles = []
    for _ in range(collectible_count):
        while True:
            x = random.randint(boundary_min, boundary_max)
            y = random.randint(boundary_min, boundary_max)
            if math.hypot(x - player_xyz[0], y - player_xyz[1]) > 150:
                break
        collectibles.append({
            "pos": [float(x), float(y), 0.0],
            "collected": False
        })

def spawn_powerups():
    global powerups
    powerups = []
    powerup_types = ["light_boost", "slow_enemies", "speed_boost"]
    for _ in range(3):
        while True:
            x = random.randint(boundary_min, boundary_max)
            y = random.randint(boundary_min, boundary_max)
            if math.hypot(x - player_xyz[0], y - player_xyz[1]) > 200:
                break
        powerups.append({
            "pos": [float(x), float(y), 0.0],
            "r": 15.0,
            "collected": False,
            "type": random.choice(powerup_types)
        })

def spawn_structures(count=30):
    global structures
    structures = []
    for _ in range(count):
        w = random.randint(40, 220)
        d = random.randint(40, 220)
        h = random.randint(40, 240)
        sx = random.randint(boundary_min + w, boundary_max - w)
        sy = random.randint(boundary_min + d, boundary_max - d)
        if math.hypot(sx - player_xyz[0], sy - player_xyz[1]) < 200:
            continue
        structures.append({
            "pos": [float(sx), float(sy)],
            "w": float(w),
            "d": float(d),
            "h": float(h),
            "type": random.choice([0,1,2])
        })

def draw_structures():
    for s in structures:
        sx, sy = s["pos"]
        w, d, h = s["w"], s["d"], s["h"]
        t = s.get("type", 0)
        visible = in_flash([sx, sy, 0.0])
        if t == 0:
            base_col = (0.2, 0.2, 0.25)
        elif t == 1:
            base_col = (0.18, 0.14, 0.12)
        else:
            base_col = (0.22, 0.18, 0.2)
        if not visible:
            base_col = tuple(c * 0.35 for c in base_col)
        glColor3f(*base_col)
        glPushMatrix()
        glTranslatef(sx, sy, h/2.0)
        glScalef(w, d, h)
        glutSolidCube(1.0)
        glPopMatrix()

def check_game_over():
    global game_over
    if lives <= 0 or flash_battery <= 0:
        game_over = True

def effects():
    global flash_brightness, flash_range, player_speed, run_speed
    t = time.time()
    base_range = 350.0
    base_brightness = 1.5

    if t < light_boost:
        flash_range = base_range * 1.5
        flash_brightness = base_brightness * 1.5
    else:
        flash_range = base_range
        flash_brightness = base_brightness

    if t < speed_boost:
        player_speed = 10.0
        run_speed = 24.0
    else:
        player_speed = 5.0
        run_speed = 12.0

def update_enemies(dt):
    global lives, last_damage
    t = time.time()
    slow_factor = 0.4 if t < slow_enemies else 1.0
    for enemy in enemies:
        ex, ey = enemy["pos"][0], enemy["pos"][1]
        px, py = player_xyz[0], player_xyz[1]

        dx = ex - px
        dy = ey - py
        visible = in_flash(enemy["pos"])
        if enemy.get("state") == "idle":
            if visible:
                enemy["state"] = "chase"
        speed = enemy["base_speed"] * slow_factor
        if enemy.get("state") == "chase":
            speed *= enemy_chase_speed
            vx = px - ex
            vy = py - ey
            length = math.sqrt(vx*vx + vy*vy)
            if length != 0:
                nx = vx / length
                ny = vy / length
            else:
                nx, ny = 0.0, 0.0
            new_x = enemy["pos"][0] + nx * speed * 60.0 * dt
            new_y = enemy["pos"][1] + ny * speed * 60.0 * dt
            collided = False
            for s in structures:
                sx, sy = s["pos"]
                hw = s["w"]/2.0 + enemy["r"]
                hd = s["d"]/2.0 + enemy["r"]
                if abs(new_x - sx) < hw and abs(new_y - sy) < hd:
                    collided = True
                    break
            if not collided:
                enemy["pos"][0] = new_x
                enemy["pos"][1] = new_y
        if enemy["pos"][0] < boundary_min:
            enemy["pos"][0] = boundary_min
        elif enemy["pos"][0] > boundary_max:
            enemy["pos"][0] = boundary_max
        if enemy["pos"][1] < boundary_min:
            enemy["pos"][1] = boundary_min
        elif enemy["pos"][1] > boundary_max:
            enemy["pos"][1] = boundary_max
        dx2 = enemy["pos"][0] - px
        dy2 = enemy["pos"][1] - py
        dist_sq = dx2*dx2 + dy2*dy2
        if dist_sq <= (enemy["r"] + player_radius) ** 2:
            if (not cheat_mode) and (t - last_damage > enemy_damage_cooldown):
                lives -= 1
                last_damage = t

def check_item_pickups():
    global lives, flash_battery, light_boost, slow_enemies, score, speed_boost
    px, py = player_xyz[0], player_xyz[1]
    for item in hidden_items:
        if item["collected"]:
            continue
        dx = item["pos"][0] - px
        dy = item["pos"][1] - py
        dist_sq = dx*dx + dy*dy

        if dist_sq <= (item["r"] + player_radius) ** 2:
            item["collected"] = True
            score += 5

            t = item["type"]
            if t == "life_refill":
                lives = min(10, lives + 1)
            elif t == "flash_recharge":
                flash_battery = min(100.0, flash_battery + 30.0)
            elif t == "light_boost":
                light_boost = time.time() + 10.0
            elif t == "slow_enemies":
                slow_enemies = time.time() + 8.0

    for collectible in collectibles:
        if collectible.get("collected"):
            continue
        dx = collectible["pos"][0] - px
        dy = collectible["pos"][1] - py
        if dx*dx + dy*dy <= (collectible_radius + player_radius) ** 2:
            collectible["collected"] = True
            score += 5

    for powerup in powerups:
        if powerup.get("collected"):
            continue
        dx = powerup["pos"][0] - px
        dy = powerup["pos"][1] - py
        if dx*dx + dy*dy <= (powerup["r"] + player_radius) ** 2:
            powerup["collected"] = True
            if powerup["type"] == "light_boost":
                light_boost = time.time() + 10.0
            elif powerup["type"] == "slow_enemies":
                slow_enemies = time.time() + 8.0
            elif powerup["type"] == "speed_boost":
                speed_boost = time.time() + 6.0

def can_move_to(x, y, radius):
    if x < boundary_min or x > boundary_max or y < boundary_min or y > boundary_max:
        return False
    for s in structures:
        sx, sy = s["pos"]
        hw = s["w"] / 2.0 + radius
        hd = s["d"] / 2.0 + radius
        if abs(x - sx) < hw and abs(y - sy) < hd:
            return False
    return True

def update_game(dt):
    global flash_battery
    if paused or game_over:
        return
    update_enemies(dt)
    check_item_pickups()
    if flash_on and (not cheat_mode):
        flash_battery -= 2.0 * dt
        if flash_battery < 0.0:
            flash_battery = 0.0
    effects()
    check_game_over()

def reset_game():
    global player_xyz, lives, score, game_over, paused, flash_battery
    global cheat_mode, cheat_vision, light_boost, slow_enemies, speed_boost, view
    global camera_angle, cam_up_down, running, player_color, current_outfit_index
    player_xyz = [0.0, 0.0, 0.0]
    lives = 5
    score = 0
    game_over = False
    paused = False
    flash_battery = 100.
    cheat_mode = False
    cheat_vision = False
    light_boost = 0.0
    slow_enemies = 0.0
    speed_boost = 0.0
    view = "third_person"
    camera_angle = 0.0
    cam_up_down = -25.0
    running = False
    current_outfit_index = 2
    player_color = outfit_colors[current_outfit_index].copy()
    spawn_enemies()
    spawn_items()
    spawn_structures()
    spawn_collectibles()
    spawn_powerups()


def change_outfit():
    global current_outfit_index, player_color
    current_outfit_index = (current_outfit_index + 1) % len(outfit_colors)
    player_color = outfit_colors[current_outfit_index].copy()

def keyboardListener(key, x, y):
    global in_menu
    if key == b' ':
        if in_menu:
            in_menu = False
            reset_game()
            return
    global paused, cheat_mode, cheat_vision, player_color, shadows
    global flash_on, show_instructions, running
    if key == b'p':
        paused = not paused
        return
    if key == b'f':
        flash_on = not flash_on
        return
    if key == b'h':
        show_instructions = not show_instructions
        return
    if key == b'x':
        running = not running
        return
    if key == b'c':
        cheat_mode = not cheat_mode
        player_color = [1.0, 1.0, 0.0] if cheat_mode else outfit_colors[current_outfit_index].copy()
        return
    if key == b'v':
        cheat_vision = not cheat_vision
        return
    if key == b'o':
        player_color = [random.random(), random.random(), random.random()]
        return
    if key == b'u':
        change_outfit()
        return
    if key == b't':
        shadows = not shadows
        return
    if key == b'r':
        reset_game()
        return
    if game_over or paused:
        return
    speed = run_speed if running else player_speed
    fx, fy = cam_direction[0], cam_direction[1]
    rx, ry = -fy, fx
    if key == b'w':
        nx = player_xyz[0] + fx * speed
        ny = player_xyz[1] + fy * speed
        if can_move_to(nx, ny, player_radius):
            player_xyz[0] = nx
            player_xyz[1] = ny
    elif key == b's':
        nx = player_xyz[0] - fx * speed
        ny = player_xyz[1] - fy * speed
        if can_move_to(nx, ny, player_radius):
            player_xyz[0] = nx
            player_xyz[1] = ny
    elif key == b'd':
        nx = player_xyz[0] - rx * speed
        ny = player_xyz[1] - ry * speed
        if can_move_to(nx, ny, player_radius):
            player_xyz[0] = nx
            player_xyz[1] = ny
    elif key == b'a':
        nx = player_xyz[0] + rx * speed
        ny = player_xyz[1] + ry * speed
        if can_move_to(nx, ny, player_radius):
            player_xyz[0] = nx
            player_xyz[1] = ny

    if player_xyz[0] < boundary_min:
        player_xyz[0] = boundary_min
    elif player_xyz[0] > boundary_max:
        player_xyz[0] = boundary_max

    if player_xyz[1] < boundary_min:
        player_xyz[1] = boundary_min
    elif player_xyz[1] > boundary_max:
        player_xyz[1] = boundary_max

def special_keys(key, x, y):
    global camera_angle, cam_up_down, player_yaw
    if key == GLUT_KEY_UP:
        cam_up_down += 2.0
    elif key == GLUT_KEY_DOWN:
        cam_up_down -= 2.0
    elif key == GLUT_KEY_RIGHT:
        camera_angle = (camera_angle - 2.0) % 360.0
        player_yaw = camera_angle
    elif key == GLUT_KEY_LEFT:
        camera_angle = (camera_angle + 2.0) % 360.0
        player_yaw = camera_angle

def mouse(button, state, x, y):
    global flash_on, view
    if state != GLUT_DOWN:
        return
    if button == GLUT_LEFT_BUTTON:
        flash_on = not flash_on
    elif button == GLUT_RIGHT_BUTTON:
        view = "first_person" if view == "third_person" else "third_person"

def idle():
    global last_time, delta_time
    now = time.time()
    delta_time = now - last_time
    last_time = now
    update_game(delta_time)
    glutPostRedisplay()

def display():
    glViewport(0, 0, win_width, win_height)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    if in_menu:
        draw_menu()
        glutSwapBuffers()
        return
    setup_camera()
    draw_ground()
    draw_structures()
    draw_walls()
    draw_items()
    draw_enemies()
    draw_player()
    if flash_on:
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(1.0, 1.0, 0.6, 0.18)
        center_ang = math.atan2(cam_direction[1], cam_direction[0])
        half_ang = math.radians(flash_fov) * 0.5
        steps = 18
        glBegin(GL_TRIANGLE_FAN)
        glVertex3f(player_xyz[0], player_xyz[1], 2.0)
        for i in range(steps + 1):
            a = center_ang - half_ang + (2 * half_ang) * (i / steps)
            glVertex3f(
                player_xyz[0] + math.cos(a) * flash_range,
                player_xyz[1] + math.sin(a) * flash_range,
                2.0
            )
        glEnd()
        glDisable(GL_BLEND)
    mode = "FPV" if view == "first_person" else "TPV"

    font = GLUT_BITMAP_HELVETICA_18
    color_names = ["Red", "Green", "Blue", "Yellow", "Orange", "Purple", "Cyan", "Magenta"]
    outfit_name = color_names[current_outfit_index]
    t_now = time.time()
    active = []
    if t_now < light_boost:
        active.append(f"Light Boost {int(light_boost - t_now)}s")
    if t_now < slow_enemies:
        active.append(f"Slow Enemies {int(slow_enemies - t_now)}s")
    if t_now < speed_boost:
        active.append(f"Speed Boost {int(speed_boost - t_now)}s")
    powerup_line = ", ".join(active) if active else "None"

    # Top-left: score and power-ups
    glColor3f(0.0, 1.0, 1.0)
    draw_text(10, win_height - 25, f"Score: {score}", font)
    glColor3f(0.8, 0.9, 0.4)
    draw_text(10, win_height - 50, f"Power-ups: {powerup_line}", font)

    # Top-right: lives and battery
    glColor3f(1.0, 0.8, 0.0)
    rt1 = f"Lives: {lives}"
    rt2 = f"Battery: {int(flash_battery)}%"
    w1 = sum(glutBitmapWidth(font, ord(c)) for c in rt1)
    w2 = sum(glutBitmapWidth(font, ord(c)) for c in rt2)
    draw_text(win_width - w1 - 10, win_height - 25, rt1, font)
    glColor3f(0.8, 0.8, 1.0)
    draw_text(win_width - w2 - 10, win_height - 50, rt2, font)

    # Middle-top: mode, outfit, toggles
    mid_strings = [
        f"Mode: {mode}",
        f"Outfit (u): {outfit_name}",
        f"Flash: {'ON' if flash_on else 'OFF'} | Run: {'ON' if running else 'OFF'} | Shadows: {'ON' if shadows else 'OFF'}"
    ]
    colors_mid = [(1.0, 1.0, 1.0), (0.6, 0.9, 1.0), (0.9, 0.7, 1.0)]
    y_offset = win_height - 25
    for idx, text in enumerate(mid_strings):
        glColor3f(*colors_mid[idx])
        w = sum(glutBitmapWidth(font, ord(c)) for c in text)
        draw_text(int(win_width/2 - w/2), y_offset - idx*25, text, font)
    if paused:
        draw_text(win_width//2 - 50, win_height//2, "PAUSED", GLUT_BITMAP_TIMES_ROMAN_24)
    if game_over:
        draw_text(win_width//2 - 90, win_height//2 + 30, "GAME OVER", GLUT_BITMAP_TIMES_ROMAN_24)
        draw_text(win_width//2 - 170, win_height//2, "Press 'r' to restart", GLUT_BITMAP_HELVETICA_18)
    if show_instructions:
        y = win_height - 80
        draw_text(10, y,     "Controls:")
        draw_text(10, y-25,  "WASD move | Arrow keys rotate/tilt | P pause | L-click flashlight | R-click FPV toggle")
        draw_text(10, y-50,  "X run | C god | V vision | O outfit | T shadows | R reset | H help")
    glutSwapBuffers()

def init():
    glClearColor(0.02, 0.02, 0.02, 1.0)
    glEnable(GL_DEPTH_TEST)
    global quadric
    quadric = gluNewQuadric()
    spawn_collectibles()
    spawn_powerups()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(win_width, win_height)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"3D Light & Shadow Game")
    init()
    spawn_enemies()
    spawn_items()
    spawn_structures()
    spawn_collectibles()
    spawn_powerups()
    glutDisplayFunc(display)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(special_keys)
    glutMouseFunc(mouse)
    glutIdleFunc(idle)
    glutMainLoop()

if __name__ == "__main__":
    main()
