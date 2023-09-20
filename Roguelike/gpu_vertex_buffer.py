from OpenGL.GL import *
import numpy as np

# Notes: use snake_case whenever possible

class VertexBuffer:
    MODES = {
        'triangle_fan': GL_TRIANGLE_FAN,
        # Add other modes as needed
    }
    
    def __init__(self, data, mode='triangle_fan', dimensions=2):
        if data is None:
            raise ValueError("Data cannot be None.")

        self.count = len(data) // dimensions
        self.mode = self.MODES[mode]
        
        self.vbo = glGenBuffers(1)
        array_data = np.array(data, dtype=np.float32)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, array_data.nbytes, array_data, GL_STATIC_DRAW)

        self.vao = glGenVertexArrays(1)
        self.bind()
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 0, None)
        glEnableVertexAttribArray(0)
        self.unbind()

    def bind(self):
        glBindVertexArray(self.vao)

    def unbind(self):
        glBindVertexArray(0)

    def cleanup(self):
        glDeleteBuffers(1, [self.vbo])
        glDeleteVertexArrays(1, [self.vao])


_unit_quad = None

def get_unit_quad():
    global _unit_quad
    if _unit_quad is None:
        _unit_quad = VertexBuffer([
                    -1.0, -1.0,  # Bottom left
                     1.0, -1.0,  # Bottom right
                     1.0,  1.0,  # Top right
                    -1.0,  1.0   # Top left
                ])
    return _unit_quad
