#version 330

in vec2 in_vert;
out vec2 pos;

void main() {
    pos = 0.5*(1.0+in_vert);
    gl_Position = vec4(in_vert, 0.0, 1.0);
}