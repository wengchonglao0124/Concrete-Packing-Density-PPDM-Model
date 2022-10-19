"""
The University of Queensland
EAIT Faculty
Bachelor of Engineering (Honours)
Civil Engineering
CIVL4584 2022 Semester 2
Concrete Packing Density Experiment
Big Ball Dominate Case
Programmer : WengChong LAO
Date : 2022/07/25
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

# Big ball govern
pygame.init()
# window size
WIDTH, HEIGHT = (pygame.display.Info().current_w*0.85, pygame.display.Info().current_h*0.85)
window = pygame.display.set_mode((WIDTH, HEIGHT))

# gravity value [m/s2]?
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

class Status(Enum):
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

# font properties
"""
base_font = pygame.font.Font(None, 40)
user_text = 'hello'
"""

def start_the_experiment():
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

# menu setup
menu = pygame_menu.Menu('Concrete Packing Density [Big Ball Dominated]', WIDTH/1.5, HEIGHT/1.5,
                        theme=pygame_menu.themes.THEME_DEFAULT)

menu.add.label("Ratio Properties:")
bigBall_container_property = menu.add.dropselect("Container : BigBall", [("1:10", 10), ("1:11", 11), ("1:12", 12), ("1:13", 13), ("1:14", 14), ("1:15", 15)], default=0)
smallBall_bigBall_property = menu.add.dropselect("BigBall : SmallBall", [("1:1", 1), ("1:2", 2), ("1:3", 3), ("1:4", 4), ("1:5", 5), ("1:6", 6), ("1:7", 7), ("1:8", 8), ("1:9", 9), ("1:10", 10)], default=4)

menu.add.label(" ")
menu.add.label("Amount Properties:")
auto_experiment_property = menu.add.toggle_switch("Auto Experiments (from 0 to selected no. of small ball):")
number_of_small_ball_property = menu.add.range_slider("Number of Small Ball:", 1000, [0, 1700], increment=100)
number_of_big_ball_property = menu.add.range_slider("Number of Big Ball:", 100, [50, 100], increment=10)

number_of_experiment_property = menu.add.range_slider("Number of Experiment:", 2, [1, 60], increment=1)
menu.add.button('"Start Experiment"', start_the_experiment)


def calculate_distance(p1, p2):
    return math.sqrt((p2[1] - p1[1])**2 + (p2[0] - p1[0])**2)


def calculate_angle(p1, p2):
    return math.atan2(p2[1] - p1[1], p2[0] - p1[0])


def draw(space: pymunk.Space, window: pygame.display, draw_options: pymunk.pygame_util.DrawOptions):
    window.fill("white")
    space.debug_draw(draw_options)
    pygame.display.update()


def create_boundaries(space: pymunk.Space, width: int, height: int):
    # [floor, ceiling, left-hand side wall, right-hand side wall]
    # object = [(centre position), (width, height)]
    rects = [
        [(width/2, height - 10), (width, 20)],
        [(width/2, 10), (width, 20)],
        [(10, height/2), (20, height)],
        [(width - 10, height/2), (20, height)]
    ]
    for pos, size in rects:
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        body.position = pos
        shape = pymunk.Poly.create_box(body, size)
        shape.elasticity = 0.4
        # friction coefficient
        shape.friction = 0.5
        space.add(body, shape)


def create_container(space: pymunk.Space, width: int, height: int, thickness: int, elasticity: float, friction: float):
    rects = [[(WIDTH/2 - width/2 + thickness/2, HEIGHT - 20 - height/2), (thickness, height)],
             [(WIDTH/2, HEIGHT - 20 - thickness/2), (width, thickness)],
             [(WIDTH/2 + width/2 - thickness/2, HEIGHT - 20 - height/2), (thickness, height)]
             ]
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
    rects = [[(WIDTH/2 - width/2 + thickness/2, HEIGHT - 20 - container_height), (thickness, height)],
             [(WIDTH/2 + width/2 - thickness/2, HEIGHT - 20 - container_height), (thickness, height)]
             ]
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
    rects = [(WIDTH/2, HEIGHT - 20 - container_height - thickness*0.5), (width, thickness)]
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


def create_particle(space: pymunk.Space, radius: float, mass: float, pos: tuple[float, float], elasticity: float, friction: float, density: float, color: tuple[int, int, int, int]):
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


def random_generate_particles(space: pymunk.Space, generate_centre: tuple[float, float], generate_width: float, generate_height: float, number_of_particle: int, radius: float, mass: float, elasticity: float, friction: float, density: float, color: tuple[int, int, int, int]):
    particle_list = []
    for n in range(1, number_of_particle+1):
        x_pos = random.randint(int(generate_centre[0] - generate_width/2), int(generate_centre[0] + generate_width/2))
        y_pos = random.randint(int(generate_centre[1] - generate_height/2), int(generate_centre[1] + generate_height/2))
        particle_list.append(create_particle(space, radius, mass, (x_pos, y_pos), elasticity, friction, density, color))
    return particle_list


def generate_big_ball(space: pymunk.Space, type: int):
    if type == 1:
        return random_generate_particles(space, (WIDTH/2, HEIGHT - 20 - container_thickness - container_height*0.5), container_width - 2*big_ball_size, container_height - 2*big_ball_size, number_of_big_ball, big_ball_size, big_ball_mass, big_ball_elasticity, big_ball_friction, big_ball_density, big_ball_color)
    if type == 2:
        ball_list = random_generate_particles(space, (WIDTH/2, HEIGHT - 20 - container_thickness - container_height - 80), container_width - 2*big_ball_size, container_height/4, number_of_big_ball, big_ball_size, big_ball_mass, big_ball_elasticity, big_ball_friction, big_ball_density, big_ball_color)
        ball_list.extend(random_generate_particles(space, (WIDTH/2, HEIGHT - 20 - container_thickness - container_height - 40), container_width - 2*big_ball_size, container_height/4, number_of_big_ball, big_ball_size, big_ball_mass, big_ball_elasticity, big_ball_friction, big_ball_density, big_ball_color))
        return ball_list
    if type == 3:
        ball_list = random_generate_particles(space, (WIDTH/2 - container_width/4, HEIGHT - 20 - container_thickness - container_height*0.75), container_width - 2*big_ball_size, container_height - 2*big_ball_size, number_of_big_ball, big_ball_size, big_ball_mass, big_ball_elasticity, big_ball_friction, big_ball_density, big_ball_color)
        ball_list.extend(random_generate_particles(space, (WIDTH/2 + container_width/4, HEIGHT - 20 - container_thickness - container_height*0.75), container_width - 2*big_ball_size, container_height - 2*big_ball_size, number_of_big_ball, big_ball_size, big_ball_mass, big_ball_elasticity, big_ball_friction, big_ball_density, big_ball_color))
        return ball_list
    if type == 4:
        ball_list = random_generate_particles(space, (WIDTH/2, HEIGHT - 20 - container_thickness - container_height*0.1), container_width - 2*big_ball_size, 0.1*container_height, number_of_big_ball, big_ball_size, big_ball_mass, big_ball_elasticity, big_ball_friction, big_ball_density, big_ball_color)
        return ball_list


def generate_small_ball(space: pymunk.Space):
    return random_generate_particles(space, (WIDTH/2, HEIGHT - 20 - container_thickness - container_height*0.5), container_width - 2*small_ball_size - 2*container_thickness, container_height - small_ball_size - container_thickness, number_of_small_ball, small_ball_size, small_ball_mass, small_ball_elasticity, small_ball_friction, small_ball_density, small_ball_color)


def generate_small_ball_to_fill(space: pymunk.Space, number_of_small: int):
    return random_generate_particles(space, (WIDTH/2, HEIGHT - 20 - container_thickness - container_height), container_width - 2*small_ball_size - 2*container_thickness, 1, number_of_small, small_ball_size, small_ball_mass, small_ball_elasticity, small_ball_friction, small_ball_density, small_ball_color)


def remove_big_ball_for_fully_packed(space: pymunk.Space, ball_list: [pymunk.Circle]):
    ball_size = ball_list[0].radius
    for particle in ball_list.copy():
        if ((HEIGHT - 20 - container_height) - (particle.body.position.y - ball_size))/(HEIGHT - 20 - container_height) > 0.02:
            space.remove(particle, particle.body)
            ball_list.remove(particle)
        elif particle.body.position.x - ball_size < (WIDTH-container_width)/2 or particle.body.position.x + ball_size > (WIDTH-container_width)/2 + container_width:
            space.remove(particle, particle.body)
            ball_list.remove(particle)


def remove_small_ball_for_fully_packed(space: pymunk.Space, ball_list: [pymunk.Circle]):
    if len(ball_list) > 0:
        ball_size = ball_list[0].radius
        for particle in ball_list.copy():
            if ((HEIGHT - 20 - container_height) - (particle.body.position.y - ball_size))/(HEIGHT - 20 - container_height) > 0.001:
                space.remove(particle, particle.body)
                ball_list.remove(particle)
            elif particle.body.position.x - ball_size < (WIDTH-container_width)/2 or particle.body.position.x + ball_size > (WIDTH-container_width)/2 + container_width:
                space.remove(particle, particle.body)
                ball_list.remove(particle)


def calculate_packing_density(ball_list: [pymunk.Circle]):
    if len(ball_list) == 0:
        return 0
    else:
        return (math.pi*(ball_list[0].radius**2))*len(ball_list)/((container_width-2*container_thickness)*(container_height-container_thickness))


def calculate_volume_of_small_ball(smallBall_list: [pymunk.Circle], bigBall_list: [pymunk.Circle]):
    if len(smallBall_list) == 0:
        return 0
    else:
        return (math.pi*(smallBall_list[0].radius**2))*len(smallBall_list)/((math.pi*(smallBall_list[0].radius**2))*len(smallBall_list) + (math.pi*(bigBall_list[0].radius**2))*len(bigBall_list))


def execute(window: pygame.display, width: int, height: int):

    timer = 0
    status = Status.EMPTY

    resultX = []
    resultY = []

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

        if status == Status.START and (pyTime.get_ticks()-timer)*0.001 >= 3: # 5 seconds after big ball generated
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

            """
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    pass
                    #pressed_pos = pygame.mouse.get_pos()
                    #small_ball1_list.extend(random_generate_particles(space, pressed_pos, WIDTH*0.3, HEIGHT*0.3, 150, 2, 10, 0.9, 0.4, (54, 89, 122, 100)))
            """

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

                """
                # generate big ball: type 1
                if event.key == pygame.key.key_code("1"):
                    big_ball_list.extend(generate_big_ball(space, 1))

                # generate big ball: type 2
                if event.key == pygame.key.key_code("2"):
                    big_ball_list.extend(generate_big_ball(space, 2))

                # generate big ball: type 3
                if event.key == pygame.key.key_code("3"):
                    big_ball_list.extend(generate_big_ball(space, 3))

                # generate big ball: type 4
                if event.key == pygame.key.key_code("4"):
                    big_ball_list.extend(generate_big_ball(space, 4))

                # generate small ball
                if event.key == pygame.key.key_code("5"):
                    small_ball_list.extend(generate_small_ball(space))

                # delete balls which are out of the container
                if event.key == pygame.key.key_code("d"):
                    remove_big_ball_for_fully_packed(space, big_ball_list)
                    remove_small_ball_for_fully_packed(space, small_ball_list)

                if event.key == pygame.key.key_code("c"):
                    for wall in wall_list:
                        space.remove(wall)
                

                if event.key == pygame.key.key_code("f"):
                    for ball in big_ball_list:
                        ball.body.apply_impulse_at_local_point((0, -1000000), (0, 0))
                    for ball in small_ball_list:
                        ball.body.apply_impulse_at_local_point((0, -100000), (0, 0))

                # reset all
                if event.key == pygame.key.key_code("r"):
                    for particle in small_ball_list:
                        space.remove(particle, particle.body)
                    small_ball_list = []
                    for particle in big_ball_list:
                        space.remove(particle, particle.body)
                    big_ball_list = []

                if event.key == pygame.key.key_code(" "):
                    draw(space, window, draw_options)

                # print result
                if event.key == pygame.key.key_code("p"):
                    print("Packing Density Report:")
                    print("------------------------------------")
                    print("Packing density of big ball: " + str(round((calculate_packing_density(big_ball_list))*(10**decimal_places))/(10**decimal_places)))
                    print("------------------------------------")
                    print("Packing density of small ball: " + str(round((calculate_packing_density(small_ball_list))*(10**decimal_places))/(10**decimal_places)))
                    print("")
                    print("")

                    #currnetTime = pyTime.get_ticks()
                    #print((currnetTime-timer)*0.001, "s")
                    #timer = currnetTime
                """

        draw(space, window, draw_options)

        """
        text_surface = base_font.render(user_text, True, (0, 255, 0))
        window.blit(text_surface, (200, 200))
        pygame.display.update()
        """

        space.step(dt)
        # setting up Frame Per Second (fps) for the screen
        clock.tick(fps)

    pygame.quit()


if __name__ == "__main__":
    menu.mainloop(window)
    #execute(window, WIDTH, HEIGHT)