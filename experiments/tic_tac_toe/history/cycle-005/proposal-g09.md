- [2026-04-20] PROPOSAL target:play-tic-tac-toe (Q^L: 3.17->2.56, td:-1.23, strength:hard)
    problem: aggregated G2 evidence indicates sub-optimal behavior.
    gradient: |
      (see updated spec text)
    diff: |
      <<EVOLVE NOTE (shim+engine) - textual gradient summary>>
        [g1] Identify concrete edits to the parent skill specs that would have prevented the observed failures and amplified the observed successes. Keep YAML frontmatter intact. Preserve public trigger semantics. Be specific - cite section names when possible. Session critique: [play-tic-tac-toe] net_delta=-1 td=-1.23 strength=hard evidence="result=forfeit; moves=[]; total_mistakes=0; forfeit_side=X; bad_output='<engine error: RuntimeError: claude CLI exited 1: (no stderr)>'; last_err=RuntimeError'"
      <<END EVOLVE NOTE>>
      <<EVOLVE NOTE (shim+engine) - textual gradient summary>>
        [g1] Identify concrete edits to the parent skill specs that would have prevented the observed failures and amplified the observed successes. Keep YAML frontmatter intact. Preserve public trigger semantics. Be specific - cite section names when possible. Session critique: [play-tic-tac-toe] net_delta=-1 td=-1.62 strength=hard evidence="result=forfeit; moves=[]; total_mistakes=0; forfeit_side=X; bad_output='<engine error: RuntimeError: claude CLI exited 1: (no stderr)>'; last_err=RuntimeError'"
      <<END EVOLVE NOTE>>
      <<EVOLVE NOTE (shim+engine) - textual gradient summary>>
        [g1] Identify concrete edits to the parent skill specs that would have prevented the observed failures and amplified the observed successes. Keep YAML frontmatter intact. Preserve public trigger semantics. Be specific - cite section names when possible. Session critique: [play-tic-tac-toe] net_delta=-1 td=-2.07 strength=hard evidence="result=forfeit; moves=[X5 O1 X9 O7 X4 O6 X3 O8]; total_mistakes=0; forfeit_side=X; bad_output='<engine error: RuntimeError: claude CLI exited 1: (no stderr)>'; last_err=RuntimeError'"
      <<END EVOLVE NOTE>>
      <<EVOLVE NOTE (shim+engine) - textual gradient summary>>
      Add a "Strategy" section after "Move format" that prioritizes moves: (1) take a winning cell if available this turn; (2) block opponent's winning cell if they can win next turn; (3) prefer 
      ... (truncated; full candidate stored in evolve-apply staging)
    evidence: "result=forfeit; moves=[]; total_mistakes=0; forfeit_side=X; bad_output='<engine error: RuntimeError: claude CLI exited 1: (no stderr)>'; last_err=RuntimeError'"
    risk: Edit affects trigger description or process steps; rollback snapshot will be stored in td-nl/history/.