#version 430

in vec2 fragCoord;
out vec4 outColor;

uniform sampler2D spritesheet;
uniform sampler2D tile_indices;
uniform ivec2 target_dimensions_in_pixels; 
uniform ivec2 spritesheet_dimensions_in_tiles; 
uniform ivec2 tile_dimensions_in_pixels;
uniform int show_grid_lines;
uniform int show_chunk_lines;

void main() {
    // Convert fragCoord from [-1,1] to pixel coordinates [0, width), [0, height)
    ivec2 pixel_coord = ivec2((fragCoord + vec2(1.0)) * 0.5 * vec2(target_dimensions_in_pixels));

    // Determine index tile position
    ivec2 index_tile_pos = pixel_coord / tile_dimensions_in_pixels;

    // Convert to [0,1] range for sampling from tile_indices
    vec2 index_uv = vec2(index_tile_pos) / (vec2(target_dimensions_in_pixels) / vec2(tile_dimensions_in_pixels));
    
    int tile_index = int(texture(tile_indices, index_uv).r);

    if (tile_index >= 0) {
        ivec2 spritesheet_tile_coord = ivec2(tile_index % spritesheet_dimensions_in_tiles.x,
                                                tile_index / spritesheet_dimensions_in_tiles.x);

        ivec2 spritesheet_corner_pixel_coord = spritesheet_tile_coord * tile_dimensions_in_pixels;
    
        // Individual tiles are "upside down" in the spritesheet
        ivec2 pixel_offset = ivec2(pixel_coord.x % tile_dimensions_in_pixels.x, tile_dimensions_in_pixels.y - 1 - (pixel_coord.y % tile_dimensions_in_pixels.y));

        ivec2 spritesheet_pixel_coord = spritesheet_corner_pixel_coord + pixel_offset;

        // Convert to UV coordinates for sampling
        vec2 spritesheet_uv = (vec2(spritesheet_pixel_coord) + vec2(0.5)) / vec2(spritesheet_dimensions_in_tiles * tile_dimensions_in_pixels);

        outColor = texture(spritesheet, spritesheet_uv);
    } else {
        outColor = vec4(0.0);
    }

    if (show_grid_lines == 1 && tile_dimensions_in_pixels.x >= 8 && (pixel_coord.x % tile_dimensions_in_pixels.x == 0 || pixel_coord.y % tile_dimensions_in_pixels.y == 0)) {
        outColor = vec4(0.5, 0.5, 0.5, 1);
    }
    if (show_chunk_lines == 1 && (pixel_coord.x == 0 || pixel_coord.y == 0)) {
        outColor = vec4(1.0);
    }
}
