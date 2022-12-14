vertex_shader = '''
	uniform mat4 modelViewMatrix;
    uniform mat4 projectionMatrix;

    in vec3 position;
	in vec2 uv;

	out vec3 vColor;

    void main()
    {
		vec4 mvPosition = modelViewMatrix * vec4( position, 1.0 );
        gl_Position = projectionMatrix * mvPosition;

		vColor = vec3( uv, 1.0 );
    }
'''

fragment_shader = '''
    uniform float color;

	in vec3 vColor;

    out vec4 FragColor;

    void main()
    {
        FragColor = vec4(pow(vColor * color, vec3(2.0)), 1.0);
    }
'''