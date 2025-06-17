# -*- coding: utf-8 -*-
import math
import random
from pygame import Rect
from pgzero.actor import Actor
from pgzero.clock import clock
from pgzero import music
from pgzero.loaders import sounds
from pgzero.keyboard import keys
import pgzrun

# Janela e fisica
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
GRAVITY = 0.5
MAX_FALL_SPEED = 12
ACCELERATION = 0.5
FRICTION = 0.3
MAX_RUN_SPEED = 4
JUMP_SPEED = -16
COYOTE_TIME = 0.1
JUMP_BUFFER_TIME = 0.1
GROUND_LEVEL_Y = SCREEN_HEIGHT - 40
INTERACT_IDLE_THRESHOLD = 5.0

LEVEL_WIDTH = 4000
LEVEL_PLATFORMS = [
    Rect((0, GROUND_LEVEL_Y), (LEVEL_WIDTH, 40)),
    Rect((300, GROUND_LEVEL_Y - 80), (200, 20)),
    Rect((700, GROUND_LEVEL_Y - 100), (200, 20)),
    Rect((1100, GROUND_LEVEL_Y - 80), (200, 20)),
    Rect((1500, GROUND_LEVEL_Y - 100), (200, 20)),
    Rect((1900, GROUND_LEVEL_Y - 80), (200, 20)),
    Rect((2300, GROUND_LEVEL_Y - 100), (200, 20)),
    Rect((2700, GROUND_LEVEL_Y - 120), (200, 20)),
    Rect((3100, GROUND_LEVEL_Y - 90), (200, 20)),
    Rect((3500, GROUND_LEVEL_Y - 110), (200, 20)),
]
GOAL_AREA = Rect((LEVEL_WIDTH - 100, GROUND_LEVEL_Y - 100), (50, 100))

current_game_state = 'menu'
is_sound_enabled = True
player = None
enemy_list = []
health_pickups = []
game_end_message = None
frame_count = 0
mouse_position = (0, 0)

button_play = Rect((SCREEN_WIDTH // 2 - 100, 200), (200, 50))
button_toggle_sound = Rect((SCREEN_WIDTH // 2 - 100, 300), (200, 50))
button_exit_game = Rect((SCREEN_WIDTH // 2 - 100, 400), (200, 50))

MAX_LIVES = 3
INVINCIBILITY_DURATION = 1.5


class GameCamera:
    def __init__(self):
        self.offset_x = 0

    def update(self, target_x):
        desired = target_x - SCREEN_WIDTH // 2
        self.offset_x = max(0, min(desired, LEVEL_WIDTH - SCREEN_WIDTH))


game_camera = GameCamera()


def on_mouse_move(pos):
    global mouse_position
    mouse_position = pos


class Player:
    def __init__(self):
        self.sprite = Actor('character_robot_idle', pos=(100, GROUND_LEVEL_Y - 32))
        self.velocity_x = 0
        self.velocity_y = 0
        self.is_on_ground = False
        self.coyote_time_remaining = 0
        self.jump_buffer_remaining = 0
        self.invincibility_timer = 0
        self.idle_image = 'character_robot_idle'
        self.walk_images = [f'character_robot_walk{i}' for i in range(8)]
        self.jump_image = 'character_robot_jump'
        self.fall_image = 'character_robot_fall'
        self.animation_frame = 0
        self.lives = MAX_LIVES
        w, h = self.sprite.width * 0.6, self.sprite.height * 0.8
        self.collision_box = Rect(0, 0, w, h)
        self.idle_timer = 0.0
        self.interact_image = 'character_robot_interact'

    def update(self):
        delta_time = 1 / 60
        self.coyote_time_remaining = max(0, self.coyote_time_remaining - delta_time)
        self.jump_buffer_remaining = max(0, self.jump_buffer_remaining - delta_time)
        self.invincibility_timer = max(0, self.invincibility_timer - delta_time)

        if keyboard.up:
            self.jump_buffer_remaining = JUMP_BUFFER_TIME
        if (self.jump_buffer_remaining > 0) and (self.is_on_ground or self.coyote_time_remaining > 0):
            self.velocity_y = JUMP_SPEED
            self.is_on_ground = False
            self.coyote_time_remaining = 0
            self.jump_buffer_remaining = 0

        if keyboard.left:
            self.velocity_x = max(self.velocity_x - ACCELERATION, -MAX_RUN_SPEED)
        elif keyboard.right:
            self.velocity_x = min(self.velocity_x + ACCELERATION, MAX_RUN_SPEED)
        else:
            if abs(self.velocity_x) < FRICTION:
                self.velocity_x = 0
            else:
                self.velocity_x -= math.copysign(FRICTION, self.velocity_x)

        self.velocity_y = min(self.velocity_y + GRAVITY, MAX_FALL_SPEED)

        self.sprite.x += self.velocity_x
        for platform in LEVEL_PLATFORMS:
            if self.sprite.colliderect(platform):
                if self.velocity_x > 0:
                    self.sprite.right = platform.left
                elif self.velocity_x < 0:
                    self.sprite.left = platform.right

        self.sprite.y += self.velocity_y
        self.is_on_ground = False
        for platform in LEVEL_PLATFORMS:
            if self.sprite.colliderect(platform):
                if self.velocity_y > 0:
                    self.sprite.bottom = platform.top
                    self.velocity_y = 0
                    self.is_on_ground = True
                    self.coyote_time_remaining = COYOTE_TIME
                elif self.velocity_y < 0:
                    self.sprite.top = platform.bottom
                    self.velocity_y = 0

        self.collision_box.centerx = int(self.sprite.x)
        self.collision_box.centery = int(self.sprite.y + 8)

        moving_horiz = abs(self.velocity_x) > 0.1
        if not moving_horiz and self.is_on_ground:
            self.idle_timer += delta_time
        else:
            self.idle_timer = 0.0

        if self.idle_timer >= INTERACT_IDLE_THRESHOLD:
            self.sprite.image = self.interact_image
            return

        if not self.is_on_ground:
            self.sprite.image = self.jump_image if self.velocity_y < 0 else self.fall_image

        elif abs(self.velocity_x) > 0.1:
            self.animation_frame = (self.animation_frame + 1) % (len(self.walk_images) * 6)
            self.sprite.image = self.walk_images[self.animation_frame // 6]

        else:
            self.sprite.image = self.idle_image

    def draw(self):
        x = self.sprite.x - game_camera.offset_x
        y = self.sprite.y
        screen.blit(self.sprite.image, (x - self.sprite.width / 2, y - self.sprite.height / 2))


class Zombie:
    def __init__(self, x):
        y = GROUND_LEVEL_Y - 32
        self.sprite = Actor('character_zombie_idle', pos=(x, y))
        self.velocity_x = random.choice([-2, 2])
        self.idle_images = ['character_zombie_idle']
        self.walk_images = [f'character_zombie_walk{i}' for i in range(8)]
        self.animation_frame = 0
        w, h = self.sprite.width * 0.6, self.sprite.height * 0.8
        self.collision_box = Rect(0, 0, w, h)

    def update(self):
        self.sprite.x += self.velocity_x
        if self.sprite.left < 0 or self.sprite.right > LEVEL_WIDTH:
            self.velocity_x *= -1

        self.collision_box.centerx = int(self.sprite.x)
        self.collision_box.centery = int(self.sprite.y + 8)

        images = self.walk_images if abs(self.velocity_x) > 0 else self.idle_images
        self.animation_frame = (self.animation_frame + 1) % (len(images) * 10)
        self.sprite.image = images[self.animation_frame // 10]

    def draw(self):
        x = self.sprite.x - game_camera.offset_x
        y = self.sprite.y
        screen.blit(self.sprite.image, (x - self.sprite.width / 2, y - self.sprite.height / 2))


class HealthPickup:
    def __init__(self, x, y):
        self.sprite = Actor('heart', pos=(x, y))
        w, h = self.sprite.width, self.sprite.height
        self.collision_box = Rect((x - w / 2, y - h / 2), (w, h))

    def draw(self):
        x = self.sprite.x - game_camera.offset_x
        y = self.sprite.y
        screen.blit(self.sprite.image, (x - self.sprite.width / 2, y - self.sprite.height / 2))


def init_game():
    global player, enemy_list, health_pickups, game_end_message, frame_count
    player = Player()
    enemy_list[:] = [Zombie(x) for x in range(400, LEVEL_WIDTH, 600)]
    health_pickups[:] = [
        HealthPickup(600, GROUND_LEVEL_Y - 60),
        HealthPickup(1300, GROUND_LEVEL_Y - 150),
        HealthPickup(2200, GROUND_LEVEL_Y - 90),
    ]
    game_camera.update(player.sprite.x)
    game_end_message = None
    frame_count = 0


def draw_menu():
    for i in range(0, SCREEN_HEIGHT, 4):
        c = int(30 + i * (100 / SCREEN_HEIGHT))
        screen.draw.line((0, i), (SCREEN_WIDTH, i), (c, 30, 60))
    title = "Guerra Titanica: Robos vs Zumbis"
    screen.draw.text(title, center=(SCREEN_WIDTH // 2 + 3, 103), fontsize=64, color="black")
    screen.draw.text(title, center=(SCREEN_WIDTH // 2, 100), fontsize=64, color="red")

    def draw_button(rect, label):
        hover = rect.collidepoint(mouse_position)
        fill = "red" if hover else "black"
        screen.draw.filled_rect(rect, fill)
        screen.draw.rect(rect, "white")
        screen.draw.text(label, center=rect.center, fontsize=20,
                         color="black" if hover else "white")

    draw_button(button_play, "INICIAR")
    draw_button(button_toggle_sound, f"SOM: {'LIGADO' if is_sound_enabled else 'DESLIGADO'}")
    draw_button(button_exit_game, "SAIR")


def draw():
    screen.clear()
    if current_game_state == 'menu':
        draw_menu()
    else:
        game_camera.update(player.sprite.x)
        screen.draw.filled_rect(Rect((0, 0), (SCREEN_WIDTH, SCREEN_HEIGHT)), 'skyblue')
        for platform in LEVEL_PLATFORMS:
            r = Rect((platform.x - game_camera.offset_x, platform.y), (platform.width, platform.height))
            screen.draw.filled_rect(r, 'saddlebrown')
        pole = Rect((GOAL_AREA.x - game_camera.offset_x, GOAL_AREA.y), (10, GOAL_AREA.height))
        screen.draw.filled_rect(pole, 'saddlebrown')
        flag_color = 'lightgreen' if not enemy_list else 'darkred'
        flag = Rect((GOAL_AREA.x + 10 - game_camera.offset_x, GOAL_AREA.y), (30, 20))
        screen.draw.filled_rect(flag, flag_color)
        for pickup in health_pickups:
            pickup.draw()
        player.draw()
        for zombie in enemy_list:
            zombie.draw()

        hud = Rect((0, 0), (SCREEN_WIDTH, 30))
        screen.draw.filled_rect(hud, 'dimgray')
        for i in range(player.lives):
            screen.blit('heart', (10 + i * 34, 2))
        screen.draw.text(f"Inimigos: {len(enemy_list)}", (200, 4), fontsize=24, color='white')
        secs = frame_count // 60
        mm, ss = divmod(secs, 60)
        screen.draw.text(f"Tempo: {mm:02d}:{ss:02d}", (350, 4), fontsize=24, color='white')
        if game_end_message:
            screen.draw.text(game_end_message, center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2),
                             fontsize=60, color='white')


def update():
    global current_game_state, game_end_message, frame_count
    if current_game_state == 'menu':
        return
    frame_count += 1
    prev_bottom = player.collision_box.bottom
    player.update()

    for pickup in health_pickups[:]:
        if player.collision_box.colliderect(pickup.collision_box):
            if player.lives < MAX_LIVES:
                player.lives += 1
                sounds.powerup.play()
            health_pickups.remove(pickup)

    for zombie in enemy_list[:]:
        zombie.update()

        if (player.velocity_y > 0 and prev_bottom <= zombie.collision_box.top
                and player.collision_box.colliderect(zombie.collision_box)):
            enemy_list.remove(zombie)
            player.velocity_y = JUMP_SPEED / 2
            sounds.jump.play()
            continue

        if (player.collision_box.colliderect(zombie.collision_box)
                and player.invincibility_timer <= 0):
            player.lives -= 1
            player.invincibility_timer = INVINCIBILITY_DURATION
            sounds.hit.play()
            if player.lives <= 0:
                game_end_message = "Fim de jogo"
                clock.schedule_unique(reset_to_menu, 1.5)
                return

    if not enemy_list and player.collision_box.colliderect(GOAL_AREA):
        game_end_message = "Voce venceu!"
        music.stop()
        sounds.win.play()
        clock.schedule_unique(reset_to_menu, 1.5)


def on_mouse_down(pos):
    global current_game_state, is_sound_enabled
    if current_game_state == 'menu':
        if button_play.collidepoint(pos):
            init_game()
            current_game_state = 'game'
            if is_sound_enabled:
                music.play('bg_music')
        elif button_toggle_sound.collidepoint(pos):
            is_sound_enabled = not is_sound_enabled
            if is_sound_enabled:
                music.play('bg_music')
            else:
                music.stop()
        elif button_exit_game.collidepoint(pos):
            exit()


def reset_to_menu():
    global current_game_state
    music.stop()
    current_game_state = 'menu'


init_game()
music.set_volume(0.5)
pgzrun.go()
