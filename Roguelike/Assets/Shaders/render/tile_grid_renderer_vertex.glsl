#version 330

layout(location = 0) in vec2 in_position;
out vec2 frag_coord;

void main() {
    frag_coord = in_position;
    gl_Position = vec4(in_position, 0.0, 1.0);
}
