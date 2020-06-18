#version 120

attribute vec2 vPosition;
attribute vec2 vTexcoords;


uniform mat4 projectionMatrix;
uniform mat4 modelViewMatrix;
uniform mat4 textureMatrix;
uniform mat4 modelViewProjectionMatrix;

attribute vec4  position;
attribute vec4  color;
attribute vec3  normal;
//attribute vec2  texcoord;


varying vec2 fTexcoords;

void main()
{
    gl_Position = vec4(vPosition.x, vPosition.y, 0.0, 1.0);
    //gl_Position = modelViewProjectionMatrix * vPosition;
    fTexcoords = vTexcoords;
}
