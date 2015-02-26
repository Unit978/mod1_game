
import pygame
from components import BehaviorScript
from util_math import Vector2


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


# This script defines the behavior of how the player moves in a 2d side scroller world
class PlayerPlatformMovement(BehaviorScript):

    def __init__(self, script_name):
        super(PlayerPlatformMovement, self).__init__(script_name)
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

            grounded = self.entity.get_script("player plat move").grounded

            print(grounded)

            if not grounded:
                self.entity.rigid_body.velocity.y = 0
                self.entity.rigid_body.velocity.x *= 0.1

            if self.move_up:
                self.entity.rigid_body.velocity.y = -self.climb_speed
                self.entity.get_script("player plat move").grounded = False

            elif self.move_down:
                self.entity.rigid_body.velocity.y = self.climb_speed


# This script defines the behavior of how the player moves from a top down
# view world.
class PlayerTopDownMovement(BehaviorScript):

    def __init__(self, script_name):
        super(PlayerTopDownMovement, self).__init__(script_name)
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