# Episode 11: build fixes before blind round 3 (Lead, from the key sheet, 7 Oct 21:30)
The render of 7 Oct 21:01 passed check_video but has 4 build misses. Fix, check with stills, then return the commands.
Done by the Lead already (keep): shot 4 camera = shot 1's (1484, 1285) 2.2 (the 1.9x camera showed Snip smiling
beside sad Pip); HI40B points at a missing folder (the round-2 40b frames were stale: old staging, white marker);
SKY_PROBE moved to (1590, 760) (did NOT fix item 1). Backup of the code before these: build/ep11_friendly_glow.before_lead_fix.py.

1. **Gold railing cut-outs after sunset** (seen at 11.5 s, two hearts gold, one purple). Fix file sb2 says the
   cut-outs are never gold after the sun has gone (T_LIGHT_OUT). rail_glow2 is off after 9.4 s, so find what else
   paints them (a heart-light layer? the wall hearts' sparkle-out?). Check with --still 10.0, 11.5, 12.5.
2. **Snip's marker white after the hand cuts** (seen at 144.5 s; a white marker read as a knife). It must be blue
   in EVERY shot from ~84 s to the end. Check with --still 120.3, 133, 144.5.
3. **The 40b shot (143.5-146.1) re-renders at 3x from the current code** (no reuse). Confirm --still 144.0 matches
   the sb3 sheet (Pip's wing up catching the smile).
4. **Crinkle's face hidden by Snip's head at 42.1 s:** shift so both faces show (or ≤0.3 s).

Then return ≤80 words with the exact commands (hires pass, render, check_video --cuts, keys). No full render; no commit.
