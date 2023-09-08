from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

import gpu


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
        elif type == "1ui":
            glUniform1ui(location, *values)
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
        
    def iterate(self, workgroup_count_x, workgroup_count_y, pre_invoke_function=None, post_invoke_function=None, iterations=1):
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
        