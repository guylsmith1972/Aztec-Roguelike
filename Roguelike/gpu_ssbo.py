from OpenGL.GL import *
import numpy as np


class SSBO:
    DATA_TYPE_INFO = {
        'float': {
            'gl_type': GL_R32F,
            'format': GL_RED,
            'type': GL_FLOAT,
            'numpy_type': np.float32,
            'size': 4
        },
        'uint32': {
            'gl_type': GL_R32UI,
            'format': GL_RED_INTEGER,
            'type': GL_UNSIGNED_INT,
            'numpy_type': np.uint32,
            'size': 4
        }
    }
    
    def __init__(self, num_elements, data_type='float'):
        self.num_elements = num_elements
        self.data_type = data_type
        self.ssbo = self.create_empty_ssbo(num_elements, data_type)
    
    def create_empty_ssbo(self, num_elements, data_type):
        """Create an empty SSBO based on the specified data type."""
        ssbo = glGenBuffers(1)
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, ssbo)
        glBufferData(GL_SHADER_STORAGE_BUFFER, num_elements * self.DATA_TYPE_INFO[data_type]['size'], None, GL_DYNAMIC_DRAW)
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, 0)
        return ssbo
    
    def cleanup(self):
        """Release the SSBO resources."""
        glDeleteBuffers(1, [self.ssbo])

    def clear(self):
        """Clear the SSBO based on the specified data type."""
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.ssbo)
        info = self.DATA_TYPE_INFO[self.data_type]
        glClearBufferData(GL_SHADER_STORAGE_BUFFER, info['gl_type'], info['format'], info['type'], None)
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, 0)

    def get_sum(self, num_workgroups_x, num_workgroups_y):
        """After shader dispatch, read the accumulated values based on the specified data type and return their sum."""
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.ssbo)
        buffer_data = glGetBufferSubData(GL_SHADER_STORAGE_BUFFER, 0, num_workgroups_x * num_workgroups_y * self.DATA_TYPE_INFO[self.data_type]['size'])
        return np.sum(np.frombuffer(buffer_data, dtype=self.DATA_TYPE_INFO[self.data_type]['numpy_type']))

    def bind(self, binding_point):
        """Bind the SSBO to a specific binding point and block name in a shader program."""
        glBindBufferBase(GL_SHADER_STORAGE_BUFFER, binding_point, self.ssbo)
