#version 330 core

in vec2 frag_uv;
flat in float frag_spritesheet_index;

uniform sampler2D spritesheet;
uniform vec2 spritesheet_dimensions_in_sprites;

out vec4 out_color;

void main()
{
    if (frag_spritesheet_index == -1) {
        out_color = vec4(0.0);
    } else {
        // Compute the row and column of the sprite based on the index
        float row = floor(frag_spritesheet_index / spritesheet_dimensions_in_sprites.x);
        float col = mod(frag_spritesheet_index, spritesheet_dimensions_in_sprites.x);
    
        // We need to invert the y component because the spritesheet data is "inverted" vertically
        vec2 inverted_frag_uv = vec2(frag_uv.x, 1.0 - frag_uv.y);
        vec2 sprite_uv = (vec2(col, row) + inverted_frag_uv) / vec2(spritesheet_dimensions_in_sprites);
        out_color = texture(spritesheet, sprite_uv);
    }
}
