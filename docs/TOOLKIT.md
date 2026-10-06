# Toolkit index (read this instead of source code)

One line per module: what it is for. If you need its calls, read only its docstring (the first ~40 lines:
`sed -n 1,45p <file>`), never the whole file, unless you are changing that module. Whoever adds a module adds a line
here and an API docstring at its top.

## New standard (Episode 11 onward; 1920x1920 worlds, 2x render)
| Module | What it gives you |
|---|---|
| `episodes/hires.py` | `set_res(2)` before building sprites; `Cut(w, h)` = paper cut-out at 2x (same API as `paperlib.Cut`) |
| `episodes/rig2.py` | Snip and Crinkle puppets: `Perf2(Puppet("snip"/"crinkle", scale), x, y)`; `to` (turn, hturn, arm/elbow angles, look), `walk`, `reach` (IK), `face`, `ears`, `hop`, `wiggle`, `blink`, `face_point`, `head_pivot`, `draw` |
| `episodes/acting.py` | Faces (brows calm/up/sad/sorry/worry/think: never "focus"), eyes, mouths, eases, `Perf` timelines, `Cam` (landscape/vertical views of one world), `render_video(path, out, wav, dur, view, workers=8)`, `drawing_of` (15 drawings/s on twos) |
| `episodes/rig2_pip.py` | Pip: `PipPerf(PipPuppet(0.9))` with `puff_up`, `tuft`, `dance`, `flap`, `run`, `shiver`, `point`, `hug_self`, `grip_for_tip` + `draw_held` (marker); `crinkle(1.2)` with mouths `yum_l`/`yum_c` |
| `episodes/props_porch.py` | Episode 11 world: `Porch(cam)`, `background(t)` (golden → sunset → evening), `front(f, t)` (railing drawn after characters), `albedo` |
| `episodes/ep11_light.py` | Dusk grade, railing hearts, pumpkin glow, floor pool, projected smile on wall/body/wing, `luma`, `clearance` checks |
| `episodes/props_pumpkin.py` | `Pumpkin().paper(rot, strokes, holes, lid)` and `.emissive(...)`; `stroke_tip` for marker tracks; stages plain → drawn → cut → lit → turned |
| `episodes/props_splash.py`, `props_artcorner.py` | The pilot's art corner, jars, brushes, thought cloud, sparkle, heart (reusable) |
| `episodes/props_grownup.py` | The grown-up's jointed arm (old 1x pipeline; port to `hires.Cut` before using at 2x) |
| `episodes/music_extra.py`, `audio.py` | Synth instruments (toy piano, melodica, organ, steel pan, marimba, glock, pads, bass), sound effects, `jingle`, `Mix`, `reverb`, `write_wav` |
| `episodes/pilot02_splash_of_blue.py` | Reference episode: `render_world(t, d, cam, bg)`, `make_buses()`, flags `--keys`, `--cuts`, `--still T` |
| `episodes/pilot02_short.py` | Reference vertical Short: re-films an episode through a vertical camera, cuts its sound effects, own music bed |
| `tools/check_video.py` | `--landscape --no-loop --cuts t1,t2,...`; vertical Shorts 12-180 s; prints RESULT: PASS |
| `tools/build_agents.py` | Writes `.claude/agents/` from MASTER_PROMPT.md Appendix A |

## Facts you'd otherwise dig for
- Render speed: about 3.5 s of rendering per second of 2x landscape video on 8 cores (Episode 11's porch with light:
  about 2 s per frame, about 11 min for 160 s).
- Reach from the shoulder: Snip 60+58, Crinkle 66+64, Pip 40+44 design units. Pip's head is at the big friends'
  shoulder height. Heads turned past 36° crowd the edge.
- Zoom at most 2x (2x render). Shorts safe zones: nothing important in the bottom 19%, or in the right 12% between
  50% and 90% of the height.
- Episode 1-10 code (`paperlib.py`, `characters.py`, `scene.py`, `icons.py`, `props_*` for those episodes) is the old
  1080x1920 1x pipeline; don't mix it into new episodes except through a port.
