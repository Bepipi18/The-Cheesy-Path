import pygame
from pygame import mixer
import os
import random
import csv
import buttons

mixer.init() # Allows sounds
pygame.init() #initialize pygame

SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('The Cheesy Path')

#Setting framerate
clock = pygame.time.Clock()
fps = 60

#Define Game Variables
GRAVITY = 0.75
ITEMBOX_SIZE = (50, 50)
ROWS = 16
COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPE = 27
LEVEL = 1
MAX_LEVELS = 3 # Max level available according to the number of levels made
SCROLL_THRESH = 250
SCREEN_SCROLL = 0
BG_SCROLL = 0
START_GAME = False

#Define player action variables
move_left = False
move_right = False
shoot = False
throw = False
thrown_bomb = False

#Load music and sound
pygame.mixer.music.load('audio/game_music.mp3')
pygame.mixer.music.set_volume(0.1)
pygame.mixer.music.play(-1, 0.0, 3000)
# Sound Effects
jump_fx = pygame.mixer.Sound('audio/jump_up.mp3')
jump_fx.set_volume(0.2)
bomb_fx = pygame.mixer.Sound('audio/bomb_get.mp3')
bomb_fx.set_volume(0.3)
health_fx = pygame.mixer.Sound('audio/health_get.mp3')
health_fx.set_volume(0.5)
start_fx = pygame.mixer.Sound('audio/press_start.mp3')
start_fx.set_volume(0.2)
throw_fx = pygame.mixer.Sound('audio/bomb_throw.mp3')
throw_fx.set_volume(0.2)
shoot_fx = pygame.mixer.Sound('audio/shoot.mp3')
shoot_fx.set_volume(0.2)
death_fx = pygame.mixer.Sound('audio/death.mp3')
death_fx.set_volume(0.2)
enemy_death_fx = pygame.mixer.Sound('audio/enemy_death.mp3')
enemy_death_fx.set_volume(0.2)

#Defining Colors and Fonts
BLUE = (39, 73, 176)
WHITE = (255, 255, 255)
RED = (245, 20, 20)
GREEN = (89, 214, 0)
BLACK = (0, 0, 0)
FPS_NUM = pygame.font.SysFont("Futura", 25, bold = True)
font = pygame.font.Font('font/yoster.ttf', 20)
title_font = pygame.font.Font('font/yoster.ttf', 70)

#Load images
#Button Images
start_img = pygame.image.load('images/buttons/start_btn.png').convert_alpha()
exit_img = pygame.image.load('images/buttons/exit_btn.png').convert_alpha()
restart_img = pygame.image.load('images/buttons/restart_btn.png').convert_alpha()

#Load backgrounds
bg1_img = pygame.image.load('images/backgrounds/bg_1.png').convert_alpha()
bg2_img = pygame.image.load('images/backgrounds/bg_2.png').convert_alpha()
bg3_img = pygame.image.load('images/backgrounds/bg_3.png').convert_alpha()
bg4_img = pygame.image.load('images/backgrounds/bg_4.png').convert_alpha()

#Store tiles in a list
tile_img_list = []
for x in range(TILE_TYPE):
    img = pygame.image.load(f'images/tiles/{x}.png')
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    tile_img_list.append(img)
#Bullet
bullet_img = pygame.image.load('images/objects/bullet.png').convert_alpha()
#bombd
bomb_img = pygame.image.load('images/objects/bomb.png').convert_alpha()

#Pickup Boxes
health_box_img = pygame.image.load('images/objects/health_box.png').convert_alpha()
bomb_box_img = pygame.image.load('images/objects/bomb_box.png').convert_alpha()
item_boxes = {

    'Health'    : health_box_img,
    'Bomb'      : bomb_box_img,

}


#Drawing text
def draw_text(text, font, text_col, x ,y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


#Background fill
def draw_bg():
    screen.fill(BLUE)
    width = bg1_img.get_width()
    for x in range(5):
        screen.blit(bg4_img, ((x * width) - BG_SCROLL * 0.4, 0))
        screen.blit(bg3_img, ((x * width) - BG_SCROLL * 0.5, 0))
        screen.blit(bg2_img, ((x * width) - BG_SCROLL * 0.6, 0))
        screen.blit(bg1_img, ((x * width) - BG_SCROLL * 0.7, 0))

#Reset level
def reset_level():
    enemy_group.empty()
    bullet_group.empty()
    bomb_group.empty()
    kaboom_group.empty()
    item_box_group.empty()
    decor_group.empty()
    water_group.empty()
    goal_group.empty()

    #create empty tile list
    data = []
    for row in range(ROWS):
        r = [-1] * COLS
        data.append(r)

    return data

# Getting the FPS counter
def fps_counter():
    FPS = str(int(clock.get_fps() ) )
    fps_t = FPS_NUM.render(FPS, 1, pygame.Color('WHITE'))
    screen.blit(fps_t, ((SCREEN_WIDTH - 30),10))
                            


#Player Class
class Mouse(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, ammo, bomb, health):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True                 
        self.char_type = char_type     
        self.speed = speed          # Speed
        self.ammo = ammo         # This one changes
        self.start_ammo = ammo   # How much ammo a character has in the beginning
        self.bomb = bomb
        self.shoot_cooldown = 0    
        self.health = health            # Health bar
        self.max_health = self.health   # Max Health
        self.direction = 1              # Which direction it will face
        self.jump = False       
        self.in_air = True     
        self.sprint = 0
        self.vel_y = 0
        self.flip = False

        # Only for the AI
        self.move_counter = 0
        self.ai_vision = pygame.Rect(0, 0, 150, 20)
        self.ai_idle = False
        self.ai_idle_counter = 0
        self.ledge_detect = False


        #Animation by loading images
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()

        #Load animation Types
        animation_types = ['idle', 'walk', 'jump', 'death']
        for animation in animation_types:
            #reset temporary list
            temp_list = []
            #Count number of files in folder
            num_of_frames = len(os.listdir(f'images/{self.char_type}/{animation}'))
            for i in range(num_of_frames):
                img = pygame.image.load(f'images/{self.char_type}/{animation}/{animation}_{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() / scale), int(img.get_height() / scale)) ).convert_alpha()
                temp_list.append(img)
            self.animation_list.append(temp_list)    
       
        self.img = self.animation_list[self.action][self.frame_index]
        self.rect = self.img.get_rect()
        
        
        self.rect.center = (x, y)

        self.width = self.img.get_width()
        self.height = self.img.get_height()

    def update(self):
        self.update_animation()
        self.check_alive()
        #Update cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -=1


    def move(self, move_left, move_right):
        #Reset movement variables
        SCREEN_SCROLL = 0
        dx = 0 #changes in the x-coordinates
        dy = 0 #changes in the y-coordinates

        #Assigning movement if moving or right
        if move_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if move_right:
            dx = self.speed
            self.flip = False
            self.direction = 1


        #jump
        if self.jump == True and self.in_air == False:
            self.vel_y = -15
            self.jump = False
            self.in_air = True


        #Apply gravity
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y = 10
        dy += self.vel_y + 2


        #Check collision
        for tile in world.obstacle_list:
            #Check collision in the x direction
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
                #If ai hit a wall, turn around
                if self.char_type == 'enemy':
                    self.direction *= -1
                    self.move_counter = 0

            #Check for collision in the y direction
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                #Check if below ground, i.e jumping
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                #Check if above ground, i.e falling
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom


        #Check for collision with water
        if pygame.sprite.spritecollide(self, water_group, False):
            self.health = 0

        #Check for collide with goal
        level_complete = False
        if pygame.sprite.spritecollide(self, goal_group, False):
           level_complete = True  

        #If fallen off map
        if self.rect.bottom > SCREEN_HEIGHT:
            self.health = 0

        # Check if player is going off screen edges
        if self.char_type == 'player':
            if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
                dx = 0


        #updating the Rectangle position
        self.rect.x += dx
        self.rect.y += dy

        #update scroll based on player's position
        if self.char_type =='player':
            if (self.rect.right > SCREEN_WIDTH - SCROLL_THRESH and BG_SCROLL < (world.level_length * TILE_SIZE) - SCREEN_WIDTH) \
                or (self.rect.left < SCROLL_THRESH and BG_SCROLL > abs(dx)):
            
                self.rect.x -= dx
                SCREEN_SCROLL= -dx

        return SCREEN_SCROLL, level_complete

    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 60
            bullet = Bullet(self.rect.centerx + (self.rect.size[0] * 0.75 * self.direction), self.rect.centery , self.direction)
            bullet_group.add(bullet)
            self.ammo -= 1 #Decreases ammo every shot fired
            shoot_fx.play()


    def AI(self):

        if self.alive and player.alive:
            if self.ai_idle == False and random.randint(1, 500) == 3:
                self.ai_idle = True
                self.update_action(0) #AI idle
                self.ai_idle_counter = 50

            if self.ai_vision.colliderect(player.rect):
                #Stop running
                self.update_action(0)
                self.shoot()
                

            else:
                if self.ai_idle == False: # AI Moves
                    if self.direction == 1:
                        ai_move_right = True
                    else:
                        ai_move_right = False

                    ai_move_left = not ai_move_right
                    self.move(ai_move_left, ai_move_right)

                    self.update_action(1) 
                    self.move_counter += 1
                    
                    #Update ai vision as the enemy moves
                    self.ai_vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery )
                    #pygame.draw.rect(screen, RED, self.ai_vision, 2) #ENEMY VISION RANGE   

                    if self.move_counter > TILE_SIZE:
                        self.direction *= -1
                        self.move_counter *= 0

                else:
                    self.ai_idle_counter -= 1
                    if self.ai_idle_counter <= 0:
                        self.ai_idle = False

        #scroll
        self.rect.x += SCREEN_SCROLL


    def update_animation(self):
        #Update animation
        ANIIMATION_COOLDOWN = 100 # Higher is slow, lower is fast

        #Update image depending on the current frame
        self.img = self.animation_list[self.action][self.frame_index]

        #Check if enough time has passed since last update
        if pygame.time.get_ticks() - self.update_time > ANIIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1

        # Reset animation after finishing all frames
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
        
            else:
                self.frame_index = 0

    def update_action(self, new_action):
        #Check if the new action is different to the previous one
        if new_action != self.action:
            self.action = new_action
            #Update the animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()


    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(3)
            self.sound_play = False


    def draw(self):
        screen.blit(pygame.transform.flip(self.img, self.flip, False), self.rect)
        # pygame.draw.rect(screen, WHITE, self.rect, 1) #Entity Hitboxes

class World():
    def __init__(self):
        self.obstacle_list = []

    def process_data(self, data): #Process and Load world data
        self.level_length = len(data[0])
        #Iterate through each value in level data file
        for y, row in enumerate(data):
            for x, tile in enumerate(row):

                if tile >= 0:
                    img = tile_img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect) #stores the tiles into a tuple
                    
                    # Tile appending
                    if tile >= 0 and tile <= 12:
                        self.obstacle_list.append(tile_data)
                        
                    elif tile >= 13 and tile <= 14:
                        water = Water(img, x * TILE_SIZE, y * TILE_SIZE)
                        water_group.add(water)

                    elif tile == 15: #Create health boxes
                        item_box = ItemBox('Health', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)

                    elif tile == 16: #Create bomb boxes
                        item_box = ItemBox('Bomb', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)

                    elif tile == 17:
                                      #(chartype,     x,             y,      scale, speed, ammo, bomb,   health)
                        player = Mouse('player', x * TILE_SIZE, y * TILE_SIZE, 0.4,     8,     0,    6,     100)
                        health_bar = HealthBar(10, 10, player.health, player.health)

                    elif tile == 18: #Create enemy
                        enemy = Mouse('enemy', x * TILE_SIZE, y * TILE_SIZE, 0.4, 2, 999, 0, 100)
                        enemy_group.add(enemy)

                    elif tile >= 19 and tile <= 25: #Create goal
                        decor = Decoration(img, x * TILE_SIZE, y * TILE_SIZE)
                        decor_group.add(decor)

                    elif tile == 26: #Create goal
                        goal = Goal(img, x * TILE_SIZE, y * TILE_SIZE)
                        goal_group.add(goal)
                        
                        
                    #elif tile == [num]:
                    #   name = class(variables)
                    #   name_group.add(name)


        return player, health_bar

    def draw(self):
        for tile in self.obstacle_list:
            tile[1][0] += SCREEN_SCROLL
            screen.blit(tile[0], tile[1])

#Decorations
class Decoration(pygame.sprite.Sprite): #No Collisions
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()) )

    def update(self):
        self.rect.x += SCREEN_SCROLL

#Water
class Water(pygame.sprite.Sprite): 
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()) )

    def update(self):
        self.rect.x += SCREEN_SCROLL

#Goal
class Goal(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height() + 3) )

    def update(self):
        self.rect.x += SCREEN_SCROLL

#Item Drops
class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = pygame.transform.scale(item_boxes[self.item_type], ITEMBOX_SIZE)
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE -self.image.get_height()) )


    def update(self):
        self.rect.x += SCREEN_SCROLL
        #Check if the player picked up the box
        if pygame.sprite.collide_rect(self, player):
            #Check what kind of item it collides
            if self.item_type == 'Health':
                player.health += 25
                health_fx.play()
                if player.health > player.max_health:
                    player.health = player.max_health

            elif self.item_type == 'Bomb':
                player.bomb += 3
                bomb_fx.play()

            #delete item box
            self.kill()
  

class HealthBar():
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health

    def draw(self, health):
        #Update with new health
        self.health = health

        #Calculate health ratio
        ratio = self.health / self.max_health

        pygame.draw.rect(screen, BLACK, (self.x - 2, self.y - 2, 154, 24)) 
        pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20)) 
        pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20))
        

#Projectile Class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 5
        self.image = bullet_img
        self.image = pygame.transform.scale(self.image, (self.image.get_width() * 2 , self.image.get_height() * 2))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction
    
    def update(self):      #Update if the Entity is Alive or Dead
        #Move bullet
        self.rect.x += (self.direction * self.speed) + SCREEN_SCROLL
        #Check if bullet has gone offscreen
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()
        #Check for collision with level
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()
        
        #Check collision with characters
        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.alive:
                player.health -= 10
                self.kill()



class Bomb(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.timer = 100
        self.vel_y = -10
        self.speed = 5
        self.slow_down = 0.5
        self.image = bomb_img
        self.image = pygame.transform.scale(self.image, (self.image.get_width() * 2 , self.image.get_height() * 2 ))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self):
        self.vel_y += GRAVITY
        dx = self.direction * self.speed
        dy = self.vel_y
        #pygame.draw.rect(screen, WHITE, self.rect, 2) #bomb hitbox
        
        #Check for collision with level
        for tile in world.obstacle_list:
             #Check if bomb hit a wall
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                self.direction *= -1
                dx = self.direction * self.speed

             #Check for collision in the y direction
            if tile[1].colliderect(self.rect.x, self.rect.y + dy + 5, self.width, self.height):
                #Check if below ground, i.e throwing up
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                #Check if above ground, i.e throwing down
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom

                    #slow down bomb after a while
                    if self.speed > 0:
                        self.speed -= self.slow_down

                        if self.speed < 0.1:
                            self.speed = 0
                            dx = 0
                    else:
                        self.speed = 0
                        dx = 0

        #Update bomb position
        self.rect.x += dx + SCREEN_SCROLL
        self.rect.y += dy

        
        #countdown till boom
        self.timer -= 1
        if self.timer <= 0:
            self.kill()
            kaboom = Kaboom(self.rect.x, self.rect.y, 0.5)
            kaboom_group.add(kaboom)

            #Dealing damage to anyone nearby
            if abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * 2 and \
                abs(self.rect.centery - player.rect.centery) < TILE_SIZE * 2:
                player.health -= 25
                
            for enemy in enemy_group:
                if abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE * 2 and \
                    abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE * 2:
                    enemy.health -= 50



class Kaboom(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(6):
            img = pygame.image.load(f'images/effects/exp{num}.png').convert_alpha()
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            self.images.append(img)
        self.frame_index = 0
        self.image = self.images[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0

    def update(self):
        self.rect.x += SCREEN_SCROLL
        kaboom_speed = 9
        #update kaboom animation
        self.counter += 1
        if self.counter >= kaboom_speed:
            self.counter = 0
            self.frame_index += 1
            #IF animation complete then delete kaboom animation
            if self.frame_index >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.frame_index]      


#Create Buttons
start_button = buttons.Button(SCREEN_WIDTH // 2 - 113, SCREEN_HEIGHT // 2 - 50, start_img, 0.8)
exit_button = buttons.Button(SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT // 2 + 90, exit_img, 0.9)
restart_button = buttons.Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50, restart_img, 2)

#Create Sprite Group
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
bomb_group = pygame.sprite.Group()
kaboom_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
decor_group = pygame.sprite.Group()
goal_group = pygame.sprite.Group()
# name_group = pygame.sprite.Group()



#Level Data
world_data = []
for row in range(ROWS):
    r = [-1] * COLS
    world_data.append(r)

#load in level data and create world
with open(f'savefile_level{LEVEL}.csv', newline = '') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)


world = World()
player, health_bar = world.process_data(world_data)

run = True
while run:
    
    if START_GAME == False:
        #Draw Main Menu
        screen.fill(BLUE)
        draw_text('THE CHEESY PATH', title_font, WHITE, 65, 120)
        draw_text('Press [Q] to throw cheese bomb', font, WHITE, SCREEN_WIDTH // 4, SCREEN_HEIGHT - 80 )
        draw_text('Press [W] to jump', font, WHITE, SCREEN_WIDTH // 4 + 90, SCREEN_HEIGHT - 55 )
        draw_text('Press [A] or [D] to move left or right', font, WHITE, SCREEN_WIDTH // 4 - 30, SCREEN_HEIGHT - 30 )
        
        if start_button.draw(screen):
            START_GAME = True
            start_fx.play()
        if exit_button.draw(screen):
            run = False

    else:
        #update Background
        draw_bg()
        #Draw world map
        world.draw()
        fps_counter()
        #Show Health Bar
        health_bar.draw(player.health)
        #Show bomb
        draw_text(f'BLUE CHEESE: {player.bomb}', font, WHITE, 10, 40)

        #Group Updates
        for enemy in enemy_group:
            enemy.AI()
            enemy.update()
            enemy.draw()

        bullet_group.update()
        bomb_group.update()
        kaboom_group.update()
        item_box_group.update()
        water_group.update()
        decor_group.update()
        goal_group.update()
        #name_group.update()

        #Putting everything into the screen
        bullet_group.draw(screen)
        bomb_group.draw(screen)
        kaboom_group.draw(screen)
        item_box_group.draw(screen)
        water_group.draw(screen)
        decor_group.draw(screen)
        goal_group.draw(screen)
        #name_group.draw(screen)

        player.update()
        player.draw()



        #Update player actions
        if player.alive:

            if throw and thrown_bomb == False and player.bomb > 0:
                bomb = Bomb(player.rect.centerx + (player.rect.size[0] * 0.5 * player.direction),\
                        player.rect.top, player.direction)
                bomb_group.add(bomb)
                thrown_bomb = True
                player.bomb -= 1 #Reduce bomb
                throw_fx.play()
            if player.in_air:
                player.update_action(2) #[2] means jump
            elif move_left or move_right:
                player.update_action(1) # [1] means walk
            else:
                player.update_action(0) # [0] means idle

            SCREEN_SCROLL, level_complete = player.move(move_left, move_right)
            BG_SCROLL -= SCREEN_SCROLL
            #check if player has completed the level
            if level_complete:
                LEVEL += 1
                BG_SCROLL = 0
                world_data = reset_level()
                if LEVEL <= MAX_LEVELS:
                    #load in level data and create world
                    with open(f'savefile_level{LEVEL}.csv', newline = '') as csvfile:
                        reader = csv.reader(csvfile, delimiter=',')
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)

                    world = World()
                    player, health_bar = world.process_data(world_data)

                else:
                    run = False
                    print ("You Win!")
        else:
            SCREEN_SCROLL = 0
            if restart_button.draw(screen):
                BG_SCROLL = 0
                world_data = reset_level()
                #load in level data and create world
                with open(f'savefile_level{LEVEL}.csv', newline = '') as csvfile:
                    reader = csv.reader(csvfile, delimiter=',')
                    for x, row in enumerate(reader):
                        for y, tile in enumerate(row):
                            world_data[x][y] = int(tile)


                world = World()
                player, health_bar = world.process_data(world_data)

        clock.tick(fps)
    

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        #Keyboard Presses
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                move_left = True
            if event.key == pygame.K_d:
                move_right = True
            if event.key == pygame.K_w and player.alive and not player.in_air:
                player.jump = True
                jump_fx.play()
            if event.key == pygame.K_SPACE:
                shoot = True
            if event.key == pygame.K_q:
                throw = True
            if event.key == pygame.K_ESCAPE:
                run = False

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                move_left = False
            if event.key == pygame.K_d:
                move_right = False
            if event.key == pygame.K_SPACE:
                shoot = False
            if event.key == pygame.K_q:
                throw = False
                thrown_bomb = False
    
    pygame.display.update()

pygame.quit()