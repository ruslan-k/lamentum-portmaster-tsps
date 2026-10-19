#version 450
#extension GL_EXT_scalar_block_layout : require
#extension GL_ARB_shader_draw_parameters : require

layout(set = 0, binding = 0, scalar) uniform vs_cbuf_block_0u
{
    uint data[16384];
} c0;

layout(set = 0, binding = 1, scalar) uniform c1
{
    uint data[16384];
} c1_1;

layout(set = 0, binding = 2, scalar) uniform c3
{
    uint data[16384];
} c3_1;

layout(set = 0, binding = 0, scalar) uniform vs_cbuf_block_0f
{
    float data[16384];
} c0_1;

layout(set = 0, binding = 1, scalar) uniform c1_2
{
    float data[16384];
} c1_3;

layout(set = 0, binding = 2, scalar) uniform c3_2
{
    float data[16384];
} c3_3;

layout(set = 0, binding = 3, std430) buffer ssbo0
{
    uint _m0[];
} ssbo0_1;

layout(location = 0) in vec4 in_attr0;
layout(location = 1) in vec4 in_attr1;
layout(location = 2) in vec4 in_attr2;
layout(location = 3) in vec4 in_attr3;
layout(location = 1) out vec4 out_attr1;
layout(location = 3) out vec4 out_attr3;

void main()
{
    gl_Position = vec4(0.0, 0.0, 0.0, 1.0);
    out_attr1 = vec4(0.0, 0.0, 0.0, 1.0);
    out_attr3 = vec4(0.0, 0.0, 0.0, 1.0);
    bool _79 = !(0.0 == c3_3.data[6u]);
    uint _86 = (uint(gl_InstanceIndex) - uint(gl_BaseInstanceARB)) + c3_1.data[24u];
    uint _88 = _86 * 56u;
    uint _114 = uint(max(int((_88 + c0.data[68u]) - (c0.data[68u] & 4294967295u)), int(0u))) >> 2u;
    uint _129 = uint(max(int(((_88 + 16u) + c0.data[68u]) - (c0.data[68u] & 4294967295u)), int(0u))) >> 2u;
    uint _140 = uint(max(int(((_88 + 28u) + c0.data[68u]) - (c0.data[68u] & 4294967295u)), int(0u))) >> 2u;
    uint _151 = uint(max(int(((_88 + 4u) + c0.data[68u]) - (c0.data[68u] & 4294967295u)), int(0u))) >> 2u;
    uint _162 = uint(max(int(((_88 + 20u) + c0.data[68u]) - (c0.data[68u] & 4294967295u)), int(0u))) >> 2u;
    uint _173 = uint(max(int(((_88 + 32u) + c0.data[68u]) - (c0.data[68u] & 4294967295u)), int(0u))) >> 2u;
    uint _187 = uint(max(int(((_88 + 8u) + c0.data[68u]) - (c0.data[68u] & 4294967295u)), int(0u))) >> 2u;
    uint _198 = uint(max(int(((_88 + 12u) + c0.data[68u]) - (c0.data[68u] & 4294967295u)), int(0u))) >> 2u;
    uint _206 = uint(max(int(((_88 + 24u) + c0.data[68u]) - (c0.data[68u] & 4294967295u)), int(0u))) >> 2u;
    bool _279 = !(0.0 == c3_3.data[28u]);
    float _291 = fma(uintBitsToFloat(ssbo0_1._m0[_129]), uintBitsToFloat(ssbo0_1._m0[_173]), -(uintBitsToFloat(ssbo0_1._m0[_140]) * uintBitsToFloat(ssbo0_1._m0[_162])));
    float _300 = fma(uintBitsToFloat(ssbo0_1._m0[_140]), uintBitsToFloat(ssbo0_1._m0[_187]), -(uintBitsToFloat(ssbo0_1._m0[_151]) * uintBitsToFloat(ssbo0_1._m0[_173])));
    float _306 = fma(uintBitsToFloat(ssbo0_1._m0[_151]), uintBitsToFloat(ssbo0_1._m0[_162]), -(uintBitsToFloat(ssbo0_1._m0[_129]) * uintBitsToFloat(ssbo0_1._m0[_187])));
    float _328 = 1.0 / fma(_306, uintBitsToFloat(ssbo0_1._m0[_206]), fma(_300, uintBitsToFloat(ssbo0_1._m0[_198]), _291 * uintBitsToFloat(ssbo0_1._m0[_114])));
    float _380 = fma(uintBitsToFloat(ssbo0_1._m0[uint(max(int(((_88 + 36u) + c0.data[68u]) - (c0.data[68u] & 4294967295u)), int(0u))) >> 2u]), in_attr0.w, fma(uintBitsToFloat(ssbo0_1._m0[_206]), in_attr0.z, fma(uintBitsToFloat(ssbo0_1._m0[_198]), in_attr0.y, uintBitsToFloat(ssbo0_1._m0[_114]) * in_attr0.x)));
    float _391 = fma(uintBitsToFloat(ssbo0_1._m0[uint(max(int(((_88 + 40u) + c0.data[68u]) - (c0.data[68u] & 4294967295u)), int(0u))) >> 2u]), in_attr0.w, fma(uintBitsToFloat(ssbo0_1._m0[_140]), in_attr0.z, fma(uintBitsToFloat(ssbo0_1._m0[_129]), in_attr0.y, uintBitsToFloat(ssbo0_1._m0[_151]) * in_attr0.x)));
    float _398 = fma(_380, -c3_3.data[3u], c3_3.data[0u]);
    float _399 = fma(_306 * _328, in_attr1.z, fma(_300 * _328, in_attr1.y, (_291 * _328) * in_attr1.x));
    float _402 = fma(fma(uintBitsToFloat(ssbo0_1._m0[_187]), uintBitsToFloat(ssbo0_1._m0[_198]), -(uintBitsToFloat(ssbo0_1._m0[_162]) * uintBitsToFloat(ssbo0_1._m0[_114]))) * _328, in_attr1.z, fma(fma(uintBitsToFloat(ssbo0_1._m0[_173]), uintBitsToFloat(ssbo0_1._m0[_114]), -(uintBitsToFloat(ssbo0_1._m0[_187]) * uintBitsToFloat(ssbo0_1._m0[_206]))) * _328, in_attr1.y, (fma(uintBitsToFloat(ssbo0_1._m0[_162]), uintBitsToFloat(ssbo0_1._m0[_206]), -(uintBitsToFloat(ssbo0_1._m0[_173]) * uintBitsToFloat(ssbo0_1._m0[_198]))) * _328) * in_attr1.x));
    float _404 = fma(uintBitsToFloat(ssbo0_1._m0[uint(max(int(((_88 + 44u) + c0.data[68u]) - (c0.data[68u] & 4294967295u)), int(0u))) >> 2u]), in_attr0.w, fma(uintBitsToFloat(ssbo0_1._m0[_173]), in_attr0.z, fma(uintBitsToFloat(ssbo0_1._m0[_162]), in_attr0.y, uintBitsToFloat(ssbo0_1._m0[_187]) * in_attr0.x)));
    float _411 = fma(_391, -c3_3.data[3u], c3_3.data[1u]);
    float _414 = fma(fma(uintBitsToFloat(ssbo0_1._m0[_129]), uintBitsToFloat(ssbo0_1._m0[_114]), -(uintBitsToFloat(ssbo0_1._m0[_151]) * uintBitsToFloat(ssbo0_1._m0[_198]))) * _328, in_attr1.z, fma(fma(uintBitsToFloat(ssbo0_1._m0[_151]), uintBitsToFloat(ssbo0_1._m0[_206]), -(uintBitsToFloat(ssbo0_1._m0[_140]) * uintBitsToFloat(ssbo0_1._m0[_114]))) * _328, in_attr1.y, (fma(uintBitsToFloat(ssbo0_1._m0[_140]), uintBitsToFloat(ssbo0_1._m0[_198]), -(uintBitsToFloat(ssbo0_1._m0[_129]) * uintBitsToFloat(ssbo0_1._m0[_206]))) * _328) * in_attr1.x));
    float _420 = fma(_404, -c3_3.data[3u], c3_3.data[2u]);
    float _427 = floor(uintBitsToFloat(ssbo0_1._m0[uint(max(int(((((bitfieldExtract(_86, int(16u), int(16u)) * 56u) << 16u) + ((bitfieldExtract(_86, int(0u), int(16u)) * 56u) + 52u)) + c0.data[68u]) - (c0.data[68u] & 4294967295u)), int(0u))) >> 2u]));
    float _429 = inversesqrt(fma(_420, _420, fma(_411, _411, _398 * _398)));
    float _430 = inversesqrt(fma(_414, _414, fma(_402, _402, _399 * _399)));
    float _436 = _399 * _430;
    float _438 = _402 * _430;
    float _440 = _414 * _430;
    float _446 = fma(_420 * _429, _440, fma(_411 * _429, _438, (_398 * _429) * _436));
    float _448 = floor(_427 * (1.0 / c3_3.data[29u]));
    float _464 = sqrt(fma(_446, -_446, c1_3.data[0u])) * c3_3.data[6u];
    uint _479;
    if (!_79)
    {
        _479 = floatBitsToUint(_391);
    }
    else
    {
        _479 = floatBitsToUint(fma(_438, -_464, _391));
    }
    uint _486;
    if (!_79)
    {
        _486 = floatBitsToUint(_380);
    }
    else
    {
        _486 = floatBitsToUint(fma(_436, -_464, _380));
    }
    out_attr3.x = in_attr2.x;
    out_attr3.y = in_attr2.y;
    float _502 = floor(fma(_448, -c3_3.data[29u], _427)) * c3_3.data[30u];
    out_attr3.z = in_attr2.z;
    uint _510;
    if (!_79)
    {
        _510 = floatBitsToUint(_404);
    }
    else
    {
        _510 = floatBitsToUint(fma(_440, -_464, _404));
    }
    out_attr3.w = in_attr2.w;
    uint _531;
    if (!_279)
    {
        _531 = floatBitsToUint(in_attr3.y);
    }
    else
    {
        _531 = floatBitsToUint(_502);
    }
    uint _542;
    if (!_279)
    {
        _542 = floatBitsToUint(in_attr3.x);
    }
    else
    {
        _542 = floatBitsToUint(fma(in_attr3.y, c3_3.data[31u], fma(_448, -c3_3.data[31u], -c3_3.data[31u]) + 1.0));
    }
    uint _553;
    if (_279)
    {
        _553 = _542;
    }
    else
    {
        _553 = _531;
    }
    uint _554;
    if (_279)
    {
        _554 = floatBitsToUint(fma(in_attr3.x, c3_3.data[30u], _502));
    }
    else
    {
        _554 = _542;
    }
    float _567 = fma(in_attr0.w, c3_3.data[22u], fma(uintBitsToFloat(_510), c3_3.data[18u], fma(uintBitsToFloat(_486), c3_3.data[10u], uintBitsToFloat(_479) * c3_3.data[14u])));
    float _571 = fma(in_attr0.w, c3_3.data[23u], fma(uintBitsToFloat(_510), c3_3.data[19u], fma(uintBitsToFloat(_486), c3_3.data[11u], uintBitsToFloat(_479) * c3_3.data[15u])));
    gl_Position.w = _571;
    out_attr1.y = fma(uintBitsToFloat(_553), c3_3.data[33u], c3_3.data[35u]);
    out_attr1.x = fma(uintBitsToFloat(_554), c3_3.data[32u], c3_3.data[34u]);
    gl_Position.x = fma(in_attr0.w, c3_3.data[20u], fma(uintBitsToFloat(_510), c3_3.data[16u], fma(uintBitsToFloat(_486), c3_3.data[8u], uintBitsToFloat(_479) * c3_3.data[12u])));
    gl_Position.y = fma(in_attr0.w, c3_3.data[21u], fma(uintBitsToFloat(_510), c3_3.data[17u], fma(uintBitsToFloat(_486), c3_3.data[9u], uintBitsToFloat(_479) * c3_3.data[13u])));
    gl_Position.z = fma((-_567) + min(_567, _571), c3_3.data[5u], _567);
}

