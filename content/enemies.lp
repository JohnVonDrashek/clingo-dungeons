% ============================================================================
% ENEMY PLACEMENT
% Places enemies with difficulty scaling
% Expects room/1, room_type/2, min_dist/2 from graph layer
% ============================================================================

% --- Configuration ---
#const num_enemies = 6.
#const max_enemies_per_room = 3.

% --- Enemy types with difficulty levels ---
enemy_type(slime, 1).
enemy_type(goblin, 2).
enemy_type(skeleton, 3).
enemy_type(orc, 4).
enemy_type(demon, 5).

% --- Generate enemies ---
enemy(1..num_enemies).

% Each enemy has a type
{ enemy_is(E, T) : enemy_type(T, _) } = 1 :- enemy(E).

% Each enemy in exactly one room
{ enemy_in(E, R) : room(R) } = 1 :- enemy(E).

% Get enemy difficulty
enemy_difficulty(E, D) :- enemy_is(E, T), enemy_type(T, D).

% --- Constraints ---

% No enemies in spawn room
:- enemy_in(E, R), room_type(R, spawn).

% Boss room has exactly one enemy (the boss itself is separate)
% For now, no regular enemies in boss room
:- enemy_in(E, R), room_type(R, boss).

% Max enemies per room
:- room(R), #count { E : enemy_in(E, R) } > max_enemies_per_room.

% --- Difficulty scaling ---
% Enemies should generally match room distance from spawn
% Low-difficulty enemies in early rooms, high-difficulty in later rooms

% A room's expected difficulty tier (1-5 based on distance)
room_tier(R, T) :- min_dist(R, D), room(R),
                   T = 1 + (D * 4) / num_rooms.  % Scale 0..num_rooms to 1..5

% Enemy difficulty should be within 1 of room tier
:- enemy_in(E, R), enemy_difficulty(E, ED), room_tier(R, RT),
   |ED - RT| > 1.

% --- Output ---
#show enemy_in/2.
#show enemy_is/2.
#show enemy_difficulty/2.
#show room_tier/2.
