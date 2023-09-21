#version 330 core

in vec2 frag_uv;
flat in float frag_spritesheet_index;

uniform sampler2D spritesheet;
uniform vec2 spritesheet_dimensions_in_sprites;

out vec4 out_color;

void main()
{
    // Compute the row and column of the sprite based on the index
    float row = floor(frag_spritesheet_index / spritesheet_dimensions_in_sprites.x);
    float col = mod(frag_spritesheet_index, spritesheet_dimensions_in_sprites.x);
    
    vec2 sprite_uv = (vec2(col, row) + frag_uv * vec2(1, -1) + vec2(0, 1)) / vec2(spritesheet_dimensions_in_sprites);
    out_color = texture(spritesheet, sprite_uv );
}
