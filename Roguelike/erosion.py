from OpenGL.converters import Output
import configuration
import gpu
from gpu_shader import Shader
from gpu_ssbo import SSBO
from gpu_texture import Texture


def erode(bedrock, sediment, water, suspended, iterations=100):
    erosion = Shader(configuration.get('generator.world.deformation.erosion.shader', 'erosion.glsl'))
    height, width = bedrock.shape
    num_workgroups_x, num_workgroups_y = erosion.get_workgroup_count(width, height)
    
    print(f'workgroup size: {num_workgroups_x}, {num_workgroups_y}')

    input_state = Texture(arrays=[bedrock, sediment, water, suspended])
    output_state = Texture(width=width, height=height)

    # Create SSBO for cell_count
    atmospheric_water_ssbo = SSBO(num_workgroups_x * num_workgroups_y, 'uint32')
    
    erosion_factor = configuration.get('generator.world.deformation.erosion.erosion_factor', 0.05)
    evaporation_factor = configuration.get('generator.world.deformation.erosion.evaporation_factor', 0.01)
    evaporation_multiplier = configuration.get('generator.world.deformation.erosion.evaporation_multiplier', 10000)
    preciptation_factor = configuration.get('generator.world.deformation.erosion.precipitation_factor', 0.01)
    sedimentation_factor = configuration.get('generator.world.deformation.erosion.sedimentation_factor', 0.05)
    precipitation_ratio = 1
    atmospheric_water = water.shape[0] * water.shape[1] * preciptation_factor
    
    def pre_invoke():
        nonlocal atmospheric_water
        input_state.bind(0, True, False)
        output_state.bind(1, False, True)
        atmospheric_water_ssbo.bind(2)
        
        precipitation = atmospheric_water / (water.shape[0] * water.shape[1])
        atmospheric_water = 0
        
        erosion.set_uniform('precipitation', '1f', precipitation)
        erosion.set_uniform('evaporation', '1f', evaporation_factor)
        erosion.set_uniform('evaporation_multiplier', '1ui', evaporation_multiplier)
        erosion.set_uniform('erosion_factor', '1f', erosion_factor)
        erosion.set_uniform('sedimentation_factor', '1f', sedimentation_factor)
        
    def post_invoke():
        nonlocal atmospheric_water, precipitation_ratio, input_state, output_state

        # Calculate precipitation rate for next pass
        atmospheric_water += float(atmospheric_water_ssbo.get_sum(num_workgroups_x, num_workgroups_y)) / evaporation_multiplier
        atmospheric_water_ssbo.clear()
        
        # Swap input and output for the next pass
        input_state, output_state = output_state, input_state

    erosion.iterate(num_workgroups_x, num_workgroups_y, pre_invoke_function=pre_invoke, post_invoke_function=post_invoke, iterations=iterations)

    bedrock, sediment, water, suspended = input_state.to_numpy()

    input_state.cleanup()
    output_state.cleanup()
    atmospheric_water_ssbo.cleanup()
    erosion.cleanup()
    
    print(f'atmospheric_water = {atmospheric_water}')

    return bedrock, sediment, water, suspended
        