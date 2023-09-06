import gpu


def erode(bedrock, sediment, water, suspended, iterations=100):
    return gpu.iterate_rgba32f('Assets/Shaders/erosion.glsl', bedrock, sediment, water, suspended, iterations=iterations)
