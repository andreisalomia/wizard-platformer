import pygame, os, random, json

current_dir = os.path.dirname(__file__)
os.chdir(current_dir)

pygame.init()

spawn_rate = 400
SPAWN_RATE_DECREAESE = 0.02
DEFAULT_ANIMATION_SPEED = 0.2

WHITE = (255, 255, 255)

# Scores
LOW_SCORE = 10
MID_SCORE = 20
HIGH_SCORE = 30

# Create a window
WINDOW_HEIGHT = 864
WINDOW_WIDTH = 1184
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

# Set the title of the window
pygame.display.set_caption("Rizzard of Oz")

# Set fire type
fire_type = random.randint(1, 3)
if fire_type == 1:
    fire_type = "red"
elif fire_type == 2:
    fire_type = "blue"
elif fire_type == 3:
    fire_type = "pink"

# Create an array of levels for the monsters to spawn on (y-axis) IN REVERSE ORDER
levels_array = [
    WINDOW_HEIGHT - 64,
    WINDOW_HEIGHT - 128,
    WINDOW_HEIGHT - 320,
    WINDOW_HEIGHT - 512,
    WINDOW_HEIGHT - 704,
]

# Create an array of possible spawn locations for monsters
monster_locations = []
monster_locations.append((0, WINDOW_HEIGHT - 704))
monster_locations.append((WINDOW_WIDTH - 64, WINDOW_HEIGHT - 704))
monster_locations.append((0, WINDOW_HEIGHT - 512))
monster_locations.append((WINDOW_WIDTH - 64, WINDOW_HEIGHT - 512))
monster_locations.append((0, WINDOW_HEIGHT - 320))
monster_locations.append((WINDOW_WIDTH - 64, WINDOW_HEIGHT - 320))
monster_locations.append((0, WINDOW_HEIGHT - 128))
monster_locations.append((WINDOW_WIDTH - 64, WINDOW_HEIGHT - 128))
monster_locations.append((0, WINDOW_HEIGHT - 64))
monster_locations.append((WINDOW_WIDTH - 64, WINDOW_HEIGHT - 64))

monster_spawn_locations = monster_locations[:-4]


# Tiles groups
all_tiles = pygame.sprite.Group()
grass_tiles = pygame.sprite.Group()
dirt_tiles = pygame.sprite.Group()


# Load player sprites
def load_player_sprites(sprite_type, sprite_list, nr_of_sprites):
    for i in range(1, nr_of_sprites + 1):
        sprite_list.append(pygame.image.load(f"Wizard/{sprite_type}{i}.png"))


# Load the background image
background_image = pygame.transform.scale(
    pygame.image.load("background.png"), (WINDOW_WIDTH, WINDOW_HEIGHT)
)
background_rect = background_image.get_rect()
background_rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)


class Game:
    def __init__(
        self, player_group, monsters_group, fire_group, girl_group, collectible_group
    ):
        self.player_lives = 3
        self.player_score = 0
        self.player_group = player_group
        self.monsters_group = monsters_group
        self.fire_group = fire_group
        self.girl_group = girl_group
        self.collectible_group = collectible_group

        # Load a custom font
        self.font = pygame.font.Font("Font/font.ttf", 32)

    def update(self):
        self.check_collision()
        self.check_defeat()
        self.spawn_mechanisms()
        # Check the listof gems and substract 1 of each gem lifespan, if a lifespan reaches 0 then kill the gem
        for gem in collectible_group:
            gem.lifespan -= 1
            if gem.lifespan == 0:
                gem.kill()

    def draw(self):
        # Draw the score
        score_text = self.font.render(f"Score: {self.player_score}", True, WHITE)
        screen.blit(score_text, (10, WINDOW_HEIGHT - 50))

        # Draw the lives
        lives_text = self.font.render(f"Lives: {self.player_lives}", True, WHITE)
        screen.blit(lives_text, (WINDOW_WIDTH - 144, WINDOW_HEIGHT - 50))

    def check_collision(self):
        # Check if player collides with a monster
        if pygame.sprite.spritecollide(
            player_sprite, monsters_group, False, pygame.sprite.collide_rect
        ):
            self.player_lives -= 1
            if self.player_lives == 0:
                self.game_over("player_death")
            else:
                player_sprite.rect.x = player_sprite.starting_x
                player_sprite.rect.y = player_sprite.starting_y
                player_sprite.pos.x = player_sprite.starting_x
                player_sprite.pos.y = player_sprite.starting_y

        # Check if player collides with a collectible
        # If it's a blue gem the player gets 10 points, if it's a red gem the player gets 20 points, and if it's a green gem the player gets 30 points
        collided_collectibles = pygame.sprite.spritecollide(
            player_sprite, collectible_group, True, pygame.sprite.collide_rect
        )

        for collectible in collided_collectibles:
            if collectible.type_of_collectible == 1:
                self.player_score += LOW_SCORE
            elif collectible.type_of_collectible == 2:
                self.player_score += MID_SCORE
            elif collectible.type_of_collectible == 3:
                self.player_score += HIGH_SCORE

        # Check if fire collides with a monster and if it does spawn a gem
        collided_monsters = pygame.sprite.groupcollide(
            fire_group, monsters_group, True, True, pygame.sprite.collide_rect
        )
        for monster in collided_monsters:
            self.player_score += LOW_SCORE
            gem = Collectible(monster.rect.x, monster.rect.y)
            if random.randint(1, 5) == 1:
                new_monster = Monster(
                    random.choice(monster_spawn_locations),
                    random.choice(["1", "3", "4", "5", "6", "7", "8", "10"]),
                )
                monsters_group.add(new_monster)
            collectible_group.add(gem)

    def check_defeat(self):
        if self.player_lives == 0:
            self.game_over("player_death")
        # Check collision of girl with monsters
        if pygame.sprite.groupcollide(girl_group, monsters_group, False, False):
            self.game_over("girl_death")

    def pause_game(self):
        # Tell the user to press R to restart the game or to quit the game
        pause_text = self.font.render(
            "Press R to restart the game or Q to quit the game", True, WHITE
        )

        # Calculate the position to center the text
        text_rect = pause_text.get_rect(
            center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 200)
        )

        # Blit the text to the screen
        screen.blit(pause_text, text_rect)
        pygame.display.update()

        paused = True
        while paused:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (
                    event.type == pygame.KEYDOWN and event.key == pygame.K_q
                ):
                    pygame.quit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    paused = False
                self.restart_game()

    def game_over(self, how_game_ended):
        end_text = self.font.render("Game Over", True, WHITE)

        if how_game_ended == "player_death":
            death_reason_text = self.font.render(
                "The monsters killed you!", True, WHITE
            )

            screen.blit(end_text, (WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT // 2 - 50))
            screen.blit(
                death_reason_text, (WINDOW_WIDTH // 2 - 250, WINDOW_HEIGHT // 2)
            )

        elif how_game_ended == "girl_death":
            death_reason_text = self.font.render(
                "You failed to protect the princess!", True, WHITE
            )

            screen.blit(end_text, (WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT // 2 - 50))
            screen.blit(
                death_reason_text, (WINDOW_WIDTH // 2 - 350, WINDOW_HEIGHT // 2)
            )

        pygame.display.update()
        self.pause_game()

    def restart_game(self):
        global spawn_rate
        # Reset the player's lives and score
        self.player_lives = 3
        self.player_score = 0
        # Clear all the groups
        monsters_group.empty()
        fire_group.empty()
        collectible_group.empty()
        # Create a new monster
        first_monster = Monster(
            random.choice(monster_spawn_locations),
            random.choice(["1", "3", "4", "5", "6", "7", "8", "10"]),
        )
        monsters_group.add(first_monster)
        # Reset the players position and spawn_rate
        player_sprite.rect.x = player_sprite.starting_x
        player_sprite.rect.y = player_sprite.starting_y
        player_sprite.pos.x = player_sprite.starting_x
        player_sprite.pos.y = player_sprite.starting_y
        spawn_rate = 400

    def spawn_mechanisms(self):
        global spawn_rate
        # Spawn a monster gradually every 10 seconds going up to 5 seconds and have a
        # 12% percent chance of spawning a monster when another monster is spawned
        # have also a 20% chance of spawning a monster when another one dies
        if pygame.time.get_ticks() % int(spawn_rate) == 0:
            monster = Monster(
                random.choice(monster_spawn_locations),
                random.choice(["1", "3", "4", "5", "6", "7", "8", "10"]),
            )
            monsters_group.add(monster)
            if random.randint(1, 7) == 1:
                monster = Monster(
                    random.choice(monster_spawn_locations),
                    random.choice(["1", "3", "4", "5", "6", "7", "8", "10"]),
                )
                monsters_group.add(monster)
        spawn_rate -= SPAWN_RATE_DECREAESE
        if spawn_rate < 300:
            spawn_rate = 300


class Collectible(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.lifespan = 300
        self.collectible_sprite = []
        self.nr_of_collectible_sprites = 7
        self.type_of_collectible = random.randint(1, 3)
        for i in range(1, self.nr_of_collectible_sprites):
            self.collectible_sprite.append(
                pygame.transform.scale(
                    pygame.image.load(
                        f"Jewels/Jewel{self.type_of_collectible}/{i}.png"
                    ),
                    (32, 32),
                )
            )
        self.current_sprite = 0
        self.image = self.collectible_sprite[self.current_sprite]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self):
        self.animate()

    def animate(self):
        if self.current_sprite < len(self.collectible_sprite) - 1:
            self.current_sprite += DEFAULT_ANIMATION_SPEED
        else:
            self.current_sprite = 0
        self.image = self.collectible_sprite[int(self.current_sprite)]


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, grass_tiles):
        super().__init__()

        # Initialize the player's idle, walk, jump, fall, attack, and death sprites
        self.player_idle_sprite = []
        self.player_walk_sprite = []
        self.player_jump_sprite = []
        self.player_fall_sprite = []
        self.player_attack_sprite = []
        self.player_death_sprite = []
        load_player_sprites("idle", self.player_idle_sprite, 6)
        load_player_sprites("run", self.player_walk_sprite, 8)
        load_player_sprites("jump", self.player_jump_sprite, 2)
        load_player_sprites("fall", self.player_fall_sprite, 2)
        load_player_sprites("attack", self.player_attack_sprite, 4)
        load_player_sprites("dead", self.player_death_sprite, 4)

        self.current_sprite = 0
        self.starting_x = x
        self.starting_y = y
        self.image = self.player_idle_sprite[self.current_sprite]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.grass_tiles = grass_tiles
        self.is_shooting = False

        # Initialize the player's movement variables
        self.pos = pygame.math.Vector2(x, y)
        self.velocity = pygame.math.Vector2()
        self.acceleration = pygame.math.Vector2()

        # Initialize the constants of movement
        self.x_axis_acceleration = 1
        self.x_axis_friction = 0.1
        self.y_axis_acceleration = 0.5
        self.y_axis_jump_acceleration = 10

        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.movement_keys()

        self.acceleration.x -= self.velocity.x * self.x_axis_friction
        self.velocity += self.acceleration
        self.pos += self.velocity + 0.5 * self.acceleration

        self.player_wrap()
        self.rect.bottomleft = self.pos

        self.check_collision()
        if self.is_shooting == True:
            if self.velocity.x > 0:
                self.animate("right", self.player_attack_sprite, 0.1)
            else:
                self.animate("left", self.player_attack_sprite, 0.1)

        self.mask = pygame.mask.from_surface(self.image)

    def attack(self):
        if len(fire_group) < 3:
            Fire(self.rect.x, self.rect.y, fire_type, self.velocity.x)
            self.is_shooting = True

    def jump(self):
        if pygame.sprite.spritecollide(self, self.grass_tiles, False):
            self.velocity.y -= self.y_axis_jump_acceleration

    def check_collision(self):
        grass_collisions = pygame.sprite.spritecollide(
            self, self.grass_tiles, False, pygame.sprite.collide_mask
        )
        if grass_collisions:
            if self.velocity.y > 0.1:
                self.pos.y = (
                    grass_collisions[0].rect.top + 12
                )  # How the fuck is this working????
                self.velocity.y = 0
        else:
            if self.velocity.y < -1:
                if self.velocity.x > 0:
                    if self.is_shooting == False:
                        self.animate(
                            "right", self.player_jump_sprite, DEFAULT_ANIMATION_SPEED
                        )
                else:
                    if self.is_shooting == False:
                        self.animate(
                            "left", self.player_jump_sprite, DEFAULT_ANIMATION_SPEED
                        )
            elif self.velocity.y > 1:
                if self.velocity.x > 0:
                    if self.is_shooting == False:
                        self.animate(
                            "right", self.player_fall_sprite, DEFAULT_ANIMATION_SPEED
                        )
                else:
                    if self.is_shooting == False:
                        self.animate(
                            "left", self.player_fall_sprite, DEFAULT_ANIMATION_SPEED
                        )

    def player_wrap(self):
        if self.pos.x > WINDOW_WIDTH:
            self.pos.x = 0
        if self.pos.x < 0:
            self.pos.x = WINDOW_WIDTH

    def movement_keys(self):
        self.acceleration = pygame.math.Vector2(0, self.y_axis_acceleration)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.acceleration.x = -self.x_axis_acceleration
            if self.is_shooting == False:
                self.animate("left", self.player_walk_sprite, DEFAULT_ANIMATION_SPEED)
        elif keys[pygame.K_RIGHT]:
            self.acceleration.x = self.x_axis_acceleration
            if self.is_shooting == False:
                self.animate("right", self.player_walk_sprite, DEFAULT_ANIMATION_SPEED)
        else:
            if self.velocity.x > 0:
                if self.is_shooting == False:
                    self.animate(
                        "right", self.player_idle_sprite, DEFAULT_ANIMATION_SPEED
                    )
            else:
                if self.is_shooting == False:
                    self.animate(
                        "left", self.player_idle_sprite, DEFAULT_ANIMATION_SPEED
                    )

    def animate(self, direction, sprite_list, rate_of_change):
        if direction == "left":
            if self.current_sprite < len(sprite_list) - 1:
                self.current_sprite += rate_of_change
            else:
                self.current_sprite = 0
            self.image = pygame.transform.flip(
                sprite_list[int(self.current_sprite)], True, False
            )
        elif direction == "right":
            if self.current_sprite < len(sprite_list) - 1:
                self.current_sprite += rate_of_change
            else:
                self.current_sprite = 0
            self.image = sprite_list[int(self.current_sprite)]
        if self.is_shooting == True:
            if self.current_sprite >= len(sprite_list) - 1:
                self.is_shooting = False
                self.current_sprite = 0
                self.image = self.player_idle_sprite[self.current_sprite]


class Fire(pygame.sprite.Sprite):
    def __init__(self, x, y, fire_type, direction):
        super().__init__()
        self.fire_sprite = []
        self.nr_of_fire_sprites = 7
        for i in range(1, self.nr_of_fire_sprites):
            self.fire_sprite.append(
                pygame.transform.scale(
                    pygame.image.load(f"Fire/{fire_type}/{i}.png"),
                    (64, 32),
                )
            )
        self.current_sprite = 0
        self.image = self.fire_sprite[self.current_sprite]
        self.rect = self.image.get_rect()
        self.starting_x = x
        self.starting_y = y
        self.rect.x = x
        self.rect.y = y + 16
        self.velocity = 10
        self.direction = "right" if direction > 0 else "left"
        fire_group.add(self)

    def update(self):
        if self.direction == "right":
            self.rect.x += self.velocity
            self.animate("right")
        elif self.direction == "left":
            self.rect.x -= self.velocity
            self.animate("left")
        if self.rect.x > WINDOW_WIDTH or self.rect.x < 0:
            self.kill()
        # Kill if the fire has travelled more than half the screen
        if abs(self.rect.x - self.starting_x) > WINDOW_WIDTH // 2:
            self.kill()

    def animate(self, direction):
        if direction == "right":
            if self.current_sprite < len(self.fire_sprite) - 1:
                self.current_sprite += DEFAULT_ANIMATION_SPEED
            else:
                self.current_sprite = 0
            self.image = pygame.transform.flip(
                self.fire_sprite[int(self.current_sprite)], True, False
            )
        elif direction == "left":
            if self.current_sprite < len(self.fire_sprite) - 1:
                self.current_sprite += DEFAULT_ANIMATION_SPEED
            else:
                self.current_sprite = 0
            self.image = self.fire_sprite[int(self.current_sprite)]


class Girl(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.girl_idle_sprite = []
        self.nr_of_girl_idle_sprites = 16
        for i in range(1, self.nr_of_girl_idle_sprites):
            self.girl_idle_sprite.append(
                pygame.transform.scale(
                    pygame.image.load(f"Girl/Idle ({i}).png"), (64, 64)
                )
            )
        self.current_sprite = 0
        self.image = self.girl_idle_sprite[self.current_sprite]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self):
        if self.current_sprite < len(self.girl_idle_sprite) - 1:
            self.current_sprite += DEFAULT_ANIMATION_SPEED
        else:
            self.current_sprite = 0

        self.image = self.girl_idle_sprite[int(self.current_sprite)]


class Monster(pygame.sprite.Sprite):
    def __init__(self, x_y_tuple, monster_type):
        super().__init__()
        self.monster_run_sprite = []
        self.nr_of_monster_run_sprites = 19
        for i in range(1, 10):
            self.monster_run_sprite.append(
                pygame.transform.scale(
                    pygame.image.load(
                        f"Monsters/PNG/{monster_type}/{monster_type}_enemies_1_run_00{i}.png"
                    ),
                    (64, 64),
                )
            )
        for i in range(10, self.nr_of_monster_run_sprites):
            self.monster_run_sprite.append(
                pygame.transform.scale(
                    pygame.image.load(
                        f"Monsters/PNG/{monster_type}/{monster_type}_enemies_1_run_0{i}.png"
                    ),
                    (64, 64),
                )
            )
        self.current_sprite = 0
        self.monster_type = monster_type
        self.grass_tiles = grass_tiles
        self.image = self.monster_run_sprite[self.current_sprite]
        self.rect = self.image.get_rect()
        self.rect.x = x_y_tuple[0]
        self.rect.y = x_y_tuple[1]
        self.current_level = levels_array.index(x_y_tuple[1]) - 1

        self.direction = 1 if x_y_tuple[0] == 0 else -1

        self.pos = pygame.math.Vector2(x_y_tuple[0], x_y_tuple[1])
        self.velocity = pygame.math.Vector2()
        self.acceleration = pygame.math.Vector2()

        self.x_axis_acceleration = 0.5
        self.x_axis_friction = 0.1
        self.y_axis_acceleration = 0.5

    def update(self):
        self.move_monster()

        # Every 300 frames change the direction of the monster
        if pygame.time.get_ticks() % 300 == 0:
            self.direction *= -1

        self.acceleration.x -= self.velocity.x * self.x_axis_friction
        self.velocity += self.acceleration
        self.pos += self.velocity + 0.5 * self.acceleration

        self.wrap_monster()
        self.rect.bottomleft = self.pos
        self.check_collision()

    def move_monster(self):
        self.acceleration = pygame.math.Vector2(
            self.direction * self.x_axis_acceleration, self.y_axis_acceleration
        )
        if self.direction == 1:
            self.animate("right", self.monster_run_sprite, DEFAULT_ANIMATION_SPEED)
        else:
            self.animate("left", self.monster_run_sprite, DEFAULT_ANIMATION_SPEED)

    def check_collision(self):
        grass_collisions = pygame.sprite.spritecollide(
            self, self.grass_tiles, False, pygame.sprite.collide_rect
        )

        if grass_collisions:
            if self.velocity.y > 0.1:
                self.pos.y = grass_collisions[0].rect.top + 5
                self.velocity.y = 0

    def animate(self, direction, sprite_list, rate_of_change):
        if direction == "left":
            if self.current_sprite < len(sprite_list) - 1:
                self.current_sprite += rate_of_change
            else:
                self.current_sprite = 0
            self.image = pygame.transform.flip(
                sprite_list[int(self.current_sprite)], True, False
            )
        elif direction == "right":
            if self.current_sprite < len(sprite_list) - 1:
                self.current_sprite += rate_of_change
            else:
                self.current_sprite = 0
            self.image = sprite_list[int(self.current_sprite)]

    def wrap_monster(self):
        if self.pos.x > WINDOW_WIDTH:
            # Have a 20% of sending the monster onto a random level
            if random.randint(1, 5) == 1:
                self.pos.y = random.choice(levels_array)
            self.pos.x = 0
            self.direction = 1
        if self.pos.x < 0:
            # Have a 20% of sending the monster onto the next level
            if random.randint(1, 5) == 1:
                self.pos.y = levels_array[self.current_level + 1]
            self.pos.x = WINDOW_WIDTH
            self.direction = -1


# Create collectibles
collectible_group = pygame.sprite.Group()

# Create girl
girl_group = pygame.sprite.Group()
girl_sprite = Girl(WINDOW_WIDTH // 2 - 32, WINDOW_HEIGHT - 128)
girl_group.add(girl_sprite)

# Create monsters
monsters_group = pygame.sprite.Group()
first_monster = Monster(
    random.choice(monster_spawn_locations),
    random.choice(["1", "3", "4", "5", "6", "7", "8", "10"]),
)
monsters_group.add(first_monster)

# Create player
player_group = pygame.sprite.Group()
player_sprite = Player(256, WINDOW_HEIGHT - 140, grass_tiles)
player_group.add(player_sprite)

# Create fire
fire_group = pygame.sprite.Group()

# Create game
game = Game(player_group, monsters_group, fire_group, girl_group, collectible_group)

# Create FPS and clock
FPS = 60
clock = pygame.time.Clock()


def create_tilemap():
    for y, row in enumerate(tilemap["tiles"]):
        for x, tile_type in enumerate(row):
            if tile_type == 1:
                Tile(x * 32, y * 32, "1", all_tiles, grass_tiles)
            elif tile_type == 2:
                Tile(x * 32, y * 32, "2", all_tiles, grass_tiles)
            elif tile_type == 3:
                Tile(x * 32, y * 32, "3", all_tiles, grass_tiles)
            elif tile_type == 4:
                Tile(x * 32, y * 32, "4", all_tiles, grass_tiles)
            elif tile_type == 5:
                Tile(x * 32, y * 32, "5", all_tiles, dirt_tiles)


class Tile(pygame.sprite.Sprite):
    def __init__(self, x, y, tile, all_tiles, specific_tile=""):
        super().__init__()
        self.image = pygame.transform.scale(
            pygame.image.load(f"Tiles/{tile}.png"), (32, 32)
        )
        self.rect = self.image.get_rect()
        specific_tile.add(self)
        self.rect.x = x
        self.rect.y = y
        all_tiles.add(self)


with open("tilemap.json", "r") as file:
    tilemap = json.load(file)

create_tilemap()

# Main game loop
running = True
while running:
    # Did the user click the window close button?
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
            player_sprite.jump()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            player_sprite.attack()

    # Draw the player on the screen
    screen.blit(background_image, background_rect)

    # Draw tiles
    all_tiles.draw(screen)

    # Draw girl
    girl_group.update()
    girl_group.draw(screen)

    # Draw player
    player_group.update()
    player_group.draw(screen)

    # Draw fire
    fire_group.update()
    fire_group.draw(screen)

    # Draw monsters
    monsters_group.update()
    monsters_group.draw(screen)

    # Draw collectibles
    collectible_group.update()
    collectible_group.draw(screen)

    # Update the game
    game.update()
    game.draw()

    # Tick clock and update the screen
    pygame.display.update()
    clock.tick(FPS)

# Exit game
pygame.quit()
