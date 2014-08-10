## Copyright 2014 Ryan Moore

## This file is part of Avoid The Asteroids.

## Avoid The Asteroids is free software: you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation, either version 3 of the
## License, or (at your option) any later version.

## Avoid The Asteroids is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with Avoid The Asteroids.  If not, see
## <http://www.gnu.org/licenses/>.

import os, sys, math, pygame, pygame.mixer, random, time
import euclid # from http://pyeuclid.googlecode.com/svn/trunk/euclid.py
from functions import * # local file
from pygame.locals import *

# cool idea, use bullets to jump ships

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
DRAG = 0.9
FPS = 60

GOODY_SPAWN = 5
GOODY_LIFESPAN = 60 * GOODY_SPAWN

ENEMY_SPAWN = 1
NUM_ENEMIES = 6

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
ubergun = False
can_spawn = True
goody_modifier = 1
goody_kind = False
goody_collision_frame = False
goody_effect_len = False
original_values = True
bullets = []
goody_baskets = []
enemies_killed = 0
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

    if shoot and ubergun:
        bul_dir_1 = rotate_vec(gun_dir, 15) # counter clockwise 30 deg
        bul_dir_2 = gun_dir # center
        bul_dir_3 = rotate_vec(gun_dir, 360-15) # clockwise 30 deg

        bullets.append(Bullet(frame, color=WHITE, posn=player.posn+gun_dir, r=2,
                              vel=bul_dir_1*BULLET_VEL))
        bullets.append(Bullet(frame, color=WHITE, posn=player.posn+gun_dir, r=2,
                              vel=bul_dir_2*BULLET_VEL))
        bullets.append(Bullet(frame, color=WHITE, posn=player.posn+gun_dir, r=2,
                              vel=bul_dir_3*BULLET_VEL))
    elif shoot:
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
                enemies_killed += 1
                bullets.pop(bullet_idx)
                sprites.pop(sprite_idx)

    # remove old goody baskets and check for collision with player
    for goody_idx, goody_basket in enumerate(goody_baskets):
        if goody_basket.age(frame) > GOODY_LIFESPAN:
            goody_baskets.pop(goody_idx)

        foo, bar, was_collision = collide(goody_basket, player)
        if was_collision:
            # apply the affect of the goody basket
            # remove the goody basket
            original_values = False
            can_spawn = False
            goody_collision_frame = frame
            # delete all other goody baskets
            goody_baskets = []
            goody_kind = goody_basket.kind
            goody_modifier = goody_basket.modifier
            goody_effect_len = goody_basket.effect_len
            
            if goody_basket.kind == 'time warp':
                for enemy_idx, enemy in enumerate(sprites):
                    enemy.vel *= goody_modifier
            elif goody_basket.kind == 'fast shooter':
                FIRE_RATE *= 1.0/goody_modifier
                BULLET_LIFESPAN *= goody_modifier
            elif goody_basket.kind == 'uber gun':
                ubergun = True
                FIRE_RATE *= 1.0/goody_modifier
                BULLET_LIFESPAN *= goody_modifier

            break
        
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

    # draw goody baskets
    for idx, goody in enumerate(goody_baskets):
        goody.display(screen)
        goody.blink(frame)
    
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
        if goody_kind == 'time warp':
            # will slow down spawned enemies
            sprites.append(random_circle(PINK, goody_modifier))
        else:
            sprites.append(random_circle(PINK, 1))

    kinds = ['time warp', 'fast shooter', 'uber gun']
    if frame % (59 * GOODY_SPAWN) == 0 and can_spawn:
        goody_baskets.append(GoodyBasket(frame, kind=random.choice(kinds),
                                         posn=euclid.Vector2(random.randint(50, 750), 
                                                             random.randint(50, 550))))
    if not original_values:
        if goody_effect_len < frame - goody_collision_frame:
            can_spawn = True
            # revert to unmodified state
            original_values = True
            if goody_kind == 'time warp':
                for i, enemy in enumerate(sprites):
                    enemy.vel *= 1.0/goody_modifier
            elif goody_kind == 'fast shooter':
                FIRE_RATE *= goody_modifier
                BULLET_LIFESPAN *= 1.0/goody_modifier
            elif goody_kind == 'uber gun':
                ubergun = False
                FIRE_RATE *= goody_modifier
                BULLET_LIFESPAN *= 1.0/goody_modifier
                                         
                                                             

    frame += 1
    shoot = False


if not user_quit:
    font = pygame.font.SysFont('Helvetica', 40)
    words = "It took %s enemies to defeat you!" % len(sprites[1:])
    score = "You blew up %s asteroids!" % enemies_killed
    text = font.render(words, True, WHITE)
    screen.blit(text, (110, 190))
    text = font.render(score, True, WHITE)
    screen.blit(text, (160, 250))
    pygame.display.flip()

    pygame.event.set_allowed(pygame.QUIT)
    finished = False
    while not finished:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                finished = True


