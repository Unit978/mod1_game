
from world import *
from engine import *
from components import BehaviorScript

engine = Engine(1200, 700)
scale_x = 28  # original 56
scale_y = 50  # original 100
tile = pygame.image.load("assets/images/56x100 tile.png").convert()


class CameraFollow(BehaviorScript):

    def __init__(self, script_name, target_transform, cam_width, cam_height):
        super(CameraFollow, self).__init__(script_name)
        self.target_transform = target_transform
        self.width = cam_width
        self.height = cam_height

    def update(self):

        # center the target transform in the middle of the camera
        x = self.target_transform.position.x - self.width/2
        y = self.target_transform.position.y - self.height/2

        renderer = self.target_transform.entity.renderer

        # center around the image attached to the target transform
        if renderer is not None:
            x += renderer.sprite.get_width()/2
            y += renderer.sprite.get_height()/2

        world = self.entity.world

        # keep camera within world bounds
        if world.is_bounded():
            if x < world.origin.x:
                x = world.origin.x

            elif x > world.origin.x + world.width - self.width:
                x = world.origin.x + world.width - self.width

            if y < world.origin.y:
                y = world.origin.y

            elif y > world.origin.y + world.height - self.height:
                y = world.origin.y + world.height - self.height

        # set the camera position accordingly
        self.entity.transform.position = Vector2(x, y)


class PlayerMovement(BehaviorScript):

    def __init__(self, script_name):
        super(PlayerMovement, self).__init__(script_name)
        self.speed = 200.0

    def update(self):

        keys = pygame.key.get_pressed()

        velocity = self.entity.rigid_body.velocity

        if keys[pygame.K_a]:
            velocity.x = -self.speed

        elif keys[pygame.K_d]:
            velocity.x = self.speed

        else:
            velocity.x = 0

        if keys[pygame.K_w]:
            velocity.y = -self.speed

        elif keys[pygame.K_s]:
            velocity.y = self.speed

        else:
            velocity.y = 0

    def take_input(self, event):
        pass
        # if event.type == pygame.KEYDOWN:
        #     if event.key == pygame.K_SPACE:
        #         self.entity.rigid_body.velocity.y = -self.v_speed


def create_blocked_wall(c1, c2):
        lever = pygame.Surface(((c2[0]-c1[0])*scale_x, (c2[1]-c1[1])*scale_y)).convert()
        lever.fill((0, 255, 0))
        return lever


def create_lever(c1, c2):
        lever = pygame.Surface(((c2[0]-c1[0])*scale_x, (c2[1]-c1[1])*scale_y)).convert()
        lever.fill((255, 0, 0))
        return lever


def create_wall(c1, c2):
        wall = pygame.Surface(((c2[0]-c1[0])*scale_x, (c2[1]-c1[1])*scale_y)).convert()
        wall.fill((255, 255, 255))
        return wall


def find_coordinate(c):
        coordinate = c[0]*scale_x, c[1]*scale_y
        return coordinate


class Maze(World):
    def __init__(self):
        super(Maze, self).__init__()

        self.player = None
        self.background = None

        # border walls
        self.topWall = None
        self.leftWall = None
        self.rightWall = None
        self.bottomWall = None

        # location
        self.coordinate = None

        # levers
        self.lever1 = None
        self.lever2 = None
        self.lever3 = None
        self.lever4 = None
        self.lever5 = None
        self.lever6 = None

        # blocked path walls for each lever
        self.blocked1 = None
        self.blocked2 = None
        self.blocked3 = None
        self.blocked4 = None
        self.blocked5 = None
        self.blocked6 = None

        # static maze walls
        self.new_wall = None

    def construct_blocked_walls(self):
        l1c = (12, 4)
        self.blocked1 = self.create_game_object(create_blocked_wall(l1c, (l1c[0]+1, l1c[1]+1)))
        # self.blocked1 = self.create_game_object(tile)
        self.blocked1.tag = "blocked1"
        _l1c = find_coordinate(l1c)
        self.blocked1.transform.position = Vector2(_l1c[0], _l1c[1])

        l2c = (24, 6)
        self.blocked2 = self.create_game_object(create_blocked_wall(l2c, (l2c[0]+1, l2c[1]+1)))
        # self.blocked2 = self.create_game_object(tile)
        self.blocked2.tag = "blocked2"
        _l2c = find_coordinate(l2c)
        self.blocked2.transform.position = Vector2(_l2c[0], _l2c[1])

        l3c = (15, 11)
        self.blocked3 = self.create_game_object(create_blocked_wall(l3c, (l3c[0]+1, l3c[1]+1)))
        # self.blocked3 = self.create_game_object(tile)
        self.blocked3.tag = "blocked3"
        _l3c = find_coordinate(l3c)
        self.blocked3.transform.position = Vector2(_l3c[0], _l3c[1])

        l4c = (4, 12)
        self.blocked4 = self.create_game_object(create_blocked_wall(l4c, (l4c[0]+1, l4c[1]+1)))
        # self.blocked4 = self.create_game_object(tile)
        self.blocked4.tag = "blocked4"
        _l4c = find_coordinate(l4c)
        self.blocked4.transform.position = Vector2(_l4c[0], _l4c[1])

        l5c = (1, 7)
        self.blocked5 = self.create_game_object(create_blocked_wall(l5c, (l5c[0]+1, l5c[1]+1)))
        # self.blocked5 = self.create_game_object(tile)
        self.blocked5.tag = "blocked5"
        _l5c = find_coordinate(l5c)
        self.blocked5.transform.position = Vector2(_l5c[0], _l5c[1])

    def construct_levers(self):
        l1c = (14, 7)
        self.lever1 = self.create_game_object(create_lever(l1c, (l1c[0]+1, l1c[1]+1)))
        self.lever1.tag = "lever1"
        _l1c = find_coordinate(l1c)
        self.lever1.transform.position = Vector2(_l1c[0], _l1c[1])

        l2c = (23, 0)
        self.lever2 = self.create_game_object(create_lever(l2c, (l2c[0]+1, l2c[1]+1)))
        self.lever2.tag = "lever2"
        _l2c = find_coordinate(l2c)
        self.lever2.transform.position = Vector2(_l2c[0], _l2c[1])

        l3c = (16, 13)
        self.lever3 = self.create_game_object(create_lever(l3c, (l3c[0]+1, l3c[1]+1)))
        self.lever3.tag = "lever3"
        _l3c = find_coordinate(l3c)
        self.lever3.transform.position = Vector2(_l3c[0], _l3c[1])

        l4c = (5, 13)
        self.lever4 = self.create_game_object(create_lever(l4c, (l4c[0]+1, l4c[1]+1)))
        self.lever4.tag = "lever4"
        _l4c = find_coordinate(l4c)
        self.lever4.transform.position = Vector2(_l4c[0], _l4c[1])

        l5c = (0, 6)
        self.lever5 = self.create_game_object(create_lever(l5c, (l5c[0]+1, l5c[1]+1)))
        self.lever5.tag = "lever5"
        _l5c = find_coordinate(l5c)
        self.lever5.transform.position = Vector2(_l5c[0], _l5c[1])

    def construct_wall(self, c):
        self.new_wall = self.create_game_object(create_wall(c, (c[0]+1, c[1]+1)))
        # self.new_wall = self.create_game_object(tile)
        self.new_wall.tag = "wall"
        c1 = find_coordinate(c)
        self.new_wall.transform.position = Vector2(c1[0], c1[1])

    def load_scene(self):

        PhysicsSystem.gravity.zero()
        w = self.engine.display.get_width()
        h = self.engine.display.get_height()
        background_image = pygame.Surface((w, h))
        background_image.convert()
        background_image.fill((12, 0, 40))

        # add necessary components to be able to position and render the background
        background_image = pygame.image.load("assets/images/WoodenFloor.png").convert()

        # add necessary components to be able to position and render
        # the background
        self.background = self.create_entity()
        self.background.add_component(Transform(Vector2(0, 0)))
        self.background.add_component(Renderer(background_image))
        self.background.renderer.depth = 100
        self.background.renderer.is_static = True
        # frames to demonstrate animation
        frame1 = pygame.Surface((20, 20)).convert()
        frame1.fill((255, 0, 0))

        frame2 = pygame.Surface((20, 20)).convert()
        frame2.fill((0, 255, 0))

        frame3 = pygame.Surface((20, 20)).convert()
        frame3.fill((0, 0, 255))

        frame4 = pygame.Surface((20, 20)).convert()
        frame4.fill((0, 0, 0))

        self.player = self.create_game_object(frame1)
        self.player.add_component(RigidBody())
        # self.player.transform.position = Vector2(0, 0)
        self.player.transform.position = Vector2(800, 400)
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
        animation.frame_latency = 0.1

        # set the first animation
        animator = Animator()
        animator.current_animation = animation

        # add animator to player
        self.player.add_component(animator)
        # =============================================Static Maze Tiles==========================
        # create maze walls
        coordinates = []
        coordinates.append((0, 1))  # 1
        coordinates.append((0, 2))  # 2
        coordinates.append((0, 3))  # 3
        coordinates.append((0, 4))  # 4
        coordinates.append((1, 4))  # 5
        coordinates.append((2, 4))  # 6
        coordinates.append((2, 5))  # 7
        coordinates.append((3, 6))  # 8
        coordinates.append((4, 6))  # 9
        coordinates.append((5, 6))  # 10
        coordinates.append((6, 6))  # 11
        coordinates.append((2, 1))  # 12
        coordinates.append((2, 2))  # 13
        coordinates.append((3, 2))  # 14
        coordinates.append((4, 2))  # 15
        coordinates.append((4, 3))  # 16
        coordinates.append((4, 4))  # 17
        coordinates.append((5, 4))  # 18
        coordinates.append((7, 6))  # 19
        coordinates.append((7, 5))  # 20
        coordinates.append((7, 4))  # 21
        coordinates.append((7, 3))  # 22
        coordinates.append((6, 2))  # 23
        coordinates.append((7, 2))  # 24
        coordinates.append((8, 2))  # 25
        coordinates.append((4, 1))  # 26
        coordinates.append((4, 0))  # 27
        coordinates.append((5, 0))  # 28
        coordinates.append((6, 0))  # 29
        coordinates.append((7, 0))  # 30
        coordinates.append((8, 0))  # 31
        coordinates.append((9, 0))  # 32
        coordinates.append((10, 0))  # 33
        coordinates.append((10, 1))  # 34
        coordinates.append((10, 2))  # 35
        coordinates.append((10, 3))  # 36
        coordinates.append((10, 4))  # 37
        coordinates.append((9, 4))   # 38
        coordinates.append((8, 6))   # 39
        coordinates.append((9, 6))   # 40
        coordinates.append((10, 6))  # 41
        coordinates.append((10, 7))  # 42
        coordinates.append((10, 8))  # 43
        coordinates.append((10, 9))  # 44
        coordinates.append((10, 10))  # 45
        coordinates.append((11, 10))  # 46
        coordinates.append((12, 10))  # 47
        coordinates.append((13, 10))  # 48
        coordinates.append((14, 10))  # 49
        coordinates.append((15, 10))  # 50
        coordinates.append((16, 10))  # 51
        coordinates.append((17, 10))  # 52
        coordinates.append((17, 9))  # 53
        coordinates.append((17, 8))  # 54
        coordinates.append((17, 7))  # 55
        coordinates.append((17, 6))  # 56
        coordinates.append((17, 5))  # 57
        coordinates.append((17, 4))  # 58
        coordinates.append((11, 4))  # 59
        coordinates.append((12, 5))  # 60
        coordinates.append((12, 6))  # 61
        coordinates.append((12, 7))  # 62
        coordinates.append((13, 7))  # 63
        coordinates.append((12, 8))  # 64
        coordinates.append((13, 8))  # 65
        coordinates.append((14, 8))  # 66
        coordinates.append((15, 8))  # 67
        coordinates.append((15, 7))  # 68
        coordinates.append((15, 6))  # 69
        coordinates.append((15, 5))  # 70
        coordinates.append((14, 5))  # 71
        coordinates.append((13, 3))  # 72
        coordinates.append((14, 3))  # 73
        coordinates.append((15, 3))  # 74
        coordinates.append((16, 3))  # 75
        coordinates.append((13, 2))  # 76
        coordinates.append((14, 2))  # 77
        coordinates.append((15, 2))  # 78
        coordinates.append((16, 2))  # 79
        coordinates.append((11, 3))  # 80
        coordinates.append((11, 2))  # 81
        coordinates.append((11, 1))  # 82
        coordinates.append((11, 0))  # 83
        coordinates.append((12, 0))  # 84
        coordinates.append((13, 0))  # 85
        coordinates.append((14, 0))  # 86
        coordinates.append((15, 0))  # 87
        coordinates.append((16, 0))  # 88
        coordinates.append((17, 0))  # 89
        coordinates.append((18, 0))  # 90
        coordinates.append((18, 1))  # 91
        coordinates.append((18, 2))  # 92
        coordinates.append((19, 2))  # 93
        coordinates.append((19, 3))  # 94
        coordinates.append((19, 4))  # 95
        coordinates.append((19, 5))  # 96
        coordinates.append((20, 5))  # 97
        coordinates.append((21, 5))  # 98
        coordinates.append((22, 5))  # 99
        coordinates.append((18, 7))  # 100
        coordinates.append((19, 7))  # 101
        coordinates.append((20, 7))  # 102
        coordinates.append((21, 7))  # 103
        coordinates.append((22, 7))  # 104
        coordinates.append((24, 7))  # 105
        # coordinates.append((24, 6))  # 106
        coordinates.append((24, 5))  # 107
        coordinates.append((24, 4))  # 108
        coordinates.append((24, 3))  # 109
        coordinates.append((23, 3))  # 110
        coordinates.append((22, 3))  # 111
        coordinates.append((21, 3))  # 112
        coordinates.append((19, 1))  # 113
        coordinates.append((20, 1))  # 114
        coordinates.append((21, 1))  # 115
        coordinates.append((22, 1))  # 116
        coordinates.append((24, 2))  # 117
        coordinates.append((24, 1))  # 118
        coordinates.append((22, 0))  # 119
        coordinates.append((24, 0))  # 120
        coordinates.append((22, 8))  # 121
        coordinates.append((22, 9))  # 122
        coordinates.append((22, 10))  # 123
        coordinates.append((21, 10))  # 124
        coordinates.append((20, 10))  # 125
        coordinates.append((19, 10))  # 126
        coordinates.append((18, 10))  # 127
        coordinates.append((24, 8))   # 128
        coordinates.append((24, 9))   # 129
        coordinates.append((24, 10))  # 130
        coordinates.append((24, 11))  # 131
        coordinates.append((24, 12))  # 132
        coordinates.append((23, 12))  # 133
        coordinates.append((22, 12))  # 134
        coordinates.append((21, 12))  # 135
        coordinates.append((20, 12))  # 136
        coordinates.append((19, 12))   # 137
        coordinates.append((18, 12))   # 138
        coordinates.append((17, 12))   # 139
        # coordinates.append((15, 11))   # 140
        coordinates.append((15, 12))   # 141
        coordinates.append((14, 12))   # 142
        coordinates.append((13, 12))   # 143
        coordinates.append((12, 12))   # 144
        coordinates.append((11, 12))   # 145
        coordinates.append((10, 12))   # 146
        coordinates.append((9, 13))   # 147
        coordinates.append((9, 10))   # 148
        coordinates.append((8, 11))   # 149
        coordinates.append((7, 11))   # 150
        coordinates.append((8, 13))   # 151
        coordinates.append((7, 13))   # 152
        coordinates.append((6, 13))   # 153
        coordinates.append((6, 11))   # 154
        coordinates.append((5, 11))   # 155
        # coordinates.append((4, 12))   # 156
        coordinates.append((4, 13))   # 157
        coordinates.append((3, 13))   # 158
        coordinates.append((2, 13))   # 159
        coordinates.append((1, 13))   # 160
        coordinates.append((0, 13))   # 161
        coordinates.append((3, 11))   # 162
        coordinates.append((2, 11))   # 163
        coordinates.append((1, 11))   # 164
        coordinates.append((1, 10))   # 165
        coordinates.append((1, 9))   # 166
        coordinates.append((1, 8))   # 167
        # coordinates.append((1, 7))   # 168
        coordinates.append((1, 6))   # 169
        coordinates.append((1, 5))   # 170
        coordinates.append((0, 5))   # 171
        coordinates.append((2, 6))   # 172
        coordinates.append((2, 8))   # 173
        coordinates.append((2, 9))   # 174
        coordinates.append((2, 10))   # 175
        coordinates.append((4, 7))   # 176
        coordinates.append((4, 8))   # 177
        coordinates.append((4, 9))   # 178
        coordinates.append((5, 9))   # 179
        coordinates.append((6, 9))   # 180
        coordinates.append((7, 9))   # 181
        coordinates.append((7, 8))   # 182
        coordinates.append((6, 8))   # 183
        coordinates.append((4, 11))
        coordinates.append((23, -1))
        coordinates.append((25, 5))
        coordinates.append((26, 5))
        coordinates.append((28, 5))
        coordinates.append((28, 4))
        coordinates.append((28, 3))
        coordinates.append((28, 2))
        coordinates.append((28, 1))
        coordinates.append((28, 0))
        coordinates.append((28, -1))
        coordinates.append((26, 4))
        coordinates.append((26, 2))
        coordinates.append((26, 1))
        coordinates.append((25, -1))
        coordinates.append((27, 0))
        # lever 7
        coordinates.append((27, -1))
        # blocked wall 7
        coordinates.append((23, 7))

        coordinates.append((26, 6))
        coordinates.append((26, 7))
        coordinates.append((26, 8))
        coordinates.append((27, 8))
        coordinates.append((28, 8))
        coordinates.append((28, 9))
        coordinates.append((28, 10))
        coordinates.append((26, 10))
        coordinates.append((26, 11))
        coordinates.append((26, 12))
        coordinates.append((27, 12))
        coordinates.append((26, 13))
        coordinates.append((24, 14))
        coordinates.append((22, 13))
        coordinates.append((20, 14))
        coordinates.append((18, 13))
        coordinates.append((17, 13))
        coordinates.append((17, 14))
        coordinates.append((27, 13))
        coordinates.append((28, 13))
        coordinates.append((29, 13))
        coordinates.append((29, 12))
        coordinates.append((30, 12))
        coordinates.append((30, 11))
        coordinates.append((30, 10))
        coordinates.append((30, 9))
        coordinates.append((31, 9))
        coordinates.append((30, 7))
        coordinates.append((31, 7))
        coordinates.append((32, 7))
        coordinates.append((32, 6))
        coordinates.append((32, 5))
        coordinates.append((32, 4))
        coordinates.append((32, 3))
        coordinates.append((32, 2))
        coordinates.append((31, 1))
        coordinates.append((31, 0))
        coordinates.append((32, 0))
        coordinates.append((33, 0))
        coordinates.append((34, 0))
        coordinates.append((35, 1))
        coordinates.append((36, 1))
        coordinates.append((36, 2))
        coordinates.append((36, 3))
        coordinates.append((35, 3))
        coordinates.append((34, 3))
        coordinates.append((34, 4))
        coordinates.append((34, 5))
        coordinates.append((34, 6))
        coordinates.append((34, 7))
        coordinates.append((35, 7))
        coordinates.append((36, 7))
        coordinates.append((39, 0))
        coordinates.append((40, 0))
        coordinates.append((38, 1))
        coordinates.append((38, 2))
        coordinates.append((38, 3))
        coordinates.append((38, 4))
        coordinates.append((39, 5))
        coordinates.append((38, 5))
        coordinates.append((37, 5))
        coordinates.append((36, 5))
        coordinates.append((39, 6))
        coordinates.append((39, 7))
        coordinates.append((39, 8))
        coordinates.append((39, 9))
        coordinates.append((39, 10))
        coordinates.append((39, 11))
        coordinates.append((39, 12))
        coordinates.append((39, 13))
        coordinates.append((38, 13))
        coordinates.append((37, 13))
        coordinates.append((36, 13))
        coordinates.append((35, 13))
        coordinates.append((34, 13))
        coordinates.append((33, 13))
        coordinates.append((32, 13))
        coordinates.append((31, 13))
        coordinates.append((30, 13))
        coordinates.append((39, 8))
        coordinates.append((36, 8))
        coordinates.append((36, 9))
        coordinates.append((36, 10))
        coordinates.append((36, 11))
        coordinates.append((35, 11))
        coordinates.append((34, 11))
        coordinates.append((33, 11))
        coordinates.append((32, 11))
        coordinates.append((32, 9))
        coordinates.append((33, 9))
        coordinates.append((34, 9))
        coordinates.append((35, 9))
        # lever
        coordinates.append((35, 10))
        # =========================================Perimeter=======================================

        # top perimeter
        for i in range(-1, 42):
            coordinates.append((i, -2))
        # bottom perimeter
        for i in range(-1, 42):
            coordinates.append((i, 15))
        # left perimeter wall
        for i in range(-2, 16):
            coordinates.append((-2, i))

        # right perimeter wall
        for i in range(-2, 16):
            coordinates.append((42, i))

        # static walls for maze
        for i in coordinates:
            self.construct_wall(i)

        self.player.add_script(PlayerBehavior("player behavior"))

        # add camera
        render = self.get_system(RenderSystem.tag)
        render.camera = self.create_entity()
        render.camera.add_component(Transform(Vector2(0, 0)))
        render.camera.add_script(CameraFollow("cam follow", self.player.transform, w, h))

        # create levers to be triggered by player
        self.construct_levers()
        # create blocked path walls
        self.construct_blocked_walls()


class PlayerBehavior (BehaviorScript):
    def __init__(self, script_name):
        super(PlayerBehavior, self).__init__(script_name)
        self.touched_lever1 = False
        self.touched_lever2 = False
        self.touched_lever3 = False
        self.touched_lever4 = False
        self.touched_lever5 = False
        self.touched_lever6 = False

    def collision_event(self, other_collider):
        other_entity = other_collider.entity
        # hits lever 1-6
        if other_entity.tag == "lever1":
            print "You hit lever 1!"
            self.touched_lever1 = True
        elif other_entity.tag == "lever2":
            print "You hit lever 2!"
            self.touched_lever2 = True
        elif other_entity.tag == "lever3":
            print "You hit lever 3!"
            self.touched_lever3 = True
        elif other_entity.tag == "lever4":
            print "You hit lever 4!"
            self.touched_lever4 = True
        elif other_entity.tag == "lever5":
            print "You hit lever 5!"
            self.touched_lever5 = True
        elif other_entity.tag == "lever6":
            print "You hit lever 6!"
            self.touched_lever6 = True

        if other_entity.tag == "blocked1" and self.touched_lever1 is True:
            self.entity.world.destroy_entity(other_entity)
        elif other_entity.tag == "blocked2" and self.touched_lever2 is True:
            self.entity.world.destroy_entity(other_entity)
        elif other_entity.tag == "blocked3" and self.touched_lever3 is True:
            self.entity.world.destroy_entity(other_entity)
        elif other_entity.tag == "blocked4" and self.touched_lever4 is True:
            self.entity.world.destroy_entity(other_entity)
        elif other_entity.tag == "blocked5" and self.touched_lever5 is True:
            self.entity.world.destroy_entity(other_entity)
        elif other_entity.tag == "blocked6" and self.touched_lever6 is True:
            self.entity.world.destroy_entity(other_entity)

engine.set_world(Maze())
engine.run()
