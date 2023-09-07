import numpy as np
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader


def initialize_opengl_context(width=800, height=600):
    # Initialize pygame
    pygame.init()
    
    # Set the display mode with OpenGL flag
    display = pygame.display.set_mode((width, height), DOUBLEBUF | OPENGL)
    
    # Optionally set the OpenGL version (e.g., for OpenGL 3.3)
    # pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
    # pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
    
    # Print the OpenGL version (useful for debugging)
    print("OpenGL version:", glGetString(GL_VERSION).decode('utf-8'))
    
    return display


class Shader:
    def __init__(self, filename):
        with open(filename, "r") as f:
            compute_shader_source = f.read()

        self.compute_shader = compileShader(compute_shader_source, GL_COMPUTE_SHADER)
        self.shader_program = compileProgram(self.compute_shader)

    def _check_shader_errors(self, obj, mode):
        if mode == GL_COMPILE_STATUS:
            status = glGetShaderiv(obj, mode)
            error_log = glGetShaderInfoLog(obj)
        else:  # Assuming mode is GL_LINK_STATUS for programs
            status = glGetProgramiv(obj, mode)
            error_log = glGetProgramInfoLog(obj)

        if not status:
            print(f"Error Log:\n{error_log.decode('utf-8')}")
            raise RuntimeError("Shader/Program compilation/linking failed!")

    def set_uniform(self, name, type, *values):
        location = glGetUniformLocation(self.shader_program, name)
        if type == "1f":
            glUniform1f(location, *values)
        elif type == "3f":
            glUniform3f(location, *values)
        elif type == "1i":
            glUniform1i(location, *values)
        # ... Add more uniform types as needed

    def use(self):
        glUseProgram(self.shader_program)

    def cleanup(self):
        glDeleteProgram(self.shader_program)
        glDeleteShader(self.compute_shader)


def create_texture_from_numpy(np_array):
    # Ensure the numpy array is in float32 format
    np_array = np_array.astype(np.float32)

    # Get the shape of the numpy array
    height, width = np_array.shape

    # Create an OpenGL texture
    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)

    # Allocate texture memory (without data)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_R32F, width, height, 0, GL_RED, GL_FLOAT, None)

    # Upload data to texture
    glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, width, height, GL_RED, GL_FLOAT, np_array)

    # Set texture parameters if needed
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glBindTexture(GL_TEXTURE_2D, 0)

    return texture


def create_rgba32f_texture_from_numpy(arr1, arr2, arr3, arr4):
    # Ensure all arrays are of the same shape
    assert arr1.shape == arr2.shape == arr3.shape == arr4.shape, "All input arrays must have the same shape"

    # Ensure all arrays are in float32 format
    arr1 = arr1.astype(np.float32)
    arr2 = arr2.astype(np.float32)
    arr3 = arr3.astype(np.float32)
    arr4 = arr4.astype(np.float32)

    # Stack arrays along a new dimension to form an RGBA image
    combined_array = np.stack((arr1, arr2, arr3, arr4), axis=-1)

    height, width, _ = combined_array.shape

    # Create an OpenGL texture
    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)

    # Upload data to texture
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA32F, width, height, 0, GL_RGBA, GL_FLOAT, combined_array)

    # Set texture parameters
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glBindTexture(GL_TEXTURE_2D, 0)

    return texture


def create_empty_rgba32f_texture(width, height):
    # Create an OpenGL texture
    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)

    # Allocate texture memory without data (None specifies no initial data)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA32F, width, height, 0, GL_RGBA, GL_FLOAT, None)

    # Set texture parameters
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glBindTexture(GL_TEXTURE_2D, 0)

    return texture


def texture_rgba32f_to_numpy_arrays(texture, width, height):
    # Bind the texture
    glBindTexture(GL_TEXTURE_2D, texture)
    
    # Retrieve data from the texture
    data = glGetTexImage(GL_TEXTURE_2D, 0, GL_RGBA, GL_FLOAT)
    
    # Convert data to numpy array
    np_data = np.array(data, dtype=np.float32).reshape((height, width, 4))
    
    # Split the numpy array into four separate arrays based on channels
    red, green, blue, alpha = np_data[..., 0], np_data[..., 1], np_data[..., 2], np_data[..., 3]
    
    return red, green, blue, alpha


def iterate_rgba32f(shader_filename, red, green, blue, alpha, iterations):
    height, width = red.shape
    shader = Shader(shader_filename)
    input_state = create_rgba32f_texture_from_numpy(red, green, blue, alpha)
    output_state = create_empty_rgba32f_texture(width, height)
    
    for i in range(iterations):
        # Use the shader program
        shader.use()
        
        # Bind the input and output textures
        # We're assuming binding points 0 and 1 in the shader for input and output respectively
        glBindImageTexture(0, input_state, 0, GL_FALSE, 0, GL_READ_ONLY, GL_RGBA32F)
        glBindImageTexture(1, output_state, 0, GL_FALSE, 0, GL_WRITE_ONLY, GL_RGBA32F)

        # Set any required uniforms here, if any (example: shader.set_uniform("someUniform", "1f", 0.5))

        # Dispatch the compute shader
        # Assuming local workgroup size is 16x16 in the shader
        glDispatchCompute(width//16, height//16, 1)
        
        # Wait for the compute shader to complete
        glMemoryBarrier(GL_SHADER_IMAGE_ACCESS_BARRIER_BIT)

        # Swap input and output for the next pass
        input_state, output_state = output_state, input_state


    red_out, green_out, blue_out, alpha_out = texture_rgba32f_to_numpy_arrays(input_state, red.shape[1], red.shape[0])
    
    return red_out, green_out, blue_out, alpha_out
    