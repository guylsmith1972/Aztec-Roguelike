from OpenGL.GL import *
import numpy as np


class Texture:
    def __init__(self, width=None, height=None, arrays=None):
        """
        Initialize the Texture class with either specified width and height or from given numpy arrays.
        """
        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        
        if width and height:
            # Create an empty RGBA texture
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA32F, width, height, 0, GL_RGBA, GL_FLOAT, None)
        elif arrays:
            # Create texture from numpy arrays
            self.from_numpy(arrays)
        
        # Set texture parameters
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glBindTexture(GL_TEXTURE_2D, 0)
    
    def from_numpy(self, arrays):
        """
        Create an RGBA texture from up to four numpy arrays.
        """
        # Ensure all arrays are of the same shape
        assert all(arrays[0].shape == arr.shape for arr in arrays), "All input arrays must have the same shape"
        
        # Stack the arrays along a new axis to create an RGBA texture
        combined_array = np.stack(arrays, axis=-1).astype(np.float32)
        height, width, _ = combined_array.shape

        # Upload data to texture
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA32F, width, height, 0, GL_RGBA, GL_FLOAT, combined_array)
    
    def to_numpy(self):
        """
        Convert the RGBA texture to up to four numpy arrays.
        """
        # Retrieve the texture dimensions
        glBindTexture(GL_TEXTURE_2D, self.texture)
        width = glGetTexLevelParameteriv(GL_TEXTURE_2D, 0, GL_TEXTURE_WIDTH)
        height = glGetTexLevelParameteriv(GL_TEXTURE_2D, 0, GL_TEXTURE_HEIGHT)
        
        # Retrieve data from the texture
        data = glGetTexImage(GL_TEXTURE_2D, 0, GL_RGBA, GL_FLOAT)
        
        # Convert data to numpy array
        np_data = np.array(data, dtype=np.float32).reshape((height, width, 4))
        
        # Split the numpy array into four separate arrays based on channels
        red, green, blue, alpha = np_data[..., 0], np_data[..., 1], np_data[..., 2], np_data[..., 3]
        
        return red, green, blue, alpha
    
    def bind(self, index, allow_read, allow_write):
        """Bind the texture to a specified index for read/write operations."""
        if allow_read and not allow_write:
            glBindImageTexture(index, self.texture, 0, GL_FALSE, 0, GL_READ_ONLY, GL_RGBA32F)
        elif allow_write and not allow_read:
            glBindImageTexture(index, self.texture, 0, GL_FALSE, 0, GL_WRITE_ONLY, GL_RGBA32F)
    
    def cleanup(self):
        """Cleanup method to delete the texture."""
        glDeleteTextures([self.texture])