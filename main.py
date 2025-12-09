# Calico Randall
# December 9, 2025
# Running on Python 3.11.7
# Edge detection matrix: Detects the edges via OpenCV's Canny & creates a 
# visual inspired by the film The Matrix.

import cv2
import numpy as np
import pygame
import random

# -----------------------
# CONFIG
# -----------------------
# Use this width and height for testing
WIDTH  = 800
HEIGHT = 600        

# Matrix grid cell size
CELL_SIZE = 10
# Vertical scroll speed
FALL_SPEED = 0.6
# Strength of the edge halo
HALO_BLUR = 6
# How bright the edges become
BRIGHT_SCALE = 3.0

# -----------------------
# INIT
# -----------------------
pygame.init()

# Get the current monitor's resolution
info = pygame.display.Info()
SCREEN_WIDTH = info.current_w
SCREEN_HEIGHT = info.current_h

screen = pygame.display.set_mode( (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
#screen = pygame.display.set_mode( (WIDTH, HEIGHT) )
pygame.display.set_caption("Matrix Silhouette - Full Grid Method")

font = pygame.font.SysFont("Consolas", CELL_SIZE, bold=True)
clock = pygame.time.Clock()

# If using internal laptop camera, the first argument should be 0.
# If using an external camera (while also having an internal), first argument
# should be 1.
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, SCREEN_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, SCREEN_HEIGHT)

cols = SCREEN_WIDTH // CELL_SIZE
rows = SCREEN_HEIGHT // CELL_SIZE

# y offsets per column for scrolling rain
offsets = [random.uniform(0, rows) for _ in range(cols)]

def rand_char():
    return random.choice("0000000000000000000111111111111111111111123456789Z:・.=*+-<>")
# Katakana char that didn't work: 日ﾊﾐﾋｰｳｼﾅﾓﾆｻﾜﾂｵﾘｱﾎﾃﾏｹﾒｴｶｷﾑﾕﾗｾﾈｽﾀﾇﾍ

# Randomize characters for entire grid
chars = [[rand_char() for _ in range(cols)] for _ in range(rows)]

# -----------------------
# MAIN LOOP
# -----------------------
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    ret, frame = cap.read()
    if not ret:
        continue

    frame = cv2.resize(frame, (SCREEN_WIDTH, SCREEN_HEIGHT))
    frame = cv2.flip(frame, 1)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # 1. Canny edges
    edges = cv2.Canny(gray, 40, 120)

    # 2. Halo around edges (distance field)
    halo = cv2.GaussianBlur(edges.astype(np.float32), (0,0), HALO_BLUR)
    if halo.max() > 0:
        halo /= halo.max()   # 0–1

    # 3. Sample halo on the character grid
    brightness = np.zeros((rows, cols), dtype=np.float32)

    for r in range(rows):
        y0 = int(r * CELL_SIZE)
        y1 = min(y0 + CELL_SIZE, SCREEN_HEIGHT)
        for c in range(cols):
            x0 = int(c * CELL_SIZE)
            x1 = min(x0 + CELL_SIZE, SCREEN_WIDTH)
            # avg halo inside this cell
            cell_val = np.mean(halo[y0:y1, x0:x1])
            brightness[r, c] = min(1.0, cell_val * BRIGHT_SCALE)

    # Fade the screen
    fade = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    fade.fill((0, 0, 0, 55))
    screen.blit(fade, (0, 0))

    # 4. Draw matrix rain
    for c in range(cols):

        offsets[c] = (offsets[c] + FALL_SPEED * 0.1) % rows

        for r in range(rows):
            rr = int((r + offsets[c]) % rows)

            ch = chars[rr][c]

            # brightness controlled by edge halo
            b = brightness[r][c]
            g = int(60 + b * 195)
            color = (0, g, 0)

            screen.blit(font.render(ch, True, color),
                        (c * CELL_SIZE, r * CELL_SIZE))

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        running = False
        break
    
    pygame.display.flip()
    clock.tick(30)

cap.release()
pygame.quit()