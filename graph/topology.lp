% ============================================================================
% DUNGEON GRAPH TOPOLOGY
% Generates abstract room connectivity graph for roguelike dungeons
% ============================================================================

% --- Configuration (override with #const or extra facts) ---
#const num_rooms = 8.
#const min_connections = 1.  % Minimum connections per room (except dead ends)
#const max_connections = 3.  % Maximum connections per room
#const allow_cycles = 1.     % 1 = allow cycles, 0 = tree only

% --- Room generation ---
room(1..num_rooms).

% --- Room types ---
% Exactly one spawn and one boss room
{ room_type(R, spawn) : room(R) } = 1.
{ room_type(R, boss) : room(R) } = 1.

% Optional special rooms (0 or 1 of each)
{ room_type(R, shop) : room(R) } <= 1.
{ room_type(R, treasure) : room(R) } <= 1.

% Rooms without special type are normal
room_type(R, normal) :- room(R), not room_type(R, spawn),
                        not room_type(R, boss), not room_type(R, shop),
                        not room_type(R, treasure).

% --- Connections ---
% Choose which rooms connect (undirected, so R1 < R2)
{ connects(R1, R2) : room(R1), room(R2), R1 < R2 }.

% Symmetric access for easier constraint writing
edge(R1, R2) :- connects(R1, R2).
edge(R2, R1) :- connects(R1, R2).

% --- Connection count constraints ---
connection_count(R, C) :- room(R), C = #count { R2 : edge(R, R2) }.

% Every room must have at least 1 connection (no isolated rooms)
:- room(R), connection_count(R, 0).

% Respect max connections
:- room(R), connection_count(R, C), C > max_connections.

% --- Connectivity: all rooms reachable from spawn ---
reachable(R) :- room_type(R, spawn).
reachable(R2) :- reachable(R1), edge(R1, R2).
:- room(R), not reachable(R).

% --- Cycle control ---
% For tree-only mode: exactly num_rooms - 1 edges
:- allow_cycles = 0, #count { R1, R2 : connects(R1, R2) } != num_rooms - 1.

% --- Output ---
#show room/1.
#show room_type/2.
#show connects/2.
