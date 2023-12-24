import pygame
import os
vector = pygame.math.Vector2

cur_dir = os.path.dirname(__file__)
os.chdir(cur_dir)

# Initialize pygame
pygame.init()

# Create a display surface (tile size is 32x32 so 960/32 = 30 tiles wide, 640/32 = 20 tiles high)
WINDOW_WIDTH = 960
WINDOW_HEIGHT = 640
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Tile Map')

# Create a game clock
FPS = 60
game_clock = pygame.time.Clock()

# Define classes


class Player(pygame.sprite.Sprite):
    """A class to manage the player sprite"""

    def __init__(self, x, y, grass_tiles, water_tiles):
        super().__init__()

        # Animation frames
        self.move_right_sprites = []
        self.move_left_sprites = []
        self.idle_right_sprites = []
        self.idle_left_sprites = []

        # Moving right sprites
        self.move_right_sprites.append(pygame.transform.scale(
            pygame.image.load('boy/Run (1).png'), (64, 64)))
        self.move_right_sprites.append(pygame.transform.scale(
            pygame.image.load('boy/Run (2).png'), (64, 64)))
        self.move_right_sprites.append(pygame.transform.scale(
            pygame.image.load('boy/Run (3).png'), (64, 64)))
        self.move_right_sprites.append(pygame.transform.scale(
            pygame.image.load('boy/Run (4).png'), (64, 64)))
        self.move_right_sprites.append(pygame.transform.scale(
            pygame.image.load('boy/Run (5).png'), (64, 64)))
        self.move_right_sprites.append(pygame.transform.scale(
            pygame.image.load('boy/Run (6).png'), (64, 64)))
        self.move_right_sprites.append(pygame.transform.scale(
            pygame.image.load('boy/Run (7).png'), (64, 64)))
        self.move_right_sprites.append(pygame.transform.scale(
            pygame.image.load('boy/Run (8).png'), (64, 64)))
        
        # Idle right sprites
        self.idle_right_sprites.append(pygame.transform.scale(
            pygame.image.load('boy/Idle (1).png'), (64, 64)))
        self.idle_right_sprites.append(pygame.transform.scale(
            pygame.image.load('boy/Idle (2).png'), (64, 64)))
        self.idle_right_sprites.append(pygame.transform.scale(
            pygame.image.load('boy/Idle (3).png'), (64, 64)))
        self.idle_right_sprites.append(pygame.transform.scale(
            pygame.image.load('boy/Idle (4).png'), (64, 64)))
        self.idle_right_sprites.append(pygame.transform.scale(
            pygame.image.load('boy/Idle (5).png'), (64, 64)))
        self.idle_right_sprites.append(pygame.transform.scale(
            pygame.image.load('boy/Idle (6).png'), (64, 64)))
        self.idle_right_sprites.append(pygame.transform.scale(
            pygame.image.load('boy/Idle (7).png'), (64, 64)))
        self.idle_right_sprites.append(pygame.transform.scale(
            pygame.image.load('boy/Idle (8).png'), (64, 64)))
        
        # Moving left sprites
        for sprite in self.move_right_sprites:
            self.move_left_sprites.append(pygame.transform.flip(sprite, True, False))

        # Idle left sprites
        for sprite in self.idle_right_sprites:
            self.idle_left_sprites.append(pygame.transform.flip(sprite, True, False))

        self.current_sprite = 0

        self.image = self.move_right_sprites[self.current_sprite]
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (x, y)

        self.starting_x = x
        self.starting_y = y

        # Create a list of all the tiles the player can collide with
        self.grass_tiles = grass_tiles
        self.water_tiles = water_tiles

        # Kinematics vectors (first value is the x, second value is the y)
        self.position = vector(x, y)
        self.velocity = vector()
        self.acceleration = vector()

        # Kinematic vectors (first value is the x, second value is the y)
        self.HORIZONTAL_ACCELERATION = 1
        self.HORIZONTAL_FRICTION = 0.1
        self.VERTICAL_ACCELERATION = 0.5  # Gravity
        self.JUMP_VELOCITY = 10


    def update(self):
        # Vertical acceleration is always gravity
        self.acceleration = vector(0, self.VERTICAL_ACCELERATION)
        # If the user is pressing a key, set the x-componenbt of the acceleration vector to a non-zero value
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.acceleration.x = -1*self.HORIZONTAL_ACCELERATION
            self.animate(self.move_left_sprites, 0.2)
        elif keys[pygame.K_RIGHT]:
            self.acceleration.x = self.HORIZONTAL_ACCELERATION
            self.animate(self.move_right_sprites, 0.2)
        else:
            if self.velocity.x > 0:
                self.animate(self.idle_right_sprites, 0.2)
            else:
                self.animate(self.idle_left_sprites, 0.2)

        # Calculate new kinematics values
        self.acceleration.x -= self.velocity.x * self.HORIZONTAL_FRICTION
        self.velocity += self.acceleration
        self.position += self.velocity + 0.5 * self.acceleration

        # Wrap the player around the screen
        if self.position.x > WINDOW_WIDTH:
            self.position.x = 0
        if self.position.x < 0:
            self.position.x = WINDOW_WIDTH

        # Update the rect
        self.rect.bottomleft = self.position

        # Check for collisions with the grass tiles
        grass_collisions = pygame.sprite.spritecollide(
            self, self.grass_tiles, False, pygame.sprite.collide_mask)
        if grass_collisions:
            if self.velocity.y > 0:
                self.position.y = grass_collisions[0].rect.top + 10
                self.velocity.y = 0

        # Check for collisions with the water tiles
        water_collisions = pygame.sprite.spritecollide(
            self, self.water_tiles, False)
        if water_collisions:
            print('You died!')
            self.position.x = self.starting_x
            self.position.y = self.starting_y
            self.velocity = vector()

    def jump(self):
        """Make the player jump"""
        # Check for collisions with the grass tiles
        if pygame.sprite.spritecollide(self, self.grass_tiles, False):
            self.velocity.y -= self.JUMP_VELOCITY

    def animate(self, sprite_list, speed):
        """Animate the player sprite"""
        #Loop through the sprite list changing the current sprite
        if self.current_sprite < len(sprite_list) - 1:
            self.current_sprite += speed
        else:
            self.current_sprite = 0

        #Update the image
        self.image = sprite_list[int(self.current_sprite)]


class Tile(pygame.sprite.Sprite):
    """A class to read and create individual tiles and place them on the screen"""

    def __init__(self, x, y, tile_type, main_group, sub_group=""):
        """Initialize the tile and set its position on the screen"""
        super().__init__()
        self.image = pygame.image.load(f'{tile_type}.png')
        if tile_type == '2':
            self.mask = pygame.mask.from_surface(self.image)
        sub_group.add(self)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        # Add the tile to the main group
        main_group.add(self)


# Create sprite groups
main_tile_group = pygame.sprite.Group()
dirt_group = pygame.sprite.Group()
grass_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
my_player_group = pygame.sprite.Group()

# Create a tile map: 0 = empty, 1 = dirt, 2 = grass, 3 = water, 4 = player
tile_map = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
     0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2],
    [1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2],
    [1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
        0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
        3, 3, 3, 3, 3, 3, 3, 3, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
        1, 3, 3, 3, 3, 3, 3, 3, 3, 1, 1, 1, 1, 1, 1]
]

# Create individual Tile objects from the tile map
# Loop through the 20 tiles (i moves us down the map)
for i in range(len(tile_map)):
    # Loop through the 30 tiles (j moves us across the map)
    for j in range(len(tile_map[i])):
        # Check what type of tile we have and create the appropriate Tile object
        if tile_map[i][j] == 1:
            Tile(j * 32, i * 32, '1', main_tile_group, dirt_group)
        elif tile_map[i][j] == 2:
            Tile(j * 32, i * 32, '2', main_tile_group, grass_group)
        elif tile_map[i][j] == 3:
            Tile(j * 32, i * 32, '3', main_tile_group, water_group)
        elif tile_map[i][j] == 4:
            my_player = Player(j * 32, i * 32 + 32, grass_group, water_group)
            my_player_group.add(my_player)

# Load the background image
background_image = pygame.image.load('background.png')
background_rect = background_image.get_rect()
background_rect.topleft = (0, 0)

# Main game loop
running = True
while running:

    # Event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                my_player.jump()

    # Blit the background
    display_surface.blit(background_image, background_rect)

    # Draw the tiles
    main_tile_group.draw(display_surface)

    # Draw the player
    my_player_group.update()
    my_player_group.draw(display_surface)

    # Update display and tick clock
    pygame.display.update()
    game_clock.tick(FPS)


# End the game
pygame.quit()
