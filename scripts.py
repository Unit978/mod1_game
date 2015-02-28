
import pygame
from components import BehaviorScript
from util_math import Vector2

from systems import PhysicsSystem


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
            x_scale = self.entity.transform.scale.x
            y_scale = self.entity.transform.scale.y

            # change orientation of the transform based on where the player is facing.
            # turned left
            if event.key == pygame.K_a:
                # was facing right
                if x_scale > 0:
                    self.entity.transform.scale_by(-x_scale, y_scale)

                    # get the animation dictionary from the world
                    animations = self.entity.world.player_anims

                    # set the walking animation
                    #self.entity.animator.set_animation(animations["Walking"])

            # turned right
            elif event.key == pygame.K_d:
                # was facing left
                if x_scale < 0:
                    self.entity.transform.scale_by(-x_scale, y_scale)

                    # get the animation dictionary from the world
                    animations = self.entity.world.player_anims

                    # set the running animation
                    #self.entity.animator.set_animation(animations["Walking"])

            # check that we are grounded
            elif event.key == pygame.K_SPACE and self.grounded:
                self.entity.rigid_body.velocity.y = -self.v_speed

                animations = self.entity.world.player_anims

                # set the idle animation
                self.entity.animator.set_animation(animations["Jumping"])

                # shrink the collision box
                #self.entity.collider.box.h = 40

                # we are no longer grounded
                self.grounded = False

        elif event.type == pygame.KEYUP:
            # player decides to stop moving
            if event.key == pygame.K_a or event.key == pygame.K_d:
                if self.entity.get_script("player plat move").grounded:
                    animations = self.entity.world.player_anims
                    # set the idle animation
                    self.entity.animator.set_animation(animations["Idle"])

    def collision_event(self, other_collider):

        tag = other_collider.entity.tag

        # collided with a wall, floor, platform
        if tag == "wall" or tag == "floor" or tag == "platform" or "box":

            # hit from the top which means that this collider bottom side was hit by the other collider
            if PhysicsSystem.calc_box_hit_orientation(self.entity.collider, other_collider) == PhysicsSystem.bottom:

                # came back from falling down
                if not self.grounded:

                    animations = self.entity.world.player_anims
                    # set the running animation
                    self.entity.animator.set_animation(animations["Idle"])

                self.grounded = True

        if other_collider.entity.tag == "box":

            # check if the player hits the box from the sides
            side = PhysicsSystem.calc_box_hit_orientation(self.entity.collider, other_collider)

            direction = 1
            # hit the other object from the left
            if side == PhysicsSystem.left:
                direction = -1

            if side == PhysicsSystem.left or side == PhysicsSystem.right:
                if self.grounded and self.holding_crate:
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

    def take_input(self, event):
        if self.move_down or self.move_up:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w or event.key == pygame.K_s:

                    animations = self.entity.world.player_anims
                    # set the running animation
                    self.entity.animator.set_animation(animations["Climbing"])

    def collision_event(self, other_collider):

        if other_collider.entity.tag == "ladder":

            grounded = self.entity.get_script("player plat move").grounded

            if self.move_up:
                if not grounded:
                    self.entity.rigid_body.velocity.y = 0
                    self.entity.rigid_body.velocity.x *= 0.1
                self.entity.rigid_body.velocity.y = -self.climb_speed
                self.entity.get_script("player plat move").grounded = False

            elif self.move_down:
                if not grounded:
                    self.entity.rigid_body.velocity.y = 0
                    self.entity.rigid_body.velocity.x *= 0.1
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