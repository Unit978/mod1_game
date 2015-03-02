
from world import *
from engine import *

from scripts import *
from utility import *
from state_machine import *

engine = Engine(1200, 700)

# load music to play in the background
background_music = mixer.music.load("assets/music/MarysCreepyCarnivalTheme.mp3")


class UpdateAnimationHandler(WorldScript):

    def __init__(self, anim_state_machine):
        super(UpdateAnimationHandler, self).__init__("animation handler")
        self.anim_state_machine = anim_state_machine

    def update(self):
        self.anim_state_machine.update()


class PlatformWorld(World):

    def __init__(self):
        super(PlatformWorld, self).__init__()

        self.player = None
        self.player_anim_handler = None

        self.ladders = list()

    def load_scene(self):
        w = self.engine.display.get_width()
        h = self.engine.display.get_height()
        self.origin = Vector2(0, -450)

        # world bounds
        self.width = 4600
        self.height = 1100

        background_image = pygame.Surface((w, h))
        background_image.convert()
        background_image.fill((12, 0, 40))

        # add necessary components to be able to position and render the background
        background = self.create_entity()
        background.add_component(Transform(Vector2(0, 0)))
        background.add_component(Renderer(background_image))
        background.renderer.depth = 100
        background.renderer.is_static = True

        self.load_player()
        self.load_ladders()
        self.load_floors()
        self.load_ceilings()
        self.load_walls()
        self.load_platforms()
        self.load_elevators()
        self.load_boxes()

        # set up camera
        render = self.get_system(RenderSystem.tag)
        render.camera = self.create_entity()
        render.camera.add_component(Transform(Vector2(0, 0)))
        render.camera.add_script(CameraFollow("cam follow", self.player.transform, w, h))

        # start the background music and set it to loop forever
        mixer.music.play(-1)
        mixer.music.set_volume(0.3)

        PhysicsSystem.gravity.y += 200

        self.add_script(UpdateAnimationHandler(self.player_anim_handler))

    def load_ladders(self):
        path = "assets/images/ladders/"
        load = pygame.image.load
        ladder_body = load(path + "ladder_body.png").convert_alpha()
        ladder_top = load(path + "ladder_top.png").convert_alpha()

        self.create_ladder(ladder_body, ladder_top, 440, 950, 395)
        self.create_ladder(ladder_body, ladder_top, 270, 1650, 25)
        self.create_ladder(ladder_body, ladder_top, 410, 1920, 395)

    def load_platforms(self):

        path = "assets/images/platforms/"

        load = pygame.image.load

        img_200x30 = load(path + "30x200.png").convert_alpha()
        img_400x30 = load(path + "30x400.png").convert_alpha()
        img_250x50 = load(path + "50x250.png").convert_alpha()
        img_400x120 = load(path + "120x400.png").convert_alpha()
        img_300x30 = load(path + "30x300.png").convert_alpha()
        img_800x150 = load(path + "150x800.png").convert_alpha()
        img_300x50 = load(path + "50x300.png").convert_alpha()

        plat_a = self.create_game_object(img_200x30)
        plat_a.transform.position = Vector2(300, 250)
        set_platform_attributes(plat_a)

        plat_b = self.create_game_object(img_400x30)
        plat_b.transform.position = Vector2(400, 400)
        set_platform_attributes(plat_b)

        plat_c = self.create_game_object(img_250x50)
        plat_c.transform.position = Vector2(1100, 200)
        set_platform_attributes(plat_c)

        plat_d = self.create_game_object(img_250x50)
        plat_d.transform.position = Vector2(1700, 200)
        set_platform_attributes(plat_d)

        plat_e = self.create_game_object(img_250x50)
        plat_e.transform.position = Vector2(1500, -100)
        set_platform_attributes(plat_e)

        plat_f = self.create_game_object(img_400x120)
        plat_f.transform.position = Vector2(2150, 250)
        set_platform_attributes(plat_f)

        plat_g = self.create_game_object(img_200x30)
        plat_g.transform.position = Vector2(2250, 0)
        set_platform_attributes(plat_g)

        plat_h = self.create_game_object(img_300x30)
        plat_h.transform.position = Vector2(1800, -150)
        set_platform_attributes(plat_h)
        plat_h.add_script(PlatformMovement("plat move"))

        plat_i = self.create_game_object(img_800x150)
        plat_i.transform.position = Vector2(3150, 300)
        set_platform_attributes(plat_i)

        plat_j = self.create_game_object(img_300x50)
        plat_j.transform.position = Vector2(4000, 120)
        set_platform_attributes(plat_j)

    def load_walls(self):

        path = "assets/images/walls/"

        load = pygame.image.load

        img_200x500 = load(path + "200x500.png").convert_alpha()
        img_200x350 = load(path + "200x350.png").convert_alpha()
        img_200x200 = load(path + "200x200.png").convert_alpha()
        img_600x170 = load(path + "170x600.png").convert_alpha()

        wall_a = self.create_game_object(img_200x500)
        wall_a.transform.position = Vector2(100, 350)
        set_wall_attributes(wall_a)

        wall_b = self.create_game_object(img_200x350)
        wall_b.transform.position = Vector2(80, -200)
        set_wall_attributes(wall_b)

        wall_c = self.create_game_object(img_200x200)
        wall_c.transform.position = Vector2(4600, 500)
        set_wall_attributes(wall_c)

        wall_d = self.create_game_object(img_600x170)
        wall_d.transform.position = Vector2(4400, 180)
        set_wall_attributes(wall_d)

        wall_e = self.create_game_object(img_200x200)
        wall_e.transform.position = Vector2(4600, 0)
        set_wall_attributes(wall_e)

    def load_floors(self):

        w = self.engine.display.get_width()
        h = self.engine.display.get_height()

        floor_tile = pygame.image.load("assets/images/floors/floor_tile.png").convert()

        img = create_img_from_tile(floor_tile, w*2, 200)
        floor_a = self.create_game_object(img)
        floor_a.transform.position = Vector2(w, h)
        set_floor_attributes(floor_a)

        img = create_img_from_tile(floor_tile, 1000, 200)
        x = w*2 + 100 + 500 + 50
        floor_b = self.create_game_object(img)
        floor_b.transform.position = Vector2(x, h)
        set_floor_attributes(floor_b)

        x += 250 + 800 + 150
        floor_c = self.create_game_object(img)
        floor_c.transform.position = Vector2(x, h)
        set_floor_attributes(floor_c)

    def load_ceilings(self):

        ceil_color = (50, 50, 50)

        w = self.engine.display.get_width()

        img = RenderSystem.create_solid_image(w*2, 200, ceil_color)
        ceil_a = self.create_game_object(img)
        ceil_a.transform.position = Vector2(w, -470)
        set_ceiling_attributes(ceil_a)

        img = RenderSystem.create_solid_image(1200, 400, ceil_color)
        ceil_b = self.create_game_object(img)
        ceil_b.transform.position = Vector2(w*2 + 500, -350)
        set_ceiling_attributes(ceil_b)

        img = RenderSystem.create_solid_image(1150, 200, ceil_color)
        ceil_c = self.create_game_object(img)
        ceil_c.transform.position = Vector2(w*2 + 1650, -470)
        set_ceiling_attributes(ceil_c)

    def load_player(self):

        # load animation frames
        self.load_anims()

        starting_image = self.player_anim_handler.current_state.animation.frames[0]

        self.player = self.create_game_object(starting_image)
        self.player.add_component(RigidBody())
        self.player.transform.position = Vector2(230, 580)
        self.player.transform.scale = Vector2(1, 1)
        self.player.renderer.depth = -10
        self.player.rigid_body.gravity_scale = 2
        self.player.collider.restitution = 0
        self.player.name = "player"

        self.player.collider.set_box(40, 70)
        self.player.collider.set_offset(-12, 10)

        self.player.add_script(PlayerClimbing("player climb"))
        self.player.add_script(PlayerPlatformMovement("player plat move"))

        # add animator to player from the animation state machine
        self.player.add_component(self.player_anim_handler.animator)

    def load_elevators(self):

        path = "assets/images/platforms/"

        img_140x50 = pygame.image.load(path + "50x140.png").convert_alpha()
        img_180x50 = pygame.image.load(path + "50x180.png").convert_alpha()

        # create elevator platforms
        for i in range(0, 4):
            platform = self.create_game_object(img_140x50)
            x = 2475
            spawn_point = Vector2(x, 700)

            platform.transform.position = Vector2(x, 700 - i*200)
            set_platform_attributes(platform)
            platform.add_script(ElevatorPlatMovement(spawn_point, "elev move"))
            platform.collider.treat_as_dynamic = True

        for i in range(0, 5):
            platform = self.create_game_object(img_180x50)
            x = 3650
            spawn_point = Vector2(x, 700)

            platform.transform.position = Vector2(x, 700 - i*200)
            set_platform_attributes(platform)
            platform.add_script(ElevatorPlatMovement(spawn_point, "elev move"))
            platform.collider.treat_as_dynamic = True

    def load_boxes(self):
        box_img = pygame.image.load("assets/images/crates/red_green.png").convert_alpha()

        box = self.create_game_object(box_img)
        box.transform.position = Vector2(900, 300)
        box.renderer.depth = -5
        box.collider.restitution = 0
        box.collider.surface_friction = 0.8
        box.collider.box.w -= 10
        box.collider.box.h -= 10

        box.add_component(RigidBody())
        box.rigid_body.velocity = Vector2(0.0, 0.0)
        box.rigid_body.gravity_scale = 2
        box.tag = "box"

    def load_anims(self):

        self.player_anim_handler = AnimationStateMachine(Animator())

        path_to_anims = "assets/animations/"

        # setup the idle animation
        anim = load_anim_from_directory(path_to_anims + "Idle/")

        # set time between frames in seconds
        anim.frame_latency = 0.18

        # create a state and load it to the state machine
        state = AnimationStateMachine.AnimationState("idle", anim)
        self.player_anim_handler.add_state(state)

        # setup the walk animation
        anim = load_anim_from_directory(path_to_anims + "Walking/")
        anim.frame_latency = 0.1
        state = AnimationStateMachine.AnimationState("walking", anim)
        self.player_anim_handler.add_state(state)

        # add jump animation
        anim = load_anim_from_directory(path_to_anims + "Jumping/")
        anim.frame_latency = 0.12
        anim.cycle = False
        state = AnimationStateMachine.AnimationState("jumping", anim)
        self.player_anim_handler.add_state(state)

        # climb animation
        anim = load_anim_from_directory(path_to_anims + "Climbing/")
        anim.frame_latency = 0.12
        state = AnimationStateMachine.AnimationState("climbing", anim)
        self.player_anim_handler.add_state(state)

        self.player_anim_handler.set_current_state("idle")

        # transitions for the state machine
        walk_transition = StateMachine.Transition()
        idle_transition = StateMachine.Transition()
        jump_transition = StateMachine.Transition()
        climb_transition = StateMachine.Transition()

        # add conditions to the transitions
        # test to see if the player is moving on the x-axis
        min_speed_to_walk = 60

        walk_transition.add_condition(lambda: abs(self.player.rigid_body.velocity.x) > min_speed_to_walk)
        walk_transition.add_condition(lambda: self.player.get_script("player plat move").moving)
        walk_transition.add_condition(lambda: self.player.get_script("player plat move").grounded)
        walk_transition.add_condition(lambda: not self.player.get_script("player climb").climbing)

        idle_transition.add_condition(lambda: abs(self.player.rigid_body.velocity.x) < min_speed_to_walk or not self.player.get_script("player plat move").moving)
        idle_transition.add_condition(lambda: self.player.get_script("player plat move").grounded)
        idle_transition.add_condition(lambda: not self.player.get_script("player climb").climbing)

        jump_transition.add_condition(lambda: not self.player.get_script("player plat move").grounded)
        jump_transition.add_condition(lambda: not self.player.get_script("player climb").climbing)

        climb_transition.add_condition(lambda: self.player.get_script("player climb").colliding_with_ladder())
        climb_transition.add_condition(lambda: self.player.get_script("player climb").climbing)

        # set up transitions between states
        self.player_anim_handler.add_bi_transition("idle", "walking", walk_transition, idle_transition)

        self.player_anim_handler.add_bi_transition("idle", "jumping", jump_transition, idle_transition)
        self.player_anim_handler.add_bi_transition("walking", "jumping", jump_transition, walk_transition)

        self.player_anim_handler.add_bi_transition("idle", "climbing", climb_transition, idle_transition)
        self.player_anim_handler.add_bi_transition("walking", "climbing", climb_transition, walk_transition)
        self.player_anim_handler.add_bi_transition("jumping", "climbing", climb_transition, jump_transition)

    def create_ladder(self, ladder_body, ladder_top, height, x, y):
        img = create_img_from_tile(ladder_body, ladder_body.get_width(), height)

        # pad image on top of the ladder
        img = conjoin_surfaces_vertically(ladder_top, img)

        ladder = self.create_game_object(img)
        ladder.collider.is_trigger = True
        ladder.transform.position = Vector2(x, y)

        new_w = ladder.collider.box.w - 80
        new_h = ladder.collider.box.h - 50
        ladder.collider.set_box(new_w, new_h)

        ladder.tag = "ladder"

        self.ladders.append(ladder)


engine.set_world(PlatformWorld())
engine.run()

