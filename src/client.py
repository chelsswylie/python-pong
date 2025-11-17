import socket
import pickle
import pygame

# -------------------- GAME SETTINGS --------------------
WINDOW_WIDTH = 700
WINDOW_HEIGHT = 700
BAT_WIDTH = 20
BAT_HEIGHT = 100
BALL_DIAMETER = 20
DATA_SIZE = 4096
GAME_SPEED = 30

# -------------------- DTO --------------------
class PongDTO:
    def __init__(self):
        self.player_id = 0
        self.player_x = []
        self.player_y = []
        self.ball_x = 0
        self.ball_y = 0
        self.points = [0, 0]

# -------------------- CLASSES --------------------
class Bat:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.width = BAT_WIDTH
        self.height = BAT_HEIGHT
        self.points = 0

    def draw(self, window):
        pygame.draw.rect(window, self.color, (self.x, self.y, self.width, self.height))

    def move(self, direction):
        speed = 20
        if direction == 'up' and self.y > 0:
            self.y -= speed
        elif direction == 'down' and self.y < WINDOW_HEIGHT - BAT_HEIGHT:
            self.y += speed

class Ball:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color

    def draw(self, window):
        pygame.draw.circle(window, self.color, (int(self.x), int(self.y)), BALL_DIAMETER//2)

# -------------------- NETWORK SETUP --------------------
SERVER_IP = "192.168.x.xxx" 
SERVER_PORT = 5050
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER_IP, SERVER_PORT))

# Receive initial DTO
dto = pickle.loads(client.recv(DATA_SIZE))
player_id = dto.player_id
opponent_id = 1 - player_id

# Initialize objects
bats = [Bat(dto.player_x[0], dto.player_y[0], (144,238,144)),
        Bat(dto.player_x[1], dto.player_y[1], (255,185,127))]
ball = Ball(dto.ball_x, dto.ball_y, (0,0,0))

# -------------------- PYGAME SETUP --------------------
pygame.init()
win = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Pong Multiplayer")
clock = pygame.time.Clock()

# -------------------- MAIN LOOP --------------------
run = True
while run:
    clock.tick(GAME_SPEED)
    win.fill((255, 255, 255))

    # Draw objects
    bats[0].draw(win)
    bats[1].draw(win)
    ball.draw(win)

    pygame.display.set_caption(
        f'Ping-Pong Your score (Green):{dto.points[player_id]}, Opponent (Orange):{dto.points[opponent_id]}')
    pygame.display.update()

    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        bats[player_id].move('up')
    if keys[pygame.K_s]:
        bats[player_id].move('down')

    # Update DTO to send
    dto.player_y[player_id] = bats[player_id].y

    try:
        client.sendall(pickle.dumps(dto))
        dto = pickle.loads(client.recv(DATA_SIZE))

        # Update positions from server
        for i in range(2):
            bats[i].y = dto.player_y[i]
        ball.x = dto.ball_x
        ball.y = dto.ball_y

    except Exception as e:
        print("Lost connection to server:", e)
        run = False

pygame.quit()
