% ============================================================================
% POKEMON MYSTERY DUNGEON - FLOOR GENERATOR
% Generates room topology, grid placement, and content distribution
% ============================================================================

#const num_rooms = 7.
#const num_items = 4.
#const num_enemies = 5.
#const num_traps = 2.
#const grid_size = 4.  % Coarse grid for room placement (4x4)
#const min_room_size = 4.
#const max_room_size = 8.

% --- Rooms ---
room(1..num_rooms).

% --- Room types ---
{ has_stairs(R) : room(R) } = 1.
{ is_spawn(R) : room(R) } = 1.
:- has_stairs(R), is_spawn(R).

% --- Connections (corridors) ---
{ corridor(R1, R2) : room(R1), room(R2), R1 < R2 }.

edge(R1, R2) :- corridor(R1, R2).
edge(R2, R1) :- corridor(R1, R2).

connections(R, C) :- room(R), C = #count { R2 : edge(R, R2) }.
:- room(R), connections(R, 0).
:- room(R), connections(R, C), C > 3.

% --- Connectivity ---
reachable(R) :- is_spawn(R).
reachable(R2) :- reachable(R1), edge(R1, R2).
:- room(R), not reachable(R).

% ============================================================================
% CONTENT
% ============================================================================

item(1..num_items).
item_type(apple; oran_berry; reviver_seed; escape_orb).
{ item_in(I, R) : room(R) } = 1 :- item(I).
{ item_is(I, T) : item_type(T) } = 1 :- item(I).
:- room(R), #count { I : item_in(I, R) } > 2.
:- item_in(I, R), is_spawn(R).

enemy(1..num_enemies).
enemy_type(rattata; zubat; geodude; sandshrew).
{ enemy_in(E, R) : room(R) } = 1 :- enemy(E).
{ enemy_is(E, T) : enemy_type(T) } = 1 :- enemy(E).
:- room(R), #count { E : enemy_in(E, R) } > 2.
:- enemy_in(E, R), is_spawn(R).

trap(1..num_traps).
trap_type(spike; pokemon; warp; sticky).
{ trap_in(T, R) : room(R) } = 1 :- trap(T).
{ trap_is(T, Ty) : trap_type(Ty) } = 1 :- trap(T).
:- trap_in(T, R), is_spawn(R).

% Count content per room for sizing
item_count(R, C) :- room(R), C = #count { I : item_in(I, R) }.
enemy_count(R, C) :- room(R), C = #count { E : enemy_in(E, R) }.
trap_count(R, C) :- room(R), C = #count { T : trap_in(T, R) }.
content_count(R, CI+CE+CT) :- item_count(R, CI), enemy_count(R, CE), trap_count(R, CT).

% ============================================================================
% GRID POSITIONING - Coarse grid placement (no pixel-level positioning)
% ============================================================================

% Grid positions
grid_pos(0..grid_size-1).

% Each room gets a grid position
{ room_gx(R, X) : grid_pos(X) } = 1 :- room(R).
{ room_gy(R, Y) : grid_pos(Y) } = 1 :- room(R).

% No two rooms at same grid position
:- room_gx(R1, X), room_gx(R2, X), room_gy(R1, Y), room_gy(R2, Y), R1 < R2.

% Room dimensions (4-8 range) - chosen by ASP
{ room_width(R, W) : W = min_room_size..max_room_size } = 1 :- room(R).
{ room_height(R, H) : H = min_room_size..max_room_size } = 1 :- room(R).

% Connected rooms should be adjacent (Manhattan distance <= 2)
grid_dist(R1, R2, D) :- room(R1), room(R2), R1 != R2,
    room_gx(R1, X1), room_gx(R2, X2), room_gy(R1, Y1), room_gy(R2, Y2),
    D = |X1-X2| + |Y1-Y2|.
:- corridor(R1, R2), grid_dist(R1, R2, D), D > 2.

% Soft constraints: prefer larger rooms for rooms with more content
:~ room(R), content_count(R, C), C >= 2, room_width(R, W), W < 5. [1@1, R, w]
:~ room(R), content_count(R, C), C >= 2, room_height(R, H), H < 5. [1@1, R, h]

% Spawn and stairs rooms should be at least 5x5
:~ is_spawn(R), room_width(R, W), W < 5. [2@1, R, spawn_w]
:~ is_spawn(R), room_height(R, H), H < 5. [2@1, R, spawn_h]
:~ has_stairs(R), room_width(R, W), W < 5. [2@1, R, stairs_w]
:~ has_stairs(R), room_height(R, H), H < 5. [2@1, R, stairs_h]

% ============================================================================
% OUTPUT
% ============================================================================

#show room/1.
#show corridor/2.
#show is_spawn/1.
#show has_stairs/1.
#show room_gx/2.
#show room_gy/2.
#show room_width/2.
#show room_height/2.
#show item_in/2.
#show item_is/2.
#show enemy_in/2.
#show enemy_is/2.
#show trap_in/2.
#show trap_is/2.
