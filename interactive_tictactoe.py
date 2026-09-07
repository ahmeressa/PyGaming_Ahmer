import pygame
import sys
import random

# --- Window & Grid Dimensions ---
SCREEN_WIDTH = 600
UI_HEIGHT = 100
GRID_SIZE = 600
CELL_SIZE = GRID_SIZE // 3
SCREEN_HEIGHT = GRID_SIZE + UI_HEIGHT

# --- Colors ---
WHITE = (245, 245, 245)
GRAY = (200, 200, 200)
DARK_GRAY = (50, 50, 50)
BLUE = (30, 100, 220)
RED = (220, 50, 50)
GREEN = (30, 150, 30)

# --- Game State ---
board = [' ' for _ in range(9)]
score_count = 0
game_state = "PLAYING"  # "PLAYING" or "GAME_OVER"
game_result = ""

def is_board_full(b):
    return ' ' not in b

def is_winner(b, l):
    return (
        (b[0] == l and b[1] == l and b[2] == l) or
        (b[3] == l and b[4] == l and b[5] == l) or
        (b[6] == l and b[7] == l and b[8] == l) or
        (b[0] == l and b[3] == l and b[6] == l) or
        (b[1] == l and b[4] == l and b[7] == l) or
        (b[2] == l and b[5] == l and b[8] == l) or
        (b[0] == l and b[4] == l and b[8] == l) or
        (b[2] == l and b[4] == l and b[6] == l)
    )

def computer_move():
    possible_moves = [i for i, letter in enumerate(board) if letter == ' ']

    # 1. Win or Block
    for let in ['O', 'X']:
        for i in possible_moves:
            board_copy = board[:]
            board_copy[i] = let
            if is_winner(board_copy, let):
                return i

    # 2. Corners
    corners = [i for i in possible_moves if i in [0, 2, 6, 8]]
    if corners:
        return random.choice(corners)

    # 3. Center
    if 4 in possible_moves:
        return 4

    # 4. Edges
    edges = [i for i in possible_moves if i in [1, 3, 5, 7]]
    if edges:
        return random.choice(edges)

    return -1

def reset_game():
    global board, game_state, game_result, score_count
    board = [' ' for _ in range(9)]
    game_state = "PLAYING"
    game_result = ""
    if score_count < 0:
        score_count = 0

def check_game_end():
    global game_state, game_result, score_count
    if is_winner(board, 'X'):
        score_count += 1
        game_result = "You Win!"
        game_state = "GAME_OVER"
    elif is_winner(board, 'O'):
        score_count -= 1
        game_result = "Computer Wins!"
        game_state = "GAME_OVER"
    elif is_board_full(board):
        game_result = "It's a Tie!"
        game_state = "GAME_OVER"

# --- Main Pygame Loop ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tic-Tac-Toe")
clock = pygame.time.Clock()

font_score = pygame.font.SysFont(None, 36)
font_msg = pygame.font.SysFont(None, 28)
font_btn = pygame.font.SysFont(None, 24)

play_again_rect = pygame.Rect(SCREEN_WIDTH // 2 - 75, 55, 150, 35)

running = True
while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Handles both mouse clicks and trackpad taps
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_x, mouse_y = event.pos

            if game_state == "PLAYING":
                if mouse_y >= UI_HEIGHT:
                    col = mouse_x // CELL_SIZE
                    row = (mouse_y - UI_HEIGHT) // CELL_SIZE
                    idx = row * 3 + col

                    if 0 <= idx < 9 and board[idx] == ' ':
                        # Player turn
                        board[idx] = 'X'
                        check_game_end()

                        # Computer turn
                        if game_state == "PLAYING":
                            c_move = computer_move()
                            if c_move != -1:
                                board[c_move] = 'O'
                                check_game_end()

            elif game_state == "GAME_OVER":
                if play_again_rect.collidepoint(mouse_x, mouse_y):
                    reset_game()

    # --- Drawing ---
    screen.fill(WHITE)

    # Top UI Bar
    pygame.draw.rect(screen, (230, 230, 230), (0, 0, SCREEN_WIDTH, UI_HEIGHT))
    pygame.draw.line(screen, GRAY, (0, UI_HEIGHT), (SCREEN_WIDTH, UI_HEIGHT), 2)

    score_surface = font_score.render(f"Score: {score_count}", True, DARK_GRAY)
    screen.blit(score_surface, (25, 35))

    if game_state == "PLAYING":
        hint_surface = font_msg.render("Tap / Click any square", True, (100, 100, 100))
        screen.blit(hint_surface, (SCREEN_WIDTH - hint_surface.get_width() - 25, 40))
    else:
        result_color = GREEN if "Win" in game_result else (RED if "Computer" in game_result else DARK_GRAY)
        res_surface = font_msg.render(game_result, True, result_color)
        screen.blit(res_surface, (SCREEN_WIDTH // 2 - res_surface.get_width() // 2, 18))

        pygame.draw.rect(screen, (173, 216, 230), play_again_rect, border_radius=6)
        pygame.draw.rect(screen, BLUE, play_again_rect, 2, border_radius=6)
        btn_surface = font_btn.render("Play Again", True, BLUE)
        screen.blit(btn_surface, (play_again_rect.centerx - btn_surface.get_width() // 2, 
                                  play_again_rect.centery - btn_surface.get_height() // 2))

    # Grid Lines
    for i in range(1, 3):
        # Vertical
        pygame.draw.line(screen, DARK_GRAY, (i * CELL_SIZE, UI_HEIGHT), (i * CELL_SIZE, SCREEN_HEIGHT), 4)
        # Horizontal
        pygame.draw.line(screen, DARK_GRAY, (0, UI_HEIGHT + i * CELL_SIZE), (SCREEN_WIDTH, UI_HEIGHT + i * CELL_SIZE), 4)

    # Board Marks
    for i in range(9):
        if board[i] == ' ':
            continue

        col = i % 3
        row = i // 3
        center_x = col * CELL_SIZE + CELL_SIZE // 2
        center_y = UI_HEIGHT + row * CELL_SIZE + CELL_SIZE // 2
        pad = 45

        if board[i] == 'X':
            start1 = (center_x - CELL_SIZE // 2 + pad, center_y - CELL_SIZE // 2 + pad)
            end1 = (center_x + CELL_SIZE // 2 - pad, center_y + CELL_SIZE // 2 - pad)
            start2 = (center_x + CELL_SIZE // 2 - pad, center_y - CELL_SIZE // 2 + pad)
            end2 = (center_x - CELL_SIZE // 2 + pad, center_y + CELL_SIZE // 2 - pad)
            pygame.draw.line(screen, BLUE, start1, end1, 8)
            pygame.draw.line(screen, BLUE, start2, end2, 8)

        elif board[i] == 'O':
            radius = CELL_SIZE // 2 - pad
            pygame.draw.circle(screen, RED, (center_x, center_y), radius, 6)

    pygame.display.flip()

pygame.quit()
sys.exit()