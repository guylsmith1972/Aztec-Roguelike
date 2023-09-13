import configuration
import gpu_shader
import player
import pygame
import spritesheet
import utility
import world


def get_assets(tile_size):
    new_spritesheets = {
        'terrain': spritesheet.SpriteSheet(configuration.get('spritesheets.terrain', 'Terrain'), tile_size, tile_size),
        'avatars': spritesheet.SpriteSheet(configuration.get('spritesheets.avatars', 'Avatars'), tile_size, tile_size)
    }
    return new_spritesheets

def main():
    tile_sizes = [1, 2, 4, 6, 8, 10, 12, 16, 20, 24, 32]
    # Initialize pygame
    pygame.init()
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 4)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
    screen = pygame.display.set_mode((0, 0), pygame.DOUBLEBUF | pygame.OPENGL)
    
    current_tile_size = configuration.get('terrain.tile_size', 32)
    spritesheets = get_assets(current_tile_size)

    game_player = player.Player(0, 0)
    game_world = world.World(screen, game_player.get_position(), configuration.get('terrain.chunk_size', 1024), spritesheets)
    game_player.world = game_world
    
    pygame.display.set_caption('Roguelike World')

    movement_stack = []  # Stack to store the movement directions based on key presses

    current_movement = None  # Variable to store the current movement direction
    last_move_time = 0       # Variable to store the time of the last movement
    move_rate_limit = 1.0 / configuration.get('movement.moves_per_second', 100)    # Rate limit for movement 

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            key_to_movement = configuration.get('movement.key_to_movement', {
                pygame.K_KP7: [-1, 1],
                pygame.K_KP8: [0, 1],
                pygame.K_KP9: [1, 1],
                pygame.K_KP4: [-1, 0],
                pygame.K_KP6: [1, 0],
                pygame.K_KP1: [-1, -1],
                pygame.K_KP2: [0, -1],
                pygame.K_KP3: [1, -1]
            })
            key_to_movement = {int(key): value for key, value in key_to_movement.items()}
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    running = False
                elif event.key in key_to_movement:
                    direction = key_to_movement[event.key]
                    if direction not in movement_stack:
                        movement_stack.append(direction)
                    current_movement = movement_stack[-1]
                elif event.key == pygame.K_KP_MINUS:
                    new_tile_size = utility.find_before(tile_sizes, current_tile_size)
                    current_tile_size = new_tile_size
                    spritesheets = get_assets(current_tile_size)
                    game_world.set_spritesheets(spritesheets)
                    configuration.set('terrain.tile_size', current_tile_size)
                elif event.key == pygame.K_KP_PLUS:
                    new_tile_size = utility.find_after(tile_sizes, current_tile_size)
                    current_tile_size = new_tile_size
                    spritesheets = get_assets(current_tile_size)
                    game_world.set_spritesheets(spritesheets)
                    configuration.set('terrain.tile_size', current_tile_size)

            if event.type == pygame.KEYUP:
                # If the key released is a movement key, remove its corresponding movement from the stack
                if event.key in key_to_movement:
                    movement = key_to_movement[event.key]
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

    game_world.cleanup()
    gpu_shader.cleanup_shaders()
    for _, spritesheet in spritesheets.items():
        spritesheet.cleanup()

    pygame.quit()


if __name__ == "__main__":
    main()
    