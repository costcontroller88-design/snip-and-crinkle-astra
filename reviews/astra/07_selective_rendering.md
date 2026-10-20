# Selective rendering — 20 October 2026

Problem: episodes/acting.py:423–454 redraws the whole timeline; episodes/framestore.py:1–15 stamps a complete script/dependency closure. The audit's shot-reuse rating was 1/10. A shot-local edit needed an explicit dependency boundary and verified cached output.

Change: opt-in episodes/shot_render.py stores completed shots as lossless RGB drawings with content keys, dependency hashes and per-frame integrity checks. It freezes caller inputs; checks dependencies again before publishing; refuses concurrent writers; redraws missing/corrupt/incomplete shots; and cleans failed attempts. Encoding uses the established 15-drawing/30fps cadence and one continuous final WAV, checks cached frames again, rejects short audio and preserves existing outputs. Current episode renderers are unchanged.

Actual results:
- Nine focused tests PASS. Combined REGRESS PASS 172/172. Independent baseline replay in the legacy layout: REGRESS PASS 150/150; no earlier Astra implementation dependency.
- Reproducible actual-stage-rig fixture: three shots, nine drawings, 0.6 seconds. Cold: 9 drawings in 23.1297s; warm: 0 in 0.0098s; middle-shot edit: 3 in 7.4248s; clean edited rebuild: 9 in 15.0893s. Times cover drawing/cache work, excluding final encoding. Cold/warm process effects prevent treating the first cold time as a controlled speed ratio.
- The edit reused the first/third shots, reducing redrawn frames 9→3. All edited cached frame hashes equal the clean rebuild. Decoded MP4 frame hashes and decoded audio bytes also match exactly.
- ffprobe: H.264 1920×1080, 30fps, 18 frames; AAC; duration 0.600000s. This is an engineering fixture, not a final-video quality or story pass.
- Python compilation and git diff --check PASS. Reproduce with tools/benchmark_shot_render.py and a new output directory.

Limitations: caller must explicitly declare complete shot inputs and transitive code/assets. Hidden mutable state cannot be inferred. Shared code changes invalidate all dependent shots; changed duration/incoming state may correctly invalidate later shots. Cache misses draw serially; cold speed may be worse than the old multiprocess renderer. Final encoding still runs in full; production adaptation, cache retention and full-length equivalence are not completed by this API.

Scorecard: 2/2/4/7/1/4/1. Selective rendering rises 1→4 because the actual-rig fixture now demonstrates correct reuse; 10 still requires production integration and repeated trials. No clarity/safety/delivery/audience improvement is claimed. M90 OPEN records a corrected pipe-cleanup error and invalid positive audio fixture.

Carry the renderer, tests, benchmark, docs/SELECTIVE_RENDERING.md and report. Rollback: revert the destination commit and retain the existing rendering call. No live gates, agent contracts or production accounts were touched.
