# Agent craft research, 9 Oct 2026

## Decision

Make five small changes now: ground every claim in a tool result, have `return_check.py` open the evidence it is given, give every number one owner, give every brief a fixed four-part shape, and put a call tally in each agent. Change the comedy reviewer's rubric last, and treat it as a trial. Do not add agents, do not add "double-check" lines, and do not rewrite the agent files wholesale.

Evidence is strongest for the first four problems (false checks, overruns, ping-pong, vague briefs). It is weakest for comedy. Research says LLM humor judging agrees only loosely with humans, so a blind score under 7 may be the reviewer's rubric, the scripts, or the jokes, and we cannot tell which yet. Row 8 is the only way to find out, and it uses the one real audience test we have (YouTube data).

Scope: I read only `animator.md` and `fresh-eyes-reviewer.md`. The other four agents are not reviewed, so rows naming them are inferred from the problem list. Sources were read through a summarising fetch tool, not verbatim, and the arXiv items were abstracts only. Access: all links below loaded.

## Findings

| # | Finding | Which agent | Exact rule change (≤25 words) | Source |
|---|---|---|---|---|
| 1 | Telling a model to audit each progress claim against a tool result from this session nearly removed invented status reports in Anthropic's tests. | All six (rules card) | "Before returning, match every claim to a tool result from this session. Any claim without one is written as 'not checked'." | [Prompting Claude Fable 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5) |
| 2 | A model re-checking itself with no outside signal is unreliable and can make answers worse. Checks need tool output or another source. Tool errors should say what is wrong and how to fix it. | Lead (`return_check.py`) | Script opens each evidence path, confirms the file exists and any number appears in script output; on failure it prints the missing item and the fix. | [Huang et al., self-correction](https://arxiv.org/abs/2310.01798); [Writing tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents) |
| 3 | Vague briefs made subagents misread the job or repeat each other's work. Each brief needs an objective, an output format, tools or sources, and a firm boundary. | Lead | Every brief has four lines: Objective, Output (file and format), Use only (files, tools), Not your job. Nothing else is accepted. | [Anthropic multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system) |
| 4 | Without explicit effort limits, agents overspend on easy work. In Claude Code, `maxTurns` ends a run as partial, and the agent can be resumed. | Animator, then all | "Put 'calls n/budget' in every tool-call note. At 80%, start no new work: write the return, list what is left." | [Multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system); [Subagents docs](https://code.claude.com/docs/en/sub-agents) |
| 5 | Agents working apart bake in unstated assumptions that conflict. Multi-agent failure studies put "inter-agent misalignment" as one of three main failure groups. | Lead, animator, story-designer | "Each number has one owner. Others copy it from the owner's file, never restate or change it. A dispute goes to the Lead once." | [Cognition, Don't build multi-agents](https://cognition.com/blog/dont-build-multi-agents); [MAST taxonomy](https://arxiv.org/abs/2503.13657) |
| 6 | LLM humor judges weigh novelty most; humans weigh empathy most; agreement is limited. Per-dimension rubrics with an "unknown" option reduce guessing. | Fresh-eyes reviewer | "LANDED needs a visible grin or held reaction. Score set-up, break, reaction 1-5 each; write 'unclear' rather than guess. Novelty alone is NOT LANDED." | [Oogiri humor study, AAAI](https://ojs.aaai.org/index.php/AAAI/article/view/40567); [Demystifying evals](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) |
| 7 | Judges favour their own model's output and longer answers; Anthropic advises grading with a different model than the one that made the work. | Lead (reviewer setup) | "Run the blind reviewer on a different model from the animator. Keep the fixed anchors; never compare scores across reviewer models." | [Zheng et al., LLM-as-judge](https://arxiv.org/abs/2306.05685); [Develop tests](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests) |
| 8 | A model grader must be calibrated against humans before its scores are trusted. Our only human signal is YouTube data. | Growth-analyst | "Log each episode's blind comedy score beside its average view duration. After five episodes, report whether they move together." | [Demystifying evals](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) |
| 9 | Generating many gag candidates from different strategies, dropping near-duplicates, then ranking gave a modest gain. This is a small study (13 human judges), so weak evidence. | Story-designer | "Per beat, draft six gags from different character traits, drop near-duplicates, keep the best two with a one-line reason." | [HumorPlanSearch](https://arxiv.org/html/2508.11429v1) |
| 10 | Three to five relevant, varied examples in tags improve accuracy and consistency. Our agents each have one example, and it is always a pass. | Animator, reviewer (then rest) | Add one FAIL example per agent showing a "not checked" line and a blocking issue, in `<example>` tags. | [Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices) |

## Reading the evidence

- The three problems you named first all have the same root: the agent reports what it intended, not what a tool returned. Rows 1 and 2 together fix this at the agent and at the checker. Row 2 matters more, because Anthropic's own guidance and the self-correction research both say a model checking itself is weak, while a script opening a file is not.
- Overruns: our animator has `maxTurns: 62` and a 60-call build budget. The agent's budget is a prompt rule, and the hard stop is a different counter. Row 4 makes the rule visible to the agent; whether the two counts line up is a Lead check I did not run.
- Ping-pong: row 5 is partly done already (animator "owns the numbers", rule 1). The gap is the other two agents restating those numbers.
- Comedy: do rows 6 to 8 in that order, one episode each, so a change in score can be traced to one cause.

## Don't change

- Keep the rules-card pattern, the JSON return block, and the stop-at-budget rule; they match Anthropic's advice on clear boundaries and explicit limits.
- Do not add "verify twice" or "use a subagent to double-check" lines. Anthropic says Opus 5 already verifies and such lines only add cost; it also says not to use subagents to check your own work.
- Keep the blind, new-instance-per-round reviewer; it is the outside check that research favours.
- Do not move to parallel agent teams. The research warns they diverge; our sequential hand-offs are the safer shape.
