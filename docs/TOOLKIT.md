# Toolkit index (read this instead of source code)

One line per module: what it is for. If you need its calls, read only its docstring (the first ~40 lines:
`sed -n 1,45p <file>`), never the whole file, unless you are changing that module. Whoever adds a module adds a line
here and an API docstring at its top.

## New standard (Episode 11 onward; 1920x1920 worlds, 2x render)
| Module | What it gives you |
|---|---|
| `episodes/hires.py` | `set_res(2)` before building sprites; `Cut(w, h)` = paper cut-out at 2x (same API as `paperlib.Cut`) |
| `episodes/rig2.py` | Snip and Crinkle puppets: `Perf2(Puppet("snip"/"crinkle", scale), x, y)`; `to` (turn, hturn, arm/elbow angles, look), `walk`, `reach` (IK), `face`, `ears`, `hop`, `wiggle`, `blink`, `face_point`, `head_pivot`, `draw`; A2 acting (18 Oct, off by default): `acting()`, `emote(t0, t1, name)` (curious/cross/sad/delighted/neutral), `dart`, `BLINK_PRESETS` quick/soft/slow, ear overlap, breath + drift, `mouth="none"`; demo `episodes/rigtest_acting.py` |
| `episodes/framestore.py` | Stored-frame folders (`--hires` passes): `begin`, `path`, `finish`, `load(folder, d, script)`; a frame is reused only if the folder's STAMP = hash of the script + its repo imports, else drawn fresh (audit F2). `python3 episodes/framestore.py <script> <folder>` says MATCH or NO MATCH |
| `episodes/acting.py` | Faces (brows calm/up/sad/sorry/worry/think: never "focus"), eyes, mouths, eases, `Perf` timelines, `Cam` (landscape/vertical views of one world), `render_video(path, out, wav, dur, view, workers=8)`, `drawing_of` (15 drawings/s on twos) |
| `episodes/rig2_pip.py` | Pip: `PipPerf(PipPuppet(0.9))` with `puff_up`, `tuft`, `dance`, `flap`, `run`, `shiver`, `point`, `hug_self`, `grip_for_tip` + `draw_held` (marker); `crinkle(1.2)` with mouths `yum_l`/`yum_c` |
| `episodes/props_porch.py` | Episode 11 world: `Porch(cam)`, `background(t)` (golden → sunset → evening), `front(f, t)` (railing drawn after characters), `albedo` |
| `episodes/ep11_light.py` | Dusk grade, railing hearts, pumpkin glow, floor pool, projected smile on wall/body/wing, `luma`, `clearance` checks |
| `episodes/props_pumpkin.py` | `Pumpkin().paper(rot, strokes, holes, lid)` and `.emissive(...)`; `stroke_tip` for marker tracks; stages plain → drawn → cut → lit → turned |
| `episodes/props_lantern.py` | Ep 11 Short: the paper-lantern pumpkin (PK size); `Lantern().paper(strokes)` / `.lit(strokes, level)` (whole paper glows, ink stays dark), eye strokes that read as a "C" (`C_STOP`), `tip_world`, `inside_clip` (hide what goes into the ring) |
| `episodes/ep11_short_transform.py` | Ep 11 transformation Short: own timeline; a one-marker holder schedule (`marker_pose`), paws/wings behind the back (`BACK`), the hand straight down with the tea light, `--check` (measured gaps), `--hires` for the 2.4x take |
| `episodes/props_glow.py` | Episode 11 small props: sketchbook (back / plan page), tucked book, crayon, polishing cloth, battery tea light (off/on), wind chime, autumn leaves |
| `episodes/props_hand2.py` | The grown-up's arm and hands at 2x: `Arm(upper, fore)`, `draw`, `wrist_for`, `draw_hand`; hands rest / pinch / press (click) / thumb / palm; `sleeve_end()`; never a tool |
| `episodes/props_splash.py`, `props_artcorner.py` | The pilot's art corner, jars, brushes, thought cloud, sparkle, heart (reusable) |
| `episodes/props_grownup.py` | The grown-up's jointed arm (old 1x pipeline; port to `hires.Cut` before using at 2x) |
| `episodes/music_extra.py`, `audio.py` | Synth instruments (toy piano, melodica, organ, steel pan, marimba, glock, pads, bass), sound effects, `jingle`, `Mix`, `reverb`, `write_wav` |
| `episodes/pilot02_splash_of_blue.py` | Reference episode: `render_world(t, d, cam, bg)`, `make_buses()`, flags `--keys`, `--cuts`, `--still T` |
| `episodes/pilot02_short.py` | Reference vertical Short: re-films an episode through a vertical camera, cuts its sound effects, own music bed |
| `tools/check_video.py` | `--landscape --no-loop --cuts t1,t2,...`; vertical Shorts 12-180 s; `--dur 15-30` (transformation Short) or `12-60` (story Short); prints RESULT: PASS |
| `tools/build_agents.py` | Writes `.claude/agents/` from MASTER_PROMPT.md Appendix A `--allow-growth`: write even if a block has >10% more words than at the newest `agents-*` tag (otherwise exit 1, nothing written; M10). |
| `tools/blind_guard.py` | PreToolUse hook in the fresh-eyes-reviewer's frontmatter (Read, Bash, Glob, Grep): exit 2 on reviews/, episodes/, output/, Videos/, docs/ (except its reference), MASTER_PROMPT/HANDOFF/CLAUDE.md (M1); test: pipe `{"tool_name":"Read","tool_input":{"file_path":"reviews/x"}}` |
| `tools/handoff_check.py` | Checks HANDOFF.md: ≤500 words, paths exist, no trimmed fact lost; `--install` sets the pre-commit hook |
| `tools/plan_check.py` | `<plan>`: the designer's gate (gag table vs the playbook, key actions ≥1.0 s and ≥10%, storyboard covers every key action, props, ≤4,000 words); docstring = the required tables |
| `tools/handover_check.py` | `<script>`: the animator's last command (audio silence/loudness, `--check`, `keysize` vs plan; a Short also needs a `safezone <t>` line at every `keysize <t>`); `--verify` starts the render chain `--modules` prints the hashed list (the script, its repo imports, the plan; M3). A `*short*` script with no `<epNN>_short_plan.md` needs ≥2 `keysize` ≥10 instead of the episode plan's rows (M4). |
| `tools/safezone.py` | Shorts safe zones: `to_frame(mask, RES, (CAM.ox, CAM.oy), c, z)` then `line(t, name, mask)` → `safezone <t> <name> ok/FAIL` for a Short's `--check`; `--overlay frame.png` draws the zones on a still |
| `tools/title_check.py` | `<upload sheet>` or `--title "..."`: flags titles that repeat the last 5 or the live ones |
| `tools/preflight.py` | `--used --reset-min --weekly [--log step]`: the Lead's pre-flight (band, ledger row, OPEN mistakes, HANDOFF count) `--weekly-reset-days <d>` caps the band at SMALL when weekly % is >10 points over pace, `--weekly-ok` (owner's word) lifts it; exit 2 if `--log` names a forbidden agent (M6). |

## Facts you'd otherwise dig for
- Render speed: about 3.5 s of rendering per second of 2x landscape video on 8 cores (Episode 11's porch with light:
  about 2 s per frame, about 11 min for 160 s).
- Reach from the shoulder: Snip 60+58, Crinkle 66+64, Pip 40+44 design units. Pip's head is at the big friends'
  shoulder height. Heads turned past 36° crowd the edge.
- Zoom at most 2x (2x render). Shorts safe zones: nothing important in the bottom 19%, or in the right 12% between
  50% and 90% of the height.
- Episode 1-10 code (`paperlib.py`, `characters.py`, `scene.py`, `icons.py`, `props_*` for those episodes) is the old
  1080x1920 1x pipeline; don't mix it into new episodes except through a port.
