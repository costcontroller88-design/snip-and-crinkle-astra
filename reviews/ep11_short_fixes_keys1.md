# Ep 11 transformation Short: Lead key-sheet fixes before the full render (8 Oct)

Key sheet: reviews/ep11_short_transform_keys.png. Takes 0.7-1.9 and give-back 3.9-4.6: OK for look and size, keep.

| # | Time | Problem (Lead, at 1,600 px) | Fix wanted |
|---|---|---|---|
| K1 | 22.0-26.0 | The new 1.6x camera makes the cause of the wow too small: the tea light is ~3% of the width and the click/LED dome can't be seen; the lantern is ~20% of the width. Gate 1b already flagged "nobody lights it, glow reads as magic". Lesson 2: small key things get a ≥1.2 s close-up. | Go back to a close camera for shot 10 (plan: B 2.0x or tighter) so the lantern is ≥40% of the width and the tea light with its lit LED dome is clearly visible for ≥1.2 s (click → dome on → lowered in). The hand may enter from the top edge (forearm only is fine). Characters need not be in this shot; the pull-back at 26.0 shows them. Keep the 26.0+ pull-back within 0.35x/s. |
| K2 | 13.6 | Marker 15.9 units from Pip's face at the cut. | ≥30 units at all times (as elsewhere), or move the cut. |
| K3 | all | Give-back fixes came after the last full `--check`; the 6 s change rule was not checked. | Re-run `--check` on the whole Short and report the numbers; check no 6 s without a change. |

Deliver: updated key sheet (same path) with 22.0-26.0 at 0.3 s steps; don't render; don't commit.
