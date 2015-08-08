'''
Created on 15-Jul-2015

@author: YudaDiga
'''
# importing everything
import os.path
from random import randint
from math import tan,atan,trunc

import pygame
from pygame.locals import *
#from string import center

# Global Variables going to be used
DEBUG = 1
SCREENRECT     = Rect(0, 0, 640, 480)
SCORE          = 0
main_dir = os.path.split(os.path.abspath(__file__))[0]

def load_image(fn):
    "loads an image, prepares it for play"
    fn = os.path.join(main_dir, 'BlocBreaker', fn)
    try:
        surface = pygame.image.load(fn)
    except pygame.error:
        raise SystemExit('Could not load image "%s" %s'%(fn, pygame.get_error()))
    return surface.convert()

def load_images(*files):
    imgs = []
    for fil in files:
        imgs.append(load_image(fil))
    return imgs


#Bar controlled by player gets a class 
class Player(pygame.sprite.Sprite):
    speed = 5
    bounce = 24
    images = []
    def __init__(self):
        if DEBUG == 1 :  
            print ("Player.__init__")
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect(midbottom=SCREENRECT.midbottom)
        self.reloading = 0
        self.origtop = self.rect.top
        self.facing = -1

    def move(self, direction):
        if DEBUG == 1 :  
            print ("Player.move")
        if direction: self.facing = direction
        self.rect.move_ip(direction*self.speed, 0)
        self.rect = self.rect.clamp(SCREENRECT)
        
#Ball That is going to kill the blocks
class Ball(pygame.sprite.Sprite):
    speedx = 0
    speedy = 3
    images = []
    def __init__(self):
        if DEBUG == 1 :
            print ("Ball.__init__")
        pygame.sprite.Sprite.__init__(self,self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect(center = SCREENRECT.center)

    def update(self):
        if DEBUG == 1 :
            print ("Ball.update")
        self.rect.move_ip(self.speedx,self.speedy)
        if self.rect.top <= 0: 
            self.speedy = -self.speedy
        if self.rect.left <= SCREENRECT.left or self.rect.right >= SCREENRECT.right:
            self.speedx = -self.speedx
     
    
class Brick(pygame.sprite.Sprite):
    speed  = 0
    images = []
    def __init__(self,i):
        if DEBUG == 1 :
            print ("Brick.__init__")
        
        pygame.sprite.Sprite.__init__(self,self.containers)
        self.image = self.images[i]
        self.rect = self.image.get_rect()
        self.id = i
        self.health = i
        
class Score(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.font = pygame.font.Font(None, 20)
        self.font.set_italic(1)
        self.color = Color('cyan')
        self.lastscore = -1
        self.update()
        self.rect = self.image.get_rect().move(10, 450)

    def update(self):
        if DEBUG == 1 :
            print ("Score.update")
        if SCORE != self.lastscore:
            self.lastscore = SCORE
            msg = "Score: %d" % SCORE
            self.image = self.font.render(msg, 0, self.color)

class Level(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.font = pygame.font.Font(None, 20)
        self.font.set_italic(1)
        self.color = Color('yellow')
        self.lastlevel = -1
        self.update()
        self.rect = self.image.get_rect().move(570, 450)

    def update(self):
        if DEBUG == 1 :
            print ("Level.update")
        if lvl != self.lastlevel:
            self.lastscore = lvl
            msg = "Level : %d" % lvl
            self.image = self.font.render(msg, 0, self.color)

def bricklayout(brick,level):
    if DEBUG == 1 :
        print ("bricklayout")
    fn = os.path.join(main_dir, 'BlocBreaker', 'data.enc')
    layout= open(fn,"r")
    level=[]
    for lino,line in enumerate(layout): 
        if lino == lvl :  
            level = line.split()
    lvlcap = lino
    for l in level:
        brick.append(Brick(int(l)))
    for x in range(1,len(brick)):
        if x % 9 == 0:
            brick[x].rect.top+=brick[x-9].rect.bottom
            brick[x].rect.left = brick[x-9].rect.left
        else:
            brick[x].rect.left += brick[x-1].rect.right
            brick[x].rect.bottom = brick[x-1].rect.bottom
    return lvlcap
def main():
    
    #Initializing Pygame
    pygame.init()
#    print pygame.font.get_fonts()

    winstyle = 0  
    bestdepth = pygame.display.mode_ok(SCREENRECT.size, winstyle, 32)
    screen = pygame.display.set_mode(SCREENRECT.size, winstyle, bestdepth)
    
    img = load_image('Bar.gif')
    Player.images = [img, pygame.transform.flip(img, 1, 0)]
    Brick.images = load_images('LLB.png','MLB.png','HLB.png')
    img = load_image('Ball.png')
    Ball.images = [img]
    
    icon = pygame.transform.scale(load_image('icon.png'), (32, 32))
    pygame.display.set_icon(icon)
    pygame.display.set_caption('Pygame BlocBreaker')
    pygame.mouse.set_visible(0)

    # screen refreshing and background
    bgdtile = load_image('background.gif')
    background = pygame.Surface(SCREENRECT.size)
    for x in range(0, SCREENRECT.width, bgdtile.get_width()):
        background.blit(bgdtile, (x, 0))
    screen.blit(background, (0,0))
    pygame.display.flip()
    
    # Initializing game groups
    if DEBUG == 1 :
        print ("# Initializing game groups")
    bricks = pygame.sprite.Group()
    all = pygame.sprite.RenderUpdates()
    rebound = pygame.sprite.Group()
    #assign default groups to each sprite class
    if DEBUG == 1 :
        print ("#assign default groups to each sprite class")
    Player.containers = rebound,all
    Ball.containers = all
    Brick.containers = bricks, all
    Score.containers = all
    Level.containers = all

    # giving globals
    global score
    clock = pygame.time.Clock()
    
    #initialize our starting sprites
    global SCORE
    global lvl,lvlcap
    lvl = 0
    bar = Player()
    ball = Ball()
    brick = []
    lvlcap = bricklayout(brick,lvl)
    no_of_bricks = len(brick);
    if pygame.font:
        all.add(Score())
        all.add(Level())

    while ball.alive():
        if DEBUG == 1 :
            print ("Enters Game Loop!!!")    
        #getting events
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                return
        keystate = pygame.key.get_pressed()
        # clear/erase the last drawn sprites
        all.clear(screen, background)

        #update all the sprites
        if DEBUG == 1 :
            print ("#update all the sprites")            
        all.update()

        #handle player input
        direction = keystate[K_RIGHT] - keystate[K_LEFT]
        bar.move(direction)
        # if player misses the ball
        if ball.rect.bottom >= SCREENRECT.bottom:
            if DEBUG == 1 :
                print ("#update all the sprites")        
            ball.kill()
            pygame.time.delay(10)
        #Detect Collisions
        coll = False
        for bar in pygame.sprite.spritecollide(ball,rebound,0):
            if DEBUG == 1 :
                print ("Collision detected")            
            coll = True
        if coll == True:
            dist = ball.rect.midbottom[0] - bar.rect.midtop[0]
            length = bar.rect.right - bar.rect.left
            if trunc(ball.speedx) == 0:
                ball.speedx = (float(dist)*2/length) * ball.speedy
            else:
                ball.speedx = tan(atan(float(ball.speedx)/ball.speedy) + atan(float(dist)*2/length)) * ball.speedy
            ball.speedy = - ball.speedy
            coll = False
        for brick in pygame.sprite.spritecollide(ball,bricks, 0):
            coll = True
            brick.health-=1
            
            if brick.health<=0:
                SCORE+=brick.id
                brick.kill()
                no_of_bricks-=1
        if coll == True:
            ball.speedy *= -1
        
        #draw the scene
        dirty = all.draw(screen)
        pygame.display.update(dirty)
        coll = False
        
        if no_of_bricks == 0:
            if DEBUG == 1 :
                print("No bricks left")
            brick = []
            if lvlcap +1 > lvl :
                lvl += 1
                lvlcap = bricklayout(brick,lvl)
                no_of_bricks = len(brick);
            else :
                print("You are Victorious!!")
                return
            pygame.time.delay(600)
            
        #cap the framerate
        clock.tick(60)        
    
# calling the main function if the game i
if __name__ == '__main__': main()