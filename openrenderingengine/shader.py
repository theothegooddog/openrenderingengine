from OpenGL import GL


class Shader:
    _bound_id = 0

    def __init__(self, vertex_shader_path, fragment_shader_path):
        with open(vertex_shader_path) as f:
            vertex_source = f.read()
        with open(fragment_shader_path) as f:
            fragment_source = f.read()

        vertex_shader = self._compile(GL.GL_VERTEX_SHADER, vertex_source, vertex_shader_path)
        fragment_shader = self._compile(GL.GL_FRAGMENT_SHADER, fragment_source, fragment_shader_path)

        self._id = GL.glCreateProgram()
        GL.glAttachShader(self._id, vertex_shader)
        GL.glAttachShader(self._id, fragment_shader)
        GL.glLinkProgram(self._id)
        if not GL.glGetProgramiv(self._id, GL.GL_LINK_STATUS):
            raise RuntimeError("Shader link failed: " + GL.glGetProgramInfoLog(self._id).decode())

        GL.glDeleteShader(vertex_shader)
        GL.glDeleteShader(fragment_shader)

        self._uniform_cache = {}
        self.bind()

    @staticmethod
    def _compile(kind, source, path):
        shader = GL.glCreateShader(kind)
        GL.glShaderSource(shader, source)
        GL.glCompileShader(shader)
        if not GL.glGetShaderiv(shader, GL.GL_COMPILE_STATUS):
            raise RuntimeError(f"Shader compile failed ({path}): " + GL.glGetShaderInfoLog(shader).decode())
        return shader

    def delete(self):
        GL.glDeleteProgram(self._id)

    def bind(self):
        if Shader._bound_id != self._id:
            GL.glUseProgram(self._id)
            Shader._bound_id = self._id

    def unbind(self):
        GL.glUseProgram(0)
        Shader._bound_id = 0

    def get_uniform_location(self, name):
        if name not in self._uniform_cache:
            self._uniform_cache[name] = GL.glGetUniformLocation(self._id, name)
        return self._uniform_cache[name]

    def set_int(self, name, value):
        GL.glUniform1i(self.get_uniform_location(name), value)

    def set_mat4(self, name, matrix):
        # numpy matrices are row-major, so let GL transpose them
        GL.glUniformMatrix4fv(self.get_uniform_location(name), 1, GL.GL_TRUE, matrix)

    @property
    def id(self):
        return self._id
