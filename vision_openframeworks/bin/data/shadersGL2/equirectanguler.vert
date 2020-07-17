#version 120

uniform mat4 projectionMatrix;
uniform mat4 modelViewMatrix;
uniform mat4 textureMatrix;
uniform mat4 modelViewProjectionMatrix;

attribute vec4  position;
attribute vec4  color;
attribute vec3  normal;
attribute vec2  texcoord;

varying vec2 texCoordVarying;

void main() {
    texCoordVarying = gl_MultiTexCoord0.xy;
	gl_Position = ftransform();
}