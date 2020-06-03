#version 120

varying vec2 fTexcoords;
uniform sampler2D textureObj;

/*
void main()
{
	vec2 pos = vec2(0.5, 0.5);
float dist = pow(pow(fTexcoords.x - pos.x, 2) + pow(fTexcoords.y - pos.y, 2), 0.5);
float x = 0.6 * dist 

    gl_FragColor = texture2D(textureObj, pos);
}
*/

#ifdef GL_ES
precision mediump float;
precision mediump int;
#endif



void main(void)
{
	vec2 p = fTexcoords.xy;
	float pixelSize = 1.0 / float(8);
	
	float dx = mod(p.x, pixelSize) - pixelSize*0.5;
	float dy = mod(p.y, pixelSize) - pixelSize*0.5;
	
	p.x -= dx;
	p.y -= dy;
	vec3 col = texture2D(textureObj, p).rgb;
	float bright = 0.3333*(col.r+col.g+col.b);
	
	float dist = sqrt(dx*dx + dy*dy);
	float rad = bright * pixelSize * 0.8;
	float m = step(dist, rad);

	vec3 col2 = mix(vec3(0.0), vec3(1.0), m);
	gl_FragColor = vec4(col2, 1.0);
}

