# Why the title ignores the pad: measured contract, not a mapping tweak

Status: input still does not reach the game. This round replaced two guesses with
measurements and falsified the "it is still loading" and "wrong Npad routing"
explanations.

## 1. Loading has ENDED before the title is shown

Bucketing `ROMFS_READ` and `NVN_TEXTURE_REAL` by the presented frame in the
420-second run (`../evidence/long-budget-420-01/latest.log`):

| frame bucket (50 frames) | 0 | 50 | 100 | 150 | 200+ |
|---|---:|---:|---:|---:|---:|
| RomFS reads | 474 | 378 | 226 | 48 | 0 |
| texture initialisations | 196 | 138 | 162 | 67 | 0 |

The run continues to frame 1273 and the title logo is already on screen at frame
~549. No asset I/O and no texture creation happen after ~frame 200, so the title
screen is idle, not a loading screen. "The game is still loading and ignores
input" is therefore refuted for this phase.

## 2. The title does not poll the pad over IPC

`EP_HID` (enum index 45, `endpoint=0x2d`) appears **20 times in the whole run**:
commands `0x6a`×9, `0xc8`×4, `0x0`, `0x6d`, `0x64`, `0x3`, `0x66`, `0x78`, `0xcb`.
Those are setup (styles, joy-hold type, vibration info) plus one shared-memory
handle request. There is no per-frame state query, so the title reads a **shared
memory** region, as nn::hid normally does.

## 3. What the SDK says that memory looks like

`nn::hid::detail::NpadSharedMemoryAccessor::GetInternalState(unsigned)` at
`sdk.text.seg+0x207ec0`:

```
cmp  w1,#0x10 ; mov w8,#8 ; cinc w8,w8,eq      ; id==0x10 -> 9
cmp  w1,#8    ; csel w8,w1,w8,lo               ; id<8 -> id, else 8/9
add  x8,x0,w8,sxtw #3 ; add x8,x8,#0x18 ; ldar x0,[x8]
```

So an npad id indexes a table at **+0x18 with 8-byte entries** (ids 0–7, then 8
for 0x10 and 9 for 0x20), and the loaded 64-bit value is what the accessor then
uses. The adapter currently publishes entries at `shared+0x9a00+0x5000*i` with
rings at `+0x28+0x350*ring` — a layout inherited from a different SDK generation.
That is not automatically what SDK 10.9.0.0 reads.

## 4. Falsified: "the press goes to the wrong Npad"

`LC2_HID_BROADCAST=1` (diagnostic A/B, build 194) publishes the same sample into
**every** npad entry (10) and **every** ring (7), with styles forced to FullKey.
Measured on the live title (`../evidence/hid-broadcast-01/`), with the press
confirmed in the adapter's own receipt (`HID_SAMPLE … buttons=0x2`, `0x400`):

| capture | mean luminance | band 300–600 rows | changed pixels vs title |
|---|---:|---:|---:|
| at-title | 3.72 | 3.30 | — |
| after A | 3.72 | 3.29 | 3420 (max Δ 83) |
| after Start | 3.71 | 3.18 | 3702 (max Δ 96) |

The differences are ember/rain animation spread over the frame; the region where a
menu would be drawn does not change. Broadcasting to every entry and ring produced
no visible change, so the failure is **not** which NpadId/style/ring we address.
It is the published shape (or the region) itself.

## 5. The region head is EMPTY — measured, this is the defect

`LC2_HID_DUMP=1` (build 195, diagnostic) prints the first 0xA0 bytes of the
published region on the first press, plus the id-table this SDK's accessor indexes
(`+0x18 + 8*i` for i = 0..9). Measured on a live run with the press confirmed in
the same log (`../evidence/hid-dump-01/hid-dump.txt`):

```
head:   000=00000000 … 09c=00000000        (every word zero)
id-table: +018=0000000000000000 … +060=0000000000000000   (all ten zero)
```

So the accessor at `sdk+0x207ec0` loads zero for every npad id, and no entry we
write at `+0x9a00` can be seen: the guest never reaches that table. This is the
first measured defect in the input path, and it explains why the broadcast A/B
(section 4) changed nothing — the record the title reads was never populated.

Two candidate causes remain, and they are distinguishable by one experiment each:

1. the shared region we publish into is not the one the accessor reads (the title
   may map a second HID region for the internal-state table), or
2. this SDK expects the +0x18 table to be FILLED by the platform (8 bytes per npad
   id, ids 0–7 plus 8 for 0x10 and 9 for 0x20) and our publisher writes only the
   entry table at +0x9a00, leaving the table the accessor uses at zero.

Next step: decide between them by A/B-ing the +0x18 table (guest address of our
entry block vs an offset/id), never by touching the entry table again until the
head is non-zero.

## 6. What the title's own reader expects (derived, not borrowed)

Resolving the call chain removes the guesswork:

- `nn::hid::GetNpadStates(NpadFullKeyState*, int, const uint&)` at `sdk+0x2147b0`
  is a thin wrapper; it calls through the GOT slot at `0xc62240` (R_AARCH64_ABS64,
  .dynsym index 18224) to `nn::hid::detail::GetNpadStates(Pi, NpadFullKeyState*, int,
  const uint&)` at `sdk+0x208a40` — a symbol defined in this same module.
- That function (`sdk+0x208a40`, disassembled) does:
  `bl 0x56d4e0` (instance) → `ldr w1,[x24]` (npad id) → `bl 0x56d4f0`
  (the accessor's `GetInternalState`) → **treats the returned value as a POINTER**,
  then reads `[x0+0x40]` (count) and `[x0+0x38]` (ring counter) and walks records at
  `x0 + index*0x30`, copying 0x28 bytes from `[rec+0x50..0x70]` into the caller's
  state struct, with a sequence re-check through `[rec+0x48]`.

So for this SDK the platform must publish a **table of pointers at `+0x18`**
(8 bytes per npad id: ids 0–7, 8 for 0x10, 9 for 0x20), each pointing at a
per-npad block whose ring records have a **0x30-byte stride**, a sequence word at
`+0x48`, counters at `+0x38`/`+0x40`, and the state payload at `+0x50`–`+0x70`.

The adapter instead writes an entry table at `+0x9a00` with 0x5000-byte entries and
0x350-byte rings — a different SDK generation's shape. Combined with section 5
(the table is zero), that is why every press is invisible: the title's reader
dereferences zero before it ever looks at our entry table.

## 7. Consequences

- Do not retry `LC2_HID_BROADCAST` or Npad-id A/Bs; that axis is measured and dead.
- Next: extend the publisher for SDK 10.9.0.0 — fill the `+0x18` pointer table and
  emit 0x30-stride ring records per npad, keeping the existing 0x9a00 entry layout
  untouched until the new path is measured to move the menu.
- The run still ends on `TIME_LIMIT` with 563 textures and no defect stop, so the
  graphics side is stable while input is worked on.

## 6. Device state

Build 194 installed (`lamentum-nextos.before-194` keeps build 193), SHA-256
`4c467c366b340362c8b7251d6801aaccd09e56d1ff44e652ad4127ed6149c197`, read back on
the device. After the probe: no port process, MainUI=1, principal=1, runtime=1;
the restored Spruce menu is in `../evidence/hid-broadcast-01/clean-menu.png`.
`LC2_HID_BROADCAST` is off unless explicitly set to `1`.
