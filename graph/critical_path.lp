% ============================================================================
% CRITICAL PATH CONSTRAINTS
% Ensures meaningful progression from spawn to boss
% Include after topology.lp
% ============================================================================

% --- Configuration ---
#const min_boss_distance = 3.  % Boss must be at least this far from spawn

% --- Distance calculation from spawn ---
% A room is reachable at distance D if there's a path of length D
dist(R, 0) :- room_type(R, spawn).
dist(R2, D+1) :- dist(R1, D), edge(R1, R2), D < num_rooms.

% Minimum distance is the smallest D for which dist(R, D) holds
min_dist(R, D) :- dist(R, D), #false : dist(R, D2), D2 < D.

% --- Boss distance constraint ---
:- room_type(R, boss), min_dist(R, D), D < min_boss_distance.

% --- Critical path: shortest path from spawn to boss ---
% Mark rooms on at least one shortest path to boss
on_critical_path(R) :- room_type(R, spawn).
on_critical_path(R) :- room_type(R, boss).

% Room is on critical path if it's between spawn and boss distance-wise
% and connects to both a closer and farther critical path room
on_critical_path(R) :-
    min_dist(R, D), D > 0,
    room_type(Boss, boss), min_dist(Boss, BossD), D < BossD,
    edge(R, Prev), min_dist(Prev, D-1), on_critical_path(Prev).

% --- Optional: boss should have limited connections (dead end feel) ---
% Uncomment to enforce:
% :- room_type(R, boss), connection_count(R, C), C > 1.

% --- Special room placement hints ---
% Shop should not be on critical path (optional detour)
% Uncomment to enforce:
% :- room_type(R, shop), on_critical_path(R).

% Treasure should be off critical path
% Uncomment to enforce:
% :- room_type(R, treasure), on_critical_path(R).

% --- Output ---
#show min_dist/2.
#show on_critical_path/1.
