% ============================================================================
% KEY AND LOCK PLACEMENT
% Classic Zelda-style key-before-lock constraints
% Expects room/1, connects/2, room_type/2, edge/2 from graph layer
% ============================================================================

% --- Configuration ---
#const num_keys = 2.

% --- Key colors ---
key_color(red).
key_color(blue).

% Use first N colors
active_color(C) :- key_color(C), C = red, num_keys >= 1.
active_color(C) :- key_color(C), C = blue, num_keys >= 2.

% --- Key placement ---
% Each active key placed in exactly one room
{ key_in(C, R) : room(R) } = 1 :- active_color(C).

% --- Lock placement ---
% Each active key has exactly one locked door
{ locked_door(R1, R2, C) : connects(R1, R2) } = 1 :- active_color(C).
{ locked_door(R1, R2, C) : connects(R2, R1) } = 1 :- active_color(C).

% Normalize locked doors (smaller room first)
locked_door_norm(R1, R2, C) :- locked_door(R1, R2, C), R1 < R2.
locked_door_norm(R2, R1, C) :- locked_door(R1, R2, C), R1 >= R2.

% --- Key-before-lock constraint ---
% A room is key-reachable if you can get there without passing through the lock

% Start from spawn
key_reachable(C, R) :- active_color(C), room_type(R, spawn).

% Can reach adjacent rooms if not blocked by THIS key's lock
key_reachable(C, R2) :-
    key_reachable(C, R1),
    edge(R1, R2),
    not locked_door_norm(R1, R2, C),
    not locked_door_norm(R2, R1, C).

% Key must be in a key-reachable room
:- key_in(C, R), not key_reachable(C, R).

% --- Additional constraints ---

% No keys in spawn room (too easy)
:- key_in(C, R), room_type(R, spawn).

% No keys in boss room
:- key_in(C, R), room_type(R, boss).

% Lock should be on path to boss (not blocking side areas only)
% Boss must be reachable after getting all keys
all_keys_reachable(R) :- room_type(R, spawn).
all_keys_reachable(R2) :-
    all_keys_reachable(R1),
    edge(R1, R2),
    not blocked_without_key(R1, R2).

blocked_without_key(R1, R2) :- locked_door_norm(R1, R2, _).
blocked_without_key(R1, R2) :- locked_door_norm(R2, R1, _).

% Actually we want: boss IS reachable once you have all keys
% This is automatically true if the graph is connected and locks don't form cycles

% --- Output ---
#show key_in/2.
#show locked_door_norm/3.
#show key_reachable/2.
