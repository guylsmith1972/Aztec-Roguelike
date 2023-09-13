from gpu_shader import get_shader, COMPUTE
from gpu_texture import Texture
import gpu
import numpy as np

max_seeds = 100

def noisy_voronoi(noise_texture_data, seeds, x, y, width, height):
    assert noise_texture_data.shape[0] == noise_texture_data.shape[1]
    
    shader = get_shader(COMPUTE, 'noisy_voronoi')

    flat_seeds = np.array(seeds, dtype=np.float32).flatten()

    num_workgroups_x, num_workgroups_y = shader.get_workgroup_count(width, height)

    noise_texture = Texture({'type': 'numpy', 'data_format': 'R', 'data': {'red': noise_texture_data}}, min_filter='linear', mag_filter='linear')
    output_texture = Texture({'type': 'empty', 'data_format': 'R', 'width': width, 'height': height})

    def pre_invoke():
        output_texture.bind(0, False, True)
        shader.set_uniform('noise_texture', 'sampler2D', noise_texture.texture, 0)
        shader.set_uniform('seeds', '1fv', len(flat_seeds), flat_seeds)
        shader.set_uniform('seed_count', '1i', len(seeds))
        shader.set_uniform('noise_size', '1f', noise_texture_data.shape[0])
        shader.set_uniform('corner_coord', '2i', x, y)

    def post_invoke():
        pass

    shader.compute(num_workgroups_x, num_workgroups_y, pre_invoke_function=pre_invoke, post_invoke_function=post_invoke, iterations=1)

    numpy_data = output_texture.to_numpy()
    result = numpy_data['red']

    return result, seeds
