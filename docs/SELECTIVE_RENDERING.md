# Selective shot rendering

`episodes/shot_render.py` is an opt-in drawing cache and encoder. Existing episode
scripts and `acting.render_video` keep their current behavior. Use this adapter
only when the renderer can declare each shot's complete inputs. Do not omit
dependencies merely to get cache hits.

## Contract

```python
import shot_render

shots = [
    {"id": "s01", "start": 0, "frames": 30, "seed": 1,
     "config": {"camera": "W", "incoming_state": {}, "beats": []}},
    {"id": "s02", "start": 30, "frames": 30, "seed": 2,
     "config": {"camera": "M", "incoming_state": {}, "beats": []}}
]
result = shot_render.render(shots, draw, dependencies, "build/shot-cache", size=(1920, 1080))
shot_render.encode(result, "build/continuous-audio.wav", "build/revision02.mp4")
```

`draw(shot, absolute_drawing_index)` returns a Pillow image at the requested size.
There are 15 drawings per second, repeated twice for 30fps. Shot ranges must be
consecutive from drawing zero. Size must contain positive even dimensions.

The callback must be deterministic from the shot configuration, seed, drawing
index and declared dependencies. Put all pose/prop incoming states, camera,
actions, timings, per-shot assets and random seeds in those inputs. Materialize
cross-shot state explicitly: if an earlier edit changes a later shot's incoming
state, invalidate that later shot too. A duration change shifts subsequent
absolute drawing indices and correctly invalidates later shots. The cache does
not infer data flow from arbitrary Python code or automatically slice stage tables.

`dependencies` must contain the drawing entry script and all transitive imported
code, external configuration, generated assets and fonts used by it. The cache
also hashes its own implementation and records Python/Pillow/NumPy versions.
Dependencies are rehashed on every invocation and checked again before a new shot
is published. No process-lifetime hash memoization hides source changes.

A shared code/asset change intentionally invalidates every dependent shot. A
shot-local edit belongs in that shot's `config`, or a properly scoped independent
renderer contract. Hiding local edits in shared Python constants forces a broad
invalidation. The same `dependencies` collection applies to all shots in this API.

## Integrity and failure behavior

- Each content-keyed directory holds lossless RGB PNGs and a completion receipt
  containing sizes and SHA-256 hashes. Cache hits verify every frame.
- Missing, corrupt, unstamped or wrong-size entries are misses. Render failures
  leave no completed shot; new directories are published atomically.
- Only one writer uses a cache at a time. A lock fails fast if occupied. After a
  killed process, remove a stale lock only after confirming no writer remains.
- Caller shot dictionaries are copied before hashing/drawing. Hidden callback
  state is still the caller's responsibility; the cache cannot authenticate it.
- Encode rechecks frame hashes, refuses audio shorter than the visual timeline,
  and preserves existing output revisions. Failed encoding removes its partial file.

The final encoder uses one continuous WAV and the established H.264/AAC/loudnorm
settings, re-encoding the output each time. This prevents independently normalized
audio fragments at shot boundaries. Audio-only changes reuse drawings but still
run the full final encode. All final-MP4 checks remain mandatory: matching two
outputs does not demonstrate good audio, framing, story clarity or safety.

This initial implementation draws cache misses serially. It is a correctness
baseline; cold renders may be slower than the existing multiprocess renderer.
It saves repeated drawing work, not the complete encoding cost. Cache storage
grows by revision and needs deliberate retention management; no automatic deletion
policy is introduced. Never place renders or cache directories in git.

## Reproduce the engineering trial

```bash
python3 tools/test_shot_render.py
python3 tools/benchmark_shot_render.py build/astra/shot-trial-new
```

The benchmark uses the actual stage rig in a synthetic 0.6-second sequence,
generated tone audio, three shots and nine drawings. It records cold/warm/edit/
clean timings, verifies only the edited middle shot redraws, and compares lossless
frame hashes plus decoded MP4 video/audio. Its output directory must be new.
The nine focused tests also exercise seeds, shared dependencies, missing/corrupt
cache, interrupted rendering, busy locks, short audio and failed encoding cleanup.

Adoption gate: before using it for a production episode, compare a full cached
render with a clean render, pass existing video/clearance/framing checks and get
the normal independent reviews. A 10/10 selective-rendering rating requires the
production trials defined in docs/ASTRA_PRODUCTION_PIPELINE.md, not this small test.

Rollback: switch the episode back to its previous rendering call and revert the
carried package commit. Existing PNG cache files can be ignored; final media files
remain ordinary MP4s. No live gate format or rendering default was changed.
