# Menu initialization is reached; absence of UI is not proof of absent input

## Read-only code/scene mapping

`tools/inspect_il2cpp_menu.py` resolves the owner's metadata24.2 type definitions
and method tokens through the original NSO's Il2CppCodeGenModule method table.
It validates all metadata type/method token shapes and the three main segment
hashes from `inspect_nso`, then emits names and addresses only. It does not
modify the image and does not itself prove live execution.

Measured identities:

- ManagerMenuPrincipal: type-definition4687, Assembly-CSharp.dll;
- module structure main+0x2cb29d8, 4976 method pointers;
- Start token0x06000441 -> main+0x16cb4c0;
- GetResolutions token0x06000442 -> main+0x16cbb00;
- Start directly calls GetResolutions, PlayerPrefs.HasKey,
  LanguageManager.ChangeLanguage and GameObject.SetActive.

The serialized level0 GameObject282 (ManagerMenuPrincipal) is active. Its two
MonoBehaviour components1740/1741 have m_Enabled=1. Several menu panels are
serialized inactive, so actual startup activation matters. Default scene state
alone does not prove a startup defect.

## Build200 semantic trace (diagnostic, not a game patch/fix)

`LC2_MENU_TRACE=1` adds five identity-checked entries to the adapter's existing
trap/replay mechanism: Start, GetResolutions, GameObject.SetActive and two
IL2CPP exception helper thunks. Each exact original prologue is replayed, all
argument registers and API return paths are left intact. Traps affect only the
private executable mapping in RAM, never the owner segment files. The feature
is off unless explicitly set to1. Stack/entry identity guards remain strict;
speculative type-name reads log unreadable values rather than reject the game.

The host test actually executes replay logic for all five prologues and checks
stack offsets, stored register values, preservation of registers and off=0.
Cross-build200 and its deployment SHA-256 are in the evidence.

Live receipts (`evidence/menu-trace-01/live.log`):

    LC2_MENU_EVENT name=ManagerMenuPrincipal.Start caller=main.text.seg+0x7bb54
    LC2_MENU_EVENT name=ManagerMenuPrincipal.GetResolutions caller=main.text.seg+0x16cb624
    LC2_MENU_EVENT name=GameObject.SetActive caller=main.text.seg+0x16cba70 x0=0x3e9e4ca20 x1=0x1
    LC2_MENU_EVENT name=GameObject.SetActive caller=main.text.seg+0x16cba84 x0=0x3e9e4c920 x1=0x1

Disassembly of this exact Start identifies the latter arguments as the objects
loaded from manager+0x30 and manager+0x70 (CanvasMenuPrincipal and
EscenaPrincipal). This is checked against the original metadata-registration
field-offset table at main+0x2cc4508, type4687's offsets at main+0x24a9d64;
it is not inferred from field order alone. Both calls request true. The first call has returned by the
time the second entry is reached. No traced exception helper fired in the
captured interval.

The concurrent real DRM capture `live.png` still shows the Lamentum logo and
dark courtyard without readable menu choices. This is NOT a claim that the
menu is visible or playable, and the trace does not read Unity's final
activeInHierarchy/canvas visibility.

## Run completion and cleanup

The 300-second run reached presented frame379 and ended at TIME_LIMIT, with
no traced exception-helper event. Build200 installed SHA-256:
`132facb8e8a269ae3e87cf80054e720294fdaa37ae374b869d8e6861f2ba7562`.

The harness sampled MainUI=0 immediately after runtime exit. That was not the
final state: an independent later /proc read confirms MainUI=1, principal=1,
runtime=1, both game process names=0 and gdb=0. `clean-menu.png` is the frontend
clock/screensaver, NOT a game/menu frame. A safe wake-up after checking no game
was running produced `clean-menu-awake.png`, which shows the real Spruce
Recents list with Lamentum selected. No system setting or persistent launcher
default was changed.

## Consequence

Stop treating the title image as proof that the game has not activated a menu
or never reads HID. Both the canonical Npad reads and menu startup calls are
now observed. The useful next boundary is the UI draw path: distinguish
active-but-unrendered panels/text from a later activation/focus issue, then
identify the actual shader pairs, geometry and clipping/stencil state. The
existing negative button sweeps cannot resolve those graphics questions.

Do not force a canvas on, fabricate menu geometry or bypass game startup.
Do not retry direct GDB execution breakpoints without a deliberate strategy
for the adapter's own SIGTRAPs: the previous attempt induced UNKNOWN_TRAP.
