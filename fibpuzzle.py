
from world import *
from engine import *
from random import randrange
from components import BehaviorScript
from components import WorldScript

engine = Engine(1200, 700)

#lamp_light_img = pygame.image.load("assets/images/lights/lamp_light_1200x700.png").convert_alpha()

class CheckBoxes(WorldScript):

        def __init__(self, script_name):
            super(CheckBoxes, self).__init__(script_name)
                
            #list of coordinates of where boxes are supposed to be
            self.boxCoordinates = dict()
            #450, 275 500, 275 475, 200 350, 225
            # the correct position of boxes with a boolean condition
            # to check if a box has been snapped into place
            self.boxCoordinates["pbox1"] = (Vector2(450, 275), False)
            self.boxCoordinates["pbox2"] = (Vector2(500, 275), False)
            self.boxCoordinates["pbox3"] = (Vector2(475, 200), False)
            self.boxCoordinates["pbox4"] = (Vector2(350, 225), False)
            self.boxCoordinates["pbox5"] = (Vector2(400, 425), False)
            self.boxCoordinates["pbox6"] = (Vector2(692, 350), False)


        def update(self):

            # loop to iterate through all the boxes as well as the list of boxes
            for box in self.world.boxes:
                if not self.boxCoordinates[box.tag][1]:
                    tgt_position = self.boxCoordinates[box.tag][0]

                    tgt_distance = box.transform.position - tgt_position
                    if tgt_distance.sq_magnitude()< 100 :
                        if box.rigid_body is not None:
                            box.remove_component(RigidBody.tag)
                        box.transform.position=tgt_position
                # position of where boxes are supposed to go 
                # used for testing purposes
                pygame.draw.circle(self.world.engine.display, (255,255,255), (tgt_position.x, tgt_position.y), 2)



class PlayerMovement(BehaviorScript):

    def __init__(self, script_name):
        super(PlayerMovement, self).__init__(script_name)
        self.h_speed = 200
        self.v_speed = 300
        self.right = pygame.image.load("assets/images/character/character_east.png").convert_alpha()
        self.left = pygame.image.load("assets/images/character/character_west.png").convert_alpha()
        self.up = pygame.image.load("assets/images/character/character_north.png").convert_alpha()
        self.down  = pygame.image.load("assets/images/character/character_south.png").convert_alpha()

        self.up_right = pygame.image.load("assets/images/character/character_northeast.png").convert_alpha()
        self.up_left = pygame.image.load("assets/images/character/character_northwest.png").convert_alpha()
        self.down_right = pygame.image.load("assets/images/character/character_southeast.png").convert_alpha()
        self.down_left = pygame.image.load("assets/images/character/character_southwest.png").convert_alpha()

    def update(self):

        keys = pygame.key.get_pressed()

        velocity = self.entity.rigid_body.velocity

        if keys[pygame.K_a]:
            velocity.x = -self.h_speed
            self.entity.renderer.sprite = self.left
        elif keys[pygame.K_d]:
            velocity.x = self.h_speed
            self.entity.renderer.sprite = self.right

        else: 
            velocity.x = 0 

        if keys[pygame.K_w]:
            velocity.y = -self.h_speed
            self.entity.renderer.sprite = self.up

        elif keys[pygame.K_s]:
            velocity.y = self.h_speed
            self.entity.renderer.sprite = self.down

        else:
            velocity.y = 0

        if keys[pygame.K_w] and keys[pygame.K_d]:
            self.entity.renderer.sprite = self.up_right
        elif keys[pygame.K_w] and keys[pygame.K_a]:
            self.entity.renderer.sprite = self.up_left
        elif keys[pygame.K_s] and keys[pygame.K_d]:
            self.entity.renderer.sprite = self.down_right
        elif keys[pygame.K_s] and keys[pygame.K_a]:
            self.entity.renderer.sprite = self.down_left

    def take_input(self, event):

        # this should grab a box in order to move it and position it 
        # in the right place
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
            
                # check to see if next to a box that you can gra
                pass
    def collision_event(self, other_collider):

        other_entity = other_collider.entity

        # move the brick
        if other_entity.tag == "pbox": 
            # check to see if next to a box that you can grab
            #other_collidessr.velocity = self.velocity
            pass
            
class PlatformWorld(World):

    def __init__(self):
        super(PlatformWorld, self).__init__()

        self.player = None
        self.background = None
        self.box = None
        self.boxes = list()

        # walls
        self.topWall = None
        self.leftWall = None
        self.rightWall = None
        self.bottomWall = None

    def load_scene(self):

        # this is used to create the boundaries of the puzzle
        w = self.engine.display.get_width()
        h = self.engine.display.get_height()

        # dimensions for the lamp that will follow player
        # img_width = lamp_light_img.get_width()
        # img_height = lamp_light_img.get_height()

        # pivot = Vector2(img_width/2, img_height/2)

        # self.lamp_mask = self.create_entity()
        # self.lamp_mask.add_component(Transform(Vector2(0, 0)))
        # self.lamp_mask.add_component(Renderer(lamp_light_img, pivot))
        # self.lamp_mask.renderer.depth = -100



        background_image = pygame.image.load("assets/images/floors/Floor.png").convert()
        lamps_image  = pygame.image.load("assets/images/floors/Lamps.png").convert_alpha()
        circle_mask = pygame.image.load( "assets/images/floors/vignette.png" ).convert_alpha()


        # add necessary components to be able to position and render 
        # the background

        self.background = self.create_entity()
        self.background.add_component(Transform(Vector2(0, 0)))
        self.background.add_component(Renderer(background_image))
        self.background.renderer.depth = 100

        #add the lamps here

        self.background_lamps = self.create_entity()
        self.background_lamps.add_component(Transform(Vector2(0, 0)))
        self.background_lamps.add_component(Renderer(lamps_image))
        self.background_lamps.renderer.depth = -100

        # frames to demonstrate player animation
        frame1 = pygame.image.load("assets/images/character/character_west.png").convert_alpha()

        # frame2 = pygame.Surface((50, 50)).convert()
        # frame2.fill((0, 255, 0))

        # frame3 = pygame.Surface((50, 50)).convert()
        # frame3.fill((0, 0, 255))

        # frame4 = pygame.Surface((50, 50)).convert()
        # frame4.fill((255, 255, 255))

        self.player = self.create_game_object(frame1)
        self.player.add_component(RigidBody(Vector2(0, 0)))
        self.player.transform.position = Vector2(100, 100)
        self.player.renderer.depth = -10
        self.player.rigid_body.gravity_scale = 1
        self.player.add_script(PlayerMovement("player_move"))
        self.player.collider.restitution = 1
        self.player.collider.box.w -= 21
        self.player.collider.box.h -= 8

        # set up animation
        # animation = Animator.Animation()

        # add frames to animation
        # animation.add_frame(frame1)
        # animation.add_frame(frame2)
        # animation.add_frame(frame3)
        # animation.add_frame(frame4)

        # set time between frames in seconds
        # animation.frame_latency = 0.5

        # set the first animation
        # animator = Animator()
        # animator.current_animation = animation

        # add animator to player
        # self.player.add_component(animator)

        # boxes to be moved around
        # 450, 275 # 500, 275 # 475, 200 # 350, 225 # 400, 425 # 725, 350

        box_image = pygame.image.load("assets/images/crates/FibonacciBox_37a.png").convert_alpha()
        pbox = self.create_game_object(box_image)
        pbox.transform.position = Vector2(450, 100 )
        pbox.tag = "pbox1"
        pbox.add_component(RigidBody(Vector2(0,0)))
        self.boxes.append(pbox)
        pbox.transform.scale_by(0.5,0.5)

        box_image = pygame.image.load("assets/images/crates/FibonacciBox_37b.png").convert_alpha()
        pbox = self.create_game_object(box_image)
        pbox.transform.position = Vector2(500, 100 )
        pbox.tag = "pbox2"
        pbox.add_component(RigidBody(Vector2(0,0)))
        self.boxes.append(pbox)
        pbox.transform.scale_by(0.5,0.5)

        box_image = pygame.image.load("assets/images/crates/FibonacciBox_74.png").convert_alpha()
        pbox = self.create_game_object(box_image)
        pbox.transform.position = Vector2(475, 200 )
        pbox.tag = "pbox3"
        pbox.add_component(RigidBody(Vector2(0,0)))
        self.boxes.append(pbox)

        box_image = pygame.image.load("assets/images/crates/FibonacciBox_111.png").convert_alpha()
        pbox = self.create_game_object(box_image)
        pbox.transform.position = Vector2(350, 225 )
        pbox.tag = "pbox4"
        pbox.add_component(RigidBody(Vector2(0,0)))
        self.boxes.append(pbox)

        box_image = pygame.image.load("assets/images/crates/FibonacciBox_185.png").convert_alpha()
        pbox = self.create_game_object(box_image)
        pbox.transform.position = Vector2(452, 400 )
        pbox.tag = "pbox5"
        pbox.add_component(RigidBody(Vector2(0,0)))
        self.boxes.append(pbox)

        box_image = pygame.image.load("assets/images/crates/FibonacciBox_296.png").convert_alpha()
        pbox = self.create_game_object(box_image)
        pbox.transform.position = Vector2(692, 350 )
        pbox.tag = "pbox6"
        pbox.add_component(RigidBody(Vector2(0,0)))
        self.boxes.append(pbox)
        #pbox.transform.scale_by(0.5,0.5)
        #pbox.collider.box.h -= 25



        #screen dimensions halved 
        half_w = self.engine.display.get_width()/2
        half_h = self.engine.display.get_height()/2

        # Create the wall entities and set their collision boxes.
        # Make these wall thick, so the ball doesn't escape from the level.
        self.topWall = self.create_box_collider_object(half_w*4, 50)
        self.bottomWall = self.create_box_collider_object(half_w*4, 50)
        self.leftWall = self.create_box_collider_object(200, half_h*4)
        self.rightWall = self.create_box_collider_object(200, half_h*4)

        # set up wall positions
        self.topWall.transform.position = Vector2(half_w, 0-25)
        self.bottomWall.transform.position = Vector2(half_w, half_h*2+25)
        self.leftWall.transform.position = Vector2(0-50-50, half_h)
        self.rightWall.transform.position = Vector2(half_w*2+50+50, half_h)

        PhysicsSystem.gravity.zero()
        self.add_script(CheckBoxes("BoxChecking"))

engine.set_world(PlatformWorld())
engine.run()
