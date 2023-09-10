from OpenGL.GL import *
import gpu
import numpy as np

class Texture:
    # Internal mappings from generic parameters to OpenGL constants
    FORMAT_MAPPING = {
        'RGBA': GL_RGBA32F,
        'R': GL_R32F
    }
    
    PIXEL_FORMAT_MAPPING = {
        'RGBA': GL_RGBA,
        'R': GL_RED
    }

    FILTER_MAPPING = {
        'nearest': GL_NEAREST,
        'linear': GL_LINEAR
    }

    WRAP_MAPPING = {
        'repeat': GL_REPEAT,
        'clamp': GL_CLAMP_TO_EDGE
    }

    def __init__(self, width=None, height=None, data_dict=None, data_format='RGBA', min_filter='nearest', mag_filter='nearest', wrap_s='repeat', wrap_t='repeat'):
        '''
        Initialize the Texture class with either specified width and height or from given numpy arrays.
        '''
        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture)

        self.data_format = data_format

        if width and height:
            # Create an empty texture based on the specified format
            glTexImage2D(GL_TEXTURE_2D, 0, self.FORMAT_MAPPING[data_format], width, height, 0, GL_RGBA, GL_FLOAT, None)
        elif data_dict:
            # Create texture from numpy arrays
            print('extracting data from numpy arrays')
            self.from_numpy(data_dict, do_bind=False)
        
        print('setting texture parameters')
        # Set texture parameters
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, self.FILTER_MAPPING[min_filter])
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, self.FILTER_MAPPING[mag_filter])
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, self.WRAP_MAPPING[wrap_s])
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, self.WRAP_MAPPING[wrap_t])
        
        glBindTexture(GL_TEXTURE_2D, 0)
    
    def from_numpy(self, data_dict, do_bind=True):
        '''
        Create a texture from a dictionary of numpy arrays. The dictionary keys specify the channels ('red', 'green', 'blue', 'alpha').
        '''
        # Ensure all arrays are of the same shape
        shapes = [arr.shape for arr in data_dict.values()]
        assert all(shapes[0] == shape for shape in shapes), 'All input arrays must have the same shape'

        # Determine the texture format based on dictionary keys
        print('getting channels and format')  
        channels = ''.join([ch[0].upper() for ch in data_dict.keys()])
        gl_format = self.FORMAT_MAPPING[channels]
    
        # Concatenate the numpy arrays based on the keys present
        print('concatenatting arrays')
        combined_array = np.stack(list(data_dict.values()), axis=-1).astype(np.float32)
        height, width, _ = combined_array.shape

        # Bind the texture
        if do_bind:
            print('binding texture')
            glBindTexture(GL_TEXTURE_2D, self.texture)
            gpu.check_opengl_error()
    
        # Upload data to texture
        print('uploading data')
        glTexImage2D(GL_TEXTURE_2D, 0, gl_format, width, height, 0, self.PIXEL_FORMAT_MAPPING[self.data_format], GL_FLOAT, combined_array)
        gpu.check_opengl_error()
    
        # Unbind the texture
        if do_bind:
            print('unbinding texture')
            glBindTexture(GL_TEXTURE_2D, 0)
            gpu.check_opengl_error()
    
    def to_numpy(self):
        '''
        Convert the texture to a dictionary of numpy arrays based on its format.
        '''
        # Retrieve the texture dimensions
        glBindTexture(GL_TEXTURE_2D, self.texture)
        width = glGetTexLevelParameteriv(GL_TEXTURE_2D, 0, GL_TEXTURE_WIDTH)
        height = glGetTexLevelParameteriv(GL_TEXTURE_2D, 0, GL_TEXTURE_HEIGHT)
    
        # Determine the number of channels based on the texture format
        format_key = self.data_format
        num_channels = len(format_key)
    
        # Retrieve data from the texture
        data = glGetTexImage(GL_TEXTURE_2D, 0, self.PIXEL_FORMAT_MAPPING[self.data_format], GL_FLOAT)
    
        # Convert data to numpy array
        np_data = np.array(data, dtype=np.float32).reshape((height, width, num_channels))
    
        # Create the output dictionary
        channels_dict = {'R': 'red', 'G': 'green', 'B': 'blue', 'A': 'alpha'}
        output_dict = {}
        for i, ch in enumerate(format_key):
            output_dict[channels_dict[ch]] = np_data[..., i]
    
        return output_dict
    
    
    def bind(self, index, allow_read, allow_write):
        '''
        Bind the texture to a specified index for read/write operations based on the texture format.
        '''
        # Ensure the texture is in a bindable state
        if not self.texture:
            raise ValueError('Texture is not initialized or in a bindable state.')
    
        # Determine the appropriate OpenGL format based on the texture format
        gl_format = self.FORMAT_MAPPING[self.data_format]
    
        # Bind the texture based on read/write permissions
        if allow_read and not allow_write:
            glBindImageTexture(index, self.texture, 0, GL_FALSE, 0, GL_READ_ONLY, gl_format)
        elif allow_write and not allow_read:
            glBindImageTexture(index, self.texture, 0, GL_FALSE, 0, GL_WRITE_ONLY, gl_format)
        else:
            raise ValueError('Invalid combination of allow_read and allow_write flags.')

    def cleanup(self):
        '''
        Cleanup method to delete the texture.
        '''
        glDeleteTextures([self.texture])
