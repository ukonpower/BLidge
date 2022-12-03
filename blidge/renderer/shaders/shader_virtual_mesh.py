vertex_shader = '''
	uniform mat4 modelViewMatrix;
    uniform mat4 projectionMatrix;
	uniform mat3 normalMatrix;

    in vec3 position;
	in vec3 normal;
	in vec2 uv;

	out vec3 vColor;
	out vec3 vNormal;

    void main()
    {
		vec4 mvPosition = modelViewMatrix * vec4( position, 1.0 );
        gl_Position = projectionMatrix * mvPosition;

		vColor = vec3( uv, 1.0 );
		vNormal = normalize( normalMatrix * normal );
    }
'''

fragment_shader = '''

	in vec3 vColor;
	in vec3 vNormal;

    out vec4 FragColor;

    void main()
    {
        FragColor = vec4(pow(vColor, vec3(2.0)), 1.0);
    }
'''