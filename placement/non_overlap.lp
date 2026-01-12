% ============================================================================
% NON-OVERLAP CONSTRAINTS
% Ensures rooms don't overlap (with padding)
% Include after rooms.lp
% ============================================================================

% Two rooms overlap if their padded bounding boxes intersect
% R1's right edge + padding >= R2's left edge AND
% R2's right edge + padding >= R1's left edge AND
% (same for Y axis)

overlap(R1, R2) :-
    room(R1), room(R2), R1 < R2,
    room_x(R1, X1), room_x2(R1, X1E), room_x(R2, X2), room_x2(R2, X2E),
    room_y(R1, Y1), room_y2(R1, Y1E), room_y(R2, Y2), room_y2(R2, Y2E),
    X1E + room_padding >= X2, X2E + room_padding >= X1,
    Y1E + room_padding >= Y2, Y2E + room_padding >= Y1.

% No overlap allowed
:- overlap(R1, R2).
