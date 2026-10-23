#include <assert.h>
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef unsigned int GLenum;
typedef unsigned int GLuint;
typedef int GLint;
typedef int GLsizei;
typedef unsigned char GLboolean;
typedef float GLfloat;

#define GL_NO_ERROR 0U
#define GL_FRAMEBUFFER_BINDING 0x8ca6U
#define GL_STENCIL_BITS 0x0d57U
#define GL_FRAGMENT_SHADER 0x8b30U
#define GL_VERTEX_SHADER 0x8b31U
#define GL_COMPILE_STATUS 0x8b81U
#define GL_LINK_STATUS 0x8b82U
#define GL_TEXTURE_2D 0x0de1U
#define GL_RGBA 0x1908U
#define GL_UNSIGNED_BYTE 0x1401U
#define GL_TEXTURE_MIN_FILTER 0x2801U
#define GL_TEXTURE_MAG_FILTER 0x2800U
#define GL_NEAREST 0x2600U
#define GL_RENDERBUFFER 0x8d41U
#define GL_FRAMEBUFFER 0x8d40U
#define GL_COLOR_ATTACHMENT0 0x8ce0U
#define GL_DEPTH_ATTACHMENT 0x8d00U
#define GL_STENCIL_ATTACHMENT 0x8d20U
#define GL_FRAMEBUFFER_COMPLETE 0x8cd5U
#define GL_SCISSOR_TEST 0x0c11U
#define GL_BLEND 0x0be2U
#define GL_DEPTH_TEST 0x0b71U
#define GL_COLOR_BUFFER_BIT 0x00004000U
#define GL_STENCIL_BUFFER_BIT 0x00000400U
#define GL_STENCIL_TEST 0x0b90U
#define GL_ALWAYS 0x0207U
#define GL_EQUAL 0x0202U
#define GL_KEEP 0x1e00U
#define GL_REPLACE 0x1e01U
#define GL_FLOAT 0x1406U
#define GL_FALSE 0U
#define GL_TRIANGLE_STRIP 0x0005U

static GLenum mock_error, mock_texture_setup_error, mock_texture_storage_error;
static GLenum mock_renderbuffer_setup_error, mock_renderbuffer_storage_error;
static unsigned texture_calls, renderbuffer_calls;
static struct {unsigned valid;} nvn_render_state;
static uint64_t nvn_gl_share_group_id(void) { return 42; }

static GLenum glGetError(void) { GLenum e=mock_error;mock_error=GL_NO_ERROR;return e; }
static GLuint glCreateProgram(void) { return 1; }
static GLuint glCreateShader(GLenum type) { return type==GL_VERTEX_SHADER?2U:3U; }
static void glGetShaderiv(GLuint shader,GLenum pname,GLint *value) { (void)shader;(void)pname;*value=1; }
static void glGetProgramiv(GLuint program,GLenum pname,GLint *value) { (void)program;(void)pname;*value=1; }
static GLint glGetUniformLocation(GLuint program,const char *name) { (void)program;(void)name;return 0; }
static void glGetIntegerv(GLenum pname,GLint *value) { *value=pname==GL_STENCIL_BITS?8:0; }
static void glGenTextures(GLsizei n,GLuint *names) { for(GLsizei i=0;i<n;i++)names[i]=11U+(GLuint)i; }
static void glBindTexture(GLenum target,GLuint name) { (void)target;(void)name;mock_error=mock_texture_setup_error; }
static void glTexImage2D(GLenum target,GLint level,GLint internal,GLsizei width,GLsizei height,GLint border,GLenum format,GLenum type,const void *pixels) {
    (void)target;(void)level;(void)internal;(void)width;(void)height;(void)border;(void)format;(void)type;(void)pixels;
    texture_calls++;mock_error=mock_texture_storage_error;
}
static void glGenRenderbuffers(GLsizei n,GLuint *names) { for(GLsizei i=0;i<n;i++)names[i]=21U+(GLuint)i; }
static void glBindRenderbuffer(GLenum target,GLuint name) { (void)target;(void)name;mock_error=mock_renderbuffer_setup_error; }
static void glRenderbufferStorage(GLenum target,GLenum internal,GLsizei width,GLsizei height) {
    (void)target;(void)internal;(void)width;(void)height;renderbuffer_calls++;mock_error=mock_renderbuffer_storage_error;
}
static void glGenFramebuffers(GLsizei n,GLuint *names) { for(GLsizei i=0;i<n;i++)names[i]=31U+(GLuint)i; }
static GLenum glCheckFramebufferStatus(GLenum target) { (void)target;return GL_FRAMEBUFFER_COMPLETE; }

#define glShaderSource(...) ((void)0)
#define glCompileShader(...) ((void)0)
#define glAttachShader(...) ((void)0)
#define glBindAttribLocation(...) ((void)0)
#define glLinkProgram(...) ((void)0)
#define glDetachShader(...) ((void)0)
#define glDeleteShader(...) ((void)0)
#define glDeleteProgram(...) ((void)0)
#define glTexParameteri(...) ((void)0)
#define glBindFramebuffer(...) ((void)0)
#define glFramebufferTexture2D(...) ((void)0)
#define glFramebufferRenderbuffer(...) ((void)0)
#define glViewport(...) ((void)0)
#define glDisable(...) ((void)0)
#define glClearColor(...) ((void)0)
#define glClearStencil(...) ((void)0)
#define glClear(...) ((void)0)
#define glUseProgram(...) ((void)0)
#define glEnableVertexAttribArray(...) ((void)0)
#define glEnable(...) ((void)0)
#define glStencilFunc(...) ((void)0)
#define glStencilMask(...) ((void)0)
#define glStencilOp(...) ((void)0)
#define glColorMask(...) ((void)0)
#define glVertexAttribPointer(...) ((void)0)
#define glUniform4f(...) ((void)0)
#define glDrawArrays(...) ((void)0)
#define glReadPixels(...) ((void)0)
#define glDisableVertexAttribArray(...) ((void)0)
#define glDeleteFramebuffers(...) ((void)0)
#define glDeleteRenderbuffers(...) ((void)0)
#define glDeleteTextures(...) ((void)0)

#include "momo_stencil_bench.h"

int main(void) {
    const char *value=getenv("MOCK_TEXTURE_SETUP_ERROR");if(value)mock_texture_setup_error=(GLenum)strtoul(value,NULL,0);
    value=getenv("MOCK_TEXTURE_STORAGE_ERROR");if(value)mock_texture_storage_error=(GLenum)strtoul(value,NULL,0);
    value=getenv("MOCK_RENDERBUFFER_SETUP_ERROR");if(value)mock_renderbuffer_setup_error=(GLenum)strtoul(value,NULL,0);
    value=getenv("MOCK_RENDERBUFFER_STORAGE_ERROR");if(value)mock_renderbuffer_storage_error=(GLenum)strtoul(value,NULL,0);
    momo_stencil_selftest();
    printf("MOCK_STORAGE_CALLS texture=%u renderbuffer=%u\n",texture_calls,renderbuffer_calls);
    return 0;
}
