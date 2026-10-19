#version 450

layout(set = 0, binding = 0) uniform sampler2D fs_tex0_20;

layout(location = 0) in vec4 in_attr0;
layout(location = 0) out vec4 frag_color0;

void main()
{
    uvec4 _41 = uvec4(uvec2(textureSize(fs_tex0_20, int(0u))), 0u, uint(textureQueryLevels(fs_tex0_20)));
    float _51 = float(int(_41.x)) * in_attr0.x;
    float _52 = float(int(_41.y)) * in_attr0.y;
    uint _60 = isnan(_51) ? 0u : uint(int(clamp(trunc(_51), -2147483648.0, 2147483648.0)));
    uint _65 = isnan(_52) ? 0u : uint(int(clamp(trunc(_52), -2147483648.0, 2147483648.0)));
    vec4 _69 = texelFetch(fs_tex0_20, ivec2(uvec2(_60, _65)), int(0u), 1u);
    vec4 _77 = texelFetch(fs_tex0_20, ivec2(uvec2(_60, _65)), int(0u), 0u);
    frag_color0.x = (_69.x + _77.x) * 0.5;
    frag_color0.y = (_69.y + _77.y) * 0.5;
    frag_color0.z = (_69.z + _77.z) * 0.5;
    frag_color0.w = (_69.w + _77.w) * 0.5;
}

