
from world import *
from engine import *
from components import WorldScript

from random import randrange
from math import pi

engine = Engine(1200, 700)


class InteractionScript(WorldScript):

    def __init__(self, script_name):
        super(WorldScript, self).__init__(script_name)

    def take_input(self, event):

        if event.type == pygame.MOUSEBUTTONDOWN:
            radius = randrange(10, 70)
            ball = self.world.create_circle_collider_object(radius)
            ball.add_component(RigidBody())
            ball.collider.restitution = 0.85
            ball.rigid_body.gravity_scale = 1.0

            # random velocity
            x = randrange(800, 1000)
            y = randrange(800, 1000)

            invert_x = randrange(0, 2)
            invert_y = randrange(0, 2)

            if invert_x == 0:
                x *= -1
            if invert_y == 0:
                y *= -1

            ball.rigid_body.velocity = Vector2(10, 10)

            ball.rigid_body.velocity.set_magnitude(800)
            ball.rigid_body.velocity.set_direction(-pi/4)

            # get mouse position
            x = pygame.mouse.get_pos()[0]
            y = pygame.mouse.get_pos()[1]

            ball.transform.position = Vector2(x, y)

            ball.rigid_body.mass = ball.collider.radius * 2


class MyWorld(World):

    def __init__(self):
        super(MyWorld, self).__init__()

        self.background = None

        # walls
        self.topWall = None
        self.bottomWall = None
        self.leftWall = None
        self.rightWall = None

    def load_scene(self):

        # set debug to true
        self.engine.debug = True

        w = self.engine.display.get_width()
        h = self.engine.display.get_height()
        background_image = pygame.Surface((w, h))
        background_image.convert()
        background_image.fill((12, 0, 40))

        # add necessary components to be able to position and render the background
        self.background = self.create_entity()
        self.background.add_component(Transform(Vector2(0, 0)))
        self.background.add_component(Renderer(background_image))
        self.background.renderer.depth = 100

        # make the balls
        # for i in range(0, 8):
        #
        #     radius = randrange(10, 60)
        #     ball = self.create_circle_collider_object(radius)
        #     ball.add_component(RigidBody())
        #     ball.collider.restitution = 0.9
        #     ball.rigid_body.gravity_scale = 1
        #
        #     # random velocity
        #     x = randrange(100, 500)
        #     y = randrange(100, 500)
        #
        #     invert_x = randrange(0, 2)
        #     invert_y = randrange(0, 2)
        #
        #     if invert_x == 0:
        #         x *= -1
        #     if invert_y == 0:
        #         y *= -1
        #
        #     ball.rigid_body.velocity = Vector2(x, y)
        #     ball.transform.position = Vector2(i*100+100, i*60+100)
        #
        #     ball.rigid_body.mass = ball.collider.radius * 2

        # Create the wall entities and set their collision boxes.
        # Make these wall thick, so the ball doesn't escape from the level.
        self.topWall = self.create_box_collider_object(w*2, 100)
        self.bottomWall = self.create_box_collider_object(w*2, 100)
        self.leftWall = self.create_box_collider_object(200, h*2)
        self.rightWall = self.create_box_collider_object(200, h*2)

        self.topWall.collider.restitution = 0.85
        self.bottomWall.collider.restitution = 0.85
        self.leftWall.collider.restitution = 0.85
        self.rightWall.collider.restitution = 0.85

        self.topWall.collider.surface_friction = 0.98
        self.bottomWall.collider.surface_friction = 0.98
        self.leftWall.collider.surface_friction = 0.98
        self.rightWall.collider.surface_friction = 0.98

        # set up wall positions
        self.topWall.transform.position = Vector2(w/2, 0-25)
        self.bottomWall.transform.position = Vector2(w/2, h+25)
        self.leftWall.transform.position = Vector2(0-50-25, h/2)
        self.rightWall.transform.position = Vector2(w+75, h/2)

        self.bottomWall.collider.restitution = 0.5

        self.add_script(InteractionScript("interaction"))


engine.set_world(MyWorld())
engine.run()