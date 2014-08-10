import pygame, euclid, math, random

def reflect_x(vec):
    return vec.reflect(euclid.Vector2(1, 0))

def reflect_y(vec):
    return vec.reflect(euclid.Vector2(0, 1))

def get_first_vel(current, start_vel):
    if abs(current) < 0.1:
        return start_vel
    else:
        return current + start_vel

def get_new_vel(current, accel, max_vel):
    new = current + accel
    if abs(new) > max_vel and new < 0:
        return -max_vel
    elif abs(new) > max_vel and new > 0:
        return max_vel
    else:
        return new

class MySprite:
    def __init__(self, color=(0, 0, 0), posn=(20, 20), line_width=0):
        self.color = color
        self.x = posn[0]
        self.posn.y = posn[1]
        self.line_width = line_width

class MyCircle:
    def __init__(self, color=(0, 0, 0), posn=euclid.Vector2(20, 20), r=10, 
                 line_width=0, vel=euclid.Vector2(0,0)):
        self.color = color
        self.posn = posn
        self.r = r
        self.line_width = line_width
        self.vel = vel

    def display(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.posn.x), int(self.posn.y)), 
                           self.r, 
                           self.line_width)

    def bounce(self, (screen_width, screen_height)):
        # bounce off bottom
        if self.posn.y >= screen_height - self.r:
            self.vel = reflect_y(self.vel)
        # bounce off top
        elif self.posn.y <= 0 + self.r:
            self.vel = reflect_y(self.vel)

        # bounce of right
        if self.posn.x >= screen_width - self.r:
            self.vel = reflect_x(self.vel)
        # bounce off left
        elif self.posn.x <= 0 + self.r:
            self.vel = reflect_x(self.vel)

    def toroid(self, (screen_width, screen_height)):
        # bounce off bottom
        if self.posn.y >= screen_height:
            self.posn.y = 0 # go to top
        # bounce off top
        elif self.posn.y < 0:
            self.posn.y = screen_height

        # bounce of right
        if self.posn.x >= screen_width:
            self.posn.x = 0
        # bounce off left
        elif self.posn.x < 0:
            self.posn.x = screen_width

    def solid_wall(self, (screen_width, screen_height)):
        hit_x = False
        hit_y = False
        # bounce off bottom
        if self.posn.y >= screen_height - self.r:
            self.posn.y = screen_height - self.r # go to top
            hit_y = True
        # bounce off top
        elif self.posn.y < self.r:
            self.posn.y = self.r
            hit_y = True

        # bounce of right
        if self.posn.x >= screen_width - self.r:
            self.posn.x = screen_width - self.r
            hit_x = True
        # bounce off left
        elif self.posn.x < self.r:
            self.posn.x = self.r
            hit_x = True

        return [hit_x, hit_y]

            
    def move(self, (screen_width, screen_height)):
        self.posn.x += self.vel.x
        self.posn.y += self.vel.y
        #        return self.solid_wall((screen_width, screen_height))
        self.toroid((screen_width, screen_height))

class MyRect:
    def __init__(self, color=(0, 0, 0), top_left=(20, 20), w=10, h=10, line_width=0):
        self.color = color
        self.posn.x = top_left[0]
        self.posn.y = top_left[1]
        self.top_left = top_left
        self.w = w
        self.h = h
        self.line_width = line_width

    def display(self, surface):
        pygame.draw.rect(surface, self.color, (self.posn.x, self.posn.y, self.w, 
                                               self.h), 
                         self.line_width)

def degrees_between_vecs(vec1, vec2):
    vec1_deg = math.degrees(math.atan2(vec1.y, vec1.x))
    vec2_deg = math.degrees(math.atan2(vec2.y, vec2.x))

    return abs(vec1_deg - vec2_deg)
        
def vec_len(vec):
    """vec is a euclid.Vector2"""
    return math.hypot(vec.x, vec.y)
        
def in_contact(circ1, circ2):
    """circ1 and circ2 are MyCircle objects. returns collision plane if in contact"""
    difference = circ1.posn - circ2.posn
    distance = vec_len(difference)
    if distance < circ1.r + circ2.r:
        return [circ1.r+circ2.r - distance, difference.normalize()]
    else:
         return [False, False]

def rotate_ninety(vec):
    return euclid.Vector2(-vec.y, vec.x)

def collide(circ1, circ2):
    """to adjust for overlap, pick second circle, adjust its pos by
    the overlap percent of its vel vector."""

    degrees_between = degrees_between_vecs(circ1.vel, circ2.vel)

    overlap, col_plane = in_contact(circ1, circ2)
    # if col_plane and degrees_between < 0.45:
    #     print 'here'
    #     circ1_vel = circ1.vel.reflect(rotate_ninety(col_plane))
    #     circ2_vel = circ2.vel.reflect(rotate_ninety(col_plane))
    #     return [circ1_vel, circ2_vel]
    if col_plane:
        circ1_vel = circ1.vel.reflect(col_plane)
        circ2_vel = circ2.vel.reflect(col_plane)
        return [circ1_vel, circ2_vel, True]

    else:
        # return the original values
        return [circ1.vel, circ2.vel, False]
                

def random_circle(color):
    rad = int(random.gauss(12, 10))
    if rad < 5:
        rad = 5
    return MyCircle(color=color, 
                    posn=euclid.Vector2(random.randint(50, 750), 
                                        random.randint(50, 550)), 
                                        r=rad, 
                                        vel = euclid.Vector2(random.randint(-2, 2), 
                                                             random.randint(-2, 2)))