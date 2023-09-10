from pygame.locals import *
from OpenGL.GL import *
import pygame


def check_opengl_error():
    # After critical OpenGL operations
    error = glGetError()
    if error != GL_NO_ERROR:
        # Convert error code to string and raise exception (or handle appropriately)
        raise Exception(f"OpenGL error occurred: {error}")


def initialize_opengl_context(width=800, height=600):
    # Initialize pygame
    pygame.init()
    
    # set the OpenGL version (e.g., for OpenGL 4.3)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 4)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)

    # Set the display mode with OpenGL flag
    display = pygame.display.set_mode((width, height), DOUBLEBUF | OPENGL)
    
    # Print the OpenGL version (useful for debugging)
    print("OpenGL version:", glGetString(GL_VERSION).decode('utf-8'))
    
    return display
