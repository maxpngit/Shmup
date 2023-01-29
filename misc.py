from os import path

import pygame

# определение путей для изображений, анимаций и звуков
img_dir = path.join(path.dirname(__file__), 'images')  # Все картинки "живут" в images
snd_dir = path.join(path.dirname(__file__), 'sounds')  # Все звуки "живут" в sounds
anim_dir = path.join(path.dirname(__file__), 'anim')  # Все анимации "живут" в anim

# константы
WIDTH = 480  # окно 480 х 640
HEIGHT = 600
FPS = 60  # с частотой кадров = 60 Гц
Y = -600  # для прокрутки фона (эффект полёта)
VEL = 5  # скорость полёта

# Задаем цвета
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (210, 225, 230)
WHITE = (160, 160, 160)  # почти белый
RED = (255, 0, 0)

# Стартоовая инициализация переменных
fire = False  # ведётся ли огонь
score = 0  # для счёта очков
shots = 0  # для счёта выстрелов
success = 0  # счётчик попаданий
ammo = 200  # стартовый запас снарядов
gameplay = 1  # Если игра запущена впервые
boss_appear = False  # изначально босс не появляется
once = False  # Если босс появился, то это происходит один раз
level_up = 0  # количество очков, после которых появится босс
boss_pass = 'Не пройден!'  # побеждён ли босс (изначально - НЕТ)

# Создаем игру и окно
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Заголовок и иконка окна игры
pygame.display.set_caption('Космический странник')
pygame.display.set_icon(pygame.image.load('images/icon.ico'))

# Загрузка всей игровой графики
background = pygame.image.load(path.join(img_dir, 'starfield.jpg')).convert()
background_rect = background.get_rect()
scoreboard = pygame.image.load(path.join(img_dir, 'scoreboard.png')).convert()
scoreboard.set_colorkey(BLACK)

# Информационные экраны
# 1. ну держись!!!
keepout = pygame.image.load(path.join(img_dir, 'keepout.png')).convert()
# 2. ты проиграл!!!
youloose = pygame.image.load(path.join(img_dir, 'youloose.png')).convert()
# 3. победа!!!
victory = pygame.image.load(path.join(img_dir, 'victory.png')).convert()

# загрузка изображений игрока и босса
player_img = pygame.image.load(path.join(img_dir, 'turret.png')).convert()
boss_img = pygame.image.load(path.join(img_dir, 'enemy.png')).convert()
boss_img.set_colorkey(BLACK)

# дополнительное информирование о состоянии брони и числе жизней
heroes = []
ava_list = ['ava1.png', 'ava2.png', 'ava3.png', 'ava4.png']
for img in ava_list:
    heroes.append(pygame.image.load(path.join(anim_dir, img)).convert())
# иконки жизней игрока
player_mini_img = pygame.transform.scale(player_img, (27, 30))
player_mini_img.set_colorkey(BLACK)

# вращающиеся астероиды, загружаем несколько картинок
asteroid_images = []
asteroid_list = ['asteroid1.png', 'asteroid2.png', 'asteroid3.png']  # достаточно 3-х размеров
# но можно добавить и покрупнее: 'asteroid4.png', 'asteroid5.png', 'asteroid6.png'
# картинки в каталоге anim присутствуют

# помещаем картинки в список
for img in asteroid_list:
    asteroid_images.append(pygame.image.load(path.join(anim_dir, img)).convert())

# подгрузка картинки пуль (снарядов)
bullet_img = pygame.image.load(path.join(img_dir, 'bullet.png')).convert()
bullet_img = pygame.transform.scale(bullet_img, (6, 30))

# подгрузка картинки улучшений брони
powerup_images = {'shield': pygame.image.load(path.join(img_dir, 'spaner.png')).convert()}
powerup_images['shield'].set_colorkey(BLACK)

# подгрузка падающего гаечного ключа - картинки удвоения стрельбы
powerup_images['gun'] = pygame.image.load(path.join(img_dir, 'twice.png')).convert()
powerup_images['gun'].set_colorkey(BLACK)

# подгрузка падающего ящика AMMO - картинки пополнения боеприпасов
powerup_images['ammo'] = pygame.image.load(path.join(img_dir, 'ammo.png')).convert()
powerup_images['ammo'].set_colorkey(BLACK)

expl_sounds = []
for snd in ['expl1.wav', 'expl2.wav']:
    expl_sounds.append(pygame.mixer.Sound(path.join(snd_dir, snd)))

# Загрузка изображений для анимированного взрыва
# lg - large - для астероида
# sm - small - для игрока (место удара)
explosion_anim = {'lg': [], 'sm': [], 'player': []}

# анимация взрыва при гибели игрока или босса
for i in range(9):
    filename = 'expl{}.png'.format(i + 1)
    img = pygame.image.load(path.join(anim_dir, filename)).convert()
    img.set_colorkey(BLACK)
    img_lg = pygame.transform.scale(img, (75, 75))
    explosion_anim['lg'].append(img_lg)
    img_sm = pygame.transform.scale(img, (32, 32))
    explosion_anim['sm'].append(img_sm)
    # переназначаем filename для инициализации анимации гибели игрока
    filename = 'plexplos{}.png'.format(i + 1)
    img = pygame.image.load(path.join(anim_dir, filename)).convert()
    img.set_colorkey(BLACK)
    explosion_anim['player'].append(img)

# Фоновая музыка (до появления босса)
pygame.mixer.music.load(path.join(snd_dir, 'bgmusic.ogg'))
pygame.mixer.music.set_volume(0.4)

# Загрузка мелодий выстрелов, взрывов, осечек, улучшений, столкновений...
shoot_sound = pygame.mixer.Sound(path.join(snd_dir, 'pew.wav'))  # выстрел
reload = pygame.mixer.Sound(path.join(snd_dir, 'reload.ogg'))  # перезарядка
misfire = pygame.mixer.Sound(path.join(snd_dir, 'misfire.ogg'))  # осечка (нет снарядов)
crash_sound = pygame.mixer.Sound(path.join(snd_dir, 'crash.wav'))  # враг ударил туррель
shield_sound = pygame.mixer.Sound(path.join(snd_dir, 'stamina.ogg'))  # улучшена броня (здоровье)
power_sound = pygame.mixer.Sound(path.join(snd_dir, 'bullet.ogg'))  # получено временное усиления огня
tadam = pygame.mixer.Sound(path.join(snd_dir, 'tadam.ogg'))  # появился босс
died_sound = pygame.mixer.Sound(path.join(snd_dir, 'died.ogg'))  # странник погиб

boss = None  # пока босса нет
font_name = pygame.font.match_font('arial')  # задаём шрифт


# полоска жизни игрока в левом верхнем углу
def draw_shield_bar(surf, x, y, pct, status):
    if pct < 0:
        pct = 0
    bar_length = 100
    bar_height = 10 * status
    fill = (pct / 100) * bar_length
    outline_rect = pygame.Rect(x, y, bar_length, bar_height)
    fill_rect = pygame.Rect(x, y, fill, bar_height)
    if status == 1:
        pygame.draw.rect(surf, GREEN, fill_rect)
    else:
        pygame.draw.rect(surf, RED, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)


# распечатка полученных очков (вывод текстом)
def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)
