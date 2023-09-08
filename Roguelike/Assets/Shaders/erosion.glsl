#version 430

layout(rgba32f, binding = 0) readonly uniform image2D input_data_texture;
layout(rgba32f, binding = 1) writeonly uniform image2D output_data_texture;
layout(std430, binding = 2) buffer ResultBuffer {
    uint cell_count[];
};
shared uint local_count;

layout(local_size_x = 16, local_size_y = 16) in;

uniform float precipitation;
uniform float erosion_factor;
uniform float sedimentation_factor;
uniform float evaporation;

const float near_zero = 0.0001;
const ivec2 offsets[4] = {ivec2(0, -1), ivec2(-1, 0), ivec2(1, 0), ivec2(0, 1)};


// Fast water flow is the amount of water that will flow from column A to column B due to differences in the heights of the water levels
float get_fast_water_flow(float soil_depth_a, float water_depth_a, float total_level_a, float soil_depth_b, float water_depth_b) {
    // Calculate total levels for each column
    float total_level_b = soil_depth_b + water_depth_b;

    // Calculate average water level
    float avg_water_level = (total_level_a + total_level_b) * 0.5;

    // Calculate potential flow from column A to column B
    float potential_flow = water_depth_a - (avg_water_level - soil_depth_a);

    // Limit the flow to the amount of water in column A
    potential_flow = min(potential_flow, water_depth_a);
    potential_flow = max(potential_flow, 0.0);

    return potential_flow;
}

// The diffusion water depth is the height of water between two columns that is not fast water flow and is not soil.
float get_diffusion_water_depth(float soil_depth_a, float water_depth_a, float total_level_a, float soil_depth_b, float water_depth_b) {
    return max(0, min(total_level_a, soil_depth_b + water_depth_b) - max(soil_depth_a, soil_depth_b));
}

void get_outflows(ivec2 coord, out float[4] water_outflows, out float[4] sediment_outflows, out vec4 eroded_values) {
    ivec2 dims = imageSize(input_data_texture);
    vec4 cell_data = imageLoad(input_data_texture, coord);

    float bedrock_height = cell_data.r;
    float sediment_depth = cell_data.g;
    float water_depth = max(0, cell_data.b - evaporation) + precipitation;
    float suspended_sediment = cell_data.a;

    float sediment_height = bedrock_height + sediment_depth;
    float water_level = sediment_height + water_depth + suspended_sediment;
    float sediment_concentration = (water_level > near_zero) ? suspended_sediment / water_level : 0;

    float total_potential_outflow = 0.0;
    float total_potential_sediment_transfer = 0.0;

    float water_outflows_potential[4];
    float sediment_transfers[4];

    // Calculate potential outflows and diffusions for each neighbor
    for (int i = 0; i < 4; i++) {
        vec4 neighbor_data = imageLoad(input_data_texture, (coord + offsets[i] + dims) % dims);
        
        float neighbor_bedrock = neighbor_data.r;
        float neighbor_sediment_depth = neighbor_data.g;
        float neighbor_water_depth = neighbor_data.b;
        float neighbor_suspended_sediment = neighbor_data.a;

        float neighbor_sediment_height = neighbor_bedrock + neighbor_sediment_depth;
        float neighbor_sediment_concentration = (neighbor_water_depth > near_zero) ? (neighbor_suspended_sediment / neighbor_water_depth) : 0;

        // For fast water flow, we want to move an amount of sediment proportional to the water flow without regard to sediment concentration
        float fast_water_flow = get_fast_water_flow(sediment_height, water_depth, water_level, neighbor_sediment_height, neighbor_water_depth);
        float sediment_transfer = (water_depth > near_zero) ? suspended_sediment * fast_water_flow / water_depth : 0;

        // For diffusion, we want to move an amount of sediment proportional to the diffusion water depth multiplied by half the difference in concentration. max 0 because outflow only.
        float diffusion_water_depth = get_diffusion_water_depth(sediment_height, water_depth, water_level, neighbor_sediment_height, neighbor_water_depth);
        float concentration_factor = min(1, max(0, 0.5 * (sediment_concentration - neighbor_sediment_concentration)));
        sediment_transfer += concentration_factor * diffusion_water_depth;

        water_outflows_potential[i] = fast_water_flow;
        sediment_transfers[i] = sediment_transfer;
        total_potential_outflow += water_outflows_potential[i];
        total_potential_sediment_transfer += sediment_transfers[i];
    }

    // Normalize outflows and diffusions
    float normalization_factor_water = (total_potential_outflow > near_zero) ? min(1.0, water_depth / total_potential_outflow) : 1.0;
    float normalization_factor_sediment = (total_potential_sediment_transfer > near_zero) ? min(1.0, suspended_sediment / total_potential_sediment_transfer) : 1.0;

    // Calculate the final state for the cell after distributing water and sediment
    float total_distributed_water = 0.0;
    float total_distributed_sediment = 0.0;

    for (int i = 0; i < 4; i++) {
        water_outflows[i] = water_outflows_potential[i] * normalization_factor_water;
        sediment_outflows[i] = sediment_transfers[i] * normalization_factor_sediment;
        total_distributed_water += water_outflows[i];
        total_distributed_sediment += sediment_outflows[i];
    }

    // churn is used to determine erosion of sediment later
    float churn = (water_depth > near_zero) ? total_distributed_water / water_depth : 0;

    water_depth -= total_distributed_water;
    suspended_sediment -= total_distributed_sediment;

    // Deposite some of the suspended sediment. More sediment is dumped when churn is low.
    float dumped_sediment = suspended_sediment * sedimentation_factor * (1 - churn);
    sediment_depth += dumped_sediment;
    suspended_sediment -= dumped_sediment;

    // Erosion Process
    float erosion_amount = max(0, min(sediment_depth, erosion_factor * churn));
    sediment_depth -= erosion_amount;
    suspended_sediment += erosion_amount;

    eroded_values.r = bedrock_height;
    eroded_values.g = sediment_depth;
    eroded_values.b = water_depth ;
    eroded_values.a = suspended_sediment;
}

void main() {
    ivec2 dims = imageSize(input_data_texture);
    ivec2 coord = ivec2(gl_GlobalInvocationID.xy);

    float own_water_outflow[4] = float[4](0.0, 0.0, 0.0, 0.0);
    float own_sediment_outflow[4] = float[4](0.0, 0.0, 0.0, 0.0);
    vec4 own_eroded_values;
    get_outflows(coord, own_water_outflow, own_sediment_outflow, own_eroded_values);

    // These are the values of this cell AFTER outflow to neighbors has been accounted for in get_outflows()
    float bedrock_height = own_eroded_values.r;
    float sediment_depth = own_eroded_values.g;
    float water_depth = own_eroded_values.b;
    float suspended_sediment = own_eroded_values.a;

    // Now we have to accululate the inflow from neighbors
    for (int i = 0; i < 4; i++) {
        // Calculate inflow from neighbors
        float neighbor_water_outflows[4] = float[4](0.0, 0.0, 0.0, 0.0);
        float neighbor_sediment_outflows[4] = float[4](0.0, 0.0, 0.0, 0.0);

        ivec2 neighbor_coord = (coord + offsets[i] + dims) % dims;
        vec4 neighbor_eroded_values; // We don't care about these values, but we need to pass them in anyway
        get_outflows(neighbor_coord, neighbor_water_outflows, neighbor_sediment_outflows, neighbor_eroded_values);
        int source_index = 3 - i;
        water_depth += neighbor_water_outflows[source_index];
        suspended_sediment += neighbor_sediment_outflows[source_index];
    }

    //  Update cell, accounting for evaporation
    vec4 new_cell_data = vec4(bedrock_height, sediment_depth, water_depth, suspended_sediment);

    // Count number of cells that contain positive water depths
    if (gl_LocalInvocationIndex == 0) {
        local_count = 0;
    }
    barrier();
    if (new_cell_data.b > 0) {
        atomicAdd(local_count, 1);
    }
    barrier();
    if (gl_LocalInvocationIndex == 0) {
        atomicAdd(cell_count[gl_WorkGroupID.x + gl_WorkGroupID.y * gl_NumWorkGroups.x], local_count);
    }

    imageStore(output_data_texture, coord, new_cell_data);
}
