# Jogo com som seguro – Thiago
import pgzrun
import random
from pygame import Rect

WIDTH = 640
HEIGHT = 480
TITLE = "Simple Roguelike"

MENU = 'menu'
PLAYING = 'playing'
NEXT_LEVEL = 'next_level'
GAME_OVER = 'gameover'
INSTRUCTIONS = 'instructions'

state = MENU
sound_on = True

bg_colors = ["darkgreen", "darkblue", "darkred", "darkorchid", "black"]
bg_index = 0

start_btn = Rect((220, 150), (200, 40))
instr_btn = Rect((220, 200), (200, 40))
sound_btn = Rect((220, 250), (200, 40))
exit_btn  = Rect((220, 390), (200, 40))
back_btn = Rect((WIDTH - 100, 10), (90, 30))

class Hero(Actor):
    def __init__(self):
        super().__init__('hero_idle', (100, 100))
        self.images = ['hero_idle', 'hero_walk1']
        self.speed = 3
        self.frame = 0
        self.counter = 0

    def move(self):
        if keyboard.left: self.x -= self.speed
        if keyboard.right: self.x += self.speed
        if keyboard.up: self.y -= self.speed
        if keyboard.down: self.y += self.speed

        if keyboard.left or keyboard.right or keyboard.up or keyboard.down:
            self.counter += 1
            if self.counter % 10 == 0:
                self.frame = (self.frame + 1) % len(self.images)
                self.image = self.images[self.frame]
        else:
            self.image = self.images[0]

class Enemy(Actor):
    def __init__(self, speed):
        pos = (random.randint(50, WIDTH - 50), random.randint(50, HEIGHT - 50))
        super().__init__('enemy_idle', pos)
        self.images = ['enemy_idle', 'enemy_walk1']
        self.frame = 0
        self.counter = 0
        self.direction = random.choice([-1, 1])
        self.speed = speed

    def update(self):
        self.x += self.direction * self.speed
        self.counter += 1
        if self.counter % 20 == 0:
            self.frame = (self.frame + 1) % len(self.images)
            self.image = self.images[self.frame]
        if self.left < 0 or self.right > WIDTH:
            self.direction *= -1

class Coin(Actor):
    def __init__(self):
        super().__init__('coin', (random.randint(50, WIDTH - 50), random.randint(50, HEIGHT - 50)))

    def respawn(self):
        self.pos = (random.randint(50, WIDTH - 50), random.randint(50, HEIGHT - 50))

hero = Hero()
enemy_speed = 2
enemies = [Enemy(enemy_speed) for _ in range(4)]
coins = [Coin() for _ in range(3)]
score = 0
lives = 3

def draw():
    screen.fill(bg_colors[bg_index])
    if state == MENU:
        draw_menu()
    elif state == INSTRUCTIONS:
        draw_instructions()
    elif state in (PLAYING, NEXT_LEVEL):
        draw_game()
    elif state == GAME_OVER:
        draw_game_over()

def draw_menu():
    screen.draw.text(TITLE, center=(WIDTH//2, 60), fontsize=50, color="white")
    screen.draw.text("Iniciar", center=start_btn.center, fontsize=30, color="yellow")
    screen.draw.text("Instrucoes", center=instr_btn.center, fontsize=30, color="yellow")
    sound_status = "Som: ON" if sound_on else "Som: OFF"
    screen.draw.text(sound_status, center=sound_btn.center, fontsize=30, color="yellow")
    screen.draw.text("Sair", center=exit_btn.center, fontsize=30, color="yellow")

def draw_instructions():
    screen.draw.text("Instrucoes", center=(WIDTH//2, 60), fontsize=50, color="white")
    lines = [
        "- Use as setas para mover o heroi.",
        "- Colete moedas para ganhar pontos.",
        "- Evite os inimigos; colidir reduz suas vidas.",
        "- A cada 10 moedas, voce avança de nivel.",
        "- Você começa com 3 vidas.",
        "- Clique em Som ON/OFF para alternar o som.",
    ]
    y = 140
    for line in lines:
        screen.draw.text(line, center=(WIDTH//2, y), fontsize=28, color="yellow")
        y += 35
    screen.draw.text("Voltar", center=exit_btn.center, fontsize=30, color="yellow")

def draw_game():
    hero.draw()
    for enemy in enemies: enemy.draw()
    for coin in coins: coin.draw()
    screen.draw.text(f"Score: {score}", topleft=(10, 10), fontsize=20, color="white")
    screen.draw.text(f"Lives: {lives}", topleft=(10, 50), fontsize=20, color="white")
    screen.draw.rect(back_btn, "yellow")
    screen.draw.text("Voltar", center=back_btn.center, fontsize=24, color="black")
    if state == NEXT_LEVEL:
        screen.draw.text("Next Level!", center=(WIDTH//2, HEIGHT//2), fontsize=50, color="green")

def draw_game_over():
    screen.draw.text("Game Over", center=(WIDTH//2, HEIGHT//2 - 30), fontsize=50, color="red")
    screen.draw.text(f"Score: {score}", center=(WIDTH//2, HEIGHT//2 + 20), fontsize=30, color="white")

def update():
    global state, score, lives, enemies, bg_index, enemy_speed
    if state == PLAYING:
        hero.move()
        for enemy in enemies:
            enemy.update()
            if hero.colliderect(enemy):
                lives -= 1
                try:
                    if sound_on:
                        sounds.hit.play()
                except:
                    pass
                hero.pos = (100, 100)
                if lives <= 0:
                    state = GAME_OVER
        for coin in coins:
            if hero.colliderect(coin):
                score += 1
                coin.respawn()
                try:
                    if sound_on:
                        sounds.coin.play()
                except:
                    pass
                if score % 10 == 0:
                    state = NEXT_LEVEL
                    clock.schedule_unique(start_next_level, 2.0)

def start_next_level():
    global state, enemies, bg_index, enemy_speed
    try:
        if sound_on:
            sounds.levelup.play()
    except:
        pass
    hero.pos = (100, 100)
    if bg_index < len(bg_colors) - 1:
        bg_index += 1
    enemy_speed += 0.5
    enemies[:] = [Enemy(enemy_speed) for _ in range(4)]
    for coin in coins:
        coin.respawn()
    state = PLAYING

def on_mouse_down(pos):
    global state, sound_on
    if state == MENU:
        if start_btn.collidepoint(pos):
            state = PLAYING
        elif instr_btn.collidepoint(pos):
            state = INSTRUCTIONS
        elif sound_btn.collidepoint(pos):
            sound_on = not sound_on
        elif exit_btn.collidepoint(pos):
            quit()
    elif state == INSTRUCTIONS:
        if exit_btn.collidepoint(pos):
            state = MENU
    elif state in (PLAYING, NEXT_LEVEL):
        if back_btn.collidepoint(pos):
            state = MENU

pgzrun.go()
