"""
Developer : Weng Chong LAO
Start Date : 2022/07/25

Project Information:
Name: Pygame Packing Density Model (PPDM)

The University of Queensland
Faculty of Engineering, Architecture and Information Technology
Bachelor of Engineering (Honours)
Civil Engineering

Thesis Project
CIVL4584 2022 Semester 2
Concrete Packing Density Experiment
Big Particle Dominated Case

Project Details:
This project is my individual project that is developed for my thesis project in my civil engineering degree.

This project aims to develop a 2D dry binary packing model for spheres in order to study for
the loosening, wedging and wall effects. Computational model for these experiments are developed and conducted to
understand the effect that packing density of the binary particles is depended on the size and
volume ratios of the particles in random packing.

According to Stovall et al. (1986), a great understanding and knowledge of the particle packing is important and
useful to the concrete industries. A good packing of concrete ingredients can improve the strength,
durability and workability of the concrete member directly, which cannot be achieved by purely adjusting the water and cement ratio.

Pygame Packing Density Model (PPDM) is a 2D computational model with a binary mixture of the larger grains and smaller grains,
it is a model for predicting the packing density in random particle packing.
The PPDM implements the game engine called Pygame in Python programming language,
it can simulate the collision and physical movements of the particles.

The environment of the PPDM is composed of a rigid container,
a binary mixture of the larger grains and smaller grains are generated randomly inside the container.
After a mixing process (vibration) and particle settlement, the packing density of the system,
number of larger grains and number of smaller grains can be measured as well as
the volumetric fractions of either the larger grains or the smaller grains.

The PPDM has a systematic procedure to predict the packing density of the random particle packing.
There are ten different statuses used to define and control the process of the PPDM,
they are design for the larger grains dominated situation:
(1) Start; (2) Generate smaller grains; (3) Vibration1; (4) Vibration2; (5) Elimination1;
(6) Elimination2; (7) Generate smaller grains to fill for fully packed; (8) Elimination3; (9) Measurement; (10) End.
"""

import random

import pygame
import pygame_menu
import pygame.time as pyTime
import pymunk
import pymunk.pygame_util

import math
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

import csv
from enum import Enum


# Parameter setup
# Big ball govern
pygame.init()
# window size
WIDTH, HEIGHT = (pygame.display.Info().current_w*0.85, pygame.display.Info().current_h*0.85)
window = pygame.display.set_mode((WIDTH, HEIGHT))

# gravity value [m/s2]
gravity = 50

# Container properties
container_width = WIDTH*0.4
container_height = WIDTH*0.4
container_thickness = 20
container_elasticity = 0.9
container_friction = 0.4

# scale
bigBall_container = 10 # bigBall:container = 10:1 (ball diameter)
smallBall_bigBall = 5 # smallBall:bigBall = 5:1

# volume of small ball / (volume of small ball + volume of big ball)
smallBall_percentage = 10 # [%]

# Big ball properties
big_ball_size = (container_height/bigBall_container)/2 #radius
number_of_big_ball = 100
big_ball_mass = 5
big_ball_elasticity = 0
big_ball_friction = 1
big_ball_density = 5
big_ball_color = (144, 183, 125, 100)

# Small ball properties
small_ball_size = big_ball_size/smallBall_bigBall #radius
number_of_small_ball = 1000
small_ball_mass = 1
small_ball_elasticity = 0
small_ball_friction = 1
small_ball_density = 8
small_ball_color = (159, 201, 243, 100)

# Wall list
wall_list = []

# timer
timer = 0

# Result properties
decimal_places = 3

# Experiment properties
number_of_experiment = 2
auto_experiment = False

# Font properties
"""
base_font = pygame.font.Font(None, 40)
user_text = 'hello'
"""


class Status(Enum):
    """
    Status enumeration which is used to define and control the processes of the experiment
    """
    EMPTY = -1
    START = 1
    GENERATE_SMALL = 2
    VIBRATE1 = 3.1
    VIBRATE2 = 3.2
    ELIMINATE1 = 4.1
    ELIMINATE2 = 4.2
    GENERATE_SMALL_FILL = 5
    ELIMINATE3 = 6
    MEASURE = 7
    END = 0


def start_the_experiment():
    """
    Pack and set the user's input parameters from menu section, experiment setup
    """
    global bigBall_container
    global smallBall_bigBall
    global number_of_small_ball
    global number_of_big_ball
    global number_of_experiment
    global auto_experiment

    bigBall_container = bigBall_container_property.get_value()[0][1]
    smallBall_bigBall = smallBall_bigBall_property.get_value()[0][1]
    number_of_small_ball = round(number_of_small_ball_property.get_value())
    number_of_big_ball = round(number_of_big_ball_property.get_value())
    number_of_experiment = round(number_of_experiment_property.get_value())
    auto_experiment = auto_experiment_property.get_value()
    execute(window, WIDTH, HEIGHT)


# Menu section setup
menu = pygame_menu.Menu('Concrete Packing Density [Big Ball Dominated]', WIDTH/1.5, HEIGHT/1.5,
                        theme=pygame_menu.themes.THEME_DEFAULT)

menu.add.label("Ratio Properties:")
bigBall_container_property = (
    menu.add.dropselect("Container : BigBall",
                        [("1:10", 10), ("1:11", 11), ("1:12", 12), ("1:13", 13), ("1:14", 14), ("1:15", 15)], default=0))
smallBall_bigBall_property = (
    menu.add.dropselect("BigBall : SmallBall",
                        [("1:1", 1), ("1:2", 2), ("1:3", 3), ("1:4", 4),
                         ("1:5", 5), ("1:6", 6), ("1:7", 7), ("1:8", 8), ("1:9", 9), ("1:10", 10)], default=4))

menu.add.label(" ")
menu.add.label("Amount Properties:")
auto_experiment_property = menu.add.toggle_switch("Auto Experiments (from 0 to selected no. of small ball):")
number_of_small_ball_property = menu.add.range_slider("Number of Small Ball:", 1000, [0, 1700], increment=100)
number_of_big_ball_property = menu.add.range_slider("Number of Big Ball:", 100, [50, 100], increment=10)

number_of_experiment_property = menu.add.range_slider("Number of Experiment:", 2, [1, 60], increment=1)
menu.add.button('"Start Experiment"', start_the_experiment)


def calculate_distance(p1, p2):
    """
    Calculate the distance between two points

    :param p1: point 1 coordinate
    :param p2: point 2 coordinate
    :return: distance between point 1 and point 2
    """
    return math.sqrt((p2[1] - p1[1])**2 + (p2[0] - p1[0])**2)


def calculate_angle(p1, p2):
    """
    Calculate the rotational angle between two points in radian

    :param p1: point 1 coordinate
    :param p2: point 2 coordinate
    :return: rotational angle [radian] from point 1 to point 2 vector
    """
    return math.atan2(p2[1] - p1[1], p2[0] - p1[0])


def draw(space: pymunk.Space, window: pygame.display, draw_options: pymunk.pygame_util.DrawOptions):
    """
    Draw the main window for pygame environment

    :param space: pymunk Space
    :param window: pygame display
    :param draw_options: pymunk pygame_util DrawOptions
    """
    window.fill("white")
    space.debug_draw(draw_options)
    pygame.display.update()


def create_boundaries(space: pymunk.Space, width: int, height: int):
    """
    Generate the boundaries for the experiment environment

    :param space: pymunk.Space
    :param width: width of the boundary
    :param height: height of the boundary
    """
    # format of the parameter rects:
    # [floor, ceiling, left-hand side wall, right-hand side wall]
    # each object = [(centre position), (width, height)]
    rects = [
        [(width/2, height - 10), (width, 20)],
        [(width/2, 10), (width, 20)],
        [(10, height/2), (20, height)],
        [(width - 10, height/2), (20, height)]
    ]

    # Generate the boundaries
    for pos, size in rects:
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        body.position = pos
        shape = pymunk.Poly.create_box(body, size)
        shape.elasticity = 0.4
        # friction coefficient
        shape.friction = 0.5
        space.add(body, shape)


def create_container(space: pymunk.Space, width: int, height: int, thickness: int, elasticity: float, friction: float):
    """
    Generate the boundaries for the experiment container

    :param space: pymunk.Space
    :param width: width of the container
    :param height: height of the container
    :param thickness: thickness of the boundaries
    :param elasticity: elasticity of the container boundaries
    :param friction: friction of the container boundaries
    """
    # format of the parameter rects:
    # [left-hand side wall, bottom floor, right-hand side wall]
    # each object = [(centre position), (width, height)]
    rects = [[(WIDTH/2 - width/2 + thickness/2, HEIGHT - 20 - height/2), (thickness, height)],
             [(WIDTH/2, HEIGHT - 20 - thickness/2), (width, thickness)],
             [(WIDTH/2 + width/2 - thickness/2, HEIGHT - 20 - height/2), (thickness, height)]
             ]

    # Generate the boundaries
    for pos, size in rects:
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        body.position = pos
        shape = pymunk.Poly.create_box(body, size)
        shape.elasticity = elasticity
        # friction coefficient
        shape.friction = friction
        # RGB color with the opacity [%]
        shape.color = (43, 43, 43, 100)
        space.add(body, shape)


def create_wall(space: pymunk.Space, width: int, height: int, thickness: int, elasticity: float, friction: float):
    """
    Generate the boundaries for the experiment walls
    which are used to prevent particles overflow outside the container during the experiment

    :param space: pymunk.Space
    :param width: width of the wall
    :param height: height of the wall
    :param thickness: thickness of the boundaries
    :param elasticity: elasticity of the wall boundaries
    :param friction: friction of the wall boundaries
    """
    # format of the parameter rects:
    # [left-hand side wall, right-hand side wall]
    # each object = [(centre position), (width, height)]
    rects = [[(WIDTH/2 - width/2 + thickness/2, HEIGHT - 20 - container_height), (thickness, height)],
             [(WIDTH/2 + width/2 - thickness/2, HEIGHT - 20 - container_height), (thickness, height)]
             ]

    # Generate the boundaries
    for pos, size in rects:
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        body.position = pos
        shape = pymunk.Poly.create_box(body, size)
        shape.elasticity = elasticity
        # friction coefficient
        shape.friction = friction
        # RGB color with the opacity [%]
        shape.color = (43, 43, 43, 100)
        space.add(body, shape)
        wall_list.append(shape)


def create_cover(space: pymunk.Space, width: int, height: int, thickness: int, elasticity: float, friction: float):
    """
    Generate the boundaries for the container top cover
    which is used to prevent particles overflow outside the container after the experiment

    :param space: pymunk.Space
    :param width: width of the cover
    :param height: height of the cover
    :param thickness: thickness of the boundary
    :param elasticity: elasticity of the cover boundary
    :param friction: friction of the cover boundary
    """
    # rects = [container top cover]
    # each object = [(centre position), (width, height)]
    rects = [(WIDTH/2, HEIGHT - 20 - container_height - thickness*0.5), (width, thickness)]

    # Generate the boundaries
    pos, size = rects
    body = pymunk.Body(body_type=pymunk.Body.STATIC)
    body.position = pos
    shape = pymunk.Poly.create_box(body, size)
    shape.elasticity = elasticity
    # friction coefficient
    shape.friction = friction
    # RGB color with the opacity [%]
    shape.color = (43, 43, 43, 100)
    space.add(body, shape)
    return shape


def create_particle(space: pymunk.Space, radius: float, mass: float, pos: tuple[float, float],
                    elasticity: float, friction: float, density: float, color: tuple[int, int, int, int]):
    """
    Generate the particle (sphere) for the experiment

    :param space: pymunk.Space
    :param radius: radius of the experiment particle
    :param mass: mass of the experiment particle
    :param pos: position of the experiment particle
    :param elasticity: elasticity of the experiment particle
    :param friction: friction of the experiment particle
    :param density: density of the experiment particle
    :param color: color of the experiment particle
    :return: shape of the particle
    """
    body = pymunk.Body()
    body.position = pos
    shape = pymunk.Circle(body, radius)
    shape.mass = mass
    #shape.elasticity = elasticity
    #shape.friction = friction
    shape.density = density
    # RGB color with the opacity [%]
    shape.color = color
    space.add(body, shape)
    return shape


def random_generate_particles(space: pymunk.Space, generate_centre: tuple[float, float],
                              generate_width: float, generate_height: float, number_of_particle: int,
                              radius: float, mass: float, elasticity: float, friction: float,
                              density: float, color: tuple[int, int, int, int]):
    """
    Randomly generate the particles (spheres) in different positions inside the container

    :param space: pymunk.Space
    :param generate_centre: centre of the random generation area
    :param generate_width: width of the random generation area
    :param generate_height: height of the random generation area
    :param number_of_particle: number of particles to be generated
    :param radius: radius of the particles to be generated
    :param mass: mass of the particles to be generated
    :param elasticity: elasticity of the particles to be generated
    :param friction: friction of the particles to be generated
    :param density: density of the particles to be generated
    :param color: color of the particles to be generated
    :return: a list of the generated particles
    """
    particle_list = []
    for n in range(1, number_of_particle+1):
        x_pos = random.randint(int(generate_centre[0] - generate_width/2), int(generate_centre[0] + generate_width/2))
        y_pos = random.randint(int(generate_centre[1] - generate_height/2), int(generate_centre[1] + generate_height/2))
        particle_list.append(create_particle(space, radius, mass, (x_pos, y_pos), elasticity, friction, density, color))
    return particle_list


def generate_big_ball(space: pymunk.Space, type: int):
    """
    Generate the larger particles (spheres) in the container

    :param space: pymunk.Space
    :param type: define the location and size of the generation area
    :return: a list of the generated particles
    """
    if type == 1:
        return random_generate_particles(space, (WIDTH/2, HEIGHT - 20 - container_thickness - container_height*0.5),
                                         container_width - 2*big_ball_size, container_height - 2*big_ball_size,
                                         number_of_big_ball, big_ball_size, big_ball_mass, big_ball_elasticity,
                                         big_ball_friction, big_ball_density, big_ball_color)

    if type == 2:
        ball_list = random_generate_particles(space,
                                              (WIDTH/2, HEIGHT - 20 - container_thickness - container_height - 80),
                                              container_width - 2*big_ball_size, container_height/4, number_of_big_ball,
                                              big_ball_size, big_ball_mass, big_ball_elasticity, big_ball_friction,
                                              big_ball_density, big_ball_color)
        ball_list.extend(random_generate_particles(space,
                                                   (WIDTH/2, HEIGHT - 20 - container_thickness - container_height - 40),
                                                   container_width - 2*big_ball_size, container_height/4, number_of_big_ball,
                                                   big_ball_size, big_ball_mass, big_ball_elasticity, big_ball_friction,
                                                   big_ball_density, big_ball_color))
        return ball_list

    if type == 3:
        ball_list = random_generate_particles(space,
                                              (WIDTH/2 - container_width/4, HEIGHT - 20 - container_thickness - container_height*0.75),
                                              container_width - 2*big_ball_size, container_height - 2*big_ball_size,
                                              number_of_big_ball, big_ball_size, big_ball_mass, big_ball_elasticity,
                                              big_ball_friction, big_ball_density, big_ball_color)
        ball_list.extend(random_generate_particles(space,
                                                   (WIDTH/2 + container_width/4, HEIGHT - 20 - container_thickness - container_height*0.75),
                                                   container_width - 2*big_ball_size, container_height - 2*big_ball_size,
                                                   number_of_big_ball, big_ball_size, big_ball_mass, big_ball_elasticity,
                                                   big_ball_friction, big_ball_density, big_ball_color))
        return ball_list

    if type == 4:
        ball_list = random_generate_particles(space,
                                              (WIDTH/2, HEIGHT - 20 - container_thickness - container_height*0.1),
                                              container_width - 2*big_ball_size, 0.1*container_height, number_of_big_ball,
                                              big_ball_size, big_ball_mass, big_ball_elasticity, big_ball_friction,
                                              big_ball_density, big_ball_color)
        return ball_list


def generate_small_ball(space: pymunk.Space):
    """
    Generate the smaller particles (spheres) in the container

    :param space: pymunk.Space
    :return: a list of the generated particles
    """
    return random_generate_particles(space,
                                     (WIDTH/2, HEIGHT - 20 - container_thickness - container_height*0.5),
                                     container_width - 2*small_ball_size - 2*container_thickness,
                                     container_height - small_ball_size - container_thickness,
                                     number_of_small_ball, small_ball_size, small_ball_mass,
                                     small_ball_elasticity, small_ball_friction, small_ball_density, small_ball_color)


def generate_small_ball_to_fill(space: pymunk.Space, number_of_small: int):
    """
    Generate the smaller particles (spheres) in the top of container
    in order to fill up the empty space

    :param space: pymunk.Space
    :param number_of_small: number of small particle to be generated
    :return: a list of the generated particles
    """
    return random_generate_particles(space,
                                     (WIDTH/2, HEIGHT - 20 - container_thickness - container_height),
                                     container_width - 2*small_ball_size - 2*container_thickness, 1,
                                     number_of_small, small_ball_size, small_ball_mass, small_ball_elasticity,
                                     small_ball_friction, small_ball_density, small_ball_color)


def remove_big_ball_for_fully_packed(space: pymunk.Space, ball_list: [pymunk.Circle]):
    """
    Eliminate the larger particles (spheres) which are outside the container

    :param space: pymunk.Space
    :param ball_list: a list of the generated large particles
    """
    ball_size = ball_list[0].radius
    for particle in ball_list.copy():
        if ((HEIGHT - 20 - container_height) - (particle.body.position.y - ball_size))/(HEIGHT - 20 - container_height) > 0.02:
            space.remove(particle, particle.body)
            ball_list.remove(particle)

        elif (particle.body.position.x - ball_size < (WIDTH-container_width)/2
              or particle.body.position.x + ball_size > (WIDTH-container_width)/2 + container_width):
            space.remove(particle, particle.body)
            ball_list.remove(particle)


def remove_small_ball_for_fully_packed(space: pymunk.Space, ball_list: [pymunk.Circle]):
    """
    Eliminate the smaller particles (spheres) which are outside the container

    :param space: pymunk.Space
    :param ball_list: a list of the generated small particles
    """
    if len(ball_list) > 0:
        ball_size = ball_list[0].radius
        for particle in ball_list.copy():
            if ((HEIGHT - 20 - container_height) - (particle.body.position.y - ball_size))/(HEIGHT - 20 - container_height) > 0.001:
                space.remove(particle, particle.body)
                ball_list.remove(particle)

            elif (particle.body.position.x - ball_size < (WIDTH-container_width)/2
                  or particle.body.position.x + ball_size > (WIDTH-container_width)/2 + container_width):
                space.remove(particle, particle.body)
                ball_list.remove(particle)


def calculate_packing_density(ball_list: [pymunk.Circle]):
    """
    Calculate the packing density of the system by the volume fraction

    :param ball_list: a list of the generated large or small particles
    :return: packing density of the system
    """
    if len(ball_list) == 0:
        return 0
    else:
        return ((math.pi*(ball_list[0].radius**2))*len(ball_list)/
                ((container_width-2*container_thickness)*(container_height-container_thickness)))


def calculate_volume_of_small_ball(smallBall_list: [pymunk.Circle], bigBall_list: [pymunk.Circle]):
    """
    Calculate the volume fraction of small particles over all particles

    :param smallBall_list: a list of the generated small particles
    :param bigBall_list: a list of the generated large particles
    :return: the volume fraction of small particles over all particles
    """
    if len(smallBall_list) == 0:
        return 0
    else:
        return ((math.pi*(smallBall_list[0].radius**2))*len(smallBall_list)/
                ((math.pi*(smallBall_list[0].radius**2))*len(smallBall_list) + (math.pi*(bigBall_list[0].radius**2))*len(bigBall_list)))


def execute(window: pygame.display, width: int, height: int):
    """
    Execute the designed experiment automatically and save the results for analysis

    :param window: pygame main window for display
    :param width: width of the main window
    :param height: height of the main window
    """
    timer = 0
    status = Status.EMPTY

    resultX = []
    resultY = []

    # basic setup
    run = True
    clock = pygame.time.Clock()
    fps = 30
    dt = 1 / fps

    # setting up space
    space = pymunk.Space()
    # gravity in x and y direction
    space.gravity = (0, gravity)
    # create the boundaries
    create_boundaries(space, width, height)
    # create the container
    create_container(space, container_width, container_height, container_thickness, container_elasticity, container_friction)
    create_wall(space, container_width, container_height, container_thickness, container_elasticity, container_friction)

    draw_options = pymunk.pygame_util.DrawOptions(window)

    iteration = 0
    small_ball_list = []
    big_ball_list = []
    dragging = False

    # Auto start
    status = Status.START
    iteration += 1
    timer = pyTime.get_ticks()
    big_ball_list = generate_big_ball(space, 1)

    while run:

        if status == Status.START and (pyTime.get_ticks()-timer)*0.001 >= 3: # 3 seconds after big ball generated
            status = Status.GENERATE_SMALL
            timer = pyTime.get_ticks()
            small_ball_list = generate_small_ball(space)

        if status == Status.GENERATE_SMALL and (pyTime.get_ticks()-timer)*0.001 >= 10: # 10 seconds after small ball generated
            status = Status.VIBRATE1
            timer = pyTime.get_ticks()
            # apply forces
            for ball in big_ball_list:
                ball.body.apply_impulse_at_local_point((0, -1000000), (0, 0))
            for ball in small_ball_list:
                ball.body.apply_impulse_at_local_point((0, -100000), (0, 0))

        if status == Status.VIBRATE1 and (pyTime.get_ticks()-timer)*0.001 >= 1:
            status = Status.VIBRATE2
            timer = pyTime.get_ticks()
            # apply forces
            for ball in big_ball_list:
                mode = random.randint(-1, 1)
                ball.body.apply_impulse_at_local_point((mode*50000, -500000), (0, 0))
            for ball in small_ball_list:
                mode = random.randint(-1, 1)
                ball.body.apply_impulse_at_local_point((mode*50000, -50000), (0, 0))

        if status == Status.VIBRATE2 and (pyTime.get_ticks()-timer)*0.001 >= 10:
            status = Status.ELIMINATE1
            timer = pyTime.get_ticks()
            # delete balls which are out of the container
            remove_big_ball_for_fully_packed(space, big_ball_list)
            remove_small_ball_for_fully_packed(space, small_ball_list)

        if status == Status.ELIMINATE1 and (pyTime.get_ticks()-timer)*0.001 >= 1:
            status = Status.ELIMINATE2
            timer = pyTime.get_ticks()
            # delete balls which are out of the container
            remove_big_ball_for_fully_packed(space, big_ball_list)
            remove_small_ball_for_fully_packed(space, small_ball_list)

        if status == Status.ELIMINATE2 and (pyTime.get_ticks()-timer)*0.001 >= 1:
            status = Status.GENERATE_SMALL_FILL
            timer = pyTime.get_ticks()
            generate_number = round(len(small_ball_list)*0.2)
            small_ball_list.extend(generate_small_ball_to_fill(space, generate_number))

        if status == Status.GENERATE_SMALL_FILL and (pyTime.get_ticks()-timer)*0.001 >= 3:
            status = Status.ELIMINATE3
            timer = pyTime.get_ticks()
            # delete balls which are out of the container
            remove_big_ball_for_fully_packed(space, big_ball_list)
            remove_small_ball_for_fully_packed(space, small_ball_list)

        if status == Status.ELIMINATE3 and (pyTime.get_ticks()-timer)*0.001 >= 1:
            status = Status.MEASURE
            timer = pyTime.get_ticks()

            for wall in wall_list.copy():
                space.remove(wall)
                wall_list.remove(wall)

            cover = create_cover(space, container_width, container_height, container_thickness, container_elasticity, container_friction)

            # print result
            big_ball_packing_density = round((calculate_packing_density(big_ball_list))*0.96*(10**decimal_places))/(10**decimal_places)
            small_ball_packing_density = round((calculate_packing_density(small_ball_list))*0.96*(10**decimal_places))/(10**decimal_places)
            volume_of_small_ball = round((calculate_volume_of_small_ball(small_ball_list, big_ball_list))*100*(10**decimal_places))/(10**decimal_places)
            total_packing_density = round((big_ball_packing_density + small_ball_packing_density)*(10**decimal_places))/(10**decimal_places)

            resultX.append(volume_of_small_ball)
            resultY.append(total_packing_density)

            print("Packing Density Report {Iteration #" + str(iteration) + "}:")
            print("------------------------------------")
            print("Packing density of big ball: " + str(big_ball_packing_density))
            print("------------------------------------")
            print("Packing density of small ball: " + str(small_ball_packing_density))
            print("------------------------------------")
            print("Volume of small ball: " + str(volume_of_small_ball) + " %")
            print("")
            print("")
            status = Status.END

        if status == Status.END and (pyTime.get_ticks()-timer)*0.001 >= 2:
            if iteration < number_of_experiment:

                create_wall(space, container_width, container_height, container_thickness, container_elasticity, container_friction)
                space.remove(cover)

                for particle in small_ball_list:
                    space.remove(particle, particle.body)
                small_ball_list = []
                for particle in big_ball_list:
                    space.remove(particle, particle.body)
                big_ball_list = []

                status = Status.START
                iteration += 1
                timer = pyTime.get_ticks()
                big_ball_list = generate_big_ball(space, 1)

            else:
                global number_of_small_ball
                if auto_experiment and number_of_small_ball > 0:
                    create_wall(space, container_width, container_height, container_thickness, container_elasticity, container_friction)
                    space.remove(cover)

                    for particle in small_ball_list:
                        space.remove(particle, particle.body)
                    small_ball_list = []
                    for particle in big_ball_list:
                        space.remove(particle, particle.body)
                    big_ball_list = []

                    # step = 25
                    number_of_small_ball -= 25

                    status = Status.START
                    iteration = 1
                    timer = pyTime.get_ticks()
                    big_ball_list = generate_big_ball(space, 1)

                else:
                    # need to be reset
                    status = Status.EMPTY
                    iteration = 0

                    with open('results.csv', 'w') as f:
                        writer = csv.writer(f)
                        # write the header
                        writer.writerow(resultX)
                        # write the data
                        writer.writerow(resultY)

                    #plt.scatter(resultX, resultY)
                    #plt.show()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.KEYDOWN and status == Status.EMPTY:
                if event.key == pygame.key.key_code("1"):

                    for particle in small_ball_list:
                        space.remove(particle, particle.body)
                    small_ball_list = []
                    for particle in big_ball_list:
                        space.remove(particle, particle.body)
                    big_ball_list = []

                    status = Status.START
                    iteration += 1
                    timer = pyTime.get_ticks()
                    big_ball_list = generate_big_ball(space, 1)

        draw(space, window, draw_options)
        space.step(dt)
        # setting up Frame Per Second (fps) for the screen
        clock.tick(fps)

    pygame.quit()


if __name__ == "__main__":
    menu.mainloop(window)
    #execute(window, WIDTH, HEIGHT)