from vpython import *
from random import uniform as rand

scene.background = vector(.875, .85, 1)
scene.disable_shaders = True

SCREEN_SCALE = 800
ASPECT_RATIO = 16 / 9

scene.width = SCREEN_SCALE
scene.height = SCREEN_SCALE * (ASPECT_RATIO ** -1)


PARTICLE_COLOR = color.red
PARTICLE_RADIUS = .6
WALL_COLOR = color.black
DO_COLLISION_COLOR = False
COLLISION_COLOR = color.green

particles = []

PARTICLE_COUNT = 140

MAX_SLOW_SPEED = 3
MAX_FAST_SPEED = 9

for _ in range(PARTICLE_COUNT // 2): # adding to the left box
    position = vector(rand(-19, -1), rand(-9, 9), 0)
    velocity = vector(rand(-MAX_SLOW_SPEED, MAX_SLOW_SPEED), rand(-MAX_SLOW_SPEED, MAX_SLOW_SPEED), 0)
    
    particles.append(sphere(pos=position, vel=velocity, color=PARTICLE_COLOR,
                            radius=PARTICLE_RADIUS, colliding=False))

for _ in range(PARTICLE_COUNT // 2): # adding to the right box
    position = vector(rand(1, 19), rand(-9, 9), 0)
    velocity = vector(rand(-MAX_FAST_SPEED, MAX_FAST_SPEED), rand(-MAX_FAST_SPEED, MAX_FAST_SPEED), 0)
    
    particles.append(sphere(pos=position, vel=velocity, color=PARTICLE_COLOR,
                            radius=PARTICLE_RADIUS, colliding=False))
    
TEXT_COLOR = color.black
total_energy_label = label(pos=vector(0, 12, 0), height=30, color=TEXT_COLOR)
left_energy_label = label(pos=vector(-10, -12, 0), height=20, color=TEXT_COLOR)
right_energy_label = label(pos=vector(10, -12, 0), height=20, color=TEXT_COLOR)

barriers = [
    box(pos=vector(-10, -10, 0), size=vector(20, 1, 1), color=WALL_COLOR),
    box(pos=vector(-10, 10, 0), size=vector(20, 1, 1), color=WALL_COLOR),
    box(pos=vector(-20, 0, 0), size=vector(1, 20, 1), color=WALL_COLOR),
    box(pos=vector(0, 0, 0), size=vector(1, 20, 1), color=WALL_COLOR),
    box(pos=vector(10, -10, 0), size=vector(20, 1, 1), color=WALL_COLOR),
    box(pos=vector(10, 10, 0), size=vector(20, 1, 1), color=WALL_COLOR),
    box(pos=vector(20, 0, 0), size=vector(1, 20, 1), color=WALL_COLOR),
]

def remove_middle_barrier():
    global barrier_there

    if barrier_there:
        MIDDLE_BARRIER_INDEX = 3
        barriers[MIDDLE_BARRIER_INDEX].visible = False
        barriers.pop(MIDDLE_BARRIER_INDEX)
    else:
        barriers.insert(3, box(pos=vector(0, 0, 0), size=vector(1, 20, 1), color=WALL_COLOR))
    barrier_there = not barrier_there

barrier_there = True
scene.bind("mousedown", remove_middle_barrier)

def update_movement(particle):
    
    for barrier in barriers:

        if barrier.size.x > barrier.size.y: # horizontal barrier
            if particle.pos.y < barrier.pos.y and particle.pos.y \
                    + particle.radius > barrier.pos.y - (barrier.size.y / 2):
                # particle is below the barrier and it is colliding with it
                particle.vel.y = -abs(particle.vel.y)
            elif particle.pos.y > barrier.pos.y and particle.pos.y \
                    - particle.radius < barrier.pos.y + (barrier.size.y / 2):
                # particle is above the barrier and colliding with it
                particle.vel.y = abs(particle.vel.y)

        else: # vertical barrier
            if particle.pos.x < barrier.pos.x and particle.pos.x \
                    + particle.radius > barrier.pos.x - (barrier.size.x / 2):
                # particle is below the barrier and it is colliding with it
                particle.vel.x = -abs(particle.vel.x)
            elif particle.pos.x > barrier.pos.x and particle.pos.x \
                    - particle.radius < barrier.pos.x + (barrier.size.x / 2):
                # particle is above the barrier and colliding with it
                particle.vel.x = abs(particle.vel.x)


    particle.pos += particle.vel * deltat


def is_colliding(particle_1, particle_2):
    if abs(particle_1.pos.y - particle_2.pos.y) > PARTICLE_RADIUS * 2 \
            or abs(particle_1.pos.x - particle_2.pos.x) > PARTICLE_RADIUS * 2:
        return False
    
    y_distance = particle_1.pos.y - particle_2.pos.y
    x_distance = particle_1.pos.x - particle_2.pos.x

    return (y_distance ** 2 + x_distance ** 2) ** 0.5 < PARTICLE_RADIUS * 2


def handle_collision(particle_1, particle_2):
    if sign(particle_2.vel.y - particle_1.vel.y) == sign(particle_2.pos.y - particle_1.pos.y) \
        and sign(particle_2.vel.x - particle_1.vel.x) == sign(particle_2.pos.x - particle_1.pos.x):
        return

    vel_diff = particle_1.vel - particle_2.vel
    pos_diff = particle_1.pos - particle_2.pos
    vel_change = (vel_diff.dot(pos_diff) / (mag(pos_diff) ** 2)) * pos_diff

    particle_1.vel -= vel_change
    particle_2.vel += vel_change

    if DO_COLLISION_COLOR:
        particle_1.color = COLLISION_COLOR
        particle_2.color = COLLISION_COLOR
        particle_1.colliding = True
        particle_2.colliding = True


def update(particle, index):
    update_movement(particle)
    
    if not particle.colliding and DO_COLLISION_COLOR:
        particle.color = PARTICLE_COLOR

    for other_particle in particles[index + 1:]:
        
        if is_colliding(particle, other_particle):
            handle_collision(particle, other_particle)
            
    particle.colliding = False


HEAT_SOURCE_ENABLED = False
HEATING_RATE = .5

target_frame_rate = 60
t = 0
deltat = 1 / target_frame_rate

while True:
    rate(target_frame_rate)
    t += deltat

    right_energy = 0
    left_energy = 0
    right_counter = 0
    left_counter = 0
    
    for index, particle in enumerate(particles):
        update(particle, index)

        particle_energy = (mag(particle.vel) ** 2) / 2

        particle_coloration = min(((particle_energy ** .3) / 2.8) , 1)
        particle.color = vector(particle_coloration, particle_coloration, particle_coloration)

        if particle.pos.x < 0:
            left_energy += particle_energy
            left_counter += 1
        else:
            right_energy += particle_energy
            right_counter += 1

    if t > 2 and HEAT_SOURCE_ENABLED:

        heating_particle = particles[PARTICLE_COUNT - 1]

        heating_particle.color = color.red
        heating_particle.vel.y += HEATING_RATE * sign(heating_particle.vel.y)
        heating_particle.vel.x += HEATING_RATE * sign(heating_particle.vel.x)

    if 0 in (right_counter, left_counter):
        continue

    right_avg_energy = right_energy / right_counter
    left_avg_energy = left_energy / left_counter
    total_avg_energy = (left_energy + right_energy) / PARTICLE_COUNT

    right_energy_label.text = f"avg kinetic energy on the right: {(right_avg_energy):.3} J"
    
    left_energy_label.text = f"avg kinetic energy on the left: {(left_avg_energy):.3} J"
    
    total_energy_label.text = f"total avg kinetic energy: {(total_avg_energy):.3} J"
