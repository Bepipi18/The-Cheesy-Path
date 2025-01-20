import pygame

#Button Class
class Button():
    def __init__(self, x, y, image, scale):
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform. scale(image, (int(width * scale), int(height * scale)))
        self.rect  = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False

    def draw(self, surface):

        action = False

        #Get Mouse Position
        pos = pygame.mouse.get_pos()
        
        #Check if mouse is on buttons and clicked conditions
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False: #[0] is left click, [1] is middle scroll click, [2] right click
                    self.clicked = True
                    action = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        #Draws the buttons
        surface.blit(self.image, (self.rect.x, self.rect.y))

        return (action)
