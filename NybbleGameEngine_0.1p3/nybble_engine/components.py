from pygame import Rect
from abc import ABCMeta

from util_math import Vector2


# Base class for all components
class Component (object):

    __metaclass__ = ABCMeta

    def __init__(self):

        # The associated entity
        self.entity = None


# Basic transform that handles position , rotation and scale
class Transform (Component):

    tag = "transform"

    def __init__(self, position=Vector2(0.0, 0.0), degrees=0, x_scale=1, y_scale=1):
        super(Transform, self).__init__()
        self.position = position
        self.degrees = degrees
        self.scale = Vector2(x_scale, y_scale)


# Contains image to render
# pivot is of type Vector2 - it is the position relative to the image
# which specifies where to start drawing the image from.
# Rendering a image centered on a point would require that
# pivot = Vector2(image.width/2, image.height/2)

class Renderer (Component):
    tag = "render"

    def __init__(self, image, pivot=Vector2(0, 0)):
        super(Renderer, self).__init__()
        self.original_image = image
        self.sprite = image
        self.pivot = pivot

        # the rendering order. 0 is default
        # lower values render last (use for foreground)
        # larger values render first (use for background)
        # USE THE RENDER SYSTEM TO MODIFY THIS VALUE
        self.depth = 0

        # if the renderer is affected by the camera
        self.is_static = False


# Only holds velocity vector and mass scalar, may be expanded in future development
# for a better physics simulations
class RigidBody (Component):
    tag = "rigid body"

    def __init__(self, velocity=Vector2(0.0, 0.0), m=1.0):
        super(RigidBody, self).__init__()
        self.velocity = velocity
        self.mass = m

        # gravity scale
        self.gravity_scale = 0

        self.gravity_enabled = False

        #self.fixed_angle = True
        #self.angular_velocity = Vector2(0, 0)
        #self.angular_drag = 0


class Collider(Component):
    tag = "collider"

    def __init__(self):
        super(Collider, self).__init__()

        # A value of 1 means no friction
        # A value of 0 means total friction, brings it to a complete halt.
        # Higher values add energy to the object it is colliding with
        self.surface_friction = 1

        # Bouncy-ness of a collider
        # A value of 0 means no bouncing effect
        # A value of 1 means completely elastic collision effect
        self.restitution = 0

        # It flags a static collider to be treated as one that can move but
        # does not have a rigid body. This is used to apply collision resolution
        # on the static collider.
        self.treat_as_dynamic = False


class BoxCollider (Collider):
    tag = "box collider"

    def __init__(self, width=0.0, height=0.0):
        super(BoxCollider, self).__init__()
        self.box = Rect(0, 0, width, height)

    def set_box(self, width, height):
        self.box = Rect(0, 0, width, height)


class CircleCollider(Collider):
    tag = "circle collider"

    def __init__(self, radius=1.0):
        super(CircleCollider, self).__init__()
        self.radius = radius


class Animator(Component):

    tag = "animator"

    class Animation:

        def __init__(self):

            # name to identity the animation
            self.name = "base animation"

            # a list of images
            self.frames = list()

            # time between frames in seconds
            self.frame_latency = 1.0

        def add_frame(self, frame):
            self.frames.append(frame)

    def __init__(self):
        super(Animator, self).__init__()
        self.current_animation = None

        # track how much time has passed
        self.latency_accumulator = 0.0

        # the current frame from the animation
        self.current_frame_index = 0

    def _update_animation(self):

        anim = self.current_animation

        if anim is not None:

            num_of_frames = len(anim.frames)

            if num_of_frames > 0:

                # time to go to the next frame
                if self.latency_accumulator > anim.frame_latency:

                    self.current_frame_index += 1

                    # cycle through frames
                    self.current_frame_index %= num_of_frames

                    # Update the renderer's image to display
                    index = self.current_frame_index
                    self.entity.renderer.sprite = anim.frames[index]

                    # reset accumulator
                    self.latency_accumulator = 0.0

                # increment accumulator
                dt = self.entity.world.engine.delta_time
                self.latency_accumulator += dt


# This component simply flags which entity can receive input.
class InputComponent (Component):
    tag = "input"

    def __init__(self):
        super(InputComponent, self).__init__()


class Script (object):
    tag = "script"

    def __init__(self, script_name):
        self.script_name = script_name

    def take_input(self, event):
        pass

    # Called at every game iteration. Used for logic.
    def update(self):
        pass

    # compare equality by script name
    def __eq__(self, other):
        return self.script_name == other.script_name


class WorldScript(Script):

    tag = "world script"

    def __init__(self, script_name):
        super(WorldScript, self).__init__(script_name)
        self.script_name = script_name
        self.world = None


class BehaviorScript(Script):

    tag = "behavior script"

    def __init__(self, script_name):
        super(Script, self).__init__()
        self.script_name = script_name
        self.entity = None

    # The physics system calls this function when the belonging
    # entity of this script collides with another entity's collider
    def collision_event(self, other_collider):
        pass