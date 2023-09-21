from OpenGL.GL import *


class VertexArray:
    def __init__(self, shader, attribute_map):
        """Initialize the VertexArray."""
        self.vao_id = glGenVertexArrays(1)
        self.bind()
        
        for attribute_name, vertex_buffer in attribute_map.items():
            attribute_location = glGetAttribLocation(shader.shader_program, attribute_name)
            if attribute_location == -1:
                raise ValueError(f"Attribute '{attribute_name}' not found in the shader program.")
            vertex_buffer.bind()
            vertex_buffer.set_attribute_pointer(attribute_location)
            vertex_buffer.unbind()
            
        self.unbind()

    def bind(self):
        """Bind the VAO."""
        glBindVertexArray(self.vao_id)

    def unbind(self):
        """Unbind the VAO."""
        glBindVertexArray(0)

    def cleanup(self):
        """Cleanup the VAO."""
        self.unbind()
        glDeleteVertexArrays(1, [self.vao_id])