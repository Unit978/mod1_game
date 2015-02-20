
from managers import EntityManager
from entity import GameObject
from entity import BoxColliderObject
from entity import CircleColliderObject
from systems import *


# A world is like a game level. It holds the necessary game objects
# and assets to be used for a level.
# Inherit from this class and implement the abstract methods in order
# to create a custom world.

class World (object):
    __metaclass__ = ABCMeta

    def __init__(self):
        # Reference to the engine that it exists in
        self.engine = None
        self.systems = list()
        self.entity_manager = EntityManager()

        # for world behavior
        self.scripts = list()

        # add the fundamental systems
        self.add_system(PhysicsSystem())
        self.add_system(RenderSystem())

        # bounds - negative values means no bounds
        self.width = -1
        self.height = -1
        self.origin = Vector2(0, 0)

    @abstractmethod
    def load_scene(self):
        """
        Setup the world scene by specifying how/where to create
        game objects.
        """

    # Do not override
    def _take_input(self, event):

        for s in self.scripts:
            s.take_input(event)

        # run script input for entities
        for e in self.entity_manager.entities:
            for s in e.scripts:
                s.take_input(event)

    # create an empty entity (no components)
    def create_entity(self):
        e = self.entity_manager.create_entity()
        e.world = self
        return e

    def create_game_object(self, image_surface):
        entity = GameObject(image_surface)
        entity.world = self
        self.entity_manager.add(entity)
        return entity

    def create_box_collider_object(self, width, height):
        entity = BoxColliderObject(width, height)
        entity.world = self
        self.entity_manager.add(entity)
        return entity

    def create_circle_collider_object(self, radius):
        entity = CircleColliderObject(radius)
        entity.world = self
        self.entity_manager.add(entity)
        return entity

    def destroy_entity(self, entity):

        # remove the entity from the scene
        render_system = self.get_system(RenderSystem.tag)
        render_system.remove_from_scene(entity)

        self.entity_manager.remove_entity(entity)

    def add_system(self, system):
        system.world = self

        # add to the front - so the physics and render systems are
        # the last systems to do their logic.
        self.systems.insert(0, system)

    def remove_system(self, system):
        self.systems.remove(system)

    def get_system(self, tag):
        for system in self.systems:
            if system.tag == tag:
                return system
        return None

    def add_script(self, script):
        script.world = self
        self.scripts.append(script)

    def remove_script(self, script):
        self.scripts.remove(script)

    # Have each system process the entities
    def run(self):
        for s in self.systems:
            s.process(self.entity_manager.entities)

        # run script updates
        for e in self.entity_manager.entities:
            for s in e.scripts:
                s.update()

        # world scripts
        for s in self.scripts:
            s.update()

    # determine if the world has bounds
    def is_bounded(self):
        return self.width > 0 and self.height > 0