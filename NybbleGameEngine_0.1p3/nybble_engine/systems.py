
from abc import abstractmethod

from components import *
from util_math import get_relative_rect_pos
from collections import deque

import pygame


class System (object):
    __metaclass__ = ABCMeta

    def __init__(self):
        # A reference to the world this system is operating in.
        self.world = None

    @abstractmethod
    def process(self, entities):
        """
        This is where the behavior of the system is implemented.
        """


# Detects collision between objects with Collision Box Components
# Handles basic bouncing collision between objects.

class PhysicsSystem (System):

    __metaclass__ = ABCMeta

    tag = "physics system"

    top = 0
    bottom = 1
    left = 2
    right = 3

    gravity = Vector2(0.0, 500.0)

    # This value represents a magnitude of velocity to ignore and treat it as zero
    ignore_velocity_epsilon = 10

    # holds pairs of colliding entities per iteration.
    collision_queue = deque()

    def __init__(self):
        super(PhysicsSystem, self).__init__()

    def process(self, entities):

        # empty the collision queue
        PhysicsSystem.collision_queue.clear()

        for eA in entities:

            transform_a = eA.transform
            collider_a = eA.collider
            rigid_body_a = eA.rigid_body

            if collider_a is not None and (rigid_body_a is not None or collider_a.treat_as_dynamic):

                # Move the rigid body
                if rigid_body_a is not None:
                    self._integrate_motion(transform_a, rigid_body_a)

                # Find another entity that it may collide with
                for eB in entities:

                    transform_b = eB.transform
                    collider_b = eB.collider

                    # Check that coll_comp_b is valid and that coll_comp_a is not colliding with itself
                    if collider_b is not None and eA is not eB:

                        collision_occurred = False

                        # box to box collision
                        if collider_a.tag == BoxCollider.tag and collider_b.tag == BoxCollider.tag:

                            # Get the relative collision box positions to their transforms.
                            get_relative_rect_pos(transform_a.position, collider_a.box)
                            get_relative_rect_pos(transform_b.position, collider_b.box)

                            # check for collision
                            if collider_a.box.colliderect(collider_b.box):
                                collision_occurred = True

                                if rigid_body_a is not None:
                                    PhysicsSystem.box2box_response(collider_a, collider_b)

                        # circle to circle collision
                        elif collider_a.tag == CircleCollider.tag and collider_b.tag == CircleCollider.tag:

                            # check if circles collided
                            if PhysicsSystem._circle2circle_collision(collider_a, collider_b):
                                collision_occurred = True

                                if rigid_body_a is not None:
                                    PhysicsSystem.circle2circle_response(collider_a, collider_b)

                        # circle to box
                        elif collider_a.tag == CircleCollider.tag and collider_b.tag == BoxCollider.tag:

                            # create a temporary box collider associated to A
                            box_collider_a = BoxCollider(collider_a.radius*2, collider_a.radius*2)
                            box_collider_a.entity = collider_a.entity
                            box_collider_a.restitution = collider_a.restitution
                            box_collider_a.surface_friction = collider_a.surface_friction

                            # Get the relative collision box positions to their transforms.
                            get_relative_rect_pos(transform_a.position, box_collider_a.box)
                            get_relative_rect_pos(transform_b.position, collider_b.box)

                            # check for collision
                            if PhysicsSystem._circle2box_collision(collider_a, collider_b):
                                collision_occurred = True

                                if rigid_body_a is not None:
                                    PhysicsSystem.box2box_response(box_collider_a, collider_b)

                        if collision_occurred:
                            # add collision event into the queue
                            PhysicsSystem.collision_queue.append((eA, eB))

                            # call the collision inside the scripts
                            for s in eA.scripts:
                                s.collision_event(collider_b)

                            for s in eB.scripts:
                                s.collision_event(collider_a)

    @staticmethod
    def _calc_1d_elastic_collision_velocity(vel_a, mass_a, vel_b, mass_b):

        numerator = vel_a * (mass_a - mass_b) + 2 * mass_b * vel_b

        denominator = mass_a + mass_b

        return numerator / denominator

    # collider a is the circle
    # collider b is the box
    @staticmethod
    def _circle2box_collision(collider_a, collider_b):
        position_a = collider_a.entity.transform.position

        # Find the closest point on the box to the center of the circle
        x_closest = position_a.x
        y_closest = position_a.y

        # Check if left side of the box is closer on the x coordinate
        if position_a.x < collider_b.box.left:
            x_closest = collider_b.box.left

        # Check if left side of the box is closer on the x coordinate
        elif position_a.x > collider_b.box.right:
            x_closest = collider_b.box.right

        # else --- x coordinate of circle is in between the left and right sides of the box

        # Do the same for the y-coordinate/top and bottom sides of the box
        if position_a.y < collider_b.box.top:
            y_closest = collider_b.box.top

        elif position_a.y > collider_b.box.bottom:
            y_closest = collider_b.box.bottom

        # Collision occurs if the distance from the center of the circle to the closest point on the box
        # is less than the radius of the circle.

        distance_to_closest = Vector2(x_closest, y_closest)

        distance_to_closest -= collider_a.entity.transform.position

        # square radius
        r_sq = collider_a.radius * collider_a.radius

        return distance_to_closest.sq_magnitude() < r_sq

    @staticmethod
    def _circle2circle_collision(collider_a, collider_b):

        # get the radii
        ra = collider_a.radius
        rb = collider_b.radius

        rsum_sq = ra + rb

        # square the radii sum
        rsum_sq *= rsum_sq

        # find distance between the two colliders
        distance = collider_b.entity.transform.position - collider_a.entity.transform.position

        # check if the distance is smaller than the sum of the radii, if it is then there is a collision
        # use squared values to avoid sqrt computation of vec2.magnitude()
        return distance.sq_magnitude() < rsum_sq

    @staticmethod
    def circle2circle_response(collider_a, collider_b):

        rigid_a = collider_a.entity.rigid_body
        rigid_b = collider_b.entity.rigid_body

        transform_a = rigid_a.entity.transform
        transform_b = rigid_b.entity.transform

        # do collision resolution first
        # collision with rigid body
        if rigid_b is not None:
            PhysicsSystem._resolve_circle2circle_with_rigid(transform_a, collider_a, transform_b, collider_b)

        # collision with another collider only
        else:
            PhysicsSystem._resolve_circle2circle_with_collider(transform_a, collider_a, transform_b, collider_b)

        # apply collision response

        # find the unit normal of the two circles
        normal = Vector2.get_normal(transform_b.position - transform_a.position)

        # find the unit tangent of the circles
        tangent = Vector2(-normal.y, normal.x)

        # project velocity of A to the normal
        normal_project_a = rigid_a.velocity.dot(normal)

        # project velocity of A to the tangent
        tangent_project_a = rigid_a.velocity.dot(tangent)

        # same for B
        normal_project_b = rigid_b.velocity.dot(normal)
        tangent_project_b = rigid_b.velocity.dot(tangent)

        # NOTE: tangential velocities do not change

        # find normal velocities after collision
        mass_a = rigid_a.mass
        mass_b = rigid_b.mass

        vel_a = normal_project_a
        vel_b = normal_project_b

        normal_project_a = PhysicsSystem._calc_1d_elastic_collision_velocity(vel_a, mass_a, vel_b, mass_b)
        normal_project_b = PhysicsSystem._calc_1d_elastic_collision_velocity(vel_b, mass_b, vel_a, mass_a)

        # convert normals and tangents to vectors
        normal_a = normal_project_a * normal
        tangent_a = tangent_project_a * tangent

        normal_b = normal_project_b * normal
        tangent_b = tangent_project_b * tangent

        # create the new velocities
        rigid_a.velocity = normal_a + tangent_a

        # BUG - applying restitution causes "attachment" between colliders.
        # Cause Theory: could be a result of the ignore velocity epsilon
        # apply restitution
        #rigid_a.velocity *= collider_b.restitution

        if rigid_b is not None:
            rigid_b.velocity = normal_b + tangent_b
            #rigid_b.velocity *= collider_a.restitution


    @staticmethod
    def _resolve_circle2circle_with_rigid(transform_a, collider_a, transform_b, collider_b):

        # distance between the two centers of the circles
        distance = transform_b.position - transform_a.position

        # find the unit normal from a to b
        normal_ab = Vector2.get_normal(distance)

        # overlapping distance
        overlap_mag = collider_a.radius + collider_b.radius - distance.magnitude()
        overlap_mag /= 2

        overlap_vec = normal_ab * overlap_mag

        # resolve circle a by translating it by the value of the overlap
        transform_a.position -= overlap_vec

        # same resolve for b but in the other direction
        #transform_b.position += overlap_vec

    # Same as with_rigid() but collider_b's rigid does not exist
    @staticmethod
    def _resolve_circle2circle_with_collider(transform_a, collider_a, transform_b, collider_b):

        distance = transform_b.position - transform_a.position

        normal_ab = Vector2.get_normal(distance)

        overlap_mag = collider_a.radius + collider_b.radius - distance.magnitude()
        overlap_mag /= 2

        overlap_vec = normal_ab * overlap_mag
        transform_a.position -= overlap_vec

    # Apply bouncing between two simplified rigid bodies. For right now,
    # rigid bodies are entities that do not rotate their collision polygons.
    # Basically, they are treated as particles
    # This should be called if there was a detected collision
    @staticmethod
    def box2box_response(collider_a, collider_b):

        rigid_a = collider_a.entity.rigid_body
        rigid_b = collider_b.entity.rigid_body

        # Obtain necessary components
        transform_a = collider_a.entity.transform
        transform_b = collider_b.entity.transform

        position_a = transform_a.position
        position_b = transform_b.position

        # Use the Minkowski sum(differencce) of the two box colliders in
        # order to determine which sides of the boxes collide.
        # This is relative to coll_comp_a.

        width = 0.5 * (collider_a.box.width + collider_b.box.width)
        height = 0.5 * (collider_a.box.height + collider_b.box.height)

        # Pay close attention to the operands
        dx = position_b.x - position_a.x
        dy = position_a.y - position_b.y

        # changes the velocity vector
        x_change = 1
        y_change = 1

        # Another way to detect collision
        # if abs(dx) <= width and abs(dy) <= height:

        wy = width * dy
        hx = height * dx

        # ------- determine where it hit ------- #
        if wy > hx:

            # collision from the top
            if wy > -hx:
                y_change = -1
                orientation = PhysicsSystem.top

            # collision from the left
            # wy <= -hx
            else:
                x_change = -1
                orientation = PhysicsSystem.left

        # wy <= hx
        else:
            # collision from the right
            if wy > -hx:
                x_change = -1
                orientation = PhysicsSystem.right

            # collision from the bottom
            # wy <= -hx
            else:
                y_change = -1
                orientation = PhysicsSystem.bottom

        # Apply collision resolution to avoid colliders getting stuck with each other
        # Collision with rigid body
        if rigid_b is not None:
            PhysicsSystem._resolve_box2box_with_rigid(orientation, transform_a, collider_a, transform_b, collider_b)

            # mass_a = rigid_a.mass
            # mass_b = rigid_b.mass
            #
            # vel_a = rigid_a.velocity.x
            # vel_b = rigid_b.velocity.x
            #
            # rigid_a.velocity.x = PhysicsSystem._calc_1d_elastic_collision_velocity(vel_a, mass_a, vel_b, mass_b)
            #
            # vel_a = rigid_a.velocity.y
            # vel_b = rigid_b.velocity.y
            #
            # rigid_a.velocity.y = PhysicsSystem._calc_1d_elastic_collision_velocity(vel_a, mass_a, vel_b, mass_b)

            if orientation == PhysicsSystem.top or orientation == PhysicsSystem.bottom:
                rigid_b.velocity.y *= collider_a.restitution
                rigid_b.velocity.x *= collider_a.surface_friction

            elif orientation == PhysicsSystem.left or orientation == PhysicsSystem.right:
                rigid_b.velocity.x *= collider_a.restitution
                #rigid_a.velocity.y *= collider_b.surface_friction


            # Invert velocities according to orientation
            rigid_b.velocity.x *= x_change
            rigid_b.velocity.y *= y_change

        # Collision with another collider only
        else:
            PhysicsSystem._resolve_box2box_with_collider(orientation, transform_a, collider_a, collider_b)

            # Invert velocity components depending on which side of the boxes hit
            rigid_a.velocity.x *= x_change
            rigid_a.velocity.y *= y_change

        # This was collider with collider collision. This means that the collider is treated
        # as a dynamic body that moves and needed collision resolution to be applied.
        if rigid_a is None:
            return

        # Apply restitution based on the orientation that the boxes hit
        # and apply frictional forces between the collider's surfaces
        if orientation == PhysicsSystem.top or orientation == PhysicsSystem.bottom:
            rigid_a.velocity.y *= collider_b.restitution
            rigid_a.velocity.x *= collider_b.surface_friction

        elif orientation == PhysicsSystem.left or orientation == PhysicsSystem.right:
            rigid_a.velocity.x *= collider_b.restitution
            #rigid_a.velocity.y *= collider_b.surface_friction

        # Zero out velocity components if they are too small in order to avoid
        # jittery behavior between a moving collider and a static one.
        if rigid_b is None:
            if abs(rigid_a.velocity.y) < PhysicsSystem.ignore_velocity_epsilon:
                if orientation == PhysicsSystem.top or orientation == PhysicsSystem.bottom:
                    rigid_a.velocity.y = 0

            if abs(rigid_a.velocity.x) < PhysicsSystem.ignore_velocity_epsilon:
                if orientation == PhysicsSystem.left or orientation == PhysicsSystem.right:
                    rigid_a.velocity.x = 0

    @staticmethod
    def _resolve_box2box_with_rigid(orient, transform_a, collider_a, transform_b, collider_b):
        if orient == PhysicsSystem.top:

            # amount that coll_comp_a went into coll_comp_b
            delta = collider_b.box.bottom - collider_a.box.top
            delta *= 0.5

            # move coll_comp_a out of coll_comp_b by translating it downwards
            transform_a.position.y += delta

            # translate entity_b upwards
            #transform_b.position.y -= delta

        elif orient == PhysicsSystem.bottom:
            delta = collider_a.box.bottom - collider_b.box.top
            delta *= 0.5

            # translate upwards
            transform_a.position.y -= delta
            #transform_b.position.y += delta

        elif orient == PhysicsSystem.left:
            delta = collider_b.box.right - collider_a.box.left
            delta *= 0.5

            # translate to the right
            transform_a.position.x += delta
            #transform_b.position.x -= delta

        elif orient == PhysicsSystem.right:
            delta = collider_a.box.right - collider_b.box.left
            delta *= 0.5

            # translate to the left
            transform_a.position.x -= delta
            #transform_b.position.x += delta

    @staticmethod
    def _resolve_box2box_with_collider(orientation, transform_a, collider_a, collider_b):
        if orientation == PhysicsSystem.top:

            # amount that coll_comp_a went into coll_comp_b
            delta = collider_b.box.bottom - collider_a.box.top
            delta *= 0.5

            # move coll_comp_a out of coll_comp_b by translating it downwards
            transform_a.position.y += delta

        elif orientation == PhysicsSystem.bottom:
            delta = collider_a.box.bottom - collider_b.box.top
            delta *= 0.5

            # translate upwards
            transform_a.position.y -= delta

        elif orientation == PhysicsSystem.left:
            delta = collider_b.box.right - collider_a.box.left
            delta *= 0.5

            # translate to the right
            transform_a.position.x += delta

        elif orientation == PhysicsSystem.right:
            delta = collider_a.box.right - collider_b.box.left
            delta *= 0.5

            # translate to the left
            transform_a.position.x -= delta

    def _integrate_motion(self, transform, rigid_body):
        # time step
        dt = self.world.engine.delta_time

        transform.position += dt * rigid_body.velocity

        # apply gravity
        rigid_body.velocity += dt * rigid_body.gravity_scale * PhysicsSystem.gravity


# Requires for an entity to have a render and transform component
# Holds the surface to render images
class RenderSystem (System):

    tag = "render system"

    def __init__(self):
        super(RenderSystem, self).__init__()

        # Dictionary of layers to simulate z-coordinate for
        # depth rendering.
        # Everything is added to the key '0' by default
        self.scene = dict()

        # default layer
        self.scene[0] = list()

        # Contains the layer enumerations in order from least to greatest
        self.ordered_layers = list()

        # Set up display for rendering.
        self.camera = None

    # for utility to create a solid image surface of some color
    @staticmethod
    def create_solid_image(width, height, color):
        surface = pygame.Surface((width, height)).convert()
        surface.fill(color)
        return surface

    # This should be called once the initial entities have been made and right
    # before the main loop starts unless it is necessary to reconstruct a large
    # portions of entities in the scene.
    def construct_scene(self, entities):

        # clear the entire layer dictionary
        self.scene.clear()

        for e in entities:
            renderer = e.renderer
            if renderer is not None:

                depth = renderer.depth

                # the depth layer doesn't exist yet
                if not (depth in self.scene):

                    # create an empty list for that layer
                    self.scene[depth] = list()

                # add a renderer to that layer
                self.scene[depth].append(renderer)

        # create the layer order
        for key in self.scene:
            self.ordered_layers.append(key)

        # sort the layers
        self.ordered_layers.sort()

        # have the greater values be rendered first (z-coordinate simulation)
        self.ordered_layers.reverse()

    # Add a new entity to the scene.
    # Use this during the run time of the game
    def dynamic_insertion_to_scene(self, entity):
        renderer = entity.renderer
        if renderer is not None:
            depth = renderer.depth

            # layer already exists
            if depth in self.scene:
                self.scene[depth].append(renderer)

            # create new layer and re-sort
            else:
                self.scene[depth] = [renderer]

                # find where this new layers belongs in the layer order
                i = 0
                for layer in self.ordered_layers:

                    # found where to insert the depth
                    if layer > depth:
                        self.ordered_layers.insert(i, depth)
                        return
                    i += 1

                # the depth is the last layer
                self.ordered_layers.append(depth)

    # Use this to change the depth of an entity already in the scene.
    def update_depth(self, entity, new_depth):
        renderer = entity.renderer
        if renderer is not None:

            # save old depth and assign the new one
            old_depth = renderer.depth
            renderer.depth = new_depth

            # check that it exists in the scene
            if old_depth in self.scene:
                renderer_list = self.scene[old_depth]

                # find the renderer's entity
                i = 0
                for r in renderer_list:

                    # entity found - remove the renderer for that layer
                    if r.entity == renderer.entity:
                        renderer_list.pop(i)

                    i += 1

                # reinsert to the new layer
                self.dynamic_insertion_to_scene(entity)

            else:
                print("Renderer had not been added to the scene.")

    def remove_from_scene(self, entity):
        renderer = entity.renderer
        if renderer is not None:

            depth = renderer.depth

            # check that it exists in the scene
            if depth in self.scene:
                renderer_list = self.scene[depth]

                # find the renderer's entity
                i = 0
                for r in renderer_list:

                    # entity found - remove the renderer for that layer
                    if r.entity == renderer.entity:
                        renderer_list.pop(i)

                    i += 1

    def render_scene(self):

        # Iterate through each layer in the scene in order
        for layer in self.ordered_layers:

            renderer_list = self.scene[layer]

            for renderer in renderer_list:

                # access the transform
                entity = renderer.entity
                transform = entity.transform

                # transform exists
                if transform is not None:

                    # Center it around the image pivot
                    position = transform.position - renderer.pivot

                    # Offset image position with the camera if the renderer is not static
                    if self.camera is not None and not renderer.is_static:
                        position -= self.camera.transform.position

                    display = self.world.engine.display
                    display.blit(renderer.sprite, (position.x, position.y))

                else:
                    print("Renderer has no transform associated.")

    def process(self, entities):

        self.render_scene()

        for e in entities:

            # Obtain the proper components.
            transform = e.transform

            # update the animation for an entity if possible
            animator = e.animator
            if animator is not None:
                animator._update_animation()

            # Components found.
            if transform is not None:
                display = self.world.engine.display

                # ------- Debug info -------- #

                x_origin = self.world.origin.x
                y_origin = self.world.origin.y

                # draw collision box
                if self.world.engine.debug:

                    x = transform.position.x
                    y = transform.position.y

                    # adjust for the camera
                    if self.camera is not None:
                        x -= self.camera.transform.position.x
                        y -= self.camera.transform.position.y

                    collider = e.collider
                    rigid_body = e.rigid_body

                    # transform origin crosshair
                    pygame.draw.line(display, (255, 0, 0), (x-50, y), (x+50, y))
                    pygame.draw.line(display, (255, 0, 0), (x, y-50), (x, y+50))

                    # draw position vector relative to the world origin
                    pygame.draw.line(display, (50, 50, 50), (x_origin, y_origin), (x, y))

                    if rigid_body is not None:

                        # obtain a fraction of the velocity vector
                        length = Vector2.get_scaled_by(rigid_body.velocity, 0.2)
                        xend = x + length.x
                        yend = y + length.y

                        # draw the velocity vector of the rigid
                        pygame.draw.line(display, (0, 255, 0), (x, y), (xend, yend))

                        # represent mass
                        # larger circle means more mass
                        mass = rigid_body.mass

                        # scale down the mass
                        mass /= 4

                        # mask surface to match the size of the mass circle
                        transparency_mask = pygame.Surface((mass*2, mass*2))

                        # fill surface with a color mask and set the color key
                        color_mask = (123, 54, 33)
                        transparency_mask.fill(color_mask)
                        transparency_mask.set_colorkey(color_mask)

                        # draw circle to the transparency mask
                        mass = int(mass)
                        pygame.draw.circle(transparency_mask, (0, 100, 255), (mass, mass), mass)

                        # change alpha
                        transparency_mask.set_alpha(100)

                        # draw transparency mask to the display
                        display.blit(transparency_mask, (int(x)-mass, int(y)-mass))

                    # box collider
                    if collider is not None:

                        if collider.tag == BoxCollider.tag:

                            # get relative position to transform
                            get_relative_rect_pos(transform.position, collider.box)

                            # center the box image
                            x -= collider.box.width/2
                            y -= collider.box.height/2
                            box = Rect(x, y, collider.box.width, collider.box.height)

                            # display collider rect properties
                            pygame.draw.rect(display, (255, 255, 255), box, 1)
                            pygame.draw.circle(display, (0, 255, 0), box.center, 3)
                            pygame.draw.circle(display, (0, 255, 255), box.topleft, 5)

                        elif collider.tag == CircleCollider.tag:
                            radius = collider.radius
                            pygame.draw.circle(display, (255, 255, 255), (int(x), int(y)), radius, 1)