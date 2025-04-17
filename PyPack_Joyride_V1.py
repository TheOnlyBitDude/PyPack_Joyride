try:

    from random import randint
    from pygame import *
    from time import sleep
    import os
    import shutil
    import sys
    import platform

    print(platform.system())

    init()
    mixer.init()
    font.init()

    clock = time.Clock()
    fps = 60

    screen_width = 2450
    screen_height = 768

    screen = display.set_mode((screen_width, screen_height))
    display.set_caption("PyPack Joyride")
    mixer.set_num_channels(300000)


    def update_():
        clock.tick(fps)
        display.update()


    class GameSprite(sprite.Sprite):
        def __init__(self, filename, x, y, w, h):
            super().__init__()
            self.image = transform.scale(image.load(filename), (w, h))
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y
            self.w = w
            self.h = h

        def reset(self):
            screen.blit(self.image, (self.rect.x, self.rect.y))
            draw.rect(screen, (255, 0, 0), Rect(self.rect.x, self.rect.y, self.rect.w, self.rect.h), 2)


    class Barry(GameSprite):

        def __init__(self, filename, x, y, w, h):
            super().__init__(filename, x, y, w, h)
            self.t = 0
            self.fall = 0
            self.counter = 0
            self.kind = "run"

        def animate(self):
            self.counter += 1
            if self.kind == "run":
                if 0 <= self.counter < 10:
                    self.image = transform.scale(image.load('img/Walk1.png'), (self.w, self.h))
                elif 10 <= self.counter < 20:
                    self.image = transform.scale(image.load('img/Walk2.png'), (self.w, self.h))
                elif 20 <= self.counter < 30:
                    self.image = transform.scale(image.load('img/Walk3.png'), (self.w, self.h))
                elif 30 <= self.counter < 40:
                    self.image = transform.scale(image.load('img/Walk4.png'), (self.w, self.h))

            elif self.kind == "fly":
                if 0 <= self.counter < 5:
                    self.image = transform.scale(image.load('img/Fly1.png'), (self.w, self.h))
                elif 5 <= self.counter < 10:
                    self.image = transform.scale(image.load('img/Fly2.png'), (self.w, self.h))
                elif 10 <= self.counter < 15:
                    self.image = transform.scale(image.load('img/Fly3.png'), (self.w, self.h))
                elif 15 <= self.counter < 20:
                    self.image = transform.scale(image.load('img/Fly1.png'), (self.w, self.h))
                elif 20 <= self.counter < 25:
                    self.image = transform.scale(image.load('img/Fly2.png'), (self.w, self.h))
                elif 25 <= self.counter < 30:
                    self.image = transform.scale(image.load('img/Fly3.png'), (self.w, self.h))
                elif 30 <= self.counter < 35:
                    self.image = transform.scale(image.load('img/Fly2.png'), (self.w, self.h))
                elif 35 <= self.counter < 40:
                    self.image = transform.scale(image.load('img/Fly3.png'), (self.w, self.h))

            elif self.kind == "fall":
                self.image = transform.scale(image.load('img/Walk1.png'), (self.w, self.h))

            if self.counter > 40:
                self.counter = 0

        def move(self):
            keys = key.get_pressed()
            if keys[K_SPACE]:
                self.t += 1
                if self.t == 2:
                    bullet = Bullets("img/Bullet.png", self.rect.x, self.rect.y + self.h, 10, 45)
                    bullets.append(bullet)
                    self.t = 0
                    for bullet in bullets:
                        bullet.shoot()

                self.kind = "fly"
                self.rect.y -= self.fall
                self.fall += 0.75
                if sprite.collide_rect(self, floor):
                    self.fall = 4

            if self.fall >= 10:
                self.fall = 10
            elif self.fall <= -20:
                self.fall = -20

            if sprite.collide_rect(self, roof):
                self.rect.y = 41
                self.fall = 0

            if not keys[K_SPACE]:
                self.fall -= 0.75
                self.rect.y -= self.fall
                if sprite.collide_rect(self, floor):
                    self.fall = 0
                    self.rect.y = 645
                    self.kind = "run"
                elif not sprite.collide_rect(self, floor):
                    self.kind = "fall"
                if sprite.collide_rect(self, roof):
                    self.rect.y = 41


    class BG(GameSprite):

        def __init__(self, filename, x, y, w, h):
            super().__init__(filename, x, y, w, h)

        def go(self):
            self.rect.x -= 20


    class Missile(GameSprite):

        def __init__(self, filename, x, y, w, h):
            super().__init__(filename, x, y, w, h)
            self.speed = 26
            self.counter = 0
            self.launched = None
            self.l = None
            self.f = None
            self.wait = None

        def animate(self):

            if 0 <= self.counter < 2:
                self.image = transform.scale(image.load('img/Rocket1.png'), (self.w, self.h))
            elif 5 <= self.counter < 4:
                self.image = transform.scale(image.load('img/Rocket2.png'), (self.w, self.h))
            elif 10 <= self.counter < 6:
                self.image = transform.scale(image.load('img/Rocket3.png'), (self.w, self.h))
            elif 15 <= self.counter < 8:
                self.image = transform.scale(image.load('img/Rocket4.png'), (self.w, self.h))

            self.counter += 1
            if self.counter >= 8:
                self.counter = 0

        def warning(self):
            if not self.launched:
                warning.play()
                self.pos = randint(20, 714)
                self.l = 0
                self.rect.y = self.pos
            self.launch()

        def launch(self):

            if not self.launched:
                self.i = 0
                self.rect.x = 2424
                self.launched = True
                self.wait = 0
                self.f = 0

            if self.wait == 34:
                Launch.play()

            if self.wait == 35:
                if self.i != 100:
                    self.rect.x -= self.speed
                    self.i += 1
                else:
                    self.i = 0
                    self.wait = 0
                    self.launched = False
                    self.l = 1

                if self.f != 1:

                    self.f = 1

                self.rect.y = self.pos
                self.animate()
            else:
                self.wait += 1


    class MissileTracer(GameSprite):

        def __init__(self, filename, x, y, w, h):
            super().__init__(filename, x, y, w, h)
            self.speed = 26
            self.counter = 0
            self.launched = None
            self.l = None
            self.f = None
            self.wait = None

        def animate(self):

            if 0 <= self.counter < 5:
                self.image = transform.scale(image.load('img/Rocket1.png'), (self.w, self.h))
            elif 5 <= self.counter < 10:
                self.image = transform.scale(image.load('img/Rocket2.png'), (self.w, self.h))
            elif 10 <= self.counter < 15:
                self.image = transform.scale(image.load('img/Rocket3.png'), (self.w, self.h))
            elif 15 <= self.counter < 20:
                self.image = transform.scale(image.load('img/Rocket4.png'), (self.w, self.h))

            self.counter += 1
            if self.counter >= 20:
                self.counter = 0

        def warning(self):
            if not self.launched:
                warning.play()
                self.rect.y = barry.rect.y
                self.l = 0
            self.launch()

        def launch(self):

            if not self.launched:
                self.i = 0
                self.rect.x = 2424
                self.launched = True
                self.wait = 0
                self.f = 0

            if self.wait == 35:
                if self.i != 100:
                    self.rect.x -= self.speed
                    self.i += 1
                else:
                    self.i = 0
                    self.wait = 0
                    self.launched = False
                    self.l = 1

                if self.f != 1:
                    self.f = 1

                self.animate()
            else:
                self.wait += 1


    class Bullets(GameSprite):

        def __init__(self, filename, x, y, w, h):
            super().__init__(filename, x, y, w, h)
            self.x = True

        def shoot(self):
            if self.x:
                self.rect.x = barry.rect.x + 24 + randint(-15, 10)
                self.x = False
            else:
                self.rect.x -= 3


    class Elektrik(GameSprite):
        def __init__(self, filename, x, y, w, h):
            super().__init__(filename, x, y, w, h)
            self.rect.x = 2484
            self.rect.y = randint(21, 718)

        def place(self):
            self.rect.x -= 22

            if self.rect.x <= -150:
                Elektrik_list.remove(self)


    class Koin(GameSprite):
        def __init__(self, filename, x, y, w, h):
            super().__init__(filename, x, y, w, h)
            self.fall = 0
            self.orientation = "positive"
            self.l = 0

        def float(self, speed):
            self.rect.y -= self.fall
            self.rect.x -= speed
            if self.fall >= 13:
                self.orientation = "negative"
            elif self.fall <= -13:
                self.orientation = "positive"
                self.fall += 0.5001

            if self.orientation == "positive":
                self.fall += 0.5
            elif self.orientation == "negative":
                self.fall -= 0.5

            if self.rect.x <= -150:
                self.l = 0
                self.rect.x = screen_width


    def reset(x, y):
        barry.rect.x = x
        barry.rect.y = y
        barry.fall = 0
        barry.kind = "run"

        bullet.rect.y = 1001

        for missile in missiles:
            missile.l = 1
            missile.launched = False
            missile.f = 1
            missile.i = 0
            missile.wait = 0
            missile.rect.x = 2424
            missile.rect.y = 0
        for electric in Elektrik_list:
            electric.l = 1
            electric.rect.x = 2484
        Elektrik_list.clear()


    # load essential files
    MS_DOS = font.Font("fnt/ModernDOS9x16.ttf", 100)
    MS_DOS_smol = font.Font("fnt/ModernDOS9x16.ttf", 25)


    def text(txt, x, y):
        screen.fill((0, 0, 0))
        screen.blit(loading, (430, 0))
        screen.blit(tmtaw, (475, 720))
        text_surface = MS_DOS_smol.render(txt, True, (255, 255, 255))
        screen.blit(text_surface, (x, y))
        update_()


    lost = MS_DOS.render("YOU LOST.", True, (0, 0, 0), None)
    disclaimer = MS_DOS.render("DISCLAIMER!!!!", True, (255, 0, 0))
    recreation = MS_DOS_smol.render("THIS IS ONLY A RECREATION, NOT A STOLEN GAME!!!", True, (255, 0, 0))
    halfbrick = MS_DOS_smol.render("ALL RIGHTS RESERVED FOR HALFBRICK STUDIOS!!!", True, (255, 0, 0))
    click = MS_DOS_smol.render("PRESS ANYWHERE TO CONTINUE...", True, (255, 255, 255))
    ext = False
    fac = False
    notfac = False

    while not ext:
        for e in event.get():
            if e.type == QUIT:
                exit()

            elif e.type == MOUSEBUTTONDOWN and e.button == 1:
                ext = True

        screen.fill((0, 0, 0))
        screen.blit(disclaimer, (300, 0))
        screen.blit(recreation, (335, 250))
        screen.blit(halfbrick, (345, 515))
        screen.blit(click, (455, 720))
        clock.tick(fps)
        display.update()

    github = MS_DOS_smol.render('Press "G" to redirect to the repository.', True, (255, 255, 255))
    fact_res = MS_DOS_smol.render("if you want to do a factory reset, press 'F'.", True, (255, 255, 255))
    run = True
    while run:
        for e in event.get():
            if e.type == QUIT:
                exit()

            elif e.type == KEYDOWN and e.key == K_g:
                if platform.system() == "Windows":
                    os.system("github.url")
                elif platform.system() == "Darwin":
                    os.system('open "https://github.com/TheOnlyBitDude/PyPack_Joyride"')
                elif platform.system() == "Linux":
                    os.system("xdg-open https://github.com/TheOnlyBitDude/PyPack_Joyride")

            elif e.type == MOUSEBUTTONDOWN and e.button == 1:
                run = False

            elif e.type == KEYDOWN and e.key == K_f:
                try:
                    shutil.rmtree('data/')
                    fac = True
                    run = False
                except FileNotFoundError:
                    notfac = True
                    run = False

        screen.fill((0, 0, 0))
        screen.blit(github, (405, 0))
        screen.blit(fact_res, (350, 350))
        screen.blit(click, (455, 720))
        update_()

    fact = MS_DOS.render("FACTORY RESET COMPLETED.", True, (0, 255, 255))
    notfact = MS_DOS.render("FACTORY RESET FAILED.", True, (200, 0, 0))

    if fac:
        screen.fill((0, 0, 0))
        screen.blit(fact, (40, 350))
        update_()
        sleep(3)
        fac = False
    elif notfac:
        screen.fill((0, 0, 0))
        screen.blit(notfact, (150, 350))
        update_()
        sleep(3)
        notfac = False


    # Load assets and variables

    death1 = False
    death10 = False
    death50 = False
    koin = False

    det_cnt = 0

    ez_koin = False

    loading = MS_DOS.render("LOADING...", True, (255, 255, 255))
    tmtaw = MS_DOS_smol.render("THIS MIGHT TAKE A WHILE...", True, (255, 255, 255))

    screen.fill((0, 0, 0))
    screen.blit(loading, (430, 0))
    screen.blit(tmtaw, (475, 720))
    update_()


    text("data/", 525, 360)

    basepath = os.getcwd()
    for entry in os.listdir(basepath):
        if os.path.isdir(os.path.join(basepath, entry)):
            if entry.find("data") != -1:
                print("Found data folder: " + entry)
            else:
                try:
                    os.mkdir("data/")
                except OSError:
                    pass

    for file in os.listdir(basepath + "/data"):
        if os.path.isfile(os.path.join(basepath + "/data", file)):
            if file.find("death1") != -1:
                death1 = True
            elif file.find("death10") != -1:
                death10 = True
            elif file.find("death50") != -1:
                death50 = True
            elif file.find("koin") != -1:
                koin = True


    text("snd/Elektrik.wav", 525, 360)
    Elektric = mixer.Sound("snd/Elektrik.wav")
    Elektric.set_volume(0.75)
    text("snd/Explode.wav", 525, 360)
    Explode = mixer.Sound("snd/Explode.wav")
    Explode.set_volume(0.85)
    text("snd/Launch.wav", 525, 360)
    Launch = mixer.Sound("snd/Launch.wav")
    Launch.set_volume(0.75)
    text("snd/smash.wav", 525, 360)
    smash = mixer.Sound("snd/smash.wav")
    text("snd/Theme.wav", 525, 360)
    Theme = mixer.Sound("snd/Theme.wav")
    Theme.set_volume(1.25)
    channel = mixer.Channel(299999)
    text("snd/Warning.wav", 525, 360)
    warning = mixer.Sound("snd/Warning.wav")
    warning.set_volume(0.75)
    text("snd/jetpack_fire", 525, 360)
    jetpack_fire = mixer.Sound("snd/jetpack_fire.wav")
    jetpack_fire.set_volume(0.90)
    Game = True
    m = 0
    a = 0



    text("img/Fly1.png", 525, 360)
    text("img/Fly2.png", 525, 360)
    text("img/Fly3.png", 525, 360)
    text("img/Fly4.png", 525, 360)
    text("img/FlyFall.png", 525, 360)
    text("img/Walk1.png", 525, 360)
    text("img/Walk2.png", 525, 360)
    text("img/Walk3.png", 525, 360)
    text("img/Walk4.png", 525, 360)
    barry = Barry("img/Walk1.png", 20, 675, 64, 74)

    text('img/Missile_target.png', 525, 360)
    target = 'img/Missile_Target.png'
    text("img/Koin.png", 525, 360)
    koin = Koin("img/Koin.png", screen_width, 470, 80, 80)
    text("img/booster.png", 525, 360)
    booster = Koin("img/booster.png", screen_width, 470, 110, 110)
    text("img/Floor.png", 525, 360)
    floor = GameSprite("img/floor.png", 0, 718, screen_width, 50)
    text("img/Roof.png", 525, 360)
    roof = GameSprite("img/roof.png", 0, 0, screen_width, 40)
    text("img/Missile_Target.png", 525, 360)
    missile = MissileTracer(target, 0, 0, 93, 34)
    text("img/Rocket1.png", 525, 360)
    missile2 = Missile(target, 0, 0, 93, 34)
    text("img/Rocket2.png", 525, 360)
    missile3 = Missile(target, 0, 0, 93, 34)
    text("img/Rocket3.png", 525, 360)
    missile4 = Missile(target, 0, 0, 93, 34)
    text("img/Rocket4.png", 525, 360)

    text("img/bg.jpg", 525, 360)
    bg = BG("img/bg.jpg", 0, 0, 2740, 1000)
    text("img/bg_rvrs.jpg", 525, 360)
    bg_rvrs = BG("img/bg_rvrs.jpg", 2740, 0, 2740, 1000)

    bgs = [bg, bg_rvrs]

    missiles = [missile, missile2, missile3, missile4]

    text("img/bullet.png", 525, 360)
    bullet = Bullets("img/Bullet.png", 500, 450, 10, 45)

    bullets = [bullet]

    Elektrik_list = []
    powerup = False
    times = 0
    stage = "run"
    diff = "normal"

    sounds = [Elektric, Explode, jetpack_fire, Launch, smash, Theme, warning]

    try:
        if sys.argv[1] == "--no-sounds":
            for sound in sounds:
                sound.set_volume(0)
        else:
            pass
    except IndexError:
        pass

    while Game:
        if channel.get_busy():
            pass
        else:
            channel.play(Theme)

        for e in event.get():
            if e.type == QUIT:
                exit()
            elif stage == "lost" and e.type == KEYDOWN and e.key == K_SPACE:
                sleep(0.45)
                reset(20, 675)
                stage = "run"
            elif e.type == KEYDOWN and e.key == K_o:
                times = 9
                det_cnt = 9
            elif e.type == KEYDOWN and e.key == K_5:
                times = 49
                det_cnt = 49
            elif e.type == KEYDOWN and e.key == K_p:
                powerup = True
            elif e.type == KEYDOWN and e.key == K_ESCAPE:
                stage = "pause"
            elif e.type == KEYDOWN and e.key == K_r:
                booster.l = 1
            elif e.type == KEYDOWN and e.key == K_SPACE:
                jetpack_fire.play()
            elif e.type == KEYUP and e.key == K_SPACE:
                jetpack_fire.stop()

        if stage == "run":
            if m == 0:
                m = 1
            screen.fill((100, 100, 100))
            if bg.rect.x == -2740:
                bg.rect.x = 2740
            elif bg_rvrs.rect.x == -2740:
                bg_rvrs.rect.x = 2740
            bg.reset()
            bg.go()
            bg_rvrs.reset()
            bg_rvrs.go()

            floor.reset()
            roof.reset()
            barry.animate()
            barry.move()
            barry.reset()

            for bullet in bullets:
                bullet.reset()
                bullet.rect.y += 25

            koin_rand = randint(1, 1500)
            booster_rand = randint(1, 1500 )

            if koin_rand == 500 and not powerup:
                koin.l = 1

            if koin.l == 1:
                koin.reset()
                koin.float(10)
                if sprite.collide_rect(barry, koin):
                    powerup = True
                    smash.play()
                    koin.l = 0
                    try:
                        open("data/koin", "x")
                        ez_koin = True
                    except FileExistsError:
                        pass

            elif koin.l == 0:
                koin.rect.x = 2484
                koin.rect.y = 460
                koin.fall = 0

            if booster.l == 1:
                booster.reset()
                booster.float(20)
                if sprite.collide_rect(barry, booster):
                    powerup = True
                    smash.play()
                    booster.l = 0
                    try:
                        open("data/booster", "x")
                        ez_koin = True
                    except FileExistsError:
                        pass

            if booster_rand == 1500:
                booster.l = 1

            lnch = randint(1, 225)
            if missile.l == 0:
                for missile in missiles:
                    missile.warning()
                    missile.reset()
                    if not powerup and sprite.collide_rect(barry, missile):
                        stage = "lost"
                        Explode.play()
                        times += 1
                        det_cnt += 1
                    if powerup and sprite.collide_rect(barry, missile):
                        powerup = False
                        reset(barry.rect.x, barry.rect.y)

            for elektrik in Elektrik_list:
                if elektrik.l == 0:
                    elektrik.reset()
                    elektrik.place()
                    if not powerup and sprite.collide_rect(barry, elektrik):
                        stage = "lost"
                        Elektric.play()
                        times += 1
                        det_cnt += 1
                    if powerup and sprite.collide_rect(barry, elektrik):
                        powerup = False
                        try:
                            Elektrik_list.remove(elektrik)
                        except:
                            pass
                        reset(barry.rect.x, barry.rect.y)

            if lnch == 70 or lnch == 80 or lnch == 90:
                elektrik = Elektrik("img/elektrik.png", 1376, 0, 282, 68)
                elektrik.l = 0
                Elektrik_list.append(elektrik)

            elif lnch == 10 or lnch == 20 or lnch == 30:
                elektrik = Elektrik("img/elektrik_vert.png", 1376, 0, 68, 282)
                elektrik.l = 0
                Elektrik_list.append(elektrik)

            elif lnch == 35 or lnch == 45 or lnch == 55:
                for missile in missiles:
                    missile.l = 0

            for bullet in bullets:
                if sprite.collide_rect(bullet, floor):
                    bullets.remove(bullet)


        elif stage == "lost":
            for e in event.get():
                if e.type == QUIT:
                    exit()


            screen.fill((100, 0, 0))
            screen.blit(lost, (440, 330))
            update_()

        update_()

except:
    raise