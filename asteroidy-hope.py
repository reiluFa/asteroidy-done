import math
import pyglet
from pyglet import gl
from pyglet.window import key
import random

WIDTH = 1200
HEIGHT = 800
ACCELERATION = 275
ROTATION_SPEED = 0.09

objects = []
batch = pyglet.graphics.Batch()
pressed_keyboards = set()

DELAY = 0.45
LASERLIFETIME = 0.5
LASERSPEED = 1000

score = 0
scoreLabel = pyglet.text.Label(text=str(score), font_size=40,x = 1100, y = 720, anchor_x='right', anchor_y='center', batch=batch )

deaths = 0
deathLabel = pyglet.text.Label(text=str(deaths), font_size=40, x=50, y=760, anchor_x='left', anchor_y='center', batch=batch)

def set_anchor_of_image_to_center(img):
    img.anchor_x = img.width // 2
    img.anchor_y = img.height // 2

class SpaceObject:
    def __init__(self, sprite, x, y, speed_x= 0, speed_y = 0):
        self.x_speed = speed_x
        self.y_speed = speed_y
        self.rotation = 1.57  # radiany -> smeruje hore

        self.sprite = pyglet.sprite.Sprite(sprite, batch=batch)
        self.sprite.x = x
        self.sprite.y = y
        self.radius = (self.sprite.height + self.sprite.width) // 4

    def distance(self, other):
        x = abs(self.sprite.x - other.sprite.x)
        y = abs(self.sprite.y - other.sprite.y)
        return (x**2 + y**2) ** 0.5 #pytagorova veta

    def hit_by_spaceship(self, ship):
        pass

    def hit_by_laser(self, laser):
        pass

    def delete(self, dt =0 ):
        self.sprite.delete()
        objects.remove(self)

    def checkBoundaries(self):
        if self.sprite.x > WIDTH:
            self.sprite.x = 0

        if self.sprite.x < 0:
            self.sprite.x = WIDTH

        if self.sprite.y < 0:
            self.sprite.y = HEIGHT

        if self.sprite.y > HEIGHT:
            self.sprite.y = 0

    def tick(self, dt):
        self.sprite.x += dt * self.x_speed
        self.sprite.y += dt * self.y_speed
        self.sprite.rotation = 90 - math.degrees(self.rotation)
        self.checkBoundaries()

class Spaceship(SpaceObject):

    def __init__(self, sprite, x ,y):
        super().__init__(sprite,x,y)
        self.fire = -1

    def shoot(self):
        laser = Laser(self.sprite.x, self.sprite.y, self.rotation)
        objects.append(laser)


    def tick(self, dt):
        super().tick(dt)
        if 'W' in pressed_keyboards:
            self.x_speed = self.x_speed + dt * ACCELERATION * math.cos(self.rotation)
            self.y_speed = self.y_speed + dt * ACCELERATION * math.sin(self.rotation)

        if 'S' in pressed_keyboards:
            self.x_speed = self.x_speed - dt * ACCELERATION * math.cos(self.rotation)
            self.y_speed = self.y_speed - dt * ACCELERATION * math.sin(self.rotation)

        if 'A' in pressed_keyboards:
            self.rotation += ROTATION_SPEED

        if 'D' in pressed_keyboards:
            self.rotation -= ROTATION_SPEED

        if 'SHIFT' in pressed_keyboards:
            self.x_speed = 0
            self.y_speed = 0

        if self.fire <= 0:
            if 'SPACE' in pressed_keyboards:
                self.fire = DELAY
                self.shoot()
        else:
            self.fire -= dt

        for obj in [o for o in objects if o != self]:
            # d = distance medzi objektami
            d = self.distance(obj)
            if d < self.radius + obj.radius:
                obj.hit_by_spaceship(self)
                break

    def reset(self):
        self.sprite.x = WIDTH // 2
        self.sprite.y = HEIGHT // 2
        self.x_speed = 0
        self.y_speed = 0
        self.rotation = 1.57
        global deaths
        deaths += 1
        deathLabel.text = str(deaths)

class Asteroid(SpaceObject):
    def __init__(self, sprite, x, y, lifecount, speed_x, speed_y):
        super().__init__(sprite, x, y, speed_x, speed_y)
        self.lifecount = lifecount

    def hit_by_spaceship(self, ship):
        pressed_keyboards.clear()
        ship.reset()
        self.delete()



    def hit_by_laser(self, laser):
        global score
        score += 1
        scoreLabel.text = str(score)
        laser.delete()
        if self.lifecount > 1:
            self.lifecount -= 1
        else:
            self.delete()

class Laser(SpaceObject):
    def __init__(self, x, y, rotation):
        speed_x = LASERSPEED * math.cos(rotation)
        speed_y = LASERSPEED * math.sin(rotation)
        self.laser_image = pyglet.image.load('Assetss/PNG/Lasers/laserBlue16.png')
        super().__init__(self.laser_image, x, y, speed_x, speed_y)
        self.rotation = rotation
        self.lifetime = LASERLIFETIME

    def tick(self, dt):
        super().tick(dt)
        self.lifetime -= dt

        if self.lifetime < 0:
            self.delete()

        for obj in [o for o in objects if o != self]:
            # d = distance medzi objektami
            d = self.distance(obj)
            if d < self.radius + obj.radius:
                obj.hit_by_laser(self)
                break

class Game:

    def __init__(self):
        self.window = None
        objects = []

    def load_resources(self):
        self.playerShip_image = pyglet.image.load('Assetss/PNG/playerShip2_blue.png')
        set_anchor_of_image_to_center(self.playerShip_image)
        self.background_image = pyglet.image.load('Assetss/Backgrounds/darkPurple.png')
        self.asteroid_images = ['Assetss/PNG/Meteors/meteorBrown_med3.png',
                           'Assetss/PNG/Meteors/meteorBrown_small2.png',
                           'Assetss/PNG/Meteors/meteorBrown_med1.png']
        self.asteroid2_images = ['Assetss/PNG/Meteors/meteorGrey_big4.png']
        self.asteroid3_images = ['Assetss/PNG/Meteors/meteorGrey_big2.png']

    def init_objects(self):

        spaceShip = Spaceship(self.playerShip_image, WIDTH // 2, HEIGHT // 2)
        objects.append(spaceShip)

        self.background = pyglet.sprite.Sprite(self.background_image)
        self.background.scale_x = 6
        self.background.scale_y = 4

        self.create_asteroids(count=7)
        self.create_asteroid2(count=2)
        self.create_asteroid3(count=3)
        pyglet.clock.schedule_interval(self.create_asteroids, 3, 1)
        pyglet.clock.schedule_interval(self.create_asteroid2, 11, 1)
        pyglet.clock.schedule_interval(self.create_asteroid3, 7, 1)



    def create_asteroids(self, dt=0, count=1):
        for i in range(count):
            img = pyglet.image.load(random.choice(self.asteroid_images))
            set_anchor_of_image_to_center(img)

            position = [0, 0]
            dimension = [WIDTH, HEIGHT]
            axis = random.choice([0, 1])
            position[axis] = random.uniform(0, dimension[axis])

            tmp_speed_x = random.uniform(-120, 120)
            tmp_speed_y = random.uniform(-120, 120)


            asteroid = Asteroid(img, position[0], position[1], 1, tmp_speed_x, tmp_speed_y)
            objects.append(asteroid)

    def create_asteroid2(self, dt=0, count=1):
        for i in range(count):
            img = pyglet.image.load(random.choice(self.asteroid2_images))
            set_anchor_of_image_to_center(img)

            position = [0, 0]
            dimension = [WIDTH, HEIGHT]
            axis = random.choice([0, 1])
            position[axis] = random.uniform(0, dimension[axis])

            tmp_speed_x = random.uniform(-120, 120)
            tmp_speed_y = random.uniform(-120, 120)

            asteroid = Asteroid(img, position[0], position[1], 7, tmp_speed_x, tmp_speed_y)
            objects.append(asteroid)



    def create_asteroid3(self, dt=0, count=1):
        for i in range(count):
            img = pyglet.image.load(random.choice(self.asteroid3_images))
            set_anchor_of_image_to_center(img)

            position = [0, 0]
            dimension = [WIDTH, HEIGHT]
            axis = random.choice([0, 1])
            position[axis] = random.uniform(0, dimension[axis])

            tmp_speed_x = random.uniform(-120, 120)
            tmp_speed_y = random.uniform(-120, 120)

            asteroid = Asteroid(img, position[0], position[1], 3, tmp_speed_x, tmp_speed_y)
            objects.append(asteroid)

    def draw_game(self):
        self.window.clear()
        self.background.draw()

        for x_offset in (-self.window.width, 0, self.window.width):
            for y_offset in (-self.window.height, 0, self.window.height):
                gl.glPushMatrix()
                gl.glTranslatef(x_offset, y_offset, 0)
                batch.draw()
                gl.glPopMatrix()

    def key_press(self, symbol, modifikatory):
        if symbol == key.W:
            pressed_keyboards.add('W')
        if symbol == key.S:
            pressed_keyboards.add('S')
        if symbol == key.A:
            pressed_keyboards.add('A')
        if symbol == key.D:
            pressed_keyboards.add('D')
        if symbol == key.LSHIFT:
            pressed_keyboards.add('SHIFT')
        if symbol == key.SPACE:
            pressed_keyboards.add('SPACE')

    def key_release(self, symbol, modifikatory):
        if symbol == key.W:
            pressed_keyboards.discard('W')
        if symbol == key.S:
            pressed_keyboards.discard('S')
        if symbol == key.A:
            pressed_keyboards.discard('A')
        if symbol == key.D:
            pressed_keyboards.discard('D')
        if symbol == key.LSHIFT:
            pressed_keyboards.discard('SHIFT')
        if symbol == key.SPACE:
            pressed_keyboards.discard('SPACE')

    def update(self, dt):
        for obj in objects:
            obj.tick(dt)

    def start(self):
        self.window = pyglet.window.Window(width=WIDTH, height=HEIGHT)
        self.window.push_handlers(
            on_draw=self.draw_game,
            on_key_press=self.key_press,
            on_key_release=self.key_release
        )
        self.load_resources()
        self.init_objects()
        
        pyglet.clock.schedule_interval(self.update, 1./60)


        pyglet.app.run()  # all is set, the game can start

GAME = Game().start()
