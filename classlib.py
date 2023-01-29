# Библиотека классов,
# а также группы спрайтов

import random

import pygame

# глобальные константы
WIDTH = 480
HEIGHT = 600
FPS = 60
# время жизни двойной плотности огня
POWERUP_TIME = 5000  # 5 сек

# Задаем цвета для фона
BLACK = (0, 0, 0)

# показываем спрайты и не забываем что
# каждый спрайт добавляется в all_sprites
all_sprites = pygame.sprite.Group()
bullets = pygame.sprite.Group()  # пули
spits = pygame.sprite.Group()  # пули босса
asteroids = pygame.sprite.Group()  # враги
powerups = pygame.sprite.Group()  # возможные улучшения брони


# Игрок (турель) и его поведение
class Player(pygame.sprite.Sprite):
    def __init__(self, img, snd, ammo, shots):
        pygame.sprite.Sprite.__init__(self)
        self.sound = snd
        self.ammo = ammo
        self.shots = shots
        self.image = pygame.transform.scale(img, (50, 65))
        self.image.set_colorkey(BLACK)
        self.bullet_img = None
        self.rect = self.image.get_rect()
        self.radius = 20
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10
        self.speedx = 0
        self.shield = 100  # броня (здоровье) игрока
        self.shoot_delay = 250  # задержка при нажатой клавише SPACE
        self.last_shot = pygame.time.get_ticks()
        self.lives = 3
        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()
        self.power = 1
        self.power_time = pygame.time.get_ticks()

    def update(self):
        # таймаут для улучшения оружия
        if self.power >= 2 and pygame.time.get_ticks() - self.power_time > POWERUP_TIME:
            self.power -= 1
            self.power_time = pygame.time.get_ticks()

        # показать, если скрыто
        if self.hidden and pygame.time.get_ticks() - self.hide_timer > 1000:
            self.hidden = False
            self.rect.centerx = WIDTH / 2
            self.rect.bottom = HEIGHT - 10

        self.speedx = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            self.speedx = -8
        if keystate[pygame.K_RIGHT]:
            self.speedx = 8
        if keystate[pygame.K_SPACE] and self.ammo > 0:
            self.shoot(self.bullet_img)
        self.rect.x += self.speedx
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

    def powerup(self):
        self.power += 1
        self.power_time = pygame.time.get_ticks()

    def shoot(self, img):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            # Пуля создаётся только при нажатии SPACE (пробел)
            self.bullet_img = img
            if self.power == 1:
                bullet = Bullet(img, self.rect.centerx, self.rect.centery, 1)
                all_sprites.add(bullet)
                bullets.add(bullet)
                self.sound.play()
                self.ammo -= 1
                self.shots += 1
            if self.power >= 2:
                bullet1 = Bullet(img, self.rect.left + 12, self.rect.centery, 1)
                bullet2 = Bullet(img, self.rect.right - 12, self.rect.centery, 1)
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                bullets.add(bullet1)
                bullets.add(bullet2)
                self.sound.play()
                self.ammo -= 2
                self.shots += 2

        if self.ammo < 0:
            self.ammo = 0

        return self.shots

    def hide(self):
        # временно скрыть игрока
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (WIDTH / 2, HEIGHT + 200)


# Пассивный противник (астероид) и его поведение
class Passive(pygame.sprite.Sprite):
    def __init__(self, img):
        pygame.sprite.Sprite.__init__(self)
        # self.image = pygame.Surface((30, 40))
        # self.image.fill(RED)
        # выбираем случайный образ картинки
        self.image_orig = random.choice(img)
        self.image_orig.set_colorkey(BLACK)
        # создаём копию оригинальной картинки
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * .85 / 2)
        # Временно, для отладки столкновений
        # pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = random.randrange(1, 8)
        self.speedx = random.randrange(-3, 3)
        self.rot = 0  # для угла поворота
        self.rot_speed = random.randrange(-8, 8)
        self.last_update = pygame.time.get_ticks()

    def rotate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 50:
            self.last_update = now
            self.rot = (self.rot + self.rot_speed) % 360
            new_image = pygame.transform.rotate(self.image_orig, self.rot)
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center

    def update(self):
        self.rotate()  # вращаем при обновлении
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT + 10 or self.rect.left < -25 or self.rect.right > WIDTH + 20:
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(1, 8)
        # "убить", если он заходит за пределы экрана
        if self.rect.y > 600 or self.rect.x < 0 or self.rect.x > 480:
            self.kill()


# Активный противник (босс) и его поведение
class Boss(pygame.sprite.Sprite):
    def __init__(self, img):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * .85 / 2)
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = 50
        self.shield = 100
        # по Y не перемещается
        self.speedx = random.randrange(-3, 3)
        self.last_update = pygame.time.get_ticks()

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 300:
            self.last_update = now
            self.speedx = random.randrange(-3, 3)
            spit = Bullet(self.image, self.rect.centerx, self.rect.bottom, 2)
            all_sprites.add(spit)
            spits.add(spit)

    def update(self):
        self.shoot()  # стреляем при обновлении
        self.rect.x += self.speedx
        if self.rect.left < -25 or self.rect.right > WIDTH + 25:
            self.rect.x = random.randrange(WIDTH - self.rect.width)


# снаряд и его поведение
class Bullet(pygame.sprite.Sprite):
    def __init__(self, img, x, y, status):
        # если статус = 1, то стреляет игрок (снизу вверх)
        # если статус = 2, то стреляет босс (сверху вниз)
        pygame.sprite.Sprite.__init__(self)
        # self.image = pygame.Surface((10, 20))
        # self.image.fill(YELLOW)
        self.status = status
        if self.status == 1:
            self.image = img
        else:
            self.image = pygame.transform.scale(img, (15, 20))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * .85 / 2)
        self.rect.centerx = x
        if self.status == 1:
            self.rect.bottom = y
            self.speedy = -10
        else:
            self.rect.top = y
            self.speedy = 5

    def update(self):
        if self.status == 1:
            self.rect.y += self.speedy
            # "убить", если он заходит за верхнюю часть экрана
            if self.rect.bottom < 0:
                self.kill()
        else:
            self.rect.y += self.speedy
            # "убить", если он заходит за верхнюю часть экрана
            if self.rect.top > HEIGHT:
                self.kill()


class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size, anim_img):
        pygame.sprite.Sprite.__init__(self)
        self.animated = anim_img
        self.size = size
        self.image = anim_img[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(self.animated[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = self.animated[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center


# улучшение брони (здоровья) игрока
class Powerup(pygame.sprite.Sprite):
    def __init__(self, center, img):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(['shield', 'gun', 'ammo'])
        self.image = img[self.type]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = 2

    def update(self):
        self.rect.y += self.speedy
        # "убить", когда он скроется за нижней частью экрана
        if self.rect.top > HEIGHT:
            self.kill()
