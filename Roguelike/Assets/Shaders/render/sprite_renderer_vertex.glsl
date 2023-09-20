#version 330 core

// Notes: use snake_case whenever possible

layout(location = 0) in vec2 in_position; // Vertex position of the sprite quad (should be a unit quad, and will be translated/scaled in the shader)
layout(location = 1) in vec2 in_uv;       // UVs for the sprite quad
layout(location = 2) in ivec2 in_instance_position;  // Instanced position of sprite in world coordinates. Pixel coordinates are world coordinates * sprite_size_in_pixels
layout(location = 3) in int in_spritesheet_index; // Instanced spritesheet index

uniform ivec2 sprite_size_in_pixels;             // Width and height of sprite in pixels
uniform ivec2 spritesheet_dimensions_in_sprites; // Width and height of spritesheet, measured in sprites
uniform ivec2 camera_position_in_world;          // X and Y position of camera in world coordinates. Pixel coordinates are world coordinates * sprite_size_in_pixels

out vec2 frag_uv;
flat out float frag_spritesheet_index;

void main()
{
    // Adjust the sprite's position by the camera position
    vec2 adjusted_position = (vec2(in_instance_position) - vec2(camera_position_in_world)) * vec2(sprite_size_in_pixels);

    // Scale and translate the in_position to fit the sprite's size
    vec2 sprite_position = adjusted_position + in_position * vec2(sprite_size_in_pixels);

    // Convert the sprite_position to clip space
    vec2 clip_space_position = sprite_position * 2.0 - 1.0;

    gl_Position = vec4(clip_space_position, 0.0, 1.0);
    
    // Pass through the UV coordinates and spritesheet index
    frag_uv = in_uv;
    frag_spritesheet_index = float(in_spritesheet_index);
}
