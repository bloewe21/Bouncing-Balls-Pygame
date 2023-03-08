# Brian Loewe
# CPSC 386-03
# 2022-05-09
# bloewe@csu.fullerton.edu
# @bloewe21
#
# Lab 05-00
#
# This is the file ball.py, which creates the logic for the bouncing
# ball, including math and shapes to determine how the balls should move
# and bounce off of different surfaces
#

"""A Ball class for the bouncing ball demo."""

import os.path
from random import randint
import pygame
from game import rgbcolors
from game.animation import Explosion


def random_velocity(min_val=1, max_val=5):
    """Generate a random velocity in a plane, return it as a Vector2"""
    random_x = randint(min_val, max_val)
    random_y = randint(min_val, max_val)
    if randint(0, 1):
        random_x *= -1
    if randint(0, 1):
        random_y *= -1
    return pygame.Vector2(random_x, random_y)


def random_color():
    """Return a random color."""
    return pygame.Color(randint(0, 255), randint(0, 255), randint(0, 255))


# This is the class we discussed in class. You can have this as a standalone
# definition of a circle's geometry or you can fold the Circle and Ball classes
# together into a single class definition. Your choice.
class Circle:
    """Class representing a circle with a bounding rect."""

    def __init__(self, center_x, center_y, radius):
        self._center = pygame.Vector2(center_x, center_y)
        self._radius = radius

    @property
    def radius(self):
        """Return the circle's radius"""
        return self._radius

    @property
    def center(self):
        """Return the circle's center."""
        return self._center

    @property
    def rect(self):
        """Return bounding Rect; calculate it and create a new Rect instance"""
        left = self._center[0] - self._radius
        top = self._center[1] - self._radius
        return pygame.Rect(left, top, self.width, self.width)

    @property
    def width(self):
        """Return the width of the bounding box the circle is in."""
        return self._radius * 2

    @property
    def height(self):
        """Return the height of the bounding box the circle is in."""
        return self._radius * 2

    def squared_distance_from(self, other_circle):
        """Squared distance from self to other circle."""
        return (other_circle.center - self._center).squared_length()

    def distance_from(self, other_circle):
        """Distance from self to other circle"""
        return (other_circle.center - self._center).length()

    def move_ip(self, x_dist, y_dist):
        """Move circle in place, update the circle's center"""
        self._center = self._center + pygame.Vector2(x_dist, y_dist)

    def move(self, x_dist, y_dist):
        """Move circle, return a new Circle instance"""
        center = self._center + pygame.Vector2(x_dist, y_dist)
        return Circle(center[0], center[1], self._radius)

    def stay_in_bounds(self, xmin, xmax, ymin, ymax):
        """Update position to stay within bounds"""


class Ball:
    """A class representing a moving ball."""

    default_radius = 25

    main_dir = os.path.split(os.path.abspath(__file__))[0]
    data_dir = os.path.join(main_dir, 'data')
    # Feel free to change the sounds to something else.
    # Make sure you have permssion to use the sound effect file and document
    # where you retrieved this file, who is the author, and the terms of
    # the license.
    bounce_sound = os.path.join(data_dir, 'Boing.aiff')
    reflect_sound = os.path.join(data_dir, 'Monkey.aiff')

    def __init__(self, name, center_x, center_y, sound_on=True):
        """Initialize a bouncing ball."""
        # The name can be any string. The best choice is an integer.
        self._name = name
        # Yes, we could define the details about our geometry in the Ball
        # class or we can define the geometry in an instance variable.
        # It is up to you if you want to separate them out or integrate them
        # together.
        self._circle = Circle(center_x, center_y, Ball.default_radius)
        self._color = random_color()
        self._velocity = random_velocity()
        self._sound_on = sound_on
        self._bounce_count = randint(5, 10)
        self._is_alive = True
        self._draw_text = False
        font = pygame.font.SysFont(None, Ball.default_radius)
        self._name_text = font.render(str(self._name), True, rgbcolors.BLACK)

        self._collisions = 0
        try:
            self._bounce_sound = pygame.mixer.Sound(Ball.bounce_sound)
            self._bounce_channel = pygame.mixer.Channel(2)
        except pygame.error as pygame_error:
            print(f'Cannot open {Ball.bounce_sound}')
            raise SystemExit(1) from pygame_error
        try:
            self._reflect_sound = pygame.mixer.Sound(Ball.reflect_sound)
            self._reflect_channel = pygame.mixer.Channel(3)
        except pygame.error as pygame_error:
            print(f'Cannot open {Ball.reflect_sound}')
            raise SystemExit(1) from pygame_error

    def toggle_draw_text(self):
        """Toggle the debugging text where each circle's name is drawn."""
        self._draw_text = not self._draw_text

    def draw(self, surface):
        """Draw the circle to the surface."""
        pygame.draw.circle(surface, self.color, self.center, self.radius)
        if self._draw_text:
            surface.blit(
                self._name_text,
                self._name_text.get_rect(center=self._circle.center),
            )

    def wall_reflect(self, xmin, xmax, ymin, ymax):
        """Reflect the ball off walll, play a sound if the sound flag is on."""
        right_side = self._circle.center[0] + self._circle.radius
        left_side = self._circle.center[0] - self._circle.radius
        top_side = self._circle.center[1] - self._circle.radius
        bottom_side = self._circle.center[1] + self._circle.radius

        if right_side > xmax or left_side < xmin:
            self._velocity[0] *= -1
        if top_side < ymin or bottom_side > ymax:
            self._velocity[1] *= -1

    def bounce(self, other_ball):
        """Bounce the ball off of another ball, play sound if not alive."""
        if not self._sound_on:
            pygame.mixer.Sound.set_volume(self._bounce_sound, 0.2)
        else:
            pygame.mixer.Sound.set_volume(self._bounce_sound, 0.0)
        pygame.mixer.Sound.play(self._bounce_sound)

        normal = other_ball.center - self.center
        self._velocity = self._velocity.reflect(normal)

        other_ball._collisions += 1

    def collide_with(self, other_ball):
        """Return true if self collides with other_ball."""
        return self._circle.distance_from(other_ball._circle) <= (
            self.radius + other_ball.radius
        )

    def separate_from(self, other_ball, rect):
        """Separate a ball from the other ball so they aren't overlapping."""
        overlap_distance = (self.radius + other_ball.radius) - (
            self._circle.distance_from(other_ball._circle)
        )
        half_overlap_distance = 1 + overlap_distance / 2

        reverse_velocity = self._velocity * -1
        self._circle.move_ip(*(reverse_velocity * half_overlap_distance))

        if not rect.contains(self._circle.rect):
            # undo previous move_ip
            self._circle.move_ip(
                *(-1 * reverse_velocity * half_overlap_distance)
            )

            # move other_ball half_overlap_distance, gets called twice
            reverse_velocity = other_ball._velocity * -1
            other_ball._circle.move_ip(
                *(reverse_velocity * half_overlap_distance)
            )

        reverse_velocity = other_ball._velocity * -1
        other_ball._circle.move_ip(*(reverse_velocity * half_overlap_distance))

    def check_collision(self, other_ball, explosion_toggle, rect):
        """Actions if ball should die upon bounce"""
        if self._collisions >= self._bounce_count:
            self.separate_from(other_ball, rect)
            self.stop()
            if not explosion_toggle:
                Explosion(self)

    @property
    def name(self):
        """Return the ball's name."""
        return self._name

    @property
    def rect(self):
        """Return the ball's rect."""
        return self._circle.rect

    @property
    def circle(self):
        """Return the ball's circle."""
        return self._circle

    @property
    def center(self):
        """Return the ball's center."""
        return self._circle.center

    @property
    def radius(self):
        """Return the ball's radius"""
        return self._circle.radius

    @property
    def color(self):
        """Return the color of the ball."""
        return self._color

    @property
    def velocity(self):
        """Return velocity of ball"""
        return self._velocity

    def is_alive(self):
        """Return true if the ball is still alive."""
        if self._is_alive:
            return True
        return False

    def toggle_sound(self):
        """Turn off the sound effects."""
        self._sound_on = not self._sound_on

    def too_close(self, x_dist, y_dist, min_dist):
        """Is the ball too close to some point by some min_dist?"""

    def stop(self):
        """Stop the ball from moving."""
        self._velocity = pygame.Vector2(0, 0)
        self._color = rgbcolors.WHITE
        self._is_alive = False

    def set_velocity(self, x_dist=3, y_dist=3):
        """Set the ball's velocity."""
        self._velocity[0] = x_dist
        self._velocity[1] = y_dist

        self._velocity = pygame.Vector2(x_dist, y_dist)

    def update(self):
        """Update the ball's position"""
        self._circle.move_ip(*self._velocity)
        self.wall_reflect(0, 800, 0, 800)

    def __str__(self):
        """Ball stringify."""
        # return f'Ball(name: {self._name}, xpos: {self._circle.center[0] + \
        # self._circle.radius}, ypos: {self._circle.center[1] + \
        # self._circle.radius}, color: {self._color})'
