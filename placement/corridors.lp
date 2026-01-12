% ============================================================================
% CORRIDOR GENERATION
% Creates L-shaped corridors between connected rooms
% Include after rooms.lp and non_overlap.lp
% ============================================================================

% --- Configuration ---
#const corridor_width = 3.

% --- Corridor between connected rooms ---
% For simplicity, use L-shaped corridors (horizontal then vertical or vice versa)
% Choose which turn direction for each connection

{ corridor_h_first(R1, R2) } :- connects(R1, R2).
corridor_v_first(R1, R2) :- connects(R1, R2), not corridor_h_first(R1, R2).

% Also handle reverse direction
corridor_h_first(R2, R1) :- corridor_h_first(R1, R2), R1 < R2.
corridor_v_first(R2, R1) :- corridor_v_first(R1, R2), R1 < R2.

% --- Corridor tiles (simplified: center-to-center L-path) ---
% Horizontal-first: go from R1 center horizontally to R2's X, then vertically
corridor_tile(X, CY1) :-
    corridor_h_first(R1, R2), R1 < R2,
    room_cx(R1, CX1), room_cy(R1, CY1),
    room_cx(R2, CX2),
    X = CX1..CX2.
corridor_tile(X, CY1) :-
    corridor_h_first(R1, R2), R1 < R2,
    room_cx(R1, CX1), room_cy(R1, CY1),
    room_cx(R2, CX2),
    CX2 < CX1,
    X = CX2..CX1.

corridor_tile(CX2, Y) :-
    corridor_h_first(R1, R2), R1 < R2,
    room_cy(R1, CY1), room_cy(R2, CY2),
    room_cx(R2, CX2),
    Y = CY1..CY2.
corridor_tile(CX2, Y) :-
    corridor_h_first(R1, R2), R1 < R2,
    room_cy(R1, CY1), room_cy(R2, CY2),
    room_cx(R2, CX2),
    CY2 < CY1,
    Y = CY2..CY1.

% Vertical-first: go from R1 center vertically to R2's Y, then horizontally
corridor_tile(CX1, Y) :-
    corridor_v_first(R1, R2), R1 < R2,
    room_cx(R1, CX1), room_cy(R1, CY1),
    room_cy(R2, CY2),
    Y = CY1..CY2.
corridor_tile(CX1, Y) :-
    corridor_v_first(R1, R2), R1 < R2,
    room_cx(R1, CX1), room_cy(R1, CY1),
    room_cy(R2, CY2),
    CY2 < CY1,
    Y = CY2..CY1.

corridor_tile(X, CY2) :-
    corridor_v_first(R1, R2), R1 < R2,
    room_cx(R1, CX1), room_cy(R2, CY2),
    room_cx(R2, CX2),
    X = CX1..CX2.
corridor_tile(X, CY2) :-
    corridor_v_first(R1, R2), R1 < R2,
    room_cx(R1, CX1), room_cy(R2, CY2),
    room_cx(R2, CX2),
    CX2 < CX1,
    X = CX2..CX1.

% --- Output ---
#show corridor_tile/2.
#show corridor_h_first/2.
#show corridor_v_first/2.
