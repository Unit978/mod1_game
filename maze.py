
from world import *
from engine import *
from components import BehaviorScript

engine = Engine(1200, 700)


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


def create_wall(c1, c2):
        wall = pygame.Surface(((c2[0]-c1[0])*28, (c2[1]-c1[1])*50)).convert()
        wall.fill((255, 255, 255))
        # add tile
        return wall


def find_coordinate(c):
        coordinate = c[0]*28, c[1]*50
        return coordinate


class Maze(World):
    def __init__(self):
        super(Maze, self).__init__()

        self.player = None
        self.background = None
        # self.tag = 'wall'

        # border walls
        self.topWall = None
        self.leftWall = None
        self.rightWall = None
        self.bottomWall = None

        # location
        self.coordinate = None

        # maze walls
        self.new_wall = None

        # levers
        self.lever = None

    def construct_wall(self, c):
        self.new_wall = self.create_game_object(create_wall(c, (c[0]+1, c[1]+1)))
        self.coordinate = c
        self.new_wall.tag = "wall"
        if c[0] == 14 and c[1] == 8:
            self.new_wall.collider.restitution = 4
            pass # call fibonacci
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
        self.background = self.create_entity()
        self.background.add_component(Transform(Vector2(0, 0)))
        self.background.add_component(Renderer(background_image))
        self.background.renderer.depth = 100

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
        animation.frame_latency = 0.1

        # set the first animation
        animator = Animator()
        animator.current_animation = animation

        # add animator to player
        self.player.add_component(animator)

        # create border walls
        self.topWall = self.create_box_collider_object(w*2, 1)
        self.bottomWall = self.create_box_collider_object(w*2, 1)
        self.leftWall = self.create_box_collider_object(1, h*2)
        self.rightWall = self.create_box_collider_object(1, h*2)

        # set up border wall positions
        self.bottomWall.transform.position = Vector2(0, h)
        self.leftWall.transform.position = Vector2(0, h/2-50)
        self.rightWall.transform.position = Vector2(w, h/2+50)
        # create maze walls
        list_coordinates = []
        list_coordinates.append((0, 1))  # 1
        list_coordinates.append((0, 2))  # 2
        list_coordinates.append((0, 3))  # 3
        list_coordinates.append((0, 4))  # 4
        list_coordinates.append((1, 4))  # 5
        list_coordinates.append((2, 4))  # 6
        list_coordinates.append((2, 5))  # 7
        list_coordinates.append((3, 6))  # 8
        list_coordinates.append((4, 6))  # 9
        list_coordinates.append((5, 6))  # 10
        list_coordinates.append((6, 6))  # 11
        list_coordinates.append((2, 1))  # 12
        list_coordinates.append((2, 2))  # 13
        list_coordinates.append((3, 2))  # 14
        list_coordinates.append((4, 2))  # 15
        list_coordinates.append((4, 3))  # 16
        list_coordinates.append((4, 4))  # 17
        list_coordinates.append((5, 4))  # 18
        list_coordinates.append((7, 6))  # 19
        list_coordinates.append((7, 5))  # 20
        list_coordinates.append((7, 4))  # 21
        list_coordinates.append((7, 3))  # 22
        list_coordinates.append((6, 2))  # 23
        list_coordinates.append((7, 2))  # 24
        list_coordinates.append((8, 2))  # 25
        list_coordinates.append((4, 1))  # 26
        list_coordinates.append((4, 0))  # 27
        list_coordinates.append((5, 0))  # 28
        list_coordinates.append((6, 0))  # 29
        list_coordinates.append((7, 0))  # 30
        list_coordinates.append((8, 0))  # 31
        list_coordinates.append((9, 0))  # 32
        list_coordinates.append((10, 0))  # 33
        list_coordinates.append((10, 1))  # 34
        list_coordinates.append((10, 2))  # 35
        list_coordinates.append((10, 3))  # 36
        list_coordinates.append((10, 4))  # 37
        list_coordinates.append((9, 4))   # 38
        list_coordinates.append((8, 6))   # 39
        list_coordinates.append((9, 6))   # 40
        list_coordinates.append((10, 6))  # 41
        list_coordinates.append((10, 7))  # 42
        list_coordinates.append((10, 8))  # 43
        list_coordinates.append((10, 9))  # 44
        list_coordinates.append((10, 10))  # 45
        list_coordinates.append((11, 10))  # 46
        list_coordinates.append((12, 10))  # 47
        list_coordinates.append((13, 10))  # 48
        list_coordinates.append((14, 10))  # 49
        list_coordinates.append((15, 10))  # 50
        list_coordinates.append((16, 10))  # 51
        list_coordinates.append((17, 10))  # 52
        list_coordinates.append((17, 9))  # 53
        list_coordinates.append((17, 8))  # 54
        list_coordinates.append((17, 7))  # 55
        list_coordinates.append((17, 6))  # 56
        list_coordinates.append((17, 5))  # 57
        list_coordinates.append((17, 4))  # 58
        list_coordinates.append((11, 4))  # 59
        list_coordinates.append((12, 5))  # 60
        list_coordinates.append((12, 6))  # 61
        list_coordinates.append((12, 7))  # 62
        list_coordinates.append((13, 7))  # 63
        list_coordinates.append((12, 8))  # 64
        list_coordinates.append((13, 8))  # 65

        # lever 1
        list_coordinates.append((14, 8))  # 66
        list_coordinates.append((15, 8))  # 67
        list_coordinates.append((15, 7))  # 68
        list_coordinates.append((15, 6))  # 69
        list_coordinates.append((15, 5))  # 70
        list_coordinates.append((14, 5))  # 71
        list_coordinates.append((13, 3))  # 72
        list_coordinates.append((14, 3))  # 73
        list_coordinates.append((15, 3))  # 74
        list_coordinates.append((16, 3))  # 75
        list_coordinates.append((13, 2))  # 76
        list_coordinates.append((14, 2))  # 77
        list_coordinates.append((15, 2))  # 78
        list_coordinates.append((16, 2))  # 79
        list_coordinates.append((11, 3))  # 80
        list_coordinates.append((11, 2))  # 81
        list_coordinates.append((11, 1))  # 82
        list_coordinates.append((11, 0))  # 83
        list_coordinates.append((12, 0))  # 84
        list_coordinates.append((13, 0))  # 85
        list_coordinates.append((14, 0))  # 86
        list_coordinates.append((15, 0))  # 87
        list_coordinates.append((16, 0))  # 88
        list_coordinates.append((17, 0))  # 89
        list_coordinates.append((18, 0))  # 90
        list_coordinates.append((18, 1))  # 91
        list_coordinates.append((18, 2))  # 92
        list_coordinates.append((19, 2))  # 93
        list_coordinates.append((19, 3))  # 94
        list_coordinates.append((19, 4))  # 95
        list_coordinates.append((19, 5))  # 96
        list_coordinates.append((20, 5))  # 97
        list_coordinates.append((21, 5))  # 98
        list_coordinates.append((22, 5))  # 99
        list_coordinates.append((18, 7))  # 100
        list_coordinates.append((19, 7))  # 101
        list_coordinates.append((20, 7))  # 102
        list_coordinates.append((21, 7))  # 103
        list_coordinates.append((22, 7))  # 104
        list_coordinates.append((24, 7))  # 105
        list_coordinates.append((24, 6))  # 106
        list_coordinates.append((24, 5))  # 107
        list_coordinates.append((24, 4))  # 108
        list_coordinates.append((24, 3))  # 109
        list_coordinates.append((23, 3))  # 110
        list_coordinates.append((22, 3))  # 111
        list_coordinates.append((21, 3))  # 112
        list_coordinates.append((19, 1))  # 113
        list_coordinates.append((20, 1))  # 114
        list_coordinates.append((21, 1))  # 115
        list_coordinates.append((22, 1))  # 116
        list_coordinates.append((24, 2))  # 117
        list_coordinates.append((24, 1))  # 118
        list_coordinates.append((22, 0))  # 119
        list_coordinates.append((24, 0))  # 120
        list_coordinates.append((22, 8))  # 121
        list_coordinates.append((22, 9))  # 122
        list_coordinates.append((22, 10))  # 123
        list_coordinates.append((21, 10))  # 124
        list_coordinates.append((20, 10))  # 125
        list_coordinates.append((19, 10))  # 126
        list_coordinates.append((18, 10))  # 127
        list_coordinates.append((24, 8))   # 128
        list_coordinates.append((24, 9))   # 129
        list_coordinates.append((24, 10))  # 130
        list_coordinates.append((24, 11))  # 131
        list_coordinates.append((24, 12))  # 132
        list_coordinates.append((23, 12))  # 133
        list_coordinates.append((22, 12))  # 134
        list_coordinates.append((21, 12))  # 135
        list_coordinates.append((20, 12))  # 136
        list_coordinates.append((19, 12))   # 137
        list_coordinates.append((18, 12))   # 138
        list_coordinates.append((17, 12))   # 139
        list_coordinates.append((15, 11))   # 140
        list_coordinates.append((15, 12))   # 141
        list_coordinates.append((14, 12))   # 142
        list_coordinates.append((13, 12))   # 143
        list_coordinates.append((12, 12))   # 144
        list_coordinates.append((11, 12))   # 145
        list_coordinates.append((10, 12))   # 146
        list_coordinates.append((9, 13))   # 147
        list_coordinates.append((9, 10))   # 148
        list_coordinates.append((8, 11))   # 149
        list_coordinates.append((7, 11))   # 150
        list_coordinates.append((8, 13))   # 151
        list_coordinates.append((7, 13))   # 152
        list_coordinates.append((6, 13))   # 153
        list_coordinates.append((6, 11))   # 154
        list_coordinates.append((5, 11))   # 155
        list_coordinates.append((4, 12))   # 156
        list_coordinates.append((4, 13))   # 157
        list_coordinates.append((3, 13))   # 158
        list_coordinates.append((2, 13))   # 159
        list_coordinates.append((1, 13))   # 160
        list_coordinates.append((0, 13))   # 161
        list_coordinates.append((3, 11))   # 162
        list_coordinates.append((2, 11))   # 163
        list_coordinates.append((1, 11))   # 164
        list_coordinates.append((1, 10))   # 165
        list_coordinates.append((1, 9))   # 166
        list_coordinates.append((1, 8))   # 167
        list_coordinates.append((1, 7))   # 168
        list_coordinates.append((1, 6))   # 169
        list_coordinates.append((1, 5))   # 170
        list_coordinates.append((0, 5))   # 171
        list_coordinates.append((2, 6))   # 172
        list_coordinates.append((2, 8))   # 173
        list_coordinates.append((2, 9))   # 174
        list_coordinates.append((2, 10))   # 175
        list_coordinates.append((4, 7))   # 176
        list_coordinates.append((4, 8))   # 177
        list_coordinates.append((4, 9))   # 178
        list_coordinates.append((5, 9))   # 179
        list_coordinates.append((6, 9))   # 180
        list_coordinates.append((7, 9))   # 181
        list_coordinates.append((7, 8))   # 182
        # list_coordinates.append((6, 8))   # 183

        for i in list_coordinates:
            self.construct_wall(i)

        self.player.add_script(PlayerBehavior("player behavior"))

    def get_wall(self):
        return self.coordinate


class PlayerBehavior (BehaviorScript):
    def __init__(self, script_name):
        super(PlayerBehavior, self).__init__(script_name)
        self.wall = None

    def collision_event(self, other_collider):
        other_entity = other_collider.entity

        # hits wall
        if other_entity.tag == "wall":
            pass

engine.set_world(Maze())
engine.run()
