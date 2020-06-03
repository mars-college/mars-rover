#version 120

attribute vec2 vPosition;
attribute vec2 vTexcoords;

varying vec2 fTexcoords;

void main()
{
    gl_Position = vec4(vPosition.x/1.33, vPosition.y, 0.0, 1.0);
    fTexcoords = vTexcoords;
}

