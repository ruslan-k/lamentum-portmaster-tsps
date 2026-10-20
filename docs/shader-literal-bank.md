# Embedded shader-literal bank specialization — build 178

Status: NOT PLAYABLE. This corrects a separate constant-source contract; it does
not establish a visual improvement, complete scene, menu or gameplay.

## Implementation and capture contract

Five already translated programs referred to hardware bank c1 through the generic
application-cbuf upload path. Their static float reads instead refer to embedded
literal data in their captured shader code. For the captured SDK/control layout,
the control words at 0x700 and 0x704 delimit the literal start and full code-capture
end. The sRGB shader's first literal is the original 0x3f870a3d (1.055), not a
camera/material float from an application uniform binding.

`tools/shader_literals.py` specializes those STATIC reads into
`uintBitsToFloat(0x........u)`. It validates BOTH captured code/control SHA-256
against the existing catalogue, capture length, literal-start alignment and each
read's bounds. Dynamic/unrecognized accesses and identity mismatches fail closed.
No literal values are guessed or scanned from guest application buffers. Original
shader/capture binaries are not committed.

The now-unused literal sampler declarations and corresponding cbuf metadata are
removed together. Remaining application-bank metadata, code/control hashes and
other shader text are preserved. In particular, removal of the first declaration
must NOT renumber a remaining bank. The main catalogue builder also invokes the
specialization, preserving its pre-specialization application mapping.

Specialized entries:

- dump-1792425422-0
- dump-33650b4b
- dump-8af77a17
- dump-d032944a
- dump-e6091e72

Their hashes, measured offsets and static word indices are recorded in
`../evidence/cbuf-literals-01/literal-manifest.json`. These are five existing real
translations, NOT five TEST replacements. All eight TEST substitutes remain.
Application cbuf fallbacks remain an unresolved separate contract; this change
does not claim to fix their mapping.

## Verification

- Five new host tests: exact float-bit spelling/collision suffixes, negative-zero
  and NaN word representation, application-bank preservation, malformed/dynamic
  reads, complete catalogue metadata removal/idempotence and capture-hash refusal.
  GPU NaN payload preservation is not claimed by these host string tests.
- Seven existing sampler/catalogue tests and the launcher regression pass.
- Build 178 completes against the unchanged 435-file manifest-pinned baseline.
- Installed runtime hash, independently read back on TSPS:
  `83607a54a351f0236fcb0639b63f28e17c9d9b21ea2968c8936ab35c1880f2ca`.
- The matched short probe uses the build-177 isolated-unit environment and a
  45-second budget: TIME_LIMIT, 149 texture initializations, 52 presented frames,
  no shader compile/link refusal and no post-upload cbuf-unit collision.
- Physical captures at approximately 25 and 38 seconds still show dark, incomplete
  geometry with rain. There is no demonstrated visible gain over build 177.

See `../evidence/cbuf-literals-01/` for raw build/test/run logs, capture ownership
receipts, SHA receipt and physical screenshots.

## Longer loading probe

The 300-second-budget probe uses the existing diagnostic configuration with guest
quota 3072 MiB, lazy BC uploads, two lossless backing files, 16-KiB compressor
blocks and a 10-ms cold threshold. Actual termination is T2_MEMORY_FLOOR at
58 MiB available against the unchanged 64-MiB floor, after 328 texture
initializations / frame 124. Swap-free at the floor is 1971 MiB. This demonstrates
the remaining physical-headroom stop, not kernel OOM or GPU correctness.

The 90-second DRM capture was taken with no MainUI and a live port PID (18421).
It still contains partial scene geometry/rain and no readable menu. The port
ended before the planned later captures. The previous 522-texture result used a
different run/configuration; the present result is not a matched memory regression
or improvement measurement.

Raw evidence: `../evidence/cbuf-literals-loading-01/`.

## Cleanup

Build 178 remains installed, with the prior binary saved as
`lamentum-nextos.before-178`. Independent cleanup inspection finds MainUI=1,
principal=1, runtime=1 and no port PID; the physical Spruce root menu is verified
in `clean-menu.png`. The D-pad event only woke the idle interface; it is not
physical game-input acceptance. No owner image, texture resolution, launcher
memory defaults or system VM settings were changed.
