import os, sys, math, pygame, pygame.mixer, random, time
import euclid # from http://pyeuclid.googlecode.com/svn/trunk/euclid.py
from functions import * # local file
from pygame.locals import *



# Define some colors
BLACK = 0, 0, 0
WHITE = 255, 255, 255
GREEN = 0, 255, 0
PINK = 230, 32, 32
BLUE = 120, 217, 250
PURPLE = 235, 133, 255
PI = math.pi
SIZE = 800, 600
BUTTON_ACCEL = 0.25
START_VEL = 1
START_R = 10
MAX_VEL = 4
ENEMY_SPAWN = 1
DRAG = 0.9
FPS = 60
NUM_ENEMIES = 10
START_POSN = euclid.Vector2(400, 300)
pygame.init()


screen = pygame.display.set_mode(SIZE)
pygame.display.set_caption("Foo!")

imgdir = '/Users/ryanmoore/projects/pygame/avoid_the_asteroids/images/'
images = [imgdir + 'blue_800_600.jpg', imgdir + 'blue2_800_600_darker.jpg',
          imgdir + 'purple_800_600_darker.jpg']
pic = random.choice(images)
background_image = pygame.image.load(pic).convert()

clock = pygame.time.Clock()
running = True

vel_x = 0
vel_y = 0
sprites = [MyCircle(color=BLUE, posn=START_POSN, r=START_R)]

for n in range(1, NUM_ENEMIES):
    sprites.append(random_circle(PINK))

## main program loop
frame = 1
user_quit = False
while running:
    # main event loop
    # user did something
    for event in pygame.event.get():
        # if user clicked close
        if event.type == pygame.QUIT: 
            # flag to exit loop
            running = False
            user_quit = True

        # user pressed down on a key
        if event.type == pygame.KEYDOWN:
            # check if an error key, if yes adjust speed
            if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                vel_x = get_first_vel(vel_x, -START_VEL)
            if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                vel_x = get_first_vel(vel_x, START_VEL)
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                vel_y = get_first_vel(vel_y, -START_VEL)
            if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                vel_y = get_first_vel(vel_y, START_VEL)        
                
        # # user let up on a key
        # if event.type == pygame.KEYUP:
        #     # check if an error key, if yes adjust speed
        #     if event.key == pygame.K_LEFT:
        #         vel_x = 0
        #     if event.key == pygame.K_RIGHT:
        #         vel_x = 0
        #     if event.key == pygame.K_UP:
        #         vel_y = 0
        #     if event.key == pygame.K_DOWN:
        #         vel_y = 0

    # if key pressed down accelerate, else drag, grouped by axis
    if pygame.key.get_focused(): #make sure focus on screen
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_LEFT] or pressed[pygame.K_a]:
            vel_x = get_new_vel(vel_x, -BUTTON_ACCEL, MAX_VEL)
        if pressed[pygame.K_RIGHT] or pressed[pygame.K_d]:
            vel_x = get_new_vel(vel_x, BUTTON_ACCEL, MAX_VEL)
        if not (pressed[pygame.K_LEFT] or pressed[pygame.K_a] or 
                pressed[pygame.K_RIGHT] or pressed[pygame.K_d]):
            vel_x *= DRAG
            
        if pressed[pygame.K_UP] or pressed[pygame.K_w]:
            vel_y = get_new_vel(vel_y, -BUTTON_ACCEL, MAX_VEL)
        if pressed[pygame.K_DOWN] or pressed[pygame.K_s]:
            vel_y = get_new_vel(vel_y, BUTTON_ACCEL, MAX_VEL)
        if not (pressed[pygame.K_UP] or pressed[pygame.K_w] or 
                pressed[pygame.K_DOWN] or pressed[pygame.K_s]):
            vel_y *= DRAG

    # game logic here
    sprites[0].vel.x = vel_x
    sprites[0].vel.y = vel_y

    
    # drawing code goes here

    # deal with background
    screen.fill(BLACK)
    screen.blit(background_image, (0, 0))

    # draw enemies
    for idx, sprite in enumerate(sprites):
        sprite.display(screen)
        sprite.move(SIZE)
        for i, next_sprite in enumerate(sprites[idx+1:]):
            sprite.vel, next_sprite.vel, was_collision = collide(sprite, next_sprite)
            if idx == 0 and was_collision:
                running = False
            elif idx == 0:
                vel_x, vel_y = sprites[0].vel # update these vals too
    
    # do this if you have solid wall
    # hit_x, hit_y = sprites[0].move(SIZE)

    # if hit_x:
    #     vel_x = 0
    # if hit_y:
    #     vel_y = 0
    
    
    # update screen with drawings
    pygame.display.flip()

    # limit to 60 frames per second
    clock.tick(FPS)

    if frame == 60 * ENEMY_SPAWN:
        frame = 1
        sprites.append(random_circle(PINK))

    frame += 1


if not user_quit:
    font = pygame.font.SysFont('Helvetica', 40)
    words = "It took %s enemies to defeat you!" % len(sprites[1:])
    text = font.render(words, True, WHITE)
    screen.blit(text, (110, 190))
    pygame.display.flip()

    pygame.event.set_allowed(pygame.QUIT)
    finished = False
    while not finished:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                finished = True


