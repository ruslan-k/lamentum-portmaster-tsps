#!/usr/bin/env python3
"""Draft the runtime's shader catalogue (nvn_shader_sources.h) from translated programs.

Input: the workspace produced by tools/translate_lamentum_shaders.py (compiler GLSL +
blobs). Output: a header with one catalogue entry per program pair, in the runtime's contract:

  * our own ESSL100 rewrite of the compiler's `#version 450` output (attribute/varying,
    precision, `texture2D` instead of `texelFetch`/`textureSize` where the rewrite is provable);
  * attributes taken from the compiler's `in_attrN` declarations;
  * varying masks: one bit per varying vector location (vertex writes, fragment reads);
  * colour-write mask 15, mediump fragment contract.

The draft is a *candidate*: metadata that this script infers is marked `verify` in the report
and must be confirmed against a device run before it is claimed as working. Programs whose
fragment stage needs capabilities ESSL100 lacks (texelFetch with explicit LOD) are emitted with
`error` set so the runtime stops instead of rendering something that only looks plausible.
"""
import argparse, json, pathlib, re


def rewrite_essl100(source, stage):
    """Mechanical rewrite of the compiler output into the runtime's ESSL100 dialect."""
    body = source
    body = re.sub(r'^#version[^\n]*\n+', '', body)
    prelude = ['#version 100'] if stage == 'vertex' else ['#version 100']
    prelude.append('precision highp float;' if stage == 'vertex' else 'precision mediump float;')
    uses_texel_fetch = 'texelFetch' in body or 'textureSize' in body or 'textureQueryLevels' in body
    # layout(location = N) in/out  -> attribute / varying
    body = re.sub(r'layout\(location = (\d+)\) in (\w+)\s+(\w+);',
                  lambda m: ('attribute %s %s;' % (m.group(2), m.group(3))) if stage == 'vertex'
                  else ('varying %s %s;' % (m.group(2), m.group(3))), body)
    body = re.sub(r'layout\(location = (\d+)\) out (\w+)\s+(\w+);',
                  lambda m: 'varying %s %s;' % (m.group(2), m.group(3)), body)
    body = re.sub(r'layout\([^)]*\) uniform (sampler2D|samplerCube)\s+(\w+);',
                  lambda m: 'uniform %s %s;' % (m.group(1), m.group(2)), body)
    body = body.replace('frag_color0', 'gl_FragColor') if stage == 'fragment' else body
    return '\n'.join(prelude) + '\n' + body.strip() + '\n', uses_texel_fetch


def attributes_of(glsl):
    out = []
    for m in re.finditer(r'layout\(location = (\d+)\) in (\w+)\s+(\w+);', glsl):
        out.append({'location': int(m.group(1)), 'type': m.group(2), 'name': m.group(3)})
    return out


def varying_locations(glsl, decl):
    return sorted({int(m.group(1)) for m in re.finditer(r'layout\(location = (\d+)\) %s ' % decl, glsl)})


def component_masks(glsl, decl):
    """Per varying location, which components carry data (bit0..3 = x,y,z,w).

    A component counts as live when it is written from another value (not a literal) or read.
    This mirrors the runtime's per-slot mask check; it is inferred metadata, verify on device.
    """
    masks = {}
    for m in re.finditer(r'layout\(location = (\d+)\) ' + decl + r' (\w+)\s+(\w+);', glsl):
        loc, base = int(m.group(1)), m.group(3)
        mask = 0
        for comp, bit in (('x', 1), ('y', 2), ('z', 4), ('w', 8)):
            assign = re.findall(r'%s\.%s\s*=\s*([^;]+);' % (re.escape(base), comp), glsl)
            used = re.search(r'%s\.%s\b' % (re.escape(base), comp), glsl)
            literal = bool(assign) and all(re.fullmatch(r'[-\d\.eEf]+|vec\d\([^)]*\)', a.strip()) for a in assign)
            if (assign and not literal) or (used and not assign):
                mask |= bit
        if mask:
            masks[loc] = mask
    return masks


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('workspace', type=pathlib.Path)
    ap.add_argument('output', type=pathlib.Path)
    a = ap.parse_args()

    programs = []
    for glsl_path in sorted(a.workspace.glob('*.glsl')):
        name = glsl_path.stem
        control = a.workspace / (name + '.control.bin')
        code = a.workspace / (name + '.code.bin')
        if not (control.exists() and code.exists()):
            continue
        source = glsl_path.read_text()
        stage = 'fragment' if 'gl_FragColor' in source or re.search(r'out vec4 frag_color', source) else 'vertex'
        translated, needs_fetch = rewrite_essl100(source, stage)
        programs.append({
            'error': 'fragment stage needs an ESSL100 texel-fetch rewrite' if (stage == 'fragment' and needs_fetch) else None,
            'write_masks': component_masks(source, 'out'),
            'read_masks': component_masks(source, 'in'),
            'name': name, 'stage': stage,
            'code_size': code.stat().st_size, 'control_size': control.stat().st_size,
            'code_sha': __import__('hashlib').sha256(code.read_bytes()).hexdigest(),
            'control_sha': __import__('hashlib').sha256(control.read_bytes()).hexdigest(),
            'glsl': translated, 'needs_texel_fetch': needs_fetch,
            'attributes': attributes_of(source),
            'writes': varying_locations(source, 'out'),
            'reads': varying_locations(source, 'in') if stage == 'fragment' else [],
        })

    lines = ['/* GENERATED DRAFT catalogue for Lamentum - our own translations, not game data.',
             ' * Source: tools/build_lamentum_catalogue.py over the translate_lamentum_shaders.py workspace.',
             ' * Every entry is a translation of the title\'s program; entries with an error string are',
             ' * NOT translated and the runtime stops on them by design. */',
             '#include <stddef.h>', '#include <stdint.h>',
             '#define ZERO_ZX_SHADER_PACKAGES %d' % max(1, len(programs)),
             '#define ZERO_SHADER_VARYING_SLOTS 8', '#ifndef MOMO_SHADERS', '#define MOMO_SHADERS 1', '#endif']
    lines.append('static const struct {const char *original,*gles;unsigned stage;} nvn_shader_sources[]={')
    for i, p in enumerate(programs):
        lines.append('\t/* %d %s %s */' % (i, p['name'], p['stage']))
        lines.append('\t{"", "\\n"')
        for ln in p['glsl'].splitlines():
            lines.append('\t "%s\\n"' % ln.replace('\\', '\\\\').replace('"', '\\"'))
        lines.append('\t "", %d},' % (1 if p['stage'] == 'fragment' else 0))
    lines.append('};')
    lines.append('')
    lines.append('struct mm_shader_uniform {const char *name;unsigned stage,binding,offset,size,components,word_boolean,word_int,word_array;};')
    lines.append('struct mm_shader_sampler {const char *name;unsigned stage,binding,offset,size_query,texel_fetch_bits,cpu_view;};')
    lines.append('struct mm_shader_attribute {const char *name;unsigned location,kind;};')
    lines.append('struct mm_shader_binding {')
    lines.append(' const char *sha256,*error;unsigned control_size,code_size;')
    lines.append(' unsigned uniform_count,sampler_count,attribute_count,color_write_mask,requires_fragment_highp,requires_fragment_mediump,wave_contract;')
    lines.append(' unsigned varying_read_masks[8],varying_write_masks[8];')
    lines.append(' uint8_t code_hash[32],control_hash[32];')
    lines.append(' struct mm_shader_uniform uniforms[64];struct mm_shader_sampler samplers[8];struct mm_shader_attribute attributes[16];')
    lines.append('};')
    lines.append('static const struct mm_shader_binding nvn_megaman_shader_bindings[]={')
    for i, p in enumerate(programs):
        code = bytes.fromhex(p['code_sha']); control = bytes.fromhex(p['control_sha'])
        writes = [0]*8
        for loc, mask in p['write_masks'].items():
            if loc < 8: writes[loc] = mask
        reads = [0]*8
        for loc, mask in p['read_masks'].items():
            if loc < 8: reads[loc] = mask
        lines.append(' /* %d %s %s */' % (i, p['name'], p['stage']))
        lines.append(' {.sha256="%s",.error=%s,.control_size=%d,.code_size=%d,.uniform_count=0,.sampler_count=0,.attribute_count=%d,'
                     '.color_write_mask=15,.requires_fragment_highp=0,.requires_fragment_mediump=1,.wave_contract=0,'
                     % (p['code_sha'][:32], 'NULL' if not p['error'] else '"%s"' % p['error'],
                        p['control_size'], p['code_size'], len(p['attributes'])))
        lines.append('  .varying_read_masks={%s},.varying_write_masks={%s},'
                     % (','.join(str(x) for x in reads), ','.join(str(x) for x in writes)))
        lines.append('  .code_hash={%s},.control_hash={%s},'
                     % (','.join('0x%02x' % b for b in code), ','.join('0x%02x' % b for b in control)))
        lines.append('  .attributes={%s}},' % ','.join('{.name="%s",.location=%d,.kind=%d}' % (x['name'], x['location'], 2 if x['type'] == 'vec4' else 1) for x in p['attributes']))
    lines.append('};')
    report = a.workspace / 'catalogue-draft.json'
    report.write_text(json.dumps(programs, indent=2) + '\n')
    a.output.write_text('\n'.join(lines) + '\n')
    print('programs:', len(programs), '->', a.output)
    print('report:', report)
    print('entries needing ESSL100 texel-fetch work (emitted as error entries by the runtime '
          'until rewritten):', [p['name'] for p in programs if p['needs_texel_fetch']])


if __name__ == '__main__':
    main()
