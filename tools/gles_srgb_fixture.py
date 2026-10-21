#!/usr/bin/env python3
"""Self-authored EGL/GLES fixture for the decoded sRGB upload contract.

No game data, no window, no swap: an 8x8 pbuffer surface, an 8x8 RGBA ramp
uploaded in three-row stripes (so the final stripe is partial), a fullscreen
sampling pass drawn into the default framebuffer and byte readbacks.

What it proves on the real driver, and what it does not:
  * the legal ES2 triple (internal 0x8C42 from GL_EXT_sRGB, client GL_RGBA,
    GL_UNSIGNED_BYTE) allocates, uploads every stripe and samples as sRGB;
  * the legal ES3 triple (0x8C43 / GL_RGBA / GL_UNSIGNED_BYTE) does the same;
  * the retired defect triple (0x8C42 passed as the client format as well) is
    reported as illegal by this driver, or recorded as accepted-but-lenient;
  * an identical byte ramp in a linear texture samples measurably differently,
    so "sRGB storage really decodes" is a measurement, not a claim;
  * a second mip level stores exactly the uploaded bytes, and the same upload
    and sample still work after the context is destroyed and recreated.

It says nothing about game frames, id295, residency or FPS.
"""
import ctypes as C
import json
import os
import sys

RGBA, UBYTE = 0x1908, 0x1401
SRGBA_EXT, SRGB8_A8, RGBA8 = 0x8C42, 0x8C43, 0x8058
LINEAR = 0x2600
SIDE, STRIPE = 8, 3
PIXEL = (SIDE * SIDE + 1) // 2  # one probe texel: centre of texel (4,4)


def srgb_to_linear(value):
    v = value / 255.0
    return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4


def ramp_rgba(size):
    out = bytearray()
    for y in range(size):
        for x in range(size):
            for channel in (0, 1, 2):
                out.append((x * 32 + y * 4 + x * y + channel * 11) & 0xFF)
            out.append(255 - x * 16)
    return bytes(out)


def mip_pattern(size):
    return bytes((x * 3 + y * 5) & 0xFF for y in range(size) for x in range(size) for _ in range(4))


class Gles:
    def __init__(self, egl, gl, major):
        self.egl, self.gl, self.major = egl, gl, major
        self.display = self.surface = self.context = None
        self.fd = self.gbm = None

    def f(self, lib, name, restype, *args):
        fn = getattr(lib, name)
        fn.restype, fn.argtypes = restype, list(args)
        return fn

    def open(self):
        I, U, P = C.c_int, C.c_uint, C.c_void_p
        egl = self.egl
        # EGL_DEFAULT_DISPLAY does not initialise on this GBM/Mali stack even
        # though game GLES works, so the fixture asks for the DRM device
        # explicitly and uses a surfaceless context (no scanout, no modeset).
        gbm = C.CDLL('libgbm.so.1')
        create_device = self.f(gbm, 'gbm_create_device', P, I)
        self.fd = os.open('/dev/dri/card0', os.O_RDWR)
        self.gbm = create_device(self.fd)
        assert self.gbm, 'gbm_create_device failed'
        address = self.f(egl, 'eglGetProcAddress', P, C.c_char_p)(b'eglGetPlatformDisplayEXT')
        assert address, 'EGL_EXT_platform_base unavailable'
        platform_display = C.CFUNCTYPE(P, U, P, C.POINTER(I))(address)
        self.display = platform_display(0x31D7, self.gbm, None)
        major, minor = I(), I()
        assert self.display and self.f(egl, 'eglInitialize', U, P, C.POINTER(I), C.POINTER(I))(
            self.display, C.byref(major), C.byref(minor)), 'eglInitialize failed'
        assert self.f(egl, 'eglBindAPI', U, U)(0x30A0), 'eglBindAPI(ES) failed'
        extensions = (self.f(egl, 'eglQueryString', C.c_char_p, P, I)(self.display, 0x3055) or b'').decode().split()
        assert 'EGL_KHR_surfaceless_context' in extensions or (major.value, minor.value) >= (1, 5), \
            'no surfaceless EGL context'
        config = self.config()
        self.context = self.f(egl, 'eglCreateContext', P, P, P, P, C.POINTER(I))(
            self.display, config, None, (I * 3)(0x3098, self.major, 0x3038))
        assert self.context, 'context creation failed'
        assert self.current(), 'make current failed'
        self.bind()
        self.version = self.string(0x1F02)
        self.renderer = self.string(0x1F01)
        self.extensions = (self.string(0x1F03) or '').split()

    def config(self):
        I, U, P = C.c_int, C.c_uint, C.c_void_p
        config, count = P(), I()
        attrs = (I * 13)(0x3033, 0, 0x3040, 0x40, 0x3024, 8, 0x3023, 8,
                         0x3022, 8, 0x3021, 8, 0x3038)
        assert self.f(self.egl, 'eglChooseConfig', U, P, C.POINTER(I), C.POINTER(P), I,
                      C.POINTER(I))(self.display, attrs, C.byref(config), 1, C.byref(count)), 'no ES3 config'
        assert count.value, 'empty config list'
        return config

    def current(self):
        return self.f(self.egl, 'eglMakeCurrent', C.c_uint, C.c_void_p, C.c_void_p,
                      C.c_void_p, C.c_void_p)(self.display, None, None, self.context)

    def bind(self):
        I, U, P = C.c_int, C.c_uint, C.c_void_p
        gl = self.gl
        self.gen_textures = self.f(gl, 'glGenTextures', None, I, C.POINTER(U))
        self.gen_buffers = self.f(gl, 'glGenBuffers', None, I, C.POINTER(U))
        self.bind_buffer = self.f(gl, 'glBindBuffer', None, U, U)
        self.buffer_data = self.f(gl, 'glBufferData', None, U, C.c_ssize_t, P, U)
        self.enable_attrib = self.f(gl, 'glEnableVertexAttribArray', None, U)
        self.attrib_pointer = self.f(gl, 'glVertexAttribPointer', None, U, I, U, C.c_ubyte, I, P)
        self.bind_attrib = self.f(gl, 'glBindAttribLocation', None, U, U, C.c_char_p)
        self.bind_texture = self.f(gl, 'glBindTexture', None, U, U)
        self.tex_image = self.f(gl, 'glTexImage2D', None, U, I, I, I, I, I, U, U, P)
        self.tex_sub = self.f(gl, 'glTexSubImage2D', None, U, I, I, I, I, I, U, U, P)
        self.param = self.f(gl, 'glTexParameteri', None, U, U, I)
        self.pixel_store = self.f(gl, 'glPixelStorei', None, U, I)
        self.get_error = self.f(gl, 'glGetError', U)
        self.get_string = self.f(gl, 'glGetString', C.c_char_p, U)
        self.gen_fbo = self.f(gl, 'glGenFramebuffers', None, I, C.POINTER(U))
        self.bind_fbo = self.f(gl, 'glBindFramebuffer', None, U, U)
        self.fbo_texture = self.f(gl, 'glFramebufferTexture2D', None, U, U, U, U, I)
        self.fbo_status = self.f(gl, 'glCheckFramebufferStatus', U, U)
        self.viewport = self.f(gl, 'glViewport', None, I, I, I, I)
        self.draw = self.f(gl, 'glDrawArrays', None, U, I, I)
        self.read = self.f(gl, 'glReadPixels', None, I, I, I, I, U, U, P)
        self.create_shader = self.f(gl, 'glCreateShader', U, U)
        self.shader_source = self.f(gl, 'glShaderSource', None, U, I, C.POINTER(C.c_char_p), C.POINTER(I))
        self.compile = self.f(gl, 'glCompileShader', None, U)
        self.shader_iv = self.f(gl, 'glGetShaderiv', None, U, U, C.POINTER(I))
        self.shader_log = self.f(gl, 'glGetShaderInfoLog', None, U, I, C.POINTER(I), C.c_void_p)
        self.create_program = self.f(gl, 'glCreateProgram', U)
        self.attach = self.f(gl, 'glAttachShader', None, U, U)
        self.link = self.f(gl, 'glLinkProgram', None, U)
        self.program_iv = self.f(gl, 'glGetProgramiv', None, U, U, C.POINTER(I))
        self.use = self.f(gl, 'glUseProgram', None, U)
        self.location = self.f(gl, 'glGetUniformLocation', I, U, C.c_char_p)
        self.uniform = self.f(gl, 'glUniform1i', None, I, I)
        self.delete_textures = self.f(gl, 'glDeleteTextures', None, I, C.POINTER(U))

    def string(self, name):
        value = self.get_string(name)
        return value.decode() if value else None

    def error(self, step, errors):
        code = self.get_error()
        if code:
            errors.append({'step': step, 'error': hex(code)})
        return code

    def program(self):
        I = C.c_int
        source_v = ('#version 100\nattribute vec2 p;varying vec2 uv;'
                    'void main(){uv=p*0.5+0.5;gl_Position=vec4(p,0.0,1.0);}')
        source_f = ('#version 100\nprecision highp float;varying vec2 uv;uniform sampler2D t;'
                    'void main(){gl_FragColor=texture2D(t,uv);}')
        shaders = []
        for stage, text in ((0x8B31, source_v), (0x8B30, source_f)):
            shader = self.create_shader(stage)
            encoded = text.encode()
            self.shader_source(shader, 1, (C.c_char_p * 1)(encoded), None)
            self.compile(shader)
            ok = I()
            self.shader_iv(shader, 0x8B81, C.byref(ok))
            if not ok.value:
                log = C.create_string_buffer(4096)
                self.shader_log(shader, 4096, None, log)
                raise RuntimeError('shader: ' + log.value.decode())
            shaders.append(shader)
        program = self.create_program()
        self.bind_attrib(program, 0, b'p')
        for shader in shaders:
            self.attach(program, shader)
        self.link(program)
        ok = I()
        self.program_iv(program, 0x8B82, C.byref(ok))
        assert ok.value, 'link failed'
        return program

    def texture(self, internal, external, data, level1=None):
        """Stripe upload of the base level; an optional second mip."""
        handle = C.c_uint()
        self.gen_textures(1, C.byref(handle))
        self.bind_texture(0x0DE1, handle.value)
        self.pixel_store(0x0CF5, 1)  # GL_UNPACK_ALIGNMENT
        self.tex_image(0x0DE1, 0, internal, SIDE, SIDE, 0, external, UBYTE, None)
        for y in range(0, SIDE, STRIPE):
            rows = min(STRIPE, SIDE - y)
            self.tex_sub(0x0DE1, 0, 0, y, SIDE, rows, external, UBYTE,
                         data[y * SIDE * 4:(y + rows) * SIDE * 4])
        if level1 is not None:
            self.tex_image(0x0DE1, 1, internal, SIDE // 2, SIDE // 2, 0, external, UBYTE, level1)
        self.param(0x0DE1, 0x2800, LINEAR)
        self.param(0x0DE1, 0x2801, LINEAR)
        self.param(0x0DE1, 0x2802, 0x812F)
        self.param(0x0DE1, 0x2803, 0x812F)
        return handle.value

    def sample(self, program, texture):
        """Draw one fullscreen triangle into an RGBA8 FBO and read it back.

        A surfaceless context has no default framebuffer, and an ES2 sRGB
        texture is not guaranteed colour-renderable, so the target is a plain
        linear RGBA8 image the fixture owns.
        """
        self.bind_texture(0x0DE1, texture)
        self.use(program)
        self.param(0x0DE1, 0x2801, LINEAR)
        # Explicit geometry: an attribute with no array reads (0,0) and the
        # triangle degenerates to nothing while every GL call stays clean.
        buffer = C.c_uint()
        self.gen_buffers(1, C.byref(buffer))
        self.bind_buffer(0x8892, buffer.value)  # GL_ARRAY_BUFFER
        vertices = (C.c_float * 6)(-1.0, -1.0, 3.0, -1.0, -1.0, 3.0)
        self.buffer_data(0x8892, C.sizeof(vertices), vertices, 0x88E4)  # GL_STATIC_DRAW
        self.enable_attrib(0)
        self.attrib_pointer(0, 2, 0x1406, 0, 0, None)
        self.bind_buffer(0x8892, 0)
        target = C.c_uint()
        self.gen_textures(1, C.byref(target))
        self.bind_texture(0x0DE1, target.value)
        self.tex_image(0x0DE1, 0, RGBA8 if self.major >= 3 else RGBA, SIDE, SIDE, 0,
                       RGBA, UBYTE, None)
        self.bind_texture(0x0DE1, texture)
        fbo = C.c_uint()
        self.gen_fbo(1, C.byref(fbo))
        self.bind_fbo(0x8D40, fbo.value)
        self.fbo_texture(0x8D40, 0x8CE0, 0x0DE1, target.value, 0)
        assert self.fbo_status(0x8D40) == 0x8CD5, 'RGBA8 output FBO incomplete'
        self.uniform(self.location(program, b't'), 0)
        self.viewport(0, 0, SIDE, SIDE)
        self.draw(4, 0, 3)
        out = (C.c_ubyte * (SIDE * SIDE * 4))()
        self.read(0, 0, SIDE, SIDE, RGBA, UBYTE, out)
        self.bind_fbo(0x8D40, 0)
        self.enable_attrib(0)
        self.delete_textures(1, C.byref(target))
        self.f(self.gl, 'glDeleteBuffers', None, C.c_int, C.POINTER(C.c_uint))(1, C.byref(buffer))
        return bytes(out)

    def read_level(self, texture, level, size):
        fbo = C.c_uint()
        self.gen_fbo(1, C.byref(fbo))
        self.bind_fbo(0x8D40, fbo.value)
        self.fbo_texture(0x8D40, 0x8CE0, 0x0DE1, texture, level)
        complete = self.fbo_status(0x8D40)
        out = (C.c_ubyte * (size * size * 4))()
        self.read(0, 0, size, size, RGBA, UBYTE, out)
        self.bind_fbo(0x8D40, 0)
        return complete, bytes(out)


def probe(sampled):
    index = (4 * SIDE + 4) * 4
    return sampled[index]


def scenario(major):
    egl = C.CDLL('libEGL.so.1')
    gl = C.CDLL('libGLESv2.so.2')
    g = Gles(egl, gl, major)
    result = {'requested_major': major, 'pass': False, 'errors': [], 'checks': {}}
    try:
        g.open()
        result.update(version=g.version, renderer=g.renderer,
                      ext_srgb='GL_EXT_sRGB' in g.extensions)
        program = g.program()
        internal = SRGB8_A8 if major >= 3 else SRGBA_EXT
        data = ramp_rgba(SIDE)
        srgb = g.texture(internal, RGBA, data)
        g.error('srgb-upload', result['errors'])
        sampled = g.sample(program, srgb)
        g.error('srgb-sample', result['errors'])
        stored = data[(4 * SIDE + 4) * 4]
        got = probe(sampled)
        want = round(srgb_to_linear(stored) * 255)
        result['checks']['srgb_decode'] = {'stored': stored, 'sampled': got,
                                           'expected': want, 'delta': abs(got - want)}

        linear = g.texture(RGBA8 if major >= 3 else RGBA, RGBA, data)
        g.error('linear-upload', result['errors'])
        linear_sample = probe(g.sample(program, linear))
        result['checks']['linear_control'] = {'sampled': linear_sample, 'stored': stored}
        result['checks']['srgb_differs_from_linear'] = linear_sample != got

        bad = C.c_uint()
        g.gen_textures(1, C.byref(bad))
        g.bind_texture(0x0DE1, bad.value)
        g.tex_image(0x0DE1, 0, internal, SIDE, SIDE, 0, internal, UBYTE, None)
        code = g.get_error()
        result['checks']['defect_triple'] = {'rejected': bool(code),
                                             'gl_error': hex(code) if code else None}
        g.delete_textures(1, C.byref(bad))

        # Mip bytes are read from a LINEAR image: ES2 sRGB textures are not
        # guaranteed colour-renderable, so attaching one would prove nothing
        # about the upload path we actually use.
        pattern = mip_pattern(SIDE // 2)
        mip_tex = g.texture(RGBA8 if major >= 3 else RGBA, RGBA, data, level1=pattern)
        g.error('mip-upload', result['errors'])
        complete, read = g.read_level(mip_tex, 1, SIDE // 2)
        g.error('mip-read', result['errors'])
        result['checks']['mip_level1'] = {'fbo_complete': complete == 0x8CD5,
                                          'bytes_match': read == pattern}

        g.f(egl, 'eglMakeCurrent', C.c_uint, C.c_void_p, C.c_void_p, C.c_void_p, C.c_void_p)(
            g.display, None, None, None)
        g.f(egl, 'eglDestroyContext', C.c_uint, C.c_void_p, C.c_void_p)(g.display, g.context)
        g.context = g.f(egl, 'eglCreateContext', C.c_void_p, C.c_void_p, C.c_void_p,
                        C.c_void_p, C.POINTER(C.c_int))(
            g.display, g.config(), None, (C.c_int * 3)(0x3098, major, 0x3038))
        assert g.context and g.current(), 'context recreation failed'
        g.bind()
        program = g.program()
        again_texture = g.texture(internal, RGBA, data)
        g.error('recreated-upload', result['errors'])
        again = probe(g.sample(program, again_texture))
        g.error('recreated-sample', result['errors'])
        result['checks']['context_recreation'] = {'sampled': again, 'matches_first': again == got}
        result['pass'] = (not result['errors']
                          and result['checks']['srgb_decode']['delta'] <= 3
                          and result['checks']['srgb_differs_from_linear']
                          and result['checks']['mip_level1']['bytes_match']
                          and result['checks']['context_recreation']['matches_first'])
    except Exception as error:  # keep a receipt even when the fixture cannot run
        result['exception'] = '%s: %s' % (type(error).__name__, error)
    finally:
        try:
            if g.context:
                g.f(egl, 'eglMakeCurrent', C.c_uint, C.c_void_p, C.c_void_p, C.c_void_p, C.c_void_p)(
                    g.display, None, None, None)
                g.f(egl, 'eglDestroyContext', C.c_uint, C.c_void_p, C.c_void_p)(g.display, g.context)
            if g.surface:
                g.f(egl, 'eglDestroySurface', C.c_uint, C.c_void_p, C.c_void_p)(g.display, g.surface)
            if g.display:
                g.f(egl, 'eglTerminate', C.c_uint, C.c_void_p)(g.display)
            if g.gbm:
                g.f(C.CDLL('libgbm.so.1'), 'gbm_device_destroy', None, C.c_void_p)(g.gbm)
            if g.fd is not None:
                os.close(g.fd)
        except Exception:
            pass
    return result


if __name__ == '__main__':
    results = {'scope': 'self-authored offscreen sRGB upload fixture; not a game frame, '
                        'not id295 residency and not an FPS result'}
    for major in (2, 3):
        results['es%d' % major] = scenario(major)
    results['pass'] = all(results['es%d' % m].get('pass') for m in (2, 3))
    print(json.dumps(results, indent=2))
    sys.exit(0 if results['pass'] else 1)
