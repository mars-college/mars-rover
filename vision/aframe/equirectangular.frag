#version 330

uniform sampler2D textureObj;
in vec2 pos;
out vec4 f_color;

#ifdef GL_ES
precision mediump float;
precision mediump int;
#endif

#define PI 3.14159265358979
#define _THETA_S_Y_SCALE	(640.0 / 720.0)

//uniform vec4 uvOffset;

void main() {
    vec4 uvOffset = vec4(0);
    float radius = 0.445;

    vec2 revUV = pos.xy;
    if (pos.x <= 0.5) {
        revUV.x = revUV.x * 2.0;
    } else {
        revUV.x = (revUV.x - 0.5) * 2.0;
    }
    
    revUV *= PI;

    vec3 p = vec3(cos(revUV.x), cos(revUV.y), sin(revUV.x));
    p.xz *= sqrt(1.0 - p.y * p.y);

    float r = 1.0 - asin(p.z) / (PI / 2.0);
    vec2 st = vec2(p.y, p.x);

    st *= r / sqrt(1.0 - p.z * p.z);
    st *= radius;
    st += 0.5;
    
    if (pos.x <= 0.5) {
        st.x *= 0.5;
        st.x += 0.5;
        st.y = 1.0 - st.y;
        st.xy += uvOffset.wz;
    } else {
        st.x = 1.0 - st.x;
        st.x *= 0.5;
        st.xy += uvOffset.yx;
    }
    
    st.y = st.y * _THETA_S_Y_SCALE;
    f_color = vec4(texture(textureObj, st).rgb, 1.0);
}