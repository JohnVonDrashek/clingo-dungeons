% ============================================================================
% ITEM PLACEMENT
% Places items in rooms based on constraints
% Expects room/1, room_type/2, min_dist/2 from graph layer
% ============================================================================

% --- Configuration ---
#const num_items = 5.
#const max_items_per_room = 2.

% --- Item types ---
item_type(health_potion).
item_type(mana_potion).
item_type(gold).
item_type(weapon).
item_type(armor).

% --- Generate items ---
item(1..num_items).

% Each item has a type
{ item_is(I, T) : item_type(T) } = 1 :- item(I).

% Each item placed in exactly one room
{ item_in(I, R) : room(R) } = 1 :- item(I).

% --- Constraints ---

% No items in spawn room (player starts there)
:- item_in(I, R), room_type(R, spawn).

% No items in boss room (special encounter)
:- item_in(I, R), room_type(R, boss).

% Max items per room
:- room(R), #count { I : item_in(I, R) } > max_items_per_room.

% Weapons should be in early/mid rooms (help player before boss)
:- item_is(I, weapon), item_in(I, R), min_dist(R, D), D > num_rooms * 2 / 3.

% --- Output ---
#show item_in/2.
#show item_is/2.
