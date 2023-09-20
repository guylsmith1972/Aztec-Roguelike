#version 330 core

in vec2 frag_uv;
flat in float frag_spritesheet_index;

uniform sampler2D spritesheet;
uniform ivec2 sprite_size_in_pixels;
uniform ivec2 spritesheet_dimensions_in_sprites;

out vec4 out_color;

void main()
{
    // Compute the number of sprites in each dimension
    vec2 sprites_in_sheet = vec2(spritesheet_dimensions_in_sprites) / vec2(sprite_size_in_pixels);
    
    // Compute the row and column of the sprite based on the index
    float row = floor(frag_spritesheet_index / sprites_in_sheet.x);
    float col = mod(frag_spritesheet_index, sprites_in_sheet.x);
    
    // Compute the base UVs for the sprite in the spritesheet
    vec2 base_uv = vec2(col, row) * vec2(sprite_size_in_pixels) / vec2(spritesheet_dimensions_in_sprites);
    
    // Sample the spritesheet texture using the computed UVs
    vec2 sprite_uv = base_uv + frag_uv * (vec2(sprite_size_in_pixels) / vec2(spritesheet_dimensions_in_sprites));
    out_color = texture(spritesheet, sprite_uv);
}
