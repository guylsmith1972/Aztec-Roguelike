#version 330 core

// Notes: use snake_case whenever possible

layout(location = 0) in vec2 in_position; // Vertex position of the sprite quad (should be a unit quad, and will be translated/scaled in the shader)
layout(location = 1) in ivec3 in_instance_sprite_parameters;  // Instanced position of sprite in world coordinates and sprite index. Pixel coordinates are world coordinates * sprite_size_in_pixels

uniform vec2 sprite_size_in_pixels;             // Width and height of sprite in pixels
uniform vec2 camera_position_in_world;          // X and Y position of camera in world coordinates. Pixel coordinates are world coordinates * sprite_size_in_pixels
uniform vec2 screen_dimensions_in_pixels;       // Width and height of screen in pixels

out vec2 frag_uv;
flat out float frag_spritesheet_index;

void main()
{
    vec2 normalized_vertex_coord = in_position / 2.0;
    vec2 relative_sprite_coord_in_world = in_instance_sprite_parameters.xy - camera_position_in_world + normalized_vertex_coord;
    vec2 relative_sprite_coord_in_pixels = relative_sprite_coord_in_world * sprite_size_in_pixels;
    vec2 relative_sprite_coord_in_NDC = relative_sprite_coord_in_pixels / (screen_dimensions_in_pixels / 2);

    gl_Position = vec4(relative_sprite_coord_in_NDC, 0.0, 1.0);
    
    // Compute the UV coordinates from in_position
    frag_uv = (in_position + 1.0) / 2.0;
    frag_spritesheet_index = float(in_instance_sprite_parameters.z);
}
