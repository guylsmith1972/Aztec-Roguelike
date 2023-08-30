import configuration
import player
import pygame
import spritesheet
import utility
import world


def get_assets(tile_size):
    new_spritesheets = {
        'terrain': spritesheet.SpriteSheet('Assets/Terrain', tile_size, tile_size),
        'avatars': spritesheet.SpriteSheet('Assets/Avatars', tile_size, tile_size)
    }
    return new_spritesheets

def main():
    tile_sizes = [8, 10, 12, 16, 20, 24, 32, 40, 48, 64, 80, 96, 128]
    # Initialize pygame
    pygame.init()

    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    
    current_tile_size = configuration.get('tile_size')
    spritesheets = get_assets(current_tile_size)

    game_player = player.Player(0, 0)
    game_world = world.World(screen, game_player.get_position(), configuration.get('region_size'), spritesheets)
    game_player.world = game_world
    
    pygame.display.set_caption('Roguelike World')

    movement_stack = []  # Stack to store the movement directions based on key presses

    current_movement = None  # Variable to store the current movement direction
    last_move_time = 0       # Variable to store the time of the last movement
    move_rate_limit = 1.0 / configuration.get('moves_per_second')    # Rate limit for movement 

    running = True
    while running:
        key_to_movement = configuration.get('key_to_movement')
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    running = False
                elif str(event.key) in key_to_movement:
                    direction = key_to_movement[str(event.key)]
                    if direction not in movement_stack:
                        movement_stack.append(direction)
                    current_movement = movement_stack[-1]
                elif event.key == pygame.K_KP_MINUS:
                    new_tile_size = utility.find_before(tile_sizes, current_tile_size)
                    current_tile_size = new_tile_size
                    spritesheets = get_assets(current_tile_size)
                    game_world.set_spritesheets(spritesheets)
                    configuration.set('tile_size', current_tile_size)
                elif event.key == pygame.K_KP_PLUS:
                    new_tile_size = utility.find_after(tile_sizes, current_tile_size)
                    current_tile_size = new_tile_size
                    spritesheets = get_assets(current_tile_size)
                    game_world.set_spritesheets(spritesheets)
                    configuration.set('tile_size', current_tile_size)

            if event.type == pygame.KEYUP:
                # If the key released is a movement key, remove its corresponding movement from the stack
                if str(event.key) in key_to_movement:
                    movement = key_to_movement[str(event.key)]
                    if movement in movement_stack:
                        movement_stack.remove(movement)
                    current_movement = movement_stack[-1] if movement_stack else None
        
        # Continuous movement handling
        current_time = pygame.time.get_ticks() / 1000  # Get the current time in seconds
        if current_movement and current_time - last_move_time > move_rate_limit:
            game_player.move(*current_movement)
            last_move_time = current_time

        # Update the world based on the player's current position
        current_player_position = game_player.get_position()
        game_world.update_positions(screen, current_player_position)

        game_world.render(screen, current_player_position[0], current_player_position[1])

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
    