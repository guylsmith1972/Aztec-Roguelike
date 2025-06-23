#version 430

layout(rgba32f, binding = 0) readonly uniform image2D input_data_texture;   // Input texture
layout(rgba32f, binding = 1) writeonly uniform image2D output_data_texture; // Output texture

layout(local_size_x = 16, local_size_y = 16) in;

uniform float erosion_rate;            // Rate at which erosion occurs
uniform float deposition_rate;         // Rate at which sediment is deposited
uniform float sediment_capacity;       // Maximum sediment capacity per cell
uniform float water_flow_rate;         // Rate at which water flows
uniform float evaporation_rate;        // Rate at which water evaporates
uniform float precipitation_rate;      // Rate at which water precipitates

// Constants
const float near_zero = 0.0001;
const ivec2 offsets[4] = ivec2[4](ivec2(0, -1), ivec2(-1, 0), ivec2(1, 0), ivec2(0, 1));

void main() {
    ivec2 dims = imageSize(input_data_texture);
    ivec2 coord = ivec2(gl_GlobalInvocationID.xy);

    // Read current cell data
    vec4 cell_data = imageLoad(input_data_texture, coord);

    float bedrock_height = cell_data.r;       // Red channel: bedrock height
    float sediment_depth = cell_data.g;       // Green channel: sediment depth
    float water_depth = cell_data.b;          // Blue channel: water depth
    float sediment_carried = cell_data.a;     // Alpha channel: sediment being carried by water

    float total_height = bedrock_height + sediment_depth + water_depth;

    // Initialize variables to accumulate changes
    float delta_sediment = 0.0;
    float delta_water = 0.0;

    // Loop over neighboring cells to simulate erosion and sediment transport
    for (int i = 0; i < 4; i++) {
        ivec2 neighbor_coord = (coord + offsets[i] + dims) % dims;
        vec4 neighbor_data = imageLoad(input_data_texture, neighbor_coord);

        float neighbor_bedrock_height = neighbor_data.r;
        float neighbor_sediment_depth = neighbor_data.g;
        float neighbor_water_depth = neighbor_data.b;
        float neighbor_sediment_carried = neighbor_data.a;

        float neighbor_total_height = neighbor_bedrock_height + neighbor_sediment_depth + neighbor_water_depth;

        // Height difference between the current cell and the neighbor
        float height_diff = total_height - neighbor_total_height;

        // If the neighbor is lower, simulate erosion and sediment transport
        if (height_diff > near_zero) {
            // Calculate amount of water and sediment to transfer
            float water_to_transfer = min(water_flow_rate * height_diff, water_depth);
            float sediment_to_transfer = min(erosion_rate * height_diff, sediment_depth);

            // Update accumulators
            delta_water -= water_to_transfer;
            delta_sediment -= sediment_to_transfer;

            // Send water and sediment to the neighbor
            // Since we can't write to neighbor cells directly in this pass,
            // we'll handle incoming transfers in a separate pass or use a ping-pong buffer approach.
        }
    }

    // Evaporation and precipitation
    float water_evaporated = min(evaporation_rate, water_depth);
    float water_precipitated = precipitation_rate;

    delta_water -= water_evaporated;
    delta_water += water_precipitated;

    // Sediment deposition: if the sediment being carried exceeds capacity, deposit it
    if (sediment_carried > sediment_capacity) {
        float excess_sediment = sediment_carried - sediment_capacity;
        delta_sediment += excess_sediment;
        sediment_carried -= excess_sediment;
    }

    // Update cell values
    water_depth += delta_water;
    sediment_depth += delta_sediment;

    // Ensure non-negative values
    water_depth = max(water_depth, 0.0);
    sediment_depth = max(sediment_depth, 0.0);

    // Update the output texture
    vec4 new_cell_data = vec4(bedrock_height, sediment_depth, water_depth, sediment_carried);
    imageStore(output_data_texture, coord, new_cell_data);
}
