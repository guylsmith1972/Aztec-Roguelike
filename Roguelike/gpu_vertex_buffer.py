from OpenGL.GL import *
import numpy as np

# Notes: use snake_case wherever possible

class VertexBuffer:
    MODES = {
        None: None,
        'triangle_fan': GL_TRIANGLE_FAN,
        # Add other modes as needed
    }
    
    def __init__(self, data, dimensions, mode, instance_divisor=0):
        self.dimensions = dimensions
        self.mode = self.MODES[mode]
        self.count = len(data) // dimensions
        self.instance_divisor = instance_divisor
        
        # Convert data to numpy array only if it isn't already one
        if not isinstance(data, np.ndarray):
            data = np.array(data, dtype=np.float32)
        
        # Create a VBO (Vertex Buffer Object) and upload the data
        self.vbo_id = glGenBuffers(1)
        self.bind()
        glBufferData(GL_ARRAY_BUFFER, data.nbytes, data, GL_STATIC_DRAW)
        self.unbind()

    def bind(self):
        """Bind the VBO."""
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo_id)

    def unbind(self):
        """Unbind the VBO."""
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    def set_attribute_pointer(self, attribute_location):
        """Set the vertex attribute pointer."""
        glVertexAttribPointer(attribute_location, self.dimensions, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))
        if self.instance_divisor > 0:
            glVertexAttribDivisor(attribute_location, self.instance_divisor)
        glEnableVertexAttribArray(attribute_location)

    def cleanup(self):
        """Cleanup the VBO."""
        glDeleteBuffers(1, [self.vbo_id])

_unit_quad = None

def get_unit_quad():
    global _unit_quad
    if _unit_quad is None:
        _unit_quad = VertexBuffer([
                    -1.0, -1.0,  # Bottom left
                     1.0, -1.0,  # Bottom right
                     1.0,  1.0,  # Top right
                    -1.0,  1.0   # Top left
                ], dimensions=2, mode='triangle_fan')
    return _unit_quad