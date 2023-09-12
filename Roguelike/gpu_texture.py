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

    def __init__(self, texture_config, min_filter='nearest', mag_filter='nearest', wrap_s='repeat', wrap_t='repeat'):
        '''
        Initialize the Texture class based on a configuration dictionary.
        '''
        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture)

        def init_empty():
            width = texture_config["width"]
            height = texture_config["height"]
            self.data_format = texture_config["data_format"]
            glTexImage2D(GL_TEXTURE_2D, 0, self.FORMAT_MAPPING[self.data_format], width, height, 0, Texture.PIXEL_FORMAT_MAPPING[self.data_format], GL_FLOAT, None)

        def init_image():
            self.data_format = "RGBA"
            self._from_pillow_image(texture_config["data"])

        def init_numpy():
            self.data_format = texture_config["data_format"]
            self.from_numpy(texture_config["data"], do_bind=False)

        # Simulating switch-case using a dictionary
        switcher = {
            "empty": init_empty,
            "image": init_image,
            "numpy": init_numpy
        }

        # Get the function from switcher dictionary and execute it
        func = switcher.get(texture_config.get("type"), lambda: "Invalid type")
        func()

        if not hasattr(self, "data_format"):
            raise ValueError(f"Unsupported texture type: {texture_config.get('type')}")

        # Set texture parameters
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, self.FILTER_MAPPING[min_filter])
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, self.FILTER_MAPPING[mag_filter])
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, self.WRAP_MAPPING[wrap_s])
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, self.WRAP_MAPPING[wrap_t])
        
        glBindTexture(GL_TEXTURE_2D, 0)
        
    # def __del__(self):
    #     self.cleanup()

    def _from_pillow_image(self, img):
        img_data = np.array(img.convert("RGBA"))
        glTexImage2D(GL_TEXTURE_2D, 0, self.FORMAT_MAPPING[self.data_format], img.width, img.height, 0, 
                     self.PIXEL_FORMAT_MAPPING[self.data_format], GL_UNSIGNED_BYTE, img_data)
    
    def from_numpy(self, data_dict, do_bind=True):
        '''
        Create a texture from a dictionary of numpy arrays. The dictionary keys specify the channels ('red', 'green', 'blue', 'alpha').
        '''
        # Ensure all arrays are of the same shape
        shapes = [arr.shape for arr in data_dict.values()]
        assert all(shapes[0] == shape for shape in shapes), 'All input arrays must have the same shape'

        # Determine the texture format based on dictionary keys
        channels = ''.join([ch[0].upper() for ch in data_dict.keys()])
        gl_format = self.FORMAT_MAPPING[channels]
    
        # Concatenate the numpy arrays based on the keys present
        combined_array = np.stack(list(data_dict.values()), axis=-1).astype(np.float32)
        height, width, _ = combined_array.shape

        # Bind the texture
        if do_bind:
            glBindTexture(GL_TEXTURE_2D, self.texture)
            gpu.check_opengl_error()
    
        # Upload data to texture
        glTexImage2D(GL_TEXTURE_2D, 0, gl_format, width, height, 0, self.PIXEL_FORMAT_MAPPING[self.data_format], GL_FLOAT, combined_array)
        gpu.check_opengl_error()
    
        # Unbind the texture
        if do_bind:
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
