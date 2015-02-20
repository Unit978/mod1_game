

from world import *
from engine import *
from entity import *
from components import BehaviorScript

from random import randrange
from math import pi
from math import radians

# Create the engine and pass screen display dimensions.
# This also initializes any resources that are required to make
# the engine/game work.
breakout_engine = Engine(1200, 700)

# create image assets
paddle_image = pygame.image.load("assets/images/paddle.png").convert()
ball_image = pygame.image.load("assets/images/ball.png").convert_alpha()

# create sound assets
brick_hit_sound = mixer.Sound("assets/sounds/brick_hit.wav")
paddle_hit_sound = mixer.Sound("assets/sounds/paddle_hit.wav")
wall_hit_sound = mixer.Sound("assets/sounds/paddle_hit.wav")

# create font/text assets
score_font = font.SysFont(font.get_default_font(), 32)
score_font_color = (255, 255, 255)

# these are the image surfaces to draw the text on
score_text_surface = score_font.render("SCORE:  ", False, score_font_color)
score_value_surface = score_font.render("0", False, score_font_color)

# set the volumes
brick_hit_sound.set_volume(0.5)
paddle_hit_sound.set_volume(0.5)
wall_hit_sound.set_volume(0.5)

# load music to play in the background
mixer.music.load("assets/music/back_music.mp3")


# ---------------------------------- scripts ---------------------------------- #
class BallBehavior (BehaviorScript):

    def __init__(self, script_name):
        super(BallBehavior, self).__init__(script_name)

    def collision_event(self, other_collider):

        other_entity = other_collider.entity

        # hits brick
        if other_entity.tag == "brick":

            # remove brick
            self.entity.world.destroy_entity(other_entity)
            brick_hit_sound.play()

            # update score
            self.entity.world.score_so_far += self.entity.world.score_per_brick

            # create a new text surface for the update score
            s = self.entity.world.score_so_far
            new_score_surface = score_font.render("" + str(s), False, score_font_color)
            self.entity.world.engine.gui.update_widget_image("score value", new_score_surface)

        # hits the player paddle
        elif other_entity.tag == "player":

            # Set the ball to go upward even if we hit the sides of the paddle.
            # This is just a convenience for the player.
            velocity = self.entity.rigid_body.velocity
            vel_y = -abs(velocity.y)
            velocity.y = vel_y

            paddle_hit_sound.play()

            # check which section of the paddle the ball hit
            # split the paddle sections into 3
            #   - middle, left, right

            # get necessary data
            ball_x = self.entity.transform.position.x
            paddle_x = other_entity.transform.position.x
            paddle_width = other_entity.collider.box.width

            # divide the paddle into fourths
            # -------------------------------
            # |      |       |       |      |
            # |      |       |       |      |
            # -------------------------------
            #   left    m i d d l e    right
            #
            section_len = paddle_width/4

            # top left x coordinate value of the paddle
            top_left_x = paddle_x-paddle_width/2

            # hit the left section
            if ball_x < (top_left_x + section_len):

                # set the velocity direction to 135 degrees - counter-clock wise
                self.entity.rigid_body.velocity.set_direction(-pi/4 - pi/2)

            # hit the right section
            elif ball_x > (top_left_x + paddle_width - section_len):

                # set the velocity direction to 45 degrees - counter-clock wise
                self.entity.rigid_body.velocity.set_direction(-pi/4)

            # hit middle - make the ball bounce into a random direction between the specified range
            else:
                # some random angle between 45 and 135 degrees - counter-clock wise
                angle = randrange(-45-90, -45)

                # convert from degrees to radians
                angle = radians(angle)
                self.entity.rigid_body.velocity.set_direction(angle)

        # hit some wall
        elif other_entity.tag == "wall":
            wall_hit_sound.play()

        # hits the bottom wall - reset the ball over the paddle
        elif other_entity.tag == "bottom wall":
            ball_pos = self.entity.transform.position
            rigid_body = self.entity.rigid_body

            # get player location
            player_pos = self.entity.world.player.transform.position

            # place above player
            box_height = self.entity.collider.box.height
            ball_pos.y = player_pos.y - box_height - 10
            ball_pos.x = player_pos.x

            # set upward velocity
            rigid_body.velocity.set_direction(-pi/2)


class PlayerBehavior(BehaviorScript):

    def __init__(self, script_name):
        super(PlayerBehavior, self).__init__(script_name)

    def take_input(self, event):
        # make the paddle follow the mouse on the x-axis
        # keep a fixed y value
        position = self.entity.transform.position

        # get x_position of the mouse
        mouse_x = pygame.mouse.get_pos()[0]
        position.x = mouse_x


# create a custom world
class BreakoutWorld (World):

    def __init__(self):
        super(BreakoutWorld, self).__init__()

        # ------- the necessary game attributes to be used in this world ------- #

        # game objects to be used
        self.player = None
        self.ball = None

        self.background = None

        # walls
        self.topWall = None
        self.bottomWall = None
        self.leftWall = None
        self.rightWall = None

        # score for breaking a brick
        self.score_per_brick = 100
        self.score_so_far = 0

        # start the background music and set it to loop forever
        mixer.music.play(-1)

    # create and setup the game objects in the world
    def load_scene(self):

        # create the score value widget
        w = score_text_surface.get_width()
        score_value_widget = self.engine.gui.Widget(score_value_surface, Vector2(w, 0))
        score_value_widget.tag = "score value"

        # send the text widgets to the gui handler
        self.engine.gui.add_widget(score_value_widget)
        self.engine.gui.add_widget(self.engine.gui.Widget(score_text_surface, Vector2(0, 0)))

        # create a background object
        self.background = self.create_entity()

        # create the background image
        background_surface = pygame.Surface(self.engine.display.get_size())
        background_surface.convert()
        background_surface.fill((12, 0, 40))

        # add necessary components to be able to position and render the background
        self.background.add_component(Transform())
        self.background.add_component(Renderer(background_surface))
        self.background.renderer.depth = 100

        # ------- add bricks ------- #

        # set the brick dimensions
        brick_width = 80
        brick_height = 35
        total_bricks = 120

        # position to place the first brick
        x = brick_width/2
        y = 70

        # calculate how many bricks can fit within the width of the screen
        bricks_per_width = self.engine.display.get_width() / brick_width

        # create an amount of <total_bricks> bricks
        # if total bricks was 120 then this would create 120 bricks
        for i in range(1, total_bricks+1):

            # create some random color
            r = randrange(50, 226)
            g = randrange(50, 226)
            b = randrange(50, 226)
            brick_color = (r, g, b)

            # create basic image for the brick
            brick_surface = pygame.Surface((brick_width, brick_height))
            brick_surface.convert()
            brick_surface.fill(brick_color)

            # create the brick object and the tag
            brick = self.create_game_object(brick_surface)
            brick.tag = "brick"

            # position it
            brick.transform.position = Vector2(x, y)

            # set collider dimensions
            w = brick_surface.get_width()
            h = brick_surface.get_height()

            # make the bricks bouncy against the ball
            brick.collider.restitution = 1

            # set the new x coordinate for the next brick to spawn at
            x += brick_width

            # make a new row of bricks if no more bricks fit within the width of the screen
            if i % bricks_per_width == 0:
                y += brick_height
                x = brick_width/2

        # screen dimensions halved
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
        self.bottomWall.transform.position = Vector2(half_w, half_h*2+25+75)
        self.leftWall.transform.position = Vector2(0-50-50, half_h)
        self.rightWall.transform.position = Vector2(half_w*2+50+50, half_h)

        self.topWall.collider.restitution = 1
        self.bottomWall.collider.restitution = 1
        self.leftWall.collider.restitution = 1
        self.rightWall.collider.restitution = 1

        # ------- set up player ------- #
        paddle_width = paddle_image.get_width()
        paddle_height = ball_image.get_height()

        self.player = self.create_game_object(paddle_image)

        # set player position in the world
        pos = Vector2(half_w, half_h * 2 - paddle_width * 2.0 / 3)
        self.player.transform.position = pos

        # set the player's collision box
        w = paddle_width+5
        h = paddle_height+10
        self.player.collider.set_box(w, h)
        self.player.collider.restitution = 1
        self.player.add_script(PlayerBehavior("player behavior"))

        # set depth
        self.player.renderer.depth = -2

        # ------- set up ball ------- #
        ball_width = ball_image.get_width()
        ball_height = ball_image.get_height()

        self.ball = self.create_game_object(ball_image)
        self.ball.add_component(RigidBody())

        # set the ball position in the world
        pos = Vector2(half_w, pos.y - ball_height * 2)
        self.ball.transform.position = pos

        # add a rigid body so we can give the ball a velocity
        ball_rigid = self.ball.rigid_body
        ball_rigid.velocity = Vector2(1.0, 0.0)
        ball_rigid.velocity.set_magnitude(700.0)
        ball_rigid.velocity.set_direction(-pi/2)

        # set the collision box of the ball
        self.ball.collider.set_box(ball_width, ball_height)

        # add script
        self.ball.add_script(BallBehavior("ball behavior"))
        self.ball.renderer.depth = -1

        # set up game object tags for easy identification
        self.player.tag = "player"
        self.ball.tag = "ball"
        self.topWall.tag = "wall"
        self.bottomWall.tag = "bottom wall"
        self.leftWall.tag = "wall"
        self.rightWall.tag = "wall"


breakout_engine.set_world(BreakoutWorld())

# run game
breakout_engine.run()