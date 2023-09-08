import configuration
import gpu


def erode(bedrock, sediment, water, suspended, iterations=100):
    erosion = gpu.Shader(configuration.get('generator.world.deformation.erosion.shader', 'erosion.glsl'))
    height, width = bedrock.shape
    num_workgroups_x, num_workgroups_y = erosion.get_workgroup_count(width, height)
    
    print(f'workgroup size: {num_workgroups_x}, {num_workgroups_y}')

    input_state = gpu.create_rgba32f_texture_from_numpy(bedrock, sediment, water, suspended)
    output_state = gpu.create_empty_rgba32f_texture(width, height)
    
    # Create SSBO for cell_count
    water_count_ssbo = gpu.create_empty_int_ssbo(num_workgroups_x * num_workgroups_y)
    
    erosion_factor = configuration.get('generator.world.deformation.erosion.erosion_factor', 0.05)
    evaporation_factor = configuration.get('generator.world.deformation.erosion.evaporation_factor', 0.01)
    preciptation_factor = configuration.get('generator.world.deformation.erosion.precipitation_factor', 0.01)
    sedimentation_factor = configuration.get('generator.world.deformation.erosion.sedimentation_factor', 0.1)
    precipitation_ratio = 1
    
    def pre_invoke():
        gpu.bind_rgba32f_to_index(input_state, 0, True, False)
        gpu.bind_rgba32f_to_index(output_state, 1, False, True)
        gpu.bind_ssbo_to_index(water_count_ssbo, 2)
        precipitation = preciptation_factor * precipitation_ratio
        # print(f'precipitation = {precipitation}')
        # print(f'evaporation_factor = {evaporation_factor}')
        # print(f'erosion_factor = {erosion_factor}')
        # print(f'sedimentation_factor = {sedimentation_factor}')
        erosion.set_uniform('precipitation', '1f', precipitation)
        erosion.set_uniform('evaporation', '1f', evaporation_factor)
        erosion.set_uniform('erosion_factor', '1f', erosion_factor)
        erosion.set_uniform('sedimentation_factor', '1f', sedimentation_factor)
        
    def post_invoke():
        nonlocal  precipitation_ratio, input_state, output_state

        # Calculate precipitation rate for next pass
        water_count = gpu.get_int_ssbo_sum(water_count_ssbo, num_workgroups_x, num_workgroups_y)
        gpu.clear_int_ssbo(water_count_ssbo)
        precipitation_ratio = float(water_count) / float(width * height)
        # print(f'set precipitation_ratio to {precipitation_ratio} --- water_count = {water_count}')
        
        # Swap input and output for the next pass
        input_state, output_state = output_state, input_state

    gpu.iterate_shader(erosion, num_workgroups_x, num_workgroups_y, pre_invoke_function=pre_invoke, post_invoke_function=post_invoke, iterations=iterations)

    bedrock, sediment, water, suspended = gpu.texture_rgba32f_to_numpy_arrays(input_state, bedrock.shape[1], bedrock.shape[0])
    # TODO: Cleaunup textures

    return bedrock, sediment, water, suspended
        