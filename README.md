# Nearby Warp Countdown Skip

Skips the 10s Initiating Warp hold on the Forsaken nearby-system warp.
No options, only instant. Pulse drive is untouched.

A [Nozavolochen](https://github.com/Nozavolochen/framework) mod:
the runtime patches are declared in `mod.toml` and applied by the
shared host DLL at game boot.

The hold is hardcoded in the exe (10.0 minus elapsed, converted to int
for the cockpit readout, plus a wait gate on `elapsed >= 10.0`), so no
EXML value reaches it. Two fail-loud exe patches skip it: the cockpit
count is forced to zero and the wait gate is NOPed, so the warp engages
on the first frame. Nothing else is touched: no EXML, no ship stats, no
pulse values. The Warp Destination tunnel that follows is the base game
streaming the destination system (about 20s on first visit) and is left
alone.

## Install

Requires the **Nozavolochen Framework** file (required dependency,
provides `Binaries/xinput9_1_0.dll`).

Install `dist/Nearby Warp Countdown Skip.zip` as a normal mod into `GAMEDATA/MODS`
([Amethyst](https://github.com/ChrisDKN/Amethyst-Mod-Manager)) so you end
up with `GAMEDATA/MODS/Nearby Warp Countdown Skip/mod.toml`. The framework file provides
the host DLL.

You should then have:

- `Binaries/xinput9_1_0.dll`: the Nozavolochen host, from the framework
  file (Windows DLL, runs under Proton with
  `WINEDLLOVERRIDES="xinput9_1_0=n,b" %command%`).
- `GAMEDATA/MODS/Nearby Warp Countdown Skip/mod.toml`: the patch spec.

After launch, `Binaries/nozavolochen.log` is created to help with
debugging.

## What it patches

In the exe, always applied:

- `instant-countdown-ui`: overwrites `cvttss2si ecx,xmm0` (`F3 0F 2C C8`)
  with `xor ecx,ecx; nop` (`31 C9 66 90`), so the cockpit int is always 0.
- `instant-warp-gate`: NOPs the `jb` (`0F 82 91 01 00 00` ->
  `66 0F 1F 44 00 00`) on the `elapsed >= 10.0` gate so the warp engages
  on the first frame.

Both patterns are verified unique (one hit each) and fail-loud via
`tools/check_specs.py`.

## Build (on Linux)

```sh
make release      # verify spec + pack dist/ zip (default)
make verify       # verify mod.toml against NMS.exe (read-only)
make loader       # build the Nozavolochen host DLL via the framework (dev testing)
make rootzip      # pack the root-install archive (no re-verify)
make assets       # regenerate the Nexus page images (needs Pillow)
make video        # join before/after into comparison (needs ffmpeg)
make clean        # remove build/ and dist/
```

`make verify` checks each patch against the installed `NMS.exe`:
pattern matches exactly once in `.text`, expect bytes match, replacement
fits. A game update that moves the code fails loudly instead of shipping a
patch that does nothing.

## Game updates / versioning

The mod version is `version` in `mod.toml`. When No Man's Sky updates,
re-run `make verify` against the new `NMS.exe`. If a pattern no longer
matches exactly once, re-derive it from the new binary and bump `version`
in `mod.toml`.
