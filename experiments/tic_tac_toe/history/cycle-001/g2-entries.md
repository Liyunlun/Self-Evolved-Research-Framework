- [2026-04-20] session:ttt-c001 node:g1 upstream:- skill:play-tic-tac-toe
    P1_analysis: "Game 1 of batch; skill plays X vs minimax. Trajectory: 9 moves, terminal=draw."
    P2_predict:  V=4, conf=med, reason="self-estimate pre-game from running forfeit rate"
    P4_strategy: keep, note=""
    P5_result:   outcome=better, reward=+0, ev="skill=X; result=draw; winner=draw; moves=[X5 O1 X9 O3 X2 O8 X4 O6 X7]"
- [2026-04-20] session:ttt-c001 node:g2 upstream:g1 skill:play-tic-tac-toe
    P1_analysis: "Game 2 of batch; skill plays O vs minimax. Trajectory: 9 moves, terminal=draw."
    P2_predict:  V=4, conf=high, reason="self-estimate pre-game from running forfeit rate"
    P3_td:       delta=+0.0, interp="reward change vs prior game"
    P4_strategy: keep, note=""
    P5_result:   outcome=better, reward=+0, ev="skill=O; result=draw; winner=draw; moves=[X1 O5 X2 O3 X7 O4 X6 O8 X9]"
