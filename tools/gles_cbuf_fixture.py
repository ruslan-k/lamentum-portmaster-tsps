#!/usr/bin/env python3
"""Self-authored GLES3 pbuffer fixture; no game data and no window/swap.

Run only on an idle owner device. Creates/destroys its own EGL context, textures
and pbuffer; checks cbuf lane/row addressing and explicit scalar half conversion.
"""
import ctypes as C
import json
import math
import struct
import os
import sys


def main():
    egl = C.CDLL('libEGL.so.1')
    gl = C.CDLL('libGLESv2.so.2')
    I, U, P = C.c_int, C.c_uint, C.c_void_p

    def fn(lib, name, restype, *args):
        f = getattr(lib, name); f.restype = restype; f.argtypes = list(args)
        return f

    getdisplay = fn(egl, 'eglGetDisplay', P, P)
    initialize = fn(egl, 'eglInitialize', U, P, C.POINTER(I), C.POINTER(I))
    bindapi = fn(egl, 'eglBindAPI', U, U)
    choose = fn(egl, 'eglChooseConfig', U, P, C.POINTER(I), C.POINTER(P), I, C.POINTER(I))
    create_surface = fn(egl, 'eglCreatePbufferSurface', P, P, P, C.POINTER(I))
    create_context = fn(egl, 'eglCreateContext', P, P, P, P, C.POINTER(I))
    current = fn(egl, 'eglMakeCurrent', U, P, P, P, P)
    destroy_surface = fn(egl, 'eglDestroySurface', U, P, P)
    destroy_context = fn(egl, 'eglDestroyContext', U, P, P)
    terminate = fn(egl, 'eglTerminate', U, P)
    egl_string = fn(egl, 'eglQueryString', C.c_char_p, P, I)
    string = fn(gl, 'glGetString', C.c_char_p, U)
    error = fn(gl, 'glGetError', U)
    create_shader = fn(gl, 'glCreateShader', U, U)
    shader_source = fn(gl, 'glShaderSource', None, U, I, C.POINTER(C.c_char_p), C.POINTER(I))
    compile_shader = fn(gl, 'glCompileShader', None, U)
    shader_iv = fn(gl, 'glGetShaderiv', None, U, U, C.POINTER(I))
    shader_log = fn(gl, 'glGetShaderInfoLog', None, U, I, C.POINTER(I), P)
    create_program = fn(gl, 'glCreateProgram', U)
    attach = fn(gl, 'glAttachShader', None, U, U)
    link = fn(gl, 'glLinkProgram', None, U)
    program_iv = fn(gl, 'glGetProgramiv', None, U, U, C.POINTER(I))
    use = fn(gl, 'glUseProgram', None, U)
    location = fn(gl, 'glGetUniformLocation', I, U, C.c_char_p)
    uniform = fn(gl, 'glUniform1i', None, I, I)
    gen_tex = fn(gl, 'glGenTextures', None, I, C.POINTER(U))
    active = fn(gl, 'glActiveTexture', None, U)
    bind_tex = fn(gl, 'glBindTexture', None, U, U)
    parameter = fn(gl, 'glTexParameteri', None, U, U, I)
    image = fn(gl, 'glTexImage2D', None, U, I, I, I, I, I, U, U, P)
    subimage = fn(gl, 'glTexSubImage2D', None, U, I, I, I, I, I, U, U, P)
    gen_fbo = fn(gl, 'glGenFramebuffers', None, I, C.POINTER(U))
    bind_fbo = fn(gl, 'glBindFramebuffer', None, U, U)
    attach_tex = fn(gl, 'glFramebufferTexture2D', None, U, U, U, U, I)
    check_fbo = fn(gl, 'glCheckFramebufferStatus', U, U)
    viewport = fn(gl, 'glViewport', None, I, I, I, I)
    draw = fn(gl, 'glDrawArrays', None, U, I, I)
    read = fn(gl, 'glReadPixels', None, I, I, I, I, U, U, P)
    delete_tex = fn(gl, 'glDeleteTextures', None, I, C.POINTER(U))
    delete_fbo = fn(gl, 'glDeleteFramebuffers', None, I, C.POINTER(U))
    delete_program = fn(gl, 'glDeleteProgram', None, U)
    delete_shader = fn(gl, 'glDeleteShader', None, U)
    display = getdisplay(None); surface = context = None
    device_fd = None; gbm_device = None; gbm = None
    shaders = []; program = 0; textures = []; fbo = U()
    try:
        if '--gbm' in sys.argv:
            # KMSDRM uses an explicit GBM native display. No DRM master or
            # modeset/swap is requested by this offscreen-only fixture.
            gbm = C.CDLL('libgbm.so.1')
            create_device = fn(gbm, 'gbm_create_device', P, I)
            device_fd = os.open('/dev/dri/card0', os.O_RDWR)
            gbm_device = create_device(device_fd)
            assert gbm_device, 'gbm_create_device failed'
            getproc = fn(egl, 'eglGetProcAddress', P, C.c_char_p)
            address = getproc(b'eglGetPlatformDisplayEXT')
            assert address, 'EGL_EXT_platform_base unavailable'
            platform_display = C.CFUNCTYPE(P, U, P, C.POINTER(I))(address)
            display = platform_display(0x31D7, gbm_device, None)
        major, minor = I(), I()
        assert display and initialize(display, C.byref(major), C.byref(minor)), 'eglInitialize failed'
        assert bindapi(0x30A0), 'eglBindAPI ES failed'
        if '--gbm' in sys.argv:
            extensions = (egl_string(display, 0x3055) or b'').decode().split()
            assert 'EGL_KHR_surfaceless_context' in extensions or (major.value, minor.value) >= (1, 5), 'no surfaceless EGL context'
        attrs = (I * 13)(0x3033, 0 if '--gbm' in sys.argv else 1, 0x3040, 0x40, 0x3024, 8, 0x3023, 8, 0x3022, 8, 0x3021, 8, 0x3038)
        config, count = P(), I()
        assert choose(display, attrs, C.byref(config), 1, C.byref(count)) and count.value, 'no ES3 pbuffer config'
        if '--gbm' not in sys.argv:
            surface = create_surface(display, config, (I * 5)(0x3057, 1, 0x3056, 1, 0x3038))
        context = create_context(display, config, None, (I * 3)(0x3098, 3, 0x3038))
        assert (surface or '--gbm' in sys.argv) and context and current(display, surface, surface, context), 'make current failed'
        version = string(0x1F02).decode(); renderer = string(0x1F01).decode()

        def shader(stage, text):
            s = create_shader(stage); shaders.append(s)
            b = text.encode(); a = (C.c_char_p * 1)(b)
            shader_source(s, 1, a, None); compile_shader(s)
            ok = I(); shader_iv(s, 0x8B81, C.byref(ok))
            if not ok.value:
                log = C.create_string_buffer(8192); shader_log(s, 8192, None, log)
                raise RuntimeError(log.value.decode())
            return s

        vs = shader(0x8B31, '#version 310 es\nvoid main(){vec2 p=vec2(gl_VertexID==1?3.0:-1.0,gl_VertexID==2?3.0:-1.0);gl_Position=vec4(p,0,1);}')
        fs = shader(0x8B30, '''#version 310 es
precision highp float; precision highp int;
uniform highp sampler2D c; uniform int word;
layout(location=0) out highp vec4 color;
void main(){float v=texelFetch(c,ivec2((word>>2)&1023,word>>12),0)[word&3];
float h=unpackHalf2x16(packHalf2x16(vec2(1.0003,0.0))).x;color=vec4(v,h,float(word),1.0);}
''')
        program = create_program(); attach(program, vs); attach(program, fs); link(program)
        ok = I(); program_iv(program, 0x8B82, C.byref(ok)); assert ok.value, 'link failed'
        use(program); loc_c = location(program, b'c'); loc_word = location(program, b'word')
        assert loc_c >= 0 and loc_word >= 0

        def texture(unit, width, height, data):
            active(0x84C0 + unit); t = U(); gen_tex(1, C.byref(t)); textures.append(t)
            bind_tex(0x0DE1, t.value)
            for pname, value in [(0x2801, 0x2600), (0x2800, 0x2600), (0x2802, 0x812F), (0x2803, 0x812F)]:
                parameter(0x0DE1, pname, value)
            image(0x0DE1, 0, 0x8814, width, height, 0, 0x1908, 0x1406, data)
            return t

        values = [-0.125 * i for i in range(8192)]; data = (C.c_float * len(values))(*values)
        texture(7, 1024, 2, data); output = texture(0, 1, 1, None)
        gen_fbo(1, C.byref(fbo)); bind_fbo(0x8D40, fbo.value)
        attach_tex(0x8D40, 0x8CE0, 0x0DE1, output.value, 0)
        assert check_fbo(0x8D40) == 0x8CD5, 'RGBA32F FBO incomplete'
        viewport(0, 0, 1, 1); uniform(loc_c, 7); results = []

        def sample(word, expected):
            uniform(loc_word, word); draw(4, 0, 3)
            out = (C.c_float * 4)(); read(0, 0, 1, 1, 0x1908, 0x1406, out)
            err = error(); assert err == 0, hex(err)
            want = [expected, struct.unpack('<e', struct.pack('<e', 1.0003))[0], float(word), 1.0]
            assert all(math.isclose(x, y, rel_tol=0, abs_tol=1e-6) for x, y in zip(out, want)), (word, list(out), want)
            results.append({'word': word, 'observed': list(out), 'expected': want})

        for word in [0, 1, 3, 4, 4095, 4096, 4097, 8191]:
            sample(word, values[word])
        active(0x84C0 + 7); changed = (C.c_float * 4)(-3.5, -4.5, -5.5, -6.5)
        subimage(0x0DE1, 0, 0, 0, 1, 1, 0x1908, 0x1406, changed); sample(0, -3.5)
        texture(8, 1024, 2, data); uniform(loc_c, 8); sample(0, 0.0)
        print(json.dumps({'pass': True, 'renderer': renderer, 'version': version, 'samples': results,
                          'scope': 'self-authored pbuffer, not game-frame correctness or production resource-lifetime proof'}))
    finally:
        if context:
            if fbo.value: delete_fbo(1, C.byref(fbo))
            for t in textures: delete_tex(1, C.byref(t))
            if program: delete_program(program)
            for s in shaders: delete_shader(s)
        if display:
            current(display, None, None, None)
            if context: destroy_context(display, context)
            if surface: destroy_surface(display, surface)
            terminate(display)
        if gbm_device:
            fn(gbm, 'gbm_device_destroy', None, P)(gbm_device)
        if device_fd is not None:
            os.close(device_fd)


if __name__ == '__main__':
    main()
