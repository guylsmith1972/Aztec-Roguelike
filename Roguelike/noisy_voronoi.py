from gpu_shader import Shader
from gpu_texture import Texture
import configuration
import gpu
import json
import numpy as np


max_seeds = 100

def noisy_voronoi(noise_texture_data, seeds, width, height, reference_point):
    assert noise_texture_data.shape[0] == noise_texture_data.shape[1]

    if len(seeds) > max_seeds:
        def distance(point1, point2):
            return ((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2) ** 0.5

        sorted_seeds = sorted(seeds, key=lambda seed: distance(seed, reference_point))
        seeds = sorted_seeds[0:max_seeds]

    print(json.dumps(seeds, indent=2))    

    flat_seeds = np.array(seeds, dtype=np.float32).flatten()

    shader = Shader(configuration.get('files.shaders.noisy_voronoi', 'noisy_voronoi.glsl'))
    num_workgroups_x, num_workgroups_y = shader.get_workgroup_count(width, height)

    noise_texture = Texture(data_format='R', data_dict={'red': noise_texture_data}, min_filter='linear', mag_filter='linear')
    output_texture = Texture(data_format='R', width=width, height=height)

    def pre_invoke():
        output_texture.bind(0, False, True)
        shader.set_uniform("noise_texture", "sampler2D", noise_texture.texture, 0)
        shader.set_uniform('seeds', '1fv', len(flat_seeds), flat_seeds)
        shader.set_uniform('seed_count', '1i', len(seeds))
        shader.set_uniform('noise_size', '1f', noise_texture_data.shape[0])

    def post_invoke():
        pass

    shader.iterate(num_workgroups_x, num_workgroups_y, pre_invoke_function=pre_invoke, post_invoke_function=post_invoke, iterations=1)

    numpy_data = output_texture.to_numpy()
    result = numpy_data['red']

    noise_texture.cleanup()
    output_texture.cleanup()
    shader.cleanup()

    return result, seeds
