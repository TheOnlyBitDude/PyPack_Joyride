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

    screen_width = 2450
    screen_height = 768

    fps = 60

    screen = display.set_mode((screen_width, screen_height), NOFRAME)
    display.set_caption("PyPack Joyride")
    mixer.set_num_channels(300000)


    def update_():
        for e in event.get():
            if e.type == QUIT:
                exit()
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
            global hitboxes
            if hitboxes:
                draw.rect(screen, (255, 0, 0), Rect(self.rect.x, self.rect.y, self.rect.w, self.rect.h), 2)
            else:
                pass


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
                    bullet2 = Bullets("img/Bullet.png", self.rect.x, self.rect.y + self.h, 10, 45)
                    bullets.append(bullet)
                    bullets.append(bullet2)
                    self.t = 0
                    for bullet in bullets:
                        bullet.shoot()

                self.kind = "fly"
                self.rect.y -= self.fall
                self.fall += 0.75
                if sprite.collide_rect(self, floor) or sprite.collide_rect(self, floor_rvrs):
                    self.fall = 4
                if not jetpack_channel.get_busy():
                    jetpack_channel.play(jetpack_fire, loops=-1)
            else:
                jetpack_channel.stop()

            if self.fall >= 10:
                self.fall = 10
            elif self.fall <= -20:
                self.fall = -20

            if sprite.collide_rect(self, roof):
                self.rect.y = 0
                self.fall = 0

            if not keys[K_SPACE]:
                self.fall -= 0.75
                self.rect.y -= self.fall
                if sprite.collide_rect(self, floor) or sprite.collide_rect(self, floor_rvrs):
                    self.fall = 0
                    self.rect.y = 645
                    self.kind = "run"
                elif not sprite.collide_rect(self, floor) or not sprite.collide_rect(self, floor_rvrs):
                    self.kind = "fall"
                if sprite.collide_rect(self, roof):
                    self.rect.y = 1


    class BG(GameSprite):

        def __init__(self, filename, x, y, w, h):
            super().__init__(filename, x, y, w, h)

        def go(self):
            self.rect.x -= 20


    class Missile(GameSprite):

        def __init__(self, filename, x, y, w, h):
            super().__init__(filename, x, y, w, h)
            self.speed = 50
            self.counter = 0
            self.pre_launch = None
            self.launched = None
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
            if not self.pre_launch:
                warning.play()
                self.pos = randint(20, 714)
                self.launched = 0
                self.rect.y = self.pos
            self.launch()

        def launch(self):

            if not self.pre_launch:
                self.i = 0
                self.rect.x = 2424
                self.pre_launch = True
                self.wait = 0
                self.f = 0

            if self.wait == 34:
                Launch.play()

            if self.wait == 35:
                if self.i != 52:
                    self.rect.x -= self.speed
                    self.i += 1
                else:
                    self.i = 0
                    self.wait = 0
                    self.pre_launch = False
                    self.launched = 1

                if self.f != 1:
                    self.f = 1

                self.rect.y = self.pos
                self.animate()
            else:
                self.wait += 1


    class MissileWave(GameSprite):

        def __init__(self, filename, x, y, w, h):
            super().__init__(filename, x, y, w, h)
            self.speed = 50
            self.counter = 0
            self.pre_launch = None
            self.launched = None
            self.f = None
            self.wait = None
            self.fall = 0
            self.orientation = "negative"

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
            if not self.pre_launch:
                warning.play()
                self.pos = randint(20, 714)
                self.launched = 0
                self.rect.y = self.pos
            self.launch()

        def launch(self):

            if not self.pre_launch:
                self.i = 0
                self.rect.x = 2424
                self.pre_launch = True
                self.wait = 0
                self.f = 0

            if self.wait == 34:
                Launch.play()

            if self.wait == 35:
                if self.i != 52:
                    self.pos -= self.fall
                    if self.fall >= 10:
                        self.orientation = "negative"
                    elif self.fall <= -10:
                        self.orientation = "positive"
                        self.fall += 0.5001

                    if self.orientation == "positive":
                        self.fall += 0.5
                    elif self.orientation == "negative":
                        self.fall -= 0.5

                    self.rect.x -= self.speed
                    self.i += 1
                else:
                    self.i = 0
                    self.wait = 0
                    self.pre_launch = False
                    self.launched = 1

                if self.f != 1:

                    self.f = 1

                self.rect.y = self.pos
                self.animate()
            else:
                self.wait += 1


    class MissileTracer(GameSprite):

        def __init__(self, filename, x, y, w, h):
            super().__init__(filename, x, y, w, h)
            self.speed = 50
            self.counter = 0
            self.pre_launch = None
            self.launched = None
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
            if not self.pre_launch:
                warning.play()
                self.rect.y = barry.rect.y
                self.launched = 0
            self.launch()

        def launch(self):

            if not self.pre_launch:
                self.i = 0
                self.rect.x = 2424
                self.pre_launch = True
                self.wait = 0
                self.f = 0

            if self.wait == 35:
                if self.i != 52:
                    self.rect.x -= self.speed
                    self.i += 1
                else:
                    self.i = 0
                    self.wait = 0
                    self.pre_launch = False
                    self.launched = 1

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

            if self.rect.x <= -283:
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


    loop = 0
    koin_got = False
    def reset(x, y):
        global loop, koin_got
        barry.rect.x = x
        barry.rect.y = y
        barry.fall = 0
        barry.kind = "run"

        bullet.rect.y = 1001

        for missile in missiles:
            missile.launched = 1
            missile.pre_launch = False
            missile.f = 1
            missile.i = 0
            missile.wait = 0
            missile.rect.x = 2424
            missile.rect.y = 0
        for electric in Elektrik_list:
            electric.l = 1
            electric.rect.x = 2484
        Elektrik_list.clear()
        if koin_got:
            for _ in range(10):
                if bg.rect.x == -2740:
                    bg.rect.x = 2740
                elif bg_rvrs.rect.x == -2740:
                    bg_rvrs.rect.x = 2740
                if floor.rect.x == -2740:
                    floor.rect.x = 2740
                elif floor_rvrs.rect.x == -2740:
                    floor_rvrs.rect.x = 2740
                bg.reset()
                bg.go()
                bg_rvrs.reset()
                bg_rvrs.go()
                floor.reset()
                floor.go()
                floor_rvrs.reset()
                floor_rvrs.go()

                floor.reset()
                roof.reset()
                barry.animate()
                barry.reset()
                barry.move()

                expl.explode()
            loop = 0
            koin_got = False
            explode.set_volume(0.85)


    class Explode(GameSprite):
        def __init__(self, filename, x, y, w, h):

            super().__init__(filename, x, y, w, h)
            self.counter = 0

        def explode(self):
            if 0 <= self.counter < 1:
                self.image = transform.scale(image.load('img/Explosions/Explosion1.png'), (self.w, self.h))
            elif 1 <= self.counter < 2:
                self.image = transform.scale(image.load('img/Explosions/Explosion2.png'), (self.w, self.h))
            elif 2 <= self.counter < 3:
                self.image = transform.scale(image.load('img/Explosions/Explosion3.png'), (self.w, self.h))
            elif 3 <= self.counter < 4:
                self.image = transform.scale(image.load('img/Explosions/Explosion4.png'), (self.w, self.h))
            elif 4 <= self.counter < 5:
                self.image = transform.scale(image.load('img/Explosions/Explosion5.png'), (self.w, self.h))
            elif 5 <= self.counter < 6:
                self.image = transform.scale(image.load('img/Explosions/Explosion6.png'), (self.w, self.h))
            elif 6 <= self.counter < 7:
                self.image = transform.scale(image.load('img/Explosions/Explosion7.png'), (self.w, self.h))
            elif 7 <= self.counter < 8:
                self.image = transform.scale(image.load('img/Explosions/Explosion8.png'), (self.w, self.h))
            elif 8 <= self.counter < 9:
                self.image = transform.scale(image.load('img/Explosions/Explosion9.png'), (self.w, self.h))
            elif 9 <= self.counter < 10:
                self.image = transform.scale(image.load('img/Explosions/Explosion10.png'), (self.w, self.h))

            self.counter += 1
            screen.blit(self.image, (0, 0))
            update_()
            if self.counter >= 10:
                self.counter = 0



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
        clock.tick(60)
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
    text("snd/Explode.wav", 525, 360)
    explode = mixer.Sound("snd/Explode.wav")
    explode.set_volume(0.85)
    text("snd/Launch.wav", 525, 360)
    Launch = mixer.Sound("snd/Launch.wav")
    Launch.set_volume(0.75)
    text("snd/smash.wav", 525, 360)
    smash = mixer.Sound("snd/smash.wav")
    text("snd/Theme.wav", 525, 360)
    Theme = mixer.Sound("snd/Theme.wav")
    channel = mixer.Channel(299999)
    text("snd/Warning.wav", 525, 360)
    warning = mixer.Sound("snd/Warning.wav")
    text("snd/jetpack_fire", 525, 360)
    jetpack_fire = mixer.Sound("snd/jetpack_fire.wav")
    jetpack_channel = mixer.Channel(10)
    jetpack_fire.set_volume(0.75)
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
    text("img/Roof.png", 525, 360)
    roof = GameSprite("img/roof.png", 0, -40, screen_width, 40)
    text("img/Missile_Target.png", 525, 360)
    missile1 = MissileTracer(target, -99999, 0, 93, 34)
    text("img/Rocket1.png", 525, 360)
    missile2 = Missile(target, -99999, 0, 93, 34)
    text("img/Rocket2.png", 525, 360)
    missile3 = Missile(target, -99999, 0, 93, 34)
    text("img/Rocket3.png", 525, 360)
    missile4 = Missile(target, -99999, 0, 93, 34)
    text("img/Rocket4.png", 525, 360)
    missile5 = MissileWave(target, -99999, 0, 93, 34)
    missile6 = MissileWave(target, -99999, 0, 93, 34)

    text("img/bg.jpg", 525, 360)
    bg = BG("img/bg.jpg", 0, 0, 2740, 1000)
    text("img/bg_rvrs.jpg", 525, 360)
    bg_rvrs = BG("img/bg_rvrs.jpg", 2740, 0, 2740, 1000)
    text("img/floor", 525, 360)
    floor = BG("img/floor.png", 0, 718, 2740, 50)
    text("img/floor_rvrs.png", 525, 360)
    floor_rvrs = BG("img/floor_rvrs.png", 2740, 718, 2740, 50)

    missiles = [missile1, missile2, missile3, missile4, missile5, missile6]

    text("img/bullet.png", 525, 360)
    bullet = Bullets("img/Bullet.png", 500, 450, 10, 45)

    bullets = [bullet]

    Elektrik_list = []
    powerup = False
    times = 0
    stage = "run"
    diff = "normal"

    expl = Explode("img/Explosions/Explosion1.png", 0, 0, 2400, 768)

    sounds = [Elektric, explode, jetpack_fire, Launch, smash, Theme, warning]
    hitboxes = False
    death_screen = True
    args = sys.argv[1:]
    try:
        for arg in args:
            if arg == "--no-sounds":
                for sound in sounds:
                    sound.set_volume(0)
            elif arg == "--hitboxes":
                hitboxes = True
            elif arg == "--no-death-screen":
                death_screen = False
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
            elif stage == "lost" and e.type == MOUSEBUTTONDOWN and e.button == 1:
                reset(20, 675)
                stage = "run"
            elif e.type == KEYDOWN and e.key == K_p:
                powerup = True
                print("Gave powerup")
            elif e.type == KEYDOWN and e.key == K_r:
                booster.l = 1
                print("Boosted")
            elif e.type == KEYDOWN and e.key == K_e:
                koin_got = True
                reset(barry.rect.x, barry.rect.y)

        barry.move()

        if stage == "run":
            if m == 0:
                m = 1
            screen.fill((100, 100, 100))
            if bg.rect.x == -2740:
                bg.rect.x = 2740
            elif bg_rvrs.rect.x == -2740:
                bg_rvrs.rect.x = 2740
            if floor.rect.x == -2740:
                floor.rect.x = 2740
            elif floor_rvrs.rect.x == -2740:
                floor_rvrs.rect.x = 2740
            bg.reset()
            bg.go()
            bg_rvrs.reset()
            bg_rvrs.go()
            floor.reset()
            floor.go()
            floor_rvrs.reset()
            floor_rvrs.go()

            floor.reset()
            roof.reset()
            barry.animate()
            barry.reset()

            for bullet in bullets:
                bullet.reset()
                bullet.rect.y += 35

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
            for missile in missiles:
                if missile.launched == 0:
                    missile.warning()
                    missile.reset()
                if not powerup and missile.pre_launch and sprite.collide_rect(barry, missile):
                    stage = "lost"
                    explode.play()
                    times += 1
                    det_cnt += 1
                    print("Barry:", barry.rect)
                    print("Missile:", missile.rect)
                if powerup and missile.pre_launch and sprite.collide_rect(barry, missile):
                    powerup = False
                    koin_got = True
                    explode.set_volume(1)
                    explode.play()
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

            elif lnch == 126 or lnch == 173 or lnch == 111 and missile1 != 0:
                missile1.launched = 0
                print("Missile launched")

            elif lnch == 222 or lnch == 109 or lnch == 63 and missile2 != 0:
                missile2.launched = 0
                print("Missile2 launched")

            elif lnch == 35 or lnch == 17 or lnch == 39 and missile3 != 0:
                missile3.launched = 0
                print("Missile3 launched")

            elif lnch == 2 or lnch == 44 or lnch == 22 and missile4 != 0:
                missile4.launched = 0
                print("Missile4 launched")

            elif lnch == 134 or lnch == 127 or lnch == 159 and missile5 != 0:
                missile5.launched = 0
                print("Missile5 launched")

            elif lnch == 241 or lnch == 149 or lnch == 197 and missile6 != 0:
                missile6.launched = 0
                print("Missile6 launched")

            elif lnch == 1:
                for missile in missiles:
                    missile.launched = 0
                print("All missiles launched")

            for bullet in bullets:
                if sprite.collide_rect(bullet, floor) or sprite.collide_rect(bullet, floor_rvrs) or bullet.rect.y > 768:
                    bullets.remove(bullet)



        elif stage == "lost":
            for e in event.get():
                if e.type == QUIT:
                    exit()

            if death_screen:
                screen.fill((100, 0, 0))
                screen.blit(lost, (440, 330))
            update_()

        update_()

except:
    raise