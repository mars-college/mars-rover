#version 330

#ifdef GL_ES
precision mediump float;
precision mediump int;
#endif

#define HALF_PI 1.57079632679489
#define PI 3.14159265358979
#define TWO_PI 6.28318530717958
#define _THETA_S_Y_SCALE (640.0/720.0)

uniform sampler2D camTex1;
uniform sampler2D camTex2;
in vec2 pos;
out vec4 f_color;

// field of view of the fisheye
uniform float FOV;  
uniform vec2 cam1_radius;
uniform vec2 cam2_radius;
uniform vec2 cam1_margin;
uniform vec2 cam2_margin;

// rotation parameters
uniform float yaw;
uniform float pitch;
uniform float roll;


void main() {

    // pos is desired point in equirectangular plane
    // map each fisheye to uv [0.25, 0.75] 
    vec2 uv = pos.xy;
    if (pos.x > 0.5) {
        uv.x = 0.25 + (pos.x - 0.5); 
    } else {
        uv.x = 0.25 + pos.x; 
    }

    // longitude, -pi to pi
    // latitude, -pi/2 to pi/2
    float lng = TWO_PI * (uv.x - 0.5);  
 	float lat = PI * (uv.y - 0.5);	      

    // convert to ray in 3d space
    vec3 P = vec3(
        cos(lat) * sin(lng),
	    cos(lat) * cos(lng),  
	    sin(lat) 
    );

    // rotate P 
    float p = pitch;
    float r = roll;
    float y = yaw;
    if (pos.x >= 0.5) {
        r *= -1.0;
        p *= -1.0;
    }

    mat3 rot = mat3( cos(y)*cos(p),   cos(y)*sin(p)*sin(r) - sin(y)*cos(r),  cos(y)*sin(p)*cos(r) + sin(y)*sin(r), 
                     sin(y)*cos(p),   sin(y)*sin(p)*sin(r) + cos(y)*cos(r),  sin(y)*sin(p)*cos(r) - cos(y)*sin(r), 
                    -sin(p),          cos(p)*sin(r),                         cos(p)*cos(r) );

    vec3 P_rot = rot * P;

    // derive latitude and longitude of rotated point
    float lat2 = acos(P_rot.z);
    float lng2 = atan(P_rot.y, -P_rot.x);

    // re-map to equirectangular    
    vec2 pos_rot = vec2((lng2+PI)/TWO_PI, lat2/PI);
    
    // re-map new pos_rot to uv again
    uv = pos_rot.xy;
    if (pos_rot.x > 0.5) {
        uv.x = 0.25 + (pos_rot.x - 0.5); 
    } else {
        uv.x = 0.25 + pos_rot.x; 
    }

    // get latitude and longitude in equirectangular plane again
    lng = 2.0 * PI * (uv.x - 0.5);  
    lat = PI * (uv.y - 0.5);

    // convert to ray in 3d space again
    P = vec3(
        cos(lat) * sin(lng),
	    cos(lat) * cos(lng),  
	    sin(lat) 
    );

    // convert to fisheye space
    float theta = atan(P.z, P.x);
    float phi = atan(sqrt(P.x*P.x + P.z*P.z), P.y);
    
    //if (pos.x > 0.5) {
    if ((pos.x>0.5 && lng2>0) || (pos.x<0.5 && lng2<=0)) {
            
        float radius_x = cam2_radius.x * phi / FOV;
        float radius_y = cam2_radius.y * phi / FOV;

        // Pixel in fisheye space
        vec2 pfish = vec2(
            0.5 + radius_x * cos(theta),
            0.5 + radius_y * sin(theta)
        );

        pfish.x = cam2_margin.s + (1.0 - cam2_margin.s - cam2_margin.t) * (1.0 - pfish.x);
        f_color = vec4(texture(camTex2, pfish).rgb, 1.0);
    
    } 
    else {
        
        float radius_x = cam1_radius.x * phi / FOV;
        float radius_y = cam1_radius.y * phi / FOV;

        // Pixel in fisheye space
        vec2 pfish = vec2(
            0.5 + radius_x * cos(theta),
            0.5 + radius_y * sin(theta)
        );

        pfish.x = cam1_margin.s + (1.0 - cam1_margin.s - cam1_margin.t) * (1.0 - pfish.x);
        f_color = vec4(texture(camTex1, pfish).rgb, 1.0);
    }

}
