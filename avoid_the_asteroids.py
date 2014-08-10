import os, sys, math, pygame, pygame.mixer, random, time
import euclid # from http://pyeuclid.googlecode.com/svn/trunk/euclid.py
from functions import * # local file
from pygame.locals import *

# cool bug, use bullets to jump ships


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
FIRE_RATE = 8 # ie shoot every N frames
BULLET_VEL = MAX_VEL * 2
BULLET_LIFESPAN = 20 # in frames
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
gun_dir = euclid.Vector2(0, 1)
player = MyCircle(color=BLUE, posn=START_POSN, r=START_R, is_player=True)

sprites = []
for n in range(1, NUM_ENEMIES):
    sprites.append(random_circle(PINK))

## main program loop
frame = 1
user_quit = False
shoot = False
bullets = []
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
            if event.key == pygame.K_LEFT:
                vel_x = get_first_vel(vel_x, -START_VEL)
            if event.key == pygame.K_RIGHT:
                vel_x = get_first_vel(vel_x, START_VEL)
            if event.key == pygame.K_UP:
                vel_y = get_first_vel(vel_y, -START_VEL)
            if event.key == pygame.K_DOWN:
                vel_y = get_first_vel(vel_y, START_VEL)

            # deal with gun orientation
            if event.key == pygame.K_a:
                gun_dir = get_gun_dir(gun_dir, 'left')
                if frame % FIRE_RATE == 0:
                    shoot = True
            if  event.key == pygame.K_d:
                gun_dir = get_gun_dir(gun_dir, 'right')
                if frame % FIRE_RATE == 0:
                    shoot = True
            if  event.key == pygame.K_w:
                gun_dir = get_gun_dir(gun_dir, 'up')
                if frame % FIRE_RATE == 0:
                    shoot = True
            if  event.key == pygame.K_s:
                gun_dir = get_gun_dir(gun_dir, 'down')
                if frame % FIRE_RATE == 0:
                    shoot = True

                
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
        # movement in x direction
        if pressed[pygame.K_LEFT]:
            vel_x = get_new_vel(vel_x, -BUTTON_ACCEL, MAX_VEL)
        if pressed[pygame.K_RIGHT]:
            vel_x = get_new_vel(vel_x, BUTTON_ACCEL, MAX_VEL)
        if not (pressed[pygame.K_LEFT] or pressed[pygame.K_RIGHT]):
            vel_x *= DRAG

        # movement in y direction
        if pressed[pygame.K_UP]:
            vel_y = get_new_vel(vel_y, -BUTTON_ACCEL, MAX_VEL)
        if pressed[pygame.K_DOWN]:
            vel_y = get_new_vel(vel_y, BUTTON_ACCEL, MAX_VEL)
        if not (pressed[pygame.K_UP] or pressed[pygame.K_DOWN]):
            vel_y *= DRAG

        # continued gun movement
        if pressed[pygame.K_a]:
            gun_dir = get_gun_dir(gun_dir, 'left')
            if frame % FIRE_RATE == 0:
                shoot = True
        if pressed[pygame.K_d]:
            gun_dir = get_gun_dir(gun_dir, 'right')
            if frame % FIRE_RATE == 0:
                shoot = True
        if pressed[pygame.K_w]:
            gun_dir = get_gun_dir(gun_dir, 'up')
            if frame % FIRE_RATE == 0:
                shoot = True
        if pressed[pygame.K_s]:
            gun_dir = get_gun_dir(gun_dir, 'down')
            if frame % FIRE_RATE == 0:
                shoot = True

    ## game logic here ##

    # update player vel
    player.vel.x = vel_x
    player.vel.y = vel_y

    if shoot:
        bullets.append(Bullet(frame, color=WHITE, posn=player.posn+gun_dir, r=2,
                              vel=gun_dir*BULLET_VEL))

    # remove bullts once they run out of 'time'
    for bullet_idx, bullet in enumerate(bullets):
        if bullet.age(frame) > BULLET_LIFESPAN:
            bullets.pop(bullet_idx) # remove this bullet

        # check for bullets colliding with sprites except for player
        for sprite_idx, sprite in enumerate(sprites):
            foo, bar, was_collision = collide(bullet, sprite)
            if was_collision:
                bullets.pop(bullet_idx)
                sprites.pop(sprite_idx)
    
    ## drawing code goes here ##

    # deal with background
    screen.fill(BLACK)
    screen.blit(background_image, (0, 0))

    # draw player
    player.display(screen)
    player.move(SIZE)
    # update velx and vely
    vel_x, vel_y = player.vel
    
    # collide player if needed
    for idx, sprite in enumerate(sprites):
        foo, bar, was_collision = collide(player, sprite)
        if was_collision:
            running = False

    # draw sprites and collide them
    for idx, sprite in enumerate(sprites):
        sprite.display(screen)
        sprite.move(SIZE)
        for i, next_sprite in enumerate(sprites[idx+1:]):
            sprite.vel, next_sprite.vel, was_collision = collide(sprite, next_sprite)

    # draw bullets
    for idx, bullet in enumerate(bullets):
        bullet.display(screen)
        bullet.move(SIZE)
    
    # do this if you have solid wall
    # hit_x, hit_y = player.move(SIZE)

    # if hit_x:
    #     vel_x = 0
    # if hit_y:
    #     vel_y = 0
    
    
    # update screen with drawings
    pygame.display.flip()

    # limit to 60 frames per second
    clock.tick(FPS)

    if frame % (59 * ENEMY_SPAWN) == 0:
        sprites.append(random_circle(PINK))

    frame += 1
    shoot = False


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


