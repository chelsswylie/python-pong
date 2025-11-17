import socket
import threading
import pickle
import random
import time

# -------------------- GAME SETTINGS --------------------
WINDOW_WIDTH = 700
WINDOW_HEIGHT = 700
BAT_WIDTH = 20
BAT_HEIGHT = 100
BALL_DIAMETER = 20
BALL_VELOCITY_X = 5
BALL_VELOCITY_Y = 3

# Networking
SERVER_IP = "0.0.0.0"  # listen on all interfaces
SERVER_PORT = 5050
DATA_SIZE = 4096

# -------------------- GAME STATE --------------------
player_x = [10, WINDOW_WIDTH - BAT_WIDTH - 10]
player_y = [WINDOW_HEIGHT//2 - BAT_HEIGHT//2, WINDOW_HEIGHT//2 - BAT_HEIGHT//2]
points = [0, 0]

ball_x = WINDOW_WIDTH // 2
ball_y = WINDOW_HEIGHT // 2
ball_vel_x = BALL_VELOCITY_X * random.choice([-1, 1])
ball_vel_y = BALL_VELOCITY_Y * random.choice([-1, 1])

lock = threading.Lock()

# -------------------- DTO --------------------
class PongDTO:
    def __init__(self):
        self.player_id = 0
        self.player_x = []
        self.player_y = []
        self.ball_x = 0
        self.ball_y = 0
        self.points = [0, 0]

# -------------------- CLIENT HANDLER --------------------
def handle_client(conn, player_id):
    global player_x, player_y, ball_x, ball_y, ball_vel_x, ball_vel_y, points

    # Send initial DTO with player ID
    dto = PongDTO()
    dto.player_id = player_id
    dto.player_x = player_x.copy()
    dto.player_y = player_y.copy()
    dto.ball_x = ball_x
    dto.ball_y = ball_y
    dto.points = points.copy()

    conn.sendall(pickle.dumps(dto))

    while True:
        try:
            data = conn.recv(DATA_SIZE)
            if not data:
                break
            client_dto = pickle.loads(data)

            with lock:
                # Update player position only
                player_y[player_id] = client_dto.player_y[player_id]

                # --- SERVER CONTROLS BALL ---
                ball_x += ball_vel_x
                ball_y += ball_vel_y

                # Ball collision with top/bottom
                if ball_y <= 0 or ball_y >= WINDOW_HEIGHT - BALL_DIAMETER:
                    ball_vel_y *= -1

                # Ball collision with bats
                if (ball_x <= player_x[0] + BAT_WIDTH and
                    player_y[0] < ball_y < player_y[0] + BAT_HEIGHT):
                    ball_vel_x *= -1
                    ball_x = player_x[0] + BAT_WIDTH  # avoid sticking

                elif (ball_x >= player_x[1] - BALL_DIAMETER and
                      player_y[1] < ball_y < player_y[1] + BAT_HEIGHT):
                    ball_vel_x *= -1
                    ball_x = player_x[1] - BALL_DIAMETER  # avoid sticking

                # Ball out of bounds
                if ball_x < 0:
                    points[1] += 1
                    ball_x = WINDOW_WIDTH // 2
                    ball_y = WINDOW_HEIGHT // 2
                    ball_vel_x = BALL_VELOCITY_X * random.choice([-1, 1])
                    ball_vel_y = BALL_VELOCITY_Y * random.choice([-1, 1])

                elif ball_x > WINDOW_WIDTH:
                    points[0] += 1
                    ball_x = WINDOW_WIDTH // 2
                    ball_y = WINDOW_HEIGHT // 2
                    ball_vel_x = BALL_VELOCITY_X * random.choice([-1, 1])
                    ball_vel_y = BALL_VELOCITY_Y * random.choice([-1, 1])

                # Prepare DTO to send back
                dto = PongDTO()
                dto.player_x = player_x.copy()
                dto.player_y = player_y.copy()
                dto.ball_x = ball_x
                dto.ball_y = ball_y
                dto.points = points.copy()

            conn.sendall(pickle.dumps(dto))

        except Exception as e:
            print(f"Player {player_id} disconnected: {e}")
            break

    conn.close()

# -------------------- MAIN SERVER --------------------
def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((SERVER_IP, SERVER_PORT))
    server.listen(2)
    print(f"Server listening on {SERVER_IP}:{SERVER_PORT}")

    player_id = 0
    while player_id < 2:
        conn, addr = server.accept()
        print(f"Player {player_id} connected from {addr}")
        thread = threading.Thread(target=handle_client, args=(conn, player_id))
        thread.start()
        player_id += 1

    print("Server is full. Waiting for active games...")

if __name__ == "__main__":
    main()
