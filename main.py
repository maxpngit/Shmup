import random
import sys

from classlib import Player, Passive, Explosion, Powerup, Boss  # Добавляем нужные классы из библиотек
from classlib import bullets, all_sprites, asteroids, spits, powerups  # а также нужные группы спрайтов
from misc import *  # ну и стартовую инициализацию, плюс: вспомогательные константы и переменные
from statistic import GameResult  # и класс для сохранения результатов

clock = pygame.time.Clock()  # Тайминг для FPS игры

# создаём игрока и добавляем в группу спрайтов
player = Player(player_img, shoot_sound, ammo, shots)
all_sprites.add(player)

# включаем фоновую музыку
pygame.mixer.music.play(loops=-1)


# генерация астероидов
def newasteroid(num):
    for _ in range(num):
        en = Passive(asteroid_images)
        all_sprites.add(en)
        asteroids.add(en)


# прорисовка жизней игрока в правом верхнем углу
def draw_lives(surf, x, y, lives, ship_tmb=None):
    surf.set_alpha(200)
    pygame.draw.rect(surf, YELLOW, (x - lives * 2, y, lives * (36 - lives), 30))
    for ship in range(lives):
        img_rect = ship_tmb.get_rect()
        img_rect.x = x + 30 * ship
        img_rect.y = y
        surf.blit(ship_tmb, img_rect)


# заставка
def start_screen(first_time):
    if first_time == 1:
        # Загрузка фона для первого запуска игры
        bgnd = pygame.image.load(path.join(img_dir, 'stars_start.png')).convert()
        bgnd_rect = bgnd.get_rect()
        screen.blit(bgnd, bgnd_rect)
    else:
        # Фон для рестарта
        bgnd = pygame.image.load(path.join(img_dir, 'stars_restart.png')).convert()
        bgnd_rect = bgnd.get_rect()
        screen.blit(bgnd, bgnd_rect)
        db = GameResult()  # Подключились к DB
        data = db.get_results()
        # прошлые заслуги
        draw_text(screen, data[5], 26, 350, 70)  # заголовок - дата
        draw_text(screen, 'Очки: ' + str(data[1]), 22, 340, 120)
        draw_text(screen, 'Выстрелы: ' + str(data[2]), 22, 340, 140)
        accur = 100 * (data[3] / data[2])
        if accur > 100:
            accur -= 100
        draw_text(screen, f'Точность: {accur:.2f}%', 22, 340, 160)
        draw_text(screen, 'Босс: ' + str(data[4]), 22, 340, 180)
        # текущие результаты
        draw_text(screen, 'Очки: ' + str(score), 22, 100, 120)
        draw_text(screen, 'Выстрелы: ' + str(shots), 22, 100, 140)
        accur = 100 * (success / shots)
        if accur > 100:
            accur -= 100
        draw_text(screen, f'Точность: {accur:.2f}%', 22, 100, 160)
        draw_text(screen, 'Босс: ' + boss_pass, 22, 100, 180)
        db.set_results(score, shots, success, boss_pass)
        db.disconnect()  # отключились от DB
    # Это можно отразить и на картинке
    draw_text(screen, 'КОСМИЧЕСКИЙ СТРАННИК', 34, WIDTH / 2, HEIGHT - 380)
    screen.blit(powerup_images['shield'], (119, 260))
    screen.blit(powerup_images['gun'], (105, 320))
    screen.blit(powerup_images['ammo'], (80, 370))
    draw_text(screen, '- улучшение брони корабля', 24, 275, 270)
    draw_text(screen, '- удвоение плотности огня', 24, 270, 320)
    draw_text(screen, '- пополнение боекомплекта', 24, 278, 370)
    draw_text(screen, 'Клавиши |←| и |→| - для перемещения', 22, WIDTH / 2, HEIGHT - 170)
    draw_text(screen, 'Пробел - огонь', 22, WIDTH / 2, HEIGHT - 140)
    draw_text(screen, 'Для старта нажмите клавишу | ↓ |', 18, WIDTH / 2, HEIGHT - 90)
    pygame.display.flip()
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.display.quit()
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYUP and event.key == pygame.K_DOWN:
                waiting = False


if __name__ == '__main__':
    # Цикл игры
    game_over = True
    running = True
    while running:
        if game_over:
            # для заставки возвращается нейтральная музыка
            pygame.mixer.music.load(path.join(snd_dir, 'bgmusic.ogg'))
            pygame.mixer.music.set_volume(0.4)
            pygame.mixer.music.play(loops=-1)
            boss_appear = False
            # если босс уже появлялся - удаляем
            if boss != None:
                boss.kill()
                all_sprites.remove(boss)
                once = False
            # поределяем: когда появится босс
            level_up = random.randint(5000, 7000)
            start_screen(gameplay)
            game_over = False
            player.lives = 3
            player.ammo = 200
            all_sprites.add(player)
            newasteroid(5)
            score = 0
            shots = 0
            success = 0
        # Держим цикл на заданном FPS
        clock.tick(FPS)
        # Ввод процесса (события)
        for event in pygame.event.get():
            # в случае закрытия окна "крестиком"
            if event.type == pygame.QUIT:
                running = False
            # при нажатии пробела - выстрел
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    fire = True
                    if player.ammo > 0:
                        shots = player.shoot(bullet_img)
                    else:
                        misfire.play()
                    # на каждый пятый выстрел - новый астероид
                    if not player.ammo % 5 and not boss_appear:
                        newasteroid(1)
            elif event.type == pygame.KEYUP:
                fire = False

        # Обновление
        all_sprites.update()

        # если астероидов меньше трех, то добавить ещё три (босс пока не появился)
        if not boss_appear:
            if len(asteroids) < 3:
                newasteroid(3)

        # Проверка столкновений
        if boss_appear:
            if not once:  # двух боссов быть не может
                boss = Boss(boss_img)
                all_sprites.add(boss)
                for a in asteroids:
                    a.kill()
                # если появился босс, то астероиды исчезают
                # также исчезают все улучшения
                all_sprites.remove(asteroids)
                all_sprites.remove(powerups)
                asteroids.clear(screen, background)
                screen.blit(keepout, (0, 0))
                pygame.display.update()
                pygame.time.delay(800)
                tadam.play()  # "Та-Дамммм!!!"
                # всего одна жизнь
                # и запас снарядов - 200
                player.ammo = 200
                player.lives = 1
                player.power = 1  # двойной стрельбы нет
                # но броня полноценна в любом случае
                player.shield = 100
                # меняем музыку на тревожную
                pygame.mixer.music.load(path.join(snd_dir, 'action.ogg'))
                pygame.mixer.music.set_volume(0.5)
                pygame.mixer.music.play(loops=-1)
                once = True

            # проверка попала ли пуля игрока в босса
            hits = pygame.sprite.spritecollide(boss, bullets, True, pygame.sprite.collide_circle)
            for hit in hits:
                boss.shield -= 2
                score += 50  # за каждое попадание в босса
                random.choice(expl_sounds).play()
                expl = Explosion(hit.rect.center, 'lg', explosion_anim)
                all_sprites.add(expl)
                if boss.shield <= 0:
                    death_explosion = Explosion(boss.rect.center, 'player', explosion_anim)
                    all_sprites.add(death_explosion)
                    # Если босс повержен, очки удваиваются
                    score *= 2
                    gameplay = 2
                    game_over = True
                    screen.blit(victory, (0, 0))
                    pygame.display.update()
                    pygame.time.delay(900)
                    boss_pass = 'Повержен!'
                    boss_appear = False

            # проверка не попала ли пуля босса в игрока
            hits = pygame.sprite.spritecollide(player, spits, True, pygame.sprite.collide_circle)
            for hit in hits:
                player.shield -= 5
                random.choice(expl_sounds).play()
                expl = Explosion(hit.rect.center, 'lg', explosion_anim)
                all_sprites.add(expl)
                if player.shield <= 0:
                    death_explosion = Explosion(player.rect.center, 'player', explosion_anim)
                    all_sprites.add(death_explosion)
                    player.hide()
                    player.lives -= 1
                    gameplay = 2

            if player.ammo == 0:
                death_explosion = Explosion(player.rect.center, 'player', explosion_anim)
                all_sprites.add(death_explosion)
                player.hide()
                gameplay = 2
                screen.blit(youloose, (0, 0))
                pygame.display.update()
                pygame.time.delay(900)
                boss_pass = 'Не пройден!'
                game_over = True

        # проверка, попала ли пуля в астероид
        hits = pygame.sprite.groupcollide(asteroids, bullets, True, True)
        for hit in hits:
            score += 50 - hit.radius  # в зависимости от радиуса сбитого метеора
            success += 1
            random.choice(expl_sounds).play()
            expl = Explosion(hit.rect.center, 'lg', explosion_anim)
            all_sprites.add(expl)
            # когда пуля уничтожает врага необходим
            # случайный (маленький) шанс на выпадение улучшения
            if random.random() > 0.9:
                power = Powerup(hit.rect.center, powerup_images)
                all_sprites.add(power)
                powerups.add(power)
            # два астероида вместо одного сбитого (если босс не появился)
            if not boss_appear:
                newasteroid(2)

        # Проверка, не ударил ли астероид игрока
        hits = pygame.sprite.spritecollide(player, asteroids, True, pygame.sprite.collide_circle)
        for hit in hits:
            # ущерб в зависимости от радиуса метеора
            crash_sound.play()
            player.shield -= hit.radius * 2
            expl = Explosion(hit.rect.center, 'sm', explosion_anim)
            all_sprites.add(expl)
            if not boss_appear:
                newasteroid(5)
            if player.shield <= 0:
                death_explosion = Explosion(player.rect.center, 'player', explosion_anim)
                all_sprites.add(death_explosion)
                player.hide()
                player.lives -= 1
                player.shield = 100

        # Проверка столкновений игрока и возможные улучшения
        hits = pygame.sprite.spritecollide(player, powerups, True)
        for hit in hits:
            # улучшения для брони (жизни)
            if hit.type == 'shield':
                player.shield += random.randrange(10, 30)
                shield_sound.play()
                if player.shield >= 100:
                    player.shield = 100
            if hit.type == 'gun':
                player.powerup()
                power_sound.play()
            if hit.type == 'ammo':
                player.ammo += random.randrange(40, 120)
                if player.ammo >= 200:
                    player.ammo = 200
                reload.play()

        # Если игрок погиб, игра окончена
        if player.lives == 0 and not death_explosion.alive():
            died_sound.play()
            game_over = True
            screen.blit(youloose, (0, 0))
            pygame.display.update()
            pygame.time.delay(900)
            boss_pass = 'Не пройден!'
            gameplay = 2

        # Рендеринг
        screen.fill(BLACK)

        # прокрутка звёздного неба
        screen.blit(background, (0, Y))
        # эффект полёта
        Y += VEL
        if Y > 0:
            Y = -600
        if not boss_appear:
            if fire:
                screen.blit(heroes[3], (190, 45))
            else:
                screen.blit(heroes[3 - player.lives], (190, 45))
        all_sprites.draw(screen)
        screen.blit(scoreboard, (165, 2))
        draw_text(screen, str(score), 18, WIDTH / 2, 10)
        draw_text(screen, 'AMMO:' + str(player.ammo), 20, 50, 20)
        draw_shield_bar(screen, 5, 5, player.shield, 1)
        if boss_appear:
            draw_shield_bar(screen, 190, 50, boss.shield, 2)
        draw_lives(screen, WIDTH - 100, 5, player.lives, player_mini_img)

        if score > level_up and not once:  # когда появляется босс
            boss_appear = True

        pygame.display.flip()  # После отрисовки всего...

    pygame.display.quit()
    pygame.quit()
    sys.exit()
