from OpenGL.converters import Output
import configuration
import gpu
from gpu_shader import get_shader, COMPUTE
from gpu_ssbo import SSBO
from gpu_texture import Texture


def erode(bedrock, sediment, water, suspended, iterations=100):
    erosion = get_shader(COMPUTE, configuration.get('generator.world.deformation.erosion.shader', 'erosion'))
    height, width = bedrock.shape
    num_workgroups_x, num_workgroups_y = erosion.get_workgroup_count(width, height)
    
    print(f'workgroup size: {num_workgroups_x}, {num_workgroups_y}')

    # Initialize input texture with the 'numpy' type based on the new Texture definition
    input_state = Texture(texture_config={
        'type': 'numpy',
        'data_format': 'RGBA',
        'data': {'red': bedrock, 'green': sediment, 'blue': water, 'alpha': suspended}
    })

    # Initialize output texture as an empty texture with the 'empty' type based on the new Texture definition
    output_state = Texture(texture_config={
        'type': 'empty',
        'data_format': 'RGBA',
        'width': width,
        'height': height
    })

    # Create SSBO for atmospheric water
    atmospheric_water_ssbo = SSBO(num_workgroups_x * num_workgroups_y, 'uint32')
    
    erosion_factor = configuration.get('generator.world.deformation.erosion.erosion_factor', 0.05)
    evaporation_factor = configuration.get('generator.world.deformation.erosion.evaporation_factor', 0.01)
    evaporation_multiplier = configuration.get('generator.world.deformation.erosion.evaporation_multiplier', 10000)
    preciptation_factor = configuration.get('generator.world.deformation.erosion.precipitation_factor', 0.01)
    sedimentation_factor = configuration.get('generator.world.deformation.erosion.sedimentation_factor', 0.05)
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
        nonlocal atmospheric_water, input_state, output_state

        # Calculate precipitation rate for next pass
        atmospheric_water += float(atmospheric_water_ssbo.get_sum(num_workgroups_x, num_workgroups_y)) / evaporation_multiplier
        atmospheric_water_ssbo.clear()
        
        # Swap input and output textures for the next pass
        input_state, output_state = output_state, input_state

    # Replace erosion.iterate with erosion.compute
    erosion.compute(num_workgroups_x, num_workgroups_y, pre_invoke_function=pre_invoke, post_invoke_function=post_invoke, iterations=iterations)

    # Convert the texture back to numpy arrays
    numpy_dict = input_state.to_numpy()
    bedrock, sediment, water, suspended = numpy_dict['red'], numpy_dict['green'], numpy_dict['blue'], numpy_dict['alpha']

    # Cleanup resources
    input_state.cleanup()
    output_state.cleanup()
    atmospheric_water_ssbo.cleanup()
    erosion.cleanup()
    
    print(f'atmospheric_water = {atmospheric_water}')

    return bedrock, sediment, water, suspended
