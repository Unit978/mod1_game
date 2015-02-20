
from world import *
from engine import *
from components import BehaviorScript

engine = Engine(1200, 700)


class PlayerMovement(BehaviorScript):

    def __init__(self, script_name):
        super(PlayerMovement, self).__init__(script_name)
        self.h_speed = 200
        self.v_speed = 300

    def update(self):

        keys = pygame.key.get_pressed()


        velocity = self.entity.rigid_body.velocity

        if keys[pygame.K_a]:
            velocity.x = -self.h_speed

        elif keys[pygame.K_d]:
            velocity.x = self.h_speed

        else: 
            velocity.x = 0 

        if keys[pygame.K_w]:
            velocity.y = -self.h_speed

        elif keys[pygame.K_s]:
            velocity.y = self.h_speed

        else:
            velocity.y = 0 

    def take_input(self, event):

        # this should grab a box in order to move it and position it 
        # in the right place
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # check to see if next to a box that you can grab
                self.entity.rigid_body.velocity.y = -self.v_speed


class PlatformWorld(World):

    def __init__(self):
        super(PlatformWorld, self).__init__()

        self.player = None
        self.background = None

        self.box = None


        # walls
        self.topWall = None
        self.leftWall = None
        self.rightWall = None
        self.bottomWall = None

    def load_scene(self):

        w = self.engine.display.get_width()
        h = self.engine.display.get_height()
        background_image = pygame.Surface((w, h))
        background_image.convert()
        background_image.fill((12, 0, 40))

        # add necessary components to be able to position and render 
        # the background
        self.background = self.create_entity()
        self.background.add_component(Transform(Vector2(0, 0)))
        self.background.add_component(Renderer(background_image))
        self.background.renderer.depth = 100

        # frames to demonstrate animation
        frame1 = pygame.Surface((50, 80)).convert()
        frame1.fill((255, 0, 0))

        frame2 = pygame.Surface((50, 80)).convert()
        frame2.fill((0, 255, 0))

        frame3 = pygame.Surface((50, 80)).convert()
        frame3.fill((0, 0, 255))

        frame4 = pygame.Surface((50, 80)).convert()
        frame4.fill((255, 255, 255))

        self.player = self.create_game_object(frame1)
        self.player.add_component(RigidBody())
        self.player.transform.position = Vector2(100, 100)
        self.player.renderer.depth = -10
        self.player.rigid_body.gravity_scale = 1
        self.player.add_script(PlayerMovement("player_move"))
        self.player.collider.restitution = 1

        # set up animation
        animation = Animator.Animation()

        # add frames to animation
        animation.add_frame(frame1)
        animation.add_frame(frame2)
        animation.add_frame(frame3)
        animation.add_frame(frame4)

        # set time between frames in seconds
        animation.frame_latency = 0.5

        # set the first animation
        animator = Animator()
        animator.current_animation = animation

        # add animator to player
        self.player.add_component(animator)

        

        #screen dimensions halved 
        half_w = self.engine.display.get_width()/2
        half_h = self.engine.display.get_height()/2

        box_image = pygame.Surface((300, 100)).convert()
        box_image.fill((150, 150, 150))
        self.box = self.create_game_object(box_image)
        self.box.transform.position = Vector2(200, h - 350)
        self.box.renderer.depth = -5
        self.box.collider.restitution = 0
        self.box.collider.surface_friction = 0.8

        

        


        # Create the wall entities and set their collision boxes.
        # Make these wall thick, so the ball doesn't escape from the level.
        self.topWall = self.create_box_collider_object(half_w*4, 50)
        self.bottomWall = self.create_box_collider_object(half_w*4, 50)
        self.leftWall = self.create_box_collider_object(200, half_h*4)
        self.rightWall = self.create_box_collider_object(200, half_h*4)

        # set up wall positions
        self.topWall.transform.position = Vector2(half_w, 0-25)
        self.bottomWall.transform.position = Vector2(half_w, half_h*2+25+75)
        self.leftWall.transform.position = Vector2(0-50-50, half_h)
        self.rightWall.transform.position = Vector2(half_w*2+50+50, half_h)

        self.topWall.collider.restitution = 0
        self.bottomWall.collider.restitution = 0
        self.leftWall.collider.restitution = 0
        self.rightWall.collider.restitution = 0

        PhysicsSystem.gravity.zero()

engine.set_world(PlatformWorld())
engine.run()
