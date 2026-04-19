# Skill Feedback Log
<!-- Append-only during sessions. Processed by evolve-suggest at session-close. -->
<!-- After processing, entries move to "Processed" section below. -->

<!-- SCHEMA v3 (5-phase inline TD; preferred):
     Each G2 entry is a 6-line block:

     - [DATE] session:{sid} node:{nid} upstream:{csv|-} skill:{name}
         P1_analysis: "key features; V^L coverage gap; watch-outs from prior failures"
         P2_predict:  V={1-10}, conf={high|med|low}, reason="why this V"
         P3_td:       delta={float}, interp="why the surprise"    # omit on root firings
         P4_strategy: {refine|keep|reset}, note="concrete adjustment"
         P5_result:   outcome={better|as_expected|worse}, reward={+1|0|-1}, ev="post-hoc evidence"

     Field roles:
       - P2_predict.V    : self-estimate of Q^L BEFORE firing; replaces bootstrap in td_layer
       - P3_td.delta     : inline TD error = reward_prev + gamma*V(curr) - V(prev);
                           omit on root firings (upstream:-) - no previous reward to use
       - P5_result.reward: observed outcome of THIS firing; used as r for the NEXT firing's P3

     SCHEMA v2 (single-line DAG-aware; still accepted):
       - [DATE] session:{sid} node:{nid} upstream:{csv|-} skill:{name} | outcome:{o} | delta:{d} | "{evidence}"

     SCHEMA v1 (legacy single-line; still accepted, treated as isolated root firings):
       - [DATE] skill:{name} | outcome:{o} | delta:{d} | "{evidence}" -->

## Pending Feedback

<!-- Append new G2 entries below this comment. HTML comment blocks are
     ignored by the parser, so schema examples above do not pollute the
     live log. Prefer v3 blocks; v2/v1 single-lines also accepted. -->

## Pending Proposals

<!-- Spec-edit proposals produced by evolve-suggest / textgrad backward.
     evolve-apply consumes entries from here. Format:

  - [DATE] PROPOSAL target:{skill} (Q^L: {old}->{new}, delta:{td_error})
      problem: "..."
      gradient: "..."       # aggregated textual gradient
      diff: "..."           # suggested change to SKILL.md
      evidence: "..."
      risk: "..."
-->

## Processed Feedback

<!-- Processed cycle format (written by evolve-suggest at session-close):
- Cycle YYYY-MM-DD [session:{sid}]: {N} entries across {M} skills (V^L {old}->{new})
  - {skill}: net_delta={N}, td_error={d}, strength={hard|soft|drop}
  - Spec proposal: {yes|none}
-->
