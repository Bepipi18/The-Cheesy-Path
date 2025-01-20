import pygame
import buttons
import csv
import os

pygame.init()

clock = pygame.time.Clock()
fps = 60

#Game window
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 500

LOWER_MARJIN = 100
SIDE_MARJIN = 300

screen = pygame.display.set_mode((SCREEN_WIDTH + SIDE_MARJIN, SCREEN_HEIGHT + LOWER_MARJIN))
pygame.display.set_caption('Level Editor')

#Define Game Variables-------------------------
#Tiles and grids
ROWS = 16
MAX_COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPE  = 27 #Change depending on how many tiles you have----------
current_tile = 0

#Level---------------------------------------------------------------
level = 0

#Scrolling
scroll_left = False
scroll_right = False
scroll = 0
scroll_speed = 1


#Load Background Images-----------------------------------
bg1_img = pygame.image.load('images/backgrounds/bg_1.png').convert_alpha()
bg2_img = pygame.image.load('images/backgrounds/bg_2.png').convert_alpha()
bg3_img = pygame.image.load('images/backgrounds/bg_3.png').convert_alpha()
bg4_img = pygame.image.load('images/backgrounds/bg_4.png').convert_alpha()



#Storing tiles in a list----------------------
img_list = []
for x in range(TILE_TYPE):
    img = pygame.image.load(f'images/tiles/{x}.png').convert_alpha()
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)


#Save and Load buttons------------------------
save_img = pygame.image.load('images/buttons/save_btn.png').convert_alpha()
load_img = pygame.image.load('images/buttons/load_btn.png').convert_alpha()
delete_img = pygame.image.load('images/buttons/delete_btn.png').convert_alpha()

#Defining Fonts and Colours for the menu---------------
#Colours
BLUE  = (58, 100, 224)
WHITE = (255, 255, 255)
RED = (245, 20, 20)

#Fonts
font = pygame.font.Font('font/yoster.ttf', 18)


#Create Empty Tile List----------------------
world_data = []
for row in range (ROWS):
    r = [-1] * MAX_COLS
    world_data.append(r)


#Create Ground------------------------------
for tile in range(0, MAX_COLS):
    world_data[ROWS - 1][tile] = 0

#Function to output text onto the screen---
def draw_text (text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

#Function for drawing the world tiles-------
def draw_world():
    for y, row in enumerate(world_data):
        for x, tile in enumerate(row):
            if tile >= 0:
                screen.blit(img_list[tile], (x * TILE_SIZE - scroll, y * TILE_SIZE))



#Create function for drawing background-----
def draw_bg():
    screen.fill(BLUE)
    width = bg1_img.get_width()
    for x in range(5):
        screen.blit(bg4_img, ((x * width) -  scroll * 0.4, 0))
        screen.blit(bg3_img, ((x * width) - scroll * 0.5, 0))
        screen.blit(bg2_img, ((x * width) - scroll * 0.6, 0))
        screen.blit(bg1_img, ((x * width) - scroll * 0.7, 0))

def draw_grid():
    #Vertical lines------------------------
    for c in range(MAX_COLS + 1):
            pygame.draw.line(screen, WHITE, (c * TILE_SIZE - scroll, 0), (c * TILE_SIZE - scroll, SCREEN_HEIGHT))
    #Horizontal lines
    for c in range(ROWS + 1):
            pygame.draw.line(screen, WHITE, (0, c * TILE_SIZE), (SCREEN_WIDTH, c * TILE_SIZE))


# Creating Save and Load Buttons------------------------
#   arg = buttons.Button (x, y, image, scale)
save_button = buttons.Button(SCREEN_WIDTH // 2, SCREEN_HEIGHT + LOWER_MARJIN - 60, save_img, 1)
load_button = buttons.Button(SCREEN_WIDTH // 2 + 200, SCREEN_HEIGHT + LOWER_MARJIN - 60, load_img, 1)
delete_button = buttons.Button(SCREEN_WIDTH // 2 + 106, SCREEN_HEIGHT + LOWER_MARJIN - 50, delete_img, 0.7)

# Make a button list
button_list = []
button_col = 0
button_row = 0
# Arranging the Tiles Button------------------
for i in range(len(img_list)):
    tile_button = buttons.Button(SCREEN_WIDTH + (75 *  button_col) + 20, (75 * button_row) + 40, img_list[i], 1.3) #(x, y, image, scale)
    button_list.append(tile_button)
    button_col += 1

    if button_col == 4:
        button_row += 1
        button_col = 0

#Where the Game actually [Start]---------
run = True
while run:

    clock.tick(60)
    draw_bg()
    draw_grid()
    draw_world()

    # Drawing the side panels and tiles
    # rect(x ,y, width, height)
    pygame.draw.rect(screen, BLUE, (SCREEN_WIDTH, 0, SIDE_MARJIN, SCREEN_HEIGHT))
    pygame.draw.rect(screen, BLUE, (0, SCREEN_HEIGHT - 5, SCREEN_WIDTH + SIDE_MARJIN, LOWER_MARJIN + 10))

    #Save and Load data
    if save_button.draw(screen):
        #Save level data
        with open(f'savefile_level{level}.csv', 'w', newline='') as f:
            writer = csv.writer(f, delimiter= ',')
            for row in world_data:
                writer.writerow(row)

    if load_button.draw(screen):
        #Load in level data
        #reset scroll back to zero
        scroll = 0
        with open(f'savefile_level{level}.csv', newline='') as f:
            reader = csv.reader(f, delimiter= ',')
            for x, row in enumerate(reader):
                for y, tile in enumerate(row):
                    world_data[x][y] = int(tile)

    if delete_button.draw(screen):
    #delete level data
    #reset scroll back to zero
        scroll = 0
        delete_level = f'savefile_level{level}.csv'
        os.remove(delete_level)
        print(f"{delete_level} has been deleted")


    # Outputing the texts
    #(text, font, text_col, x, y)
    draw_text(f'Level: {level}', font, WHITE, 10, SCREEN_HEIGHT + LOWER_MARJIN - 90)
    draw_text(f'Press UP or DOWN to change level', font, WHITE, 10, SCREEN_HEIGHT + LOWER_MARJIN - 70)

    # Choosing a tile
    button_count = 1
    for button_count, i in enumerate(button_list):
        if i.draw(screen):
            current_tile = button_count

    #Higlighting The Selected Tile
    pygame.draw.rect(screen, RED, button_list[current_tile].rect, 3)

    #Scrolling through the Map
    # [scroll] controls the speed of scrolling
    if scroll_left == True and scroll > 0:
        scroll -= 10 * scroll_speed
    if scroll_right == True and scroll < (MAX_COLS * TILE_SIZE) - SCREEN_WIDTH:
        scroll += 10 *scroll_speed

    #Get mouse position
    pos = pygame.mouse.get_pos()
    x = (pos[0] + scroll) // TILE_SIZE
    y = (pos[1] // TILE_SIZE)

    #Check whether the coordinates are within the drawing area
    if pos[0] < SCREEN_WIDTH and pos[1] < SCREEN_HEIGHT:

        if pygame.mouse.get_pressed()[0] == 1: #Update tile value
            if world_data[y][x] != current_tile:
                world_data[y][x] = current_tile

        if pygame.mouse.get_pressed()[2] == 1:
            world_data[y][x] = -1


    #Closing the game
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w and level < 3: #Change max level
                level += 1
            if event.key == pygame.K_s and level > 0:
                level -= 1

            if event.key == pygame.K_a:
                scroll_left = True
            if event.key == pygame.K_d:
                scroll_right = True
            if event.key == pygame.K_LSHIFT:
                scroll_speed = 5

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                scroll_left = False
            if event.key == pygame.K_d:
                scroll_right = False
            if event.key == pygame.K_LSHIFT:
                scroll_speed = 1

    pygame.display.update()

pygame.quit()