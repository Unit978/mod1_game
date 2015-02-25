
from world import *
from engine import *
from random import randrange
from components import BehaviorScript
from components import WorldScript
engine = Engine(1200, 700)


class CheckBoxes(WorldScript):

        def __init__(self, script_name):
            super(CheckBoxes, self).__init__(script_name)
                
            # list of coordinates of where box is supposed to be
            self.boxCoordinates = dict()

            # these are the boxes and their corresponding position followed by a snapped boolean 
            # to check if a box has been snapped into place 
            self.boxCoordinates["pbox1"] = (Vector2(300, 175), False) 
            self.boxCoordinates["pbox2"] = (Vector2(350, 175), False) 
            self.boxCoordinates["pbox3"] = (Vector2(325, 250), False)
            self.boxCoordinates["pbox4"] = (Vector2(450, 225), False)
            self.boxCoordinates["pbox5"] = (Vector2(400, 425), False)
            self.boxCoordinates["pbox6"] = (Vector2(725, 350), False)

        def update(self):

            for box in self.world.boxes:

                # get the boolean snap flag
                snapped = self.boxCoordinates[box.tag][1]

                if not snapped:
                    tgt_position = self.boxCoordinates[box.tag][0]

                    tgt_distance = box.transform.position - tgt_position
                    if tgt_distance.sq_magnitude() < 100:
                        if box.rigid_body is not None:
                            box.remove_component(RigidBody.tag)
                        box.transform.position = tgt_position

                        # set snap to true
                        self.boxCoordinates[box.tag] = (None, True)

                    pygame.draw.circle(self.world.engine.display, (255, 255, 255), (tgt_position.x, tgt_position.y), 2)


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
                # check to see if next to a box that you can gra
                pass

    def collision_event(self, other_collider):

        other_entity = other_collider.entity

        # move the brick
        if other_entity.tag == "pbox": 
            # check to see if next to a box that you can grab
            # other_collidessr.velocity = self.velocity
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

        w = self.engine.display.get_width()
        h = self.engine.display.get_height()

        background_image = pygame.image.load("assets/images/WoodenFloor.png").convert()

        # add necessary components to be able to position and render 
        # the background
        self.background = self.create_entity()
        self.background.add_component(Transform(Vector2(0, 0)))
        self.background.add_component(Renderer(background_image))
        self.background.renderer.depth = 100

        # frames to demonstrate player animation
        frame1 = pygame.Surface((50, 50)).convert()
        frame1.fill((255, 0, 0))

        frame2 = pygame.Surface((50, 50)).convert()
        frame2.fill((0, 255, 0))

        frame3 = pygame.Surface((50, 50)).convert()
        frame3.fill((0, 0, 255))

        frame4 = pygame.Surface((50, 50)).convert()
        frame4.fill((255, 255, 255))

        self.player = self.create_game_object(frame1)
        self.player.add_component(RigidBody(Vector2(0, 0)))
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

        #coordinates of where boxes neeed to be
        #box1 = 300, 175 box2 = 350, 175 box3 = 325, 250
        #box4 = 450, 225 box5 = 400, 425 box6 = 725, 350
        #boxes to be moved around
        box_image = pygame.Surface(( 50,50 )).convert()
        box_image.fill((0, 150, 150))
        pbox = self.create_game_object(box_image)
        pbox.transform.position = Vector2(100, 175 )
        pbox.tag = "pbox1"
        pbox.add_component(RigidBody(Vector2(0,0)))
        self.boxes.append(pbox)

        box_image = pygame.Surface(( 50,50 )).convert()
        box_image.fill((150, 0, 150))
        pbox = self.create_game_object(box_image)
        pbox.transform.position = Vector2(200, 175 )
        pbox.tag = "pbox2"
        pbox.add_component(RigidBody(Vector2(0,0)))
        self.boxes.append(pbox)


        total_bricks = 6
        fib_list = [0,1,1,2,3,5,8]

        # for i in range(1, total_bricks+1):
        #     pbox_width = 50*fib_list[i]
        #     pbox_height = 50*fib_list[i]

        #     # create some random color
        #     r = randrange(50, 226)
        #     g = randrange(50, 226)
        #     b = randrange(50, 226)
        #     brick_color = (r, g, b)

        #     # create basic image for the brick
        #     brick_surface = pygame.Surface((pbox_width, pbox_height))
        #     brick_surface.convert()
        #     brick_surface.fill(brick_color)

        #     # create the brick object and the tag
        #     brick = self.create_game_object(brick_surface)
        #     brick.tag = "pbox"

        #     # position it
        #     brick.transform.position = Vector2(pbox_width*fib_list[i], pbox_height*fib_list[i])



        # box_image = pygame.Surface(( 100,100 )).convert()
        # box_image.fill((150, 150, 0))
        # pbox3 = self.create_game_object(box_image)
        # pbox3.transform.position = Vector2(325, 250 )
        # pbox3.tag = "pbox3"
        # pbox1.add_component(RigidBody(Vector2(0,0)))
        # self.boxes.append(pbox1)

        # box_image = pygame.Surface(( 150,150 )).convert()
        # box_image.fill((0, 0, 150))
        # pbox4 = self.create_game_object(box_image)
        # pbox4.transform.position = Vector2(450, 225 )
        # pbox4.tag = "pbox4"
        # pbox1.add_component(RigidBody(Vector2(0,0)))
        # self.boxes.append(pbox1)

        # box_image = pygame.Surface(( 250,250 )).convert()
        # box_image.fill((150, 0, 0))
        # pbox5 = self.create_game_object(box_image)
        # pbox5.transform.position = Vector2(400, 425 )
        # pbox5.tag = "pbox5"
        # pbox1.add_component(RigidBody(Vector2(0,0)))
        # self.boxes.append(pbox1)

        #box_image = pygame.Surface(( 400,400 )).convert()
        #box_image.fill((0, 150, 0))
        #pbox6 = self.create_game_object(box_image)
        #pbox6.transform.position = Vector2(725, 350 )
        #pbox6.tag = "pbox6"
        # pbox1.add_component(RigidBody(Vector2(0,0)))
        # self.boxes.append(pbox1)

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
