#version 430

// Input
uniform sampler2D noise_texture; 
uniform vec4 seeds[100]; // Array of seeds (assuming max 100 seeds), where seeds[i].xy is position, seeds[i].z is weight, and seeds[i].w is noisiness
uniform int seed_count; // Actual number of seeds
uniform float noise_size;
uniform ivec2 corner_coord;

layout(local_size_x = 16, local_size_y = 16) in;

// Output
layout(r32f, binding = 0) writeonly uniform image2D output_image;

float distance_to_seed(vec2 frag_coord, vec2 seed_pos, float weight) {
    vec2 diff = frag_coord - seed_pos;
    vec2 scaled_diff = diff / noise_size;  // Scale the difference using the noise texture size
    float noise_value = texture(noise_texture, scaled_diff).r; 
    return sqrt(dot(diff, diff)) * weight * noise_value;
}

void real_main() {
   float min_distance = 1e9; // Arbitrarily large number
    int seed_index = -1; // Index of the closest seed
    
    for (int i = 0; i < seed_count; ++i) {
        float distance = distance_to_seed(vec2(ivec2(gl_GlobalInvocationID.xy) + corner_coord), seeds[i].xy, seeds[i].z);
        if (distance < min_distance) {
            min_distance = distance;
            seed_index = i;
        }
    }

    imageStore(output_image, ivec2(gl_GlobalInvocationID.xy), vec4(float(seeds[seed_index].w), 0.0, 0.0, 0.0));
}

void test_main() {
    float noise_value = texture(noise_texture, gl_GlobalInvocationID.xy / noise_size).r;
    imageStore(output_image, ivec2(gl_GlobalInvocationID.xy), vec4(noise_value, noise_value, noise_value, 1.0));
}

void main() {
    real_main();
}
