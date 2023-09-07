#version 430

layout(rgba32f, binding = 0) readonly uniform image2D input_data_texture;
layout(rgba32f, binding = 1) writeonly uniform image2D output_data_texture;

layout(local_size_x = 16, local_size_y = 16) in;

const float erosion_factor = 0.15;
const float precipitation = 0.01;
const float zero_flow_rate = 1; // At this rate of flow, no sediment is deposited

const ivec2 offsets[8] = {
    ivec2(-1, -1), ivec2(0, -1), ivec2(1, -1),
    ivec2(-1, 0), ivec2(1, 0),
    ivec2(-1, 1), ivec2(0, 1), ivec2(1, 1)
};

void get_outflows(ivec2 coord, out float[8] water_outflows, out float[8] sediment_outflows, out vec4 eroded_values) {
    ivec2 dims = imageSize(input_data_texture);
    vec4 cell_data = imageLoad(input_data_texture, coord);

    float bedrock_height = cell_data.r;
    float sediment_depth = cell_data.g;
    float water_depth = cell_data.b + precipitation;  // Add a constant amount of rainfall
    float suspended_sediment = cell_data.a;

    // Get the altitude of the current cell
    float current_altitude = bedrock_height + sediment_depth;
    
    float height_differences[8] = float[8](0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0);

    // Calculate outflow to each neighboring cell
    float total_height_differences = 0;

    for (int i = 0; i < 8; i++) {
        vec4 neighbor_data = imageLoad(input_data_texture, (coord + offsets[i] + dims) % dims);
        float neighbor_altitude = neighbor_data.r + neighbor_data.g;

        float height_difference = current_altitude - neighbor_altitude;
        if (height_difference > 0) {
            height_differences[i] = height_difference;
            total_height_differences += height_difference;
        }
    }

    float expected_water_outflow = max(0, min(total_height_differences, water_depth));

    // Deposite sediment
    float sedimentation = suspended_sediment * (1 - min(1, expected_water_outflow / zero_flow_rate));
    sediment_depth += sedimentation;
    suspended_sediment -= sedimentation;

    // Erode sediment
    float erosion = expected_water_outflow * erosion_factor;
    erosion = min(erosion, sediment_depth);
    suspended_sediment += erosion;
    sediment_depth -= erosion;

    // Initialize variables to track total distributed sediment and water
    float actual_distributed_sediment = 0.0;
    float actual_distributed_water = 0.0;

    // Distribute water and suspended sediment to neighbors
    for (int i = 0; i < 8; i++) {
        if (total_height_differences > 0) {
            float outflow_share = height_differences[i] / total_height_differences;
            water_outflows[i] = expected_water_outflow * outflow_share;
            sediment_outflows[i] = suspended_sediment * outflow_share;
            actual_distributed_sediment += sediment_outflows[i];
            actual_distributed_water += water_outflows[i];
        } else {
            water_outflows[i] = 0;
            sediment_outflows[i] = 0;
        }
    }

    eroded_values.r = bedrock_height;
    eroded_values.g = sediment_depth;
    eroded_values.b = water_depth - actual_distributed_water;
    eroded_values.a = suspended_sediment - actual_distributed_sediment;
}

void main() {
    ivec2 dims = imageSize(input_data_texture);
    ivec2 coord = ivec2(gl_GlobalInvocationID.xy);

    float own_water_outflow[8] = float[8](0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0);
    float own_sediment_outflow[8] = float[8](0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0);
    vec4 own_eroded_values;
    get_outflows(coord, own_water_outflow, own_sediment_outflow, own_eroded_values);

    // These are the values of this cell AFTER outflow to neighbors has been accounted for in get_outflows()
    float bedrock_height = own_eroded_values.r;
    float sediment_depth = own_eroded_values.g;
    float water_depth = own_eroded_values.b;
    float suspended_sediment = own_eroded_values.a;

    // Now we have to accululate the inflow from neighbors
    float neighbor_water_outflows[8] = float[8](0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0);
    float neighbor_sediment_outflows[8] = float[8](0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0);

    for (int i = 0; i < 8; i++) {
        // Calculate inflow from neighbors
        ivec2 neighbor_coord = (coord + offsets[i] + dims) % dims;
        vec4 neighbor_eroded_values; // We don't care about these values, but we need to pass them in anyway
        get_outflows(neighbor_coord, neighbor_water_outflows, neighbor_sediment_outflows, neighbor_eroded_values);
        int source_index = 7 - i;
        water_depth += neighbor_water_outflows[source_index];
        suspended_sediment += neighbor_sediment_outflows[source_index];
    }

    //  Update cell, accounting for evaporation
    vec4 new_cell_data = vec4(bedrock_height, sediment_depth, max(0, water_depth - precipitation), suspended_sediment);

    imageStore(output_data_texture, coord, new_cell_data);
}
