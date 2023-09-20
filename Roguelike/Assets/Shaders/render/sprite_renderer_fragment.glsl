#version 330 core

in vec2 frag_uv;
flat in float frag_spritesheet_index;

uniform sampler2D spritesheet;
uniform vec2 sprite_size_in_pixels;
uniform vec2 spritesheet_dimensions_in_sprites;

out vec4 outColor;

void main()
{
    // Compute the number of sprites in each dimension
    vec2 spritesInSheet = spritesheet_dimensions_in_sprites / sprite_size_in_pixels;
    
    // Compute the row and column of the sprite based on the index
    float row = floor(frag_spritesheet_index / spritesInSheet.x);
    float col = mod(frag_spritesheet_index, spritesInSheet.x);
    
    // Compute the base UVs for the sprite in the spritesheet
    vec2 baseUV = vec2(col * sprite_size_in_pixels.x, row * sprite_size_in_pixels.y) / spritesheet_dimensions_in_sprites;
    
    // Sample the spritesheet texture using the computed UVs
    vec2 spriteUV = baseUV + frag_uv * (sprite_size_in_pixels / spritesheet_dimensions_in_sprites);
    outColor = texture(spritesheet, spriteUV);
}
