import random

import pygame
import pymunk
import pymunk.pygame_util
import math

# ababdh
pygame.init()
# window size
WIDTH, HEIGHT = (pygame.display.Info().current_w*0.85, pygame.display.Info().current_h*0.85)
window = pygame.display.set_mode((WIDTH, HEIGHT))

# gravity value [m/s2]?
gravity = 981


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


def create_particle(space: pymunk.Space, radius: float, mass: float, pos: tuple[float, float], elasticity: float, friction: float, color: tuple[int, int, int, int]):
    body = pymunk.Body()
    body.position = pos
    shape = pymunk.Circle(body, radius)
    shape.mass = mass
    shape.elasticity = elasticity
    shape.friction = friction
    # RGB color with the opacity [%]
    shape.color = color
    space.add(body, shape)
    return shape


def random_generate_particles(space: pymunk.Space, generate_centre: tuple[float, float], generate_width: float, generate_height: float, number_of_particle: int, radius: float, mass: float, elasticity: float, friction: float, color: tuple[int, int, int, int]):
    particle_list = []
    for n in range(1, number_of_particle+1):
        x_pos = random.randint(int(generate_centre[0] - generate_width/2), int(generate_centre[0] + generate_width/2))
        y_pos = random.randint(int(generate_centre[1] - generate_height/2), int(generate_centre[1] + generate_height/2))
        particle_list.append(create_particle(space, radius, mass, (x_pos, y_pos), elasticity, friction, color))
    return particle_list


def execute(window: pygame.display, width: int, height: int):
    run = True
    clock = pygame.time.Clock()
    fps = 60
    dt = 1 / fps

    # setting up space
    space = pymunk.Space()
    # gravity in x and y direction
    space.gravity = (0, gravity)
    # create the boundaries
    create_boundaries(space, width, height)
    # create the container
    create_container(space, WIDTH*0.3, HEIGHT*0.3, 20, 0.9, 0.4)

    draw_options = pymunk.pygame_util.DrawOptions(window)

    particle1_list = []
    particle2_list = random_generate_particles(space, (WIDTH/2, HEIGHT - 20 - 20 - HEIGHT*0.3*0.5), WIDTH*0.3, HEIGHT*0.3, 60, 20, 30, 0.8, 0.4, (24, 5, 63, 100))
    dragging = False

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    pressed_pos = pygame.mouse.get_pos()
                    particle1_list.extend(random_generate_particles(space, pressed_pos, WIDTH*0.3, HEIGHT*0.3, 150, 2, 10, 0.9, 0.4, (54, 89, 122, 100)))

            # reset
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.key.key_code("r"):
                    for particle in particle1_list:
                        space.remove(particle, particle.body)
                    particle1_list = []
                    for particle in particle2_list:
                        space.remove(particle, particle.body)
                    particle2_list = random_generate_particles(space, (WIDTH/2, HEIGHT - 20 - 20 - HEIGHT*0.3*0.5), WIDTH*0.3, HEIGHT*0.3, 60, 20, 30, 0.8, 0.4, (24, 5, 63, 100))

        draw(space, window, draw_options)
        space.step(dt)
        # setting up Frame Per Second (fps) for the screen
        clock.tick(fps)

    pygame.quit()


if __name__ == "__main__":
    execute(window, WIDTH, HEIGHT)