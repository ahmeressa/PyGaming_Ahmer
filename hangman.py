import pygame
import sys
import random

# --- Categories & Word Pool ---
WORD_CATEGORIES = {
    "Superheroes": ["superman", "thor", "avenger", "batman", "spiderman"],
    "Animals": ["tiger", "elephant", "cheetah", "kangaroo", "dolphin"],
    "Cartoons": ["doraemon", "pikachu", "shinchan", "popeye"],
    "Nature": ["water", "stream", "forest", "glacier", "mountain"]
}

# --- Display Settings ---
WIDTH, HEIGHT = 800, 620
WHITE = (248, 249, 250)
BLACK = (33, 37, 41)
GRAY = (206, 212, 218)
DARK_GRAY = (108, 117, 125)
BLUE = (13, 110, 253)
RED = (220, 53, 69)
GREEN = (25, 135, 84)
GOLD = (212, 160, 23)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hangman: Interactive Edition")
clock = pygame.time.Clock()

# --- Fonts ---
font_category = pygame.font.SysFont("arial", 22, bold=True)
font_word = pygame.font.SysFont("consolas", 40, bold=True)
font_turns = pygame.font.SysFont("arial", 20)
font_key = pygame.font.SysFont("arial", 20, bold=True)
font_banner = pygame.font.SysFont("arial", 26, bold=True)

# --- Virtual Keyboard Layout ---
ROW1 = "QWERTYUIOP"
ROW2 = "ASDFGHJKL"
ROW3 = "ZXCVBNM"

def create_keyboard():
    keys = []
    btn_w, btn_h, gap = 44, 46, 8
    
    # Row 1 (10 keys)
    start_x = (WIDTH - (10 * btn_w + 9 * gap)) // 2
    for i, ch in enumerate(ROW1):
        rect = pygame.Rect(start_x + i * (btn_w + gap), 430, btn_w, btn_h)
        keys.append({"char": ch.lower(), "rect": rect})
        
    # Row 2 (9 keys)
    start_x = (WIDTH - (9 * btn_w + 8 * gap)) // 2
    for i, ch in enumerate(ROW2):
        rect = pygame.Rect(start_x + i * (btn_w + gap), 484, btn_w, btn_h)
        keys.append({"char": ch.lower(), "rect": rect})
        
    # Row 3 (7 keys)
    start_x = (WIDTH - (7 * btn_w + 6 * gap)) // 2
    for i, ch in enumerate(ROW3):
        rect = pygame.Rect(start_x + i * (btn_w + gap), 538, btn_w, btn_h)
        keys.append({"char": ch.lower(), "rect": rect})
        
    return keys

# --- Game State Variables ---
category = ""
word = ""
guessmade = set()
turns_left = 10
game_over = False
win = False
play_again_rect = pygame.Rect(WIDTH // 2 - 80, 365, 160, 42)
keyboard_keys = create_keyboard()

def pick_new_word():
    global category, word, guessmade, turns_left, game_over, win
    category = random.choice(list(WORD_CATEGORIES.keys()))
    word = random.choice(WORD_CATEGORIES[category]).lower()
    guessmade = set()
    turns_left = 10
    game_over = False
    win = False

    # Reveal 1 to 2 unique clue letters at start
    unique_letters = list(set(word))
    clue_count = 1 if len(unique_letters) <= 4 else 2
    clues = random.sample(unique_letters, clue_count)
    for c in clues:
        guessmade.add(c)

def make_guess(letter):
    global turns_left, game_over, win
    if game_over or letter in guessmade:
        return

    guessmade.add(letter)
    if letter not in word:
        turns_left -= 1
        if turns_left <= 0:
            turns_left = 0
            game_over = True
            win = False
    else:
        # Check if all letters in word are guessed
        if all(c in guessmade for c in word):
            game_over = True
            win = True

def draw_gallows(turns):
    # Base gallows structure
    pygame.draw.line(screen, DARK_GRAY, (60, 380), (220, 380), 6)      # Base
    pygame.draw.line(screen, DARK_GRAY, (120, 380), (120, 80), 6)      # Vertical post
    pygame.draw.line(screen, DARK_GRAY, (120, 80), (260, 80), 6)        # Top beam
    pygame.draw.line(screen, DARK_GRAY, (120, 130), (170, 80), 4)      # Support bracket
    pygame.draw.line(screen, GOLD, (260, 80), (260, 120), 4)           # Rope

    # Progressive stickman based on lost turns (10 down to 0)
    lost = 10 - turns
    hx, hy = 260, 145  # Head center

    if lost >= 1:  # 9 left: Head
        pygame.draw.circle(screen, BLACK, (hx, hy), 22, 3)
    if lost >= 2:  # 8 left: Torso
        pygame.draw.line(screen, BLACK, (hx, hy + 22), (hx, hy + 95), 4)
    if lost >= 3:  # 7 left: Left Arm
        pygame.draw.line(screen, BLACK, (hx, hy + 40), (hx - 35, hy + 75), 4)
    if lost >= 4:  # 6 left: Right Arm
        pygame.draw.line(screen, BLACK, (hx, hy + 40), (hx + 35, hy + 75), 4)
    if lost >= 5:  # 5 left: Left Leg
        pygame.draw.line(screen, BLACK, (hx, hy + 95), (hx - 30, hy + 155), 4)
    if lost >= 6:  # 4 left: Right Leg
        pygame.draw.line(screen, BLACK, (hx, hy + 95), (hx + 30, hy + 155), 4)
    if lost >= 7:  # 3 left: Left Hand/Foot detail
        pygame.draw.circle(screen, BLACK, (hx - 35, hy + 75), 4)
    if lost >= 8:  # 2 left: Right Hand/Foot detail
        pygame.draw.circle(screen, BLACK, (hx + 35, hy + 75), 4)
    if lost >= 9:  # 1 left: Face (Sad eyes)
        pygame.draw.circle(screen, BLACK, (hx - 7, hy - 4), 2)
        pygame.draw.circle(screen, BLACK, (hx + 7, hy - 4), 2)
        pygame.draw.arc(screen, BLACK, (hx - 8, hy + 4, 16, 10), 0, 3.14, 2)
    if lost >= 10: # 0 left: Dead Eyes (X X)
        # Left X
        pygame.draw.line(screen, RED, (hx - 10, hy - 7), (hx - 4, hy - 1), 2)
        pygame.draw.line(screen, RED, (hx - 4, hy - 7), (hx - 10, hy - 1), 2)
        # Right X
        pygame.draw.line(screen, RED, (hx + 4, hy - 7), (hx + 10, hy - 1), 2)
        pygame.draw.line(screen, RED, (hx + 10, hy - 7), (hx + 4, hy - 1), 2)

# Start first game
pick_new_word()

# --- Main Event Loop ---
running = True
while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Physical Keyboard Input
        if event.type == pygame.KEYDOWN:
            if not game_over and event.unicode.isalpha():
                make_guess(event.unicode.lower())
            elif game_over and event.key == pygame.K_RETURN:
                pick_new_word()

        # Touchpad / Mouse Click Input
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos

            if not game_over:
                for key in keyboard_keys:
                    if key["rect"].collidepoint(mx, my):
                        make_guess(key["char"])
                        break
            else:
                if play_again_rect.collidepoint(mx, my):
                    pick_new_word()

    # --- Draw Phase ---
    screen.fill(WHITE)

    # 1. Top Category Bar
    cat_text = font_category.render(f"CATEGORY: {category.upper()}", True, BLUE)
    screen.blit(cat_text, (WIDTH // 2 - cat_text.get_width() // 2, 20))

    turns_color = GREEN if turns_left > 4 else (GOLD if turns_left > 2 else RED)
    turns_text = font_turns.render(f"Attempts left: {turns_left}/10", True, turns_color)
    screen.blit(turns_text, (WIDTH - turns_text.get_width() - 40, 22))

    # 2. Gallows & Stickman
    draw_gallows(turns_left)

    # 3. Mystery Word Spaces
    displayed_word = " ".join([c.upper() if c in guessmade else "_" for c in word])
    word_surface = font_word.render(displayed_word, True, BLACK)
    screen.blit(word_surface, (360, 200))

    # 4. Result Banner / Play Again Button
    if game_over:
        if win:
            msg = font_banner.render("You Rescued Him! You Win!", True, GREEN)
        else:
            msg = font_banner.render(f"Game Over! The word was: {word.upper()}", True, RED)
        
        screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, 320))

        # Play Again button
        pygame.draw.rect(screen, BLUE, play_again_rect, border_radius=8)
        btn_text = font_key.render("Play Again", True, WHITE)
        screen.blit(btn_text, (play_again_rect.centerx - btn_text.get_width() // 2,
                               play_again_rect.centery - btn_text.get_height() // 2))

    # 5. Virtual Keyboard
    for key in keyboard_keys:
        ch = key["char"]
        rect = key["rect"]
        is_used = ch in guessmade

        if is_used:
            bg_color = (222, 226, 230)
            text_color = DARK_GRAY
        else:
            bg_color = WHITE
            text_color = BLACK

        pygame.draw.rect(screen, bg_color, rect, border_radius=6)
        pygame.draw.rect(screen, GRAY, rect, 2, border_radius=6)

        char_surf = font_key.render(ch.upper(), True, text_color)
        screen.blit(char_surf, (rect.centerx - char_surf.get_width() // 2, 
                                rect.centery - char_surf.get_height() // 2))

    pygame.display.flip()

pygame.quit()
sys.exit()
