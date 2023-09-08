import numpy as np
import pygame
from pygame.display import get_window_size
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader


def check_opengl_error():
    # After critical OpenGL operations
    error = glGetError()
    if error != GL_NO_ERROR:
        # Convert error code to string and raise exception (or handle appropriately)
        raise Exception(f"OpenGL error occurred: {error}")


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
        with open(f'Assets/Shaders/{filename}', "r") as f:
            compute_shader_source = f.read()

        try:
            self.compute_shader = compileShader(compute_shader_source, GL_COMPUTE_SHADER)
        except Exception as e:
            print(f"Shader Compilation Error: {str(e)}")
            raise e  # Re-raise the original exception for further handling

        try:
            self.shader_program = compileProgram(self.compute_shader)
        except Exception as e:
            print(f"Shader Program Linking Error: {str(e)}")
            raise e  # Re-raise the original exception for further handling

    def set_uniform(self, name, type, *values):
        location = glGetUniformLocation(self.shader_program, name)
        if type == "1f":
            glUniform1f(location, *values)
        elif type == "3f":
            glUniform3f(location, *values)
        elif type == "1i":
            glUniform1i(location, *values)
        else:  # ... Add more uniform types as needed
            raise RuntimeError(f'Cannot set uniform for type {type}')
        
    def get_workgroup_size(self):
        # Assuming local workgroup size is 16x16 in the shader
        return 16, 16

    def get_workgroup_count(self, width, height):
        wg_width, wg_height = self.get_workgroup_size()
        return width // wg_width, height // wg_height

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


def create_empty_int_ssbo(num_elements):
    # Create a new SSBO
    ssbo = glGenBuffers(1)
    glBindBuffer(GL_SHADER_STORAGE_BUFFER, ssbo)
    glBufferData(GL_SHADER_STORAGE_BUFFER, num_elements * 4, None, GL_DYNAMIC_DRAW)  # Assuming 4 bytes per element (uint)
    glBindBuffer(GL_SHADER_STORAGE_BUFFER, 0)
    return ssbo


def clear_int_ssbo(ssbo):
    glBindBuffer(GL_SHADER_STORAGE_BUFFER, ssbo)
    glClearBufferData(GL_SHADER_STORAGE_BUFFER, GL_R32UI, GL_RED_INTEGER, GL_UNSIGNED_INT, None)
    glBindBuffer(GL_SHADER_STORAGE_BUFFER, 0)


def get_int_ssbo_sum(ssbo, num_workgroups_x, num_workgroups_y):
    # After shader dispatch, read the cell counts
    glBindBuffer(GL_SHADER_STORAGE_BUFFER, ssbo)
    cell_counts = glGetBufferSubData(GL_SHADER_STORAGE_BUFFER, 0, num_workgroups_x * num_workgroups_y * 4)  # Assuming 4 bytes per element (uint)
    return np.sum(np.frombuffer(cell_counts, dtype=np.uint32))


def bind_rgba32f_to_index(texture, index, allow_read, allow_write):
    if allow_read and not allow_write:
        glBindImageTexture(index, texture, 0, GL_FALSE, 0, GL_READ_ONLY, GL_RGBA32F)
    elif allow_write and not allow_read:
        glBindImageTexture(index, texture, 0, GL_FALSE, 0, GL_WRITE_ONLY, GL_RGBA32F)


def bind_ssbo_to_index(ssbo, index):
    glBindBufferBase(GL_SHADER_STORAGE_BUFFER, index, ssbo)


def iterate_shader(shader, workgroup_count_x, workgroup_count_y, pre_invoke_function=None, post_invoke_function=None, iterations=1):
    # Use the shader program
    shader.use()

    for i in range(iterations):
        if pre_invoke_function is not None:
            pre_invoke_function()
            check_opengl_error()

        # Dispatch the compute shader
        glDispatchCompute(workgroup_count_x, workgroup_count_y, 1)
        check_opengl_error()

        # Wait for the compute shader to complete
        glMemoryBarrier(GL_SHADER_IMAGE_ACCESS_BARRIER_BIT)
        check_opengl_error()
        
        if post_invoke_function is not None:
            post_invoke_function()
            check_opengl_error()
            