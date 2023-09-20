from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

import configuration
import gpu

# Notes: use snake_case whenever possible

_shaders = {}

# Kinds of shaders
COMPUTE = 0
RENDER = 1

shader_kind = ['compute', 'render']


def get_shader(kind, name):
    if kind < 0 or kind >= len(shader_kind):
        raise RuntimeError(f'Invalid shader kind {kind}. Values must be between 0 and {len(shader_kind) - 1} inclusive.')
    
    class Shader:
        def __init__(self):
            if kind == COMPUTE:
                compute_filename = configuration.get(f'files.shaders.{name}.compute', f'{name}.glsl')
                with open(f'Assets/Shaders/compute/{compute_filename}', "r") as f:
                    shader_source = f.read()
                self.compute_shader = compileShader(shader_source, GL_COMPUTE_SHADER)
                self.shader_program = compileProgram(self.compute_shader)
            elif kind == RENDER:
                vertex_filename = configuration.get(f'files.shaders.{name}.vertex', f'{name}_vertex.glsl')
                fragment_filename = configuration.get(f'files.shaders.{name}.fragment', f'{name}_fragment.glsl')
                with open(f'Assets/Shaders/render/{vertex_filename}', "r") as f:
                    vertex_shader_source = f.read()
                with open(f'Assets/Shaders/render/{fragment_filename}', "r") as f:
                    fragment_shader_source = f.read()
                self.vertex_shader = compileShader(vertex_shader_source, GL_VERTEX_SHADER)
                self.fragment_shader = compileShader(fragment_shader_source, GL_FRAGMENT_SHADER)
                self.shader_program = compileProgram(self.vertex_shader, self.fragment_shader)
            else:
                raise RuntimeError(f'Unknown shader kind: {kind}')
            
        # def __del__(self):
        #     self.cleanup()

        def set_uniform(self, name, type, *values):
            location = glGetUniformLocation(self.shader_program, name)
            if type == "1f":
                glUniform1f(location, *values)
            elif type == "2i": 
                glUniform2i(location, *values)
            elif type == "2iv": 
                glUniform2iv(location, *values)
            elif type == "2f":
                glUniform2f(location, *values)
            elif type == "3f":
                glUniform3f(location, *values)
            elif type == "4f":
                glUniform4f(location, *values)
            elif type == "1i":
                glUniform1i(location, *values)
            elif type == "1ui":
                glUniform1ui(location, *values)
            elif type == "1fv":  # For setting arrays of vec4 values
                count, data = values
                glUniform4fv(location, count, data)
            elif type == "sampler2D":
                texture, texture_unit = values
                glActiveTexture(GL_TEXTURE0 + texture_unit)  # activate the texture unit
                glBindTexture(GL_TEXTURE_2D, texture)        # bind the texture
                glUniform1i(location, texture_unit)          # set the sampler2D uniform to the texture unit index
            else:
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
            if hasattr(self, "vbo"):
                glDeleteBuffers(1, [self.vbo])
            if hasattr(self, "vao"):
                glDeleteVertexArrays(1, [self.vao])
            if hasattr(self, "compute_shader"):
                glDeleteShader(self.compute_shader)
            if hasattr(self, "vertex_shader"):
                glDeleteShader(self.vertex_shader)
            if hasattr(self, "fragment_shader"):
                glDeleteShader(self.fragment_shader)
            glDeleteProgram(self.shader_program)
            
        def render(self, display, vertex_buffer, screen_x=0, screen_y=0, width=-1, height=-1, instance_count=1):
            # Set the viewport
            if width == -1:
                width = display.get_width()
            if height == -1:
                height = display.get_height()
            glViewport(screen_x, screen_y, width, height)
    
            # Use the shader program
            self.use()
    
            # Render using the vertex buffer
            vertex_buffer.bind()
            if instance_count == 1:
                glDrawArrays(vertex_buffer.mode, 0, vertex_buffer.count)
            elif instance_count > 1:
                glDrawArraysInstanced(vertex_buffer.mode(), 0, vertex_buffer.count, instancecount=instance_count)
            vertex_buffer.unbind()

        def compute(self, workgroup_count_x, workgroup_count_y, pre_invoke_function=None, post_invoke_function=None, iterations=1):
            # Use the shader program
            self.use()

            for _ in range(iterations):
                if pre_invoke_function is not None:
                    pre_invoke_function()
                    gpu.check_opengl_error()

                # Dispatch the compute shader
                glDispatchCompute(workgroup_count_x, workgroup_count_y, 1)
                gpu.check_opengl_error()

                # Wait for the compute shader to complete
                glMemoryBarrier(GL_SHADER_IMAGE_ACCESS_BARRIER_BIT)
                gpu.check_opengl_error()
        
                if post_invoke_function is not None:
                    post_invoke_function()
                    gpu.check_opengl_error()
            
        def bind(self, element_to_bind, binding_point, block_name):
            element_to_bind.bind(binding_point, block_name, self.shader_program)

    global _shaders
    key = (kind, name)
    if key not in _shaders:
        _shaders[key] = Shader()

    return _shaders[key]


def cleanup_shaders():
    for _, shader in _shaders.items():
        shader.cleanup()
