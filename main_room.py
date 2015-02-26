
from world import *
from engine import *
from components import BehaviorScript


engine = Engine(1200, 700)


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


class ElevatorPlatMovement(BehaviorScript):

    def __init__(self, spawn_point, script_name):
        super(ElevatorPlatMovement, self).__init__(script_name)

        self.velocity = Vector2(0, -100)
        self.spawn_point = spawn_point

    def update(self):
        dt = self.entity.world.engine.delta_time
        transform = self.entity.transform
        transform.position += self.velocity * dt

    def collision_event(self, other_collider):

        # reset to the bottom
        if other_collider.entity.tag == "ceiling":
            self.entity.transform.position.x = self.spawn_point.x
            self.entity.transform.position.y = self.spawn_point.y


# add movement to a platform but have it ignore physical properties
class PlatformMovement(BehaviorScript):

    def __init__(self, script_name):
        super(PlatformMovement, self).__init__(script_name)
        self.h_speed = 100
        self.velocity = Vector2(self.h_speed, 0)

    # implement custom movement without rigid
    def update(self):
        dt = self.entity.world.engine.delta_time
        transform = self.entity.transform
        transform.position += self.velocity * dt

        w = self.entity.collider.box.width

        right_limit = 2000
        left_limit = 500

        right = transform.position.x + w/2
        left = transform.position.x - w/2

        if right > right_limit:
            delta = right - right_limit
            transform.position.x -= delta

            self.velocity.x *= -1

        elif left < left_limit:
            delta = left_limit - left
            transform.position.x += delta

            self.velocity *= -1

    def collision_event(self, other_collider):

        # have the player go along with the platform
        if other_collider.entity.name == "player":
            other_collider.entity.rigid_body.velocity.x = self.velocity.x

            # apply friction sliding ???


class PlayerMovement(BehaviorScript):

    def __init__(self, script_name):
        super(PlayerMovement, self).__init__(script_name)
        self.h_speed = 250
        self.v_speed = 400

        self.grounded = True

        self.holding_crate = False

    def update(self):

        keys = pygame.key.get_pressed()

        velocity = self.entity.rigid_body.velocity

        if keys[pygame.K_a]:
            velocity.x = -self.h_speed

        if keys[pygame.K_d]:
            velocity.x = self.h_speed

        if keys[pygame.K_LCTRL]:
            self.holding_crate = True

        else:
            self.holding_crate = False

    def take_input(self, event):

        if event.type == pygame.KEYDOWN:

            # check that we are grounded
            # if event.key == pygame.K_SPACE and self.grounded :
            #     self.entity.rigid_body.velocity.y = -self.v_speed
            #
            #     # we are no longer grounded
            #     self.grounded = False

            # check that we are grounded
            if event.key == pygame.K_SPACE:
                self.entity.rigid_body.velocity.y = -self.v_speed

    def collision_event(self, other_collider):

        tag = other_collider.entity.tag

        # collided with a wall, floor, platform
        if tag == "wall" or tag == "floor" or tag == "platform":

            y_player = self.entity.transform.position.y
            h_player = self.entity.collider.box.height
            player_lower_bound = y_player + h_player/2

            y_other = other_collider.entity.transform.position.y
            h_other = other_collider.entity.collider.box.height
            other_upper_bound = y_other - h_other/2

            # check if we collided from the top
            # subtract 1 - this is like a tolerance to handle when the colliders overlap
            if player_lower_bound - 1 < other_upper_bound:
                self.grounded = True

        if other_collider.entity.tag == "box":

            # check if the player hits the box from the sides
            # add a small tolerance to the right/left values due to collider overlaps
            on_left = self.entity.collider.box.right-5 < other_collider.box.left
            on_right = self.entity.collider.box.left+5 > other_collider.box.right

            direction = 1

            if on_right:
                direction = -1

            if self.grounded and self.holding_crate and (on_left or on_right):
                other_collider.entity.rigid_body.velocity.x = 2*self.h_speed/3.0 * direction


class PlayerClimbing(BehaviorScript):

    def __init__(self, script_name):
        super(PlayerClimbing, self).__init__(script_name)

        self.climb_speed = 200.0
        self.move_up = False
        self.move_down = False

    def update(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_w]:
            self.move_up = True

        else:
            self.move_up = False

        if keys[pygame.K_s]:
            self.move_down = True

        else:
            self.move_down = False

    def collision_event(self, other_collider):

        if other_collider.entity.tag == "ladder":

            grounded = self.entity.get_script("player move").grounded

            print(grounded)

            if not grounded:
                self.entity.rigid_body.velocity.y = 0
                self.entity.rigid_body.velocity.x *= 0.1

            if self.move_up:
                self.entity.rigid_body.velocity.y = -self.climb_speed
                self.entity.get_script("player move").grounded = False

            elif self.move_down:
                self.entity.rigid_body.velocity.y = self.climb_speed


class PlatformWorld(World):

    def __init__(self):
        super(PlatformWorld, self).__init__()

        self.player = None

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
        #background_image.fill( (0, 0, 0) )
        #background_image.set_alpha(100)

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

        box_img = pygame.image.load("assets/Assets/Block_v1_100x100-01.png").convert_alpha()

        box = self.create_game_object(box_img)
        box.transform.position = Vector2(900, 300)
        box.renderer.depth = -5
        box.collider.restitution = 0
        box.collider.surface_friction = 0.8

        box.add_component(RigidBody())
        box.rigid_body.velocity = Vector2(0.0, 0.0)
        box.rigid_body.gravity_scale = 2
        box.tag = "box"

        # set up camera
        render = self.get_system(RenderSystem.tag)
        render.camera = self.create_entity()
        render.camera.add_component(Transform(Vector2(0, 0)))
        render.camera.add_script(CameraFollow("cam follow", self.player.transform, w, h))

    def load_ladders(self):
        ladder_color = (200, 200, 200)
        ladder_img = pygame.Surface((50, 440)).convert()
        ladder_img.fill(ladder_color)
        ladder1 = self.create_game_object(ladder_img)
        ladder1.collider.is_trigger = True
        ladder1.transform.position = Vector2(950, 395)
        ladder1.tag = "ladder"

    def load_platforms(self):

        plat_color = (30, 30, 30)

        img = RenderSystem.create_solid_image(200, 30, plat_color)
        plat_a = self.create_game_object(img)
        plat_a.transform.position = Vector2(300, 250)
        set_platform_attributes(plat_a)

        img = RenderSystem.create_solid_image(400, 30, plat_color)
        plat_b = self.create_game_object(img)
        plat_b.transform.position = Vector2(400, 400)
        set_platform_attributes(plat_b)

        img = RenderSystem.create_solid_image(250, 50, plat_color)
        plat_c = self.create_game_object(img)
        plat_c.transform.position = Vector2(1100, 200)
        set_platform_attributes(plat_c)

        img = RenderSystem.create_solid_image(250, 50, plat_color)
        plat_d = self.create_game_object(img)
        plat_d.transform.position = Vector2(1700, 200)
        set_platform_attributes(plat_d)

        img = RenderSystem.create_solid_image(250, 50, plat_color)
        plat_e = self.create_game_object(img)
        plat_e.transform.position = Vector2(1500, -100)
        set_platform_attributes(plat_e)

        img = RenderSystem.create_solid_image(400, 120, plat_color)
        plat_f = self.create_game_object(img)
        plat_f.transform.position = Vector2(2150, 250)
        set_platform_attributes(plat_f)

        img = RenderSystem.create_solid_image(200, 30, plat_color)
        plat_g = self.create_game_object(img)
        plat_g.transform.position = Vector2(2250, 0)
        set_platform_attributes(plat_g)

        img = RenderSystem.create_solid_image(300, 30, plat_color)
        plat_h = self.create_game_object(img)
        plat_h.transform.position = Vector2(1800, -150)
        set_platform_attributes(plat_h)
        plat_h.add_script(PlatformMovement("plat move"))

        img = RenderSystem.create_solid_image(800, 150, plat_color)
        plat_i = self.create_game_object(img)
        plat_i.transform.position = Vector2(3150, 300)
        set_platform_attributes(plat_i)

        img = RenderSystem.create_solid_image(300, 50, plat_color)
        plat_j = self.create_game_object(img)
        plat_j.transform.position = Vector2(4000, 120)
        set_platform_attributes(plat_j)

    def load_walls(self):

        wall_color = (100, 100, 100)

        img = RenderSystem.create_solid_image(200, 500, wall_color)
        wall_a = self.create_game_object(img)
        wall_a.transform.position = Vector2(100, 350)
        set_wall_attributes(wall_a)

        img = RenderSystem.create_solid_image(200, 350, wall_color)
        wall_b = self.create_game_object(img)
        wall_b.transform.position = Vector2(80, -200)
        set_wall_attributes(wall_b)

        img = RenderSystem.create_solid_image(200, 200, wall_color)
        wall_c = self.create_game_object(img)
        wall_c.transform.position = Vector2(4600, 500)
        set_wall_attributes(wall_c)

        img = RenderSystem.create_solid_image(600, 170, wall_color)
        wall_d = self.create_game_object(img)
        wall_d.transform.position = Vector2(4400, 180)
        set_wall_attributes(wall_d)

        img = RenderSystem.create_solid_image(200, 200, wall_color)
        wall_e = self.create_game_object(img)
        wall_e.transform.position = Vector2(4600, 0)
        set_wall_attributes(wall_e)

    def load_floors(self):

        for i in range(0, 10):

            plat_img = pygame.image.load("assets/Assets/Platform_Tile-01.png").convert_alpha()

            plat_sample = self.create_entity()
            plat_sample.add_component(Transform(Vector2(50*i, 300)))
            plat_sample.add_component(Renderer(plat_img))
            plat_sample.renderer.depth = -10

        floor_color = (50, 50, 50)

        w = self.engine.display.get_width()
        h = self.engine.display.get_height()

        img = RenderSystem.create_solid_image(w*2, 200, floor_color)

        floor_img = pygame.image.load("assets/Assets/Tileable_Floor-01.png").convert_alpha()

        floor_over = self.create_entity()
        floor_over.add_component(Transform(Vector2(0, 600)))
        floor_over.add_component(Renderer(floor_img))

        floor_over.renderer.depth = -100

        floor_a = self.create_game_object(img)
        floor_a.transform.position = Vector2(w, h)
        set_floor_attributes(floor_a)

        img = RenderSystem.create_solid_image(1000, 200, floor_color)
        x = w*2 + 100 + 500 + 50
        floor_b = self.create_game_object(img)
        floor_b.transform.position = Vector2(x, h)
        set_floor_attributes(floor_b)

        img = RenderSystem.create_solid_image(1000, 200, floor_color)
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

        # frames to demonstrate animation
        frame_list = list()

        for i in range(0, 10):
            path = "assets/GustavAnimations_Final/Idle/"
            frame_file = "Idle_"
            number = i + 1
            frame_file += str(number) + ".png"
            path += frame_file

            frame = pygame.image.load(path).convert_alpha()
            frame_list.append(frame)

        self.player = self.create_game_object(frame_list[0])
        self.player.add_component(RigidBody())
        self.player.transform.position = Vector2(230, 480)
        self.player.renderer.depth = -10
        self.player.rigid_body.gravity_scale = 2
        self.player.collider.restitution = 0
        self.player.name = "player"

        self.player.collider.box.width = 50
        self.player.collider.offset.x = -10

        self.player.add_script(PlayerClimbing("player climb"))
        self.player.add_script(PlayerMovement("player move"))

        # set up animation
        animation = Animator.Animation()

        for frame in frame_list:
            animation.add_frame(frame)

        # set time between frames in seconds
        animation.frame_latency = 0.105

        # set the first animation
        animator = Animator()
        animator.current_animation = animation

        # add animator to player
        self.player.add_component(animator)

    def load_elevators(self):

        # select a filler color
        plat_color = (90, 90, 90)

        # create elevator platforms
        for i in range(0, 4):

            img = RenderSystem.create_solid_image(140, 50, plat_color)
            platform = self.create_game_object(img)

            x = 2475
            spawn_point = Vector2(x, 700)

            platform.transform.position = Vector2(x, 700 - i*200)
            set_platform_attributes(platform)
            platform.add_script(ElevatorPlatMovement(spawn_point, "elev move"))
            platform.collider.treat_as_dynamic = True

        for i in range(0, 5):

            img = RenderSystem.create_solid_image(180, 50, plat_color)
            platform = self.create_game_object(img)

            x = 3650
            spawn_point = Vector2(x, 700)

            platform.transform.position = Vector2(x, 700 - i*200)
            set_platform_attributes(platform)
            platform.add_script(ElevatorPlatMovement(spawn_point, "elev move"))
            platform.collider.treat_as_dynamic = True


def set_floor_attributes(floor):
    floor.collider.restitution = 0
    floor.collider.surface_friction = 0.75
    floor.renderer.depth = -10
    floor.tag = "floor"


def set_wall_attributes(wall):
    wall.collider.restitution = 0
    wall.collider.surface_friction = 0.8
    wall.tag = "wall"


def set_ceiling_attributes(ceiling):
    ceiling.collider.restitution = 0
    ceiling.collider.surface_friction = 0.8
    ceiling.tag = "ceiling"


def set_platform_attributes(platform):
    platform.renderer.depth = 1
    platform.collider.restitution = 0
    platform.collider.surface_friction = 0.8

engine.set_world(PlatformWorld())
engine.run()