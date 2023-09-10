import configuration
import gpu
from gpu_shader import Shader
from gpu_texture import Texture
import numpy as np


def noisy_voronoi(noise_texture_data, seeds, width, height):
    assert noise_texture_data.shape[0] == noise_texture_data.shape[1]
    
    flat_seeds = np.array(seeds, dtype=np.float32).flatten()

    print('creating shader')
    voronoi_shader = Shader(configuration.get('files.shaders.noisy_voronoi', 'noisy_voronoi.glsl'))
    num_workgroups_x, num_workgroups_y = voronoi_shader.get_workgroup_count(width, height)

    print(f'creating noise texture -- shape is {noise_texture_data.shape}, data are{noise_texture_data}')
    noise_texture = Texture(data_format='R', data_dict={'red': noise_texture_data}, min_filter='linear', mag_filter='linear')
    print('creating output texture')
    output_texture = Texture(data_format='R', width=width, height=height)

    def pre_invoke():
        output_texture.bind(0, False, True)
        voronoi_shader.set_uniform("noise_texture", "sampler2D", noise_texture.texture, 0)
        voronoi_shader.set_uniform('seeds', '1fv', len(flat_seeds), flat_seeds)
        voronoi_shader.set_uniform('seed_count', '1i', len(seeds))
        voronoi_shader.set_uniform('noise_size', '1f', noise_texture_data.shape[0])

    def post_invoke():
        pass

    print('iterating')
    voronoi_shader.iterate(num_workgroups_x, num_workgroups_y, pre_invoke_function=pre_invoke, post_invoke_function=post_invoke, iterations=1)

    print('getting result')
    numpy_data = output_texture.to_numpy()
    result = numpy_data['red']

    noise_texture.cleanup()
    output_texture.cleanup()
    voronoi_shader.cleanup()

    return result
