% ============================================================================
% COARSE ROOM PLACEMENT
% Places rooms on a coarse grid to reduce search space
% Expects room/1 and connects/2 facts from graph layer
% ============================================================================

% --- Configuration ---
#const grid_cells_x = 4.   % Number of cells horizontally
#const grid_cells_y = 4.   % Number of cells vertically
#const cell_size = 12.     % Pixels per cell
#const min_room_size = 5.
#const max_room_size = 9.

% Derived grid size
#const grid_width = grid_cells_x * cell_size.
#const grid_height = grid_cells_y * cell_size.

% --- Room dimensions ---
{ room_w(R, W) : W = min_room_size..max_room_size } = 1 :- room(R).
{ room_h(R, H) : H = min_room_size..max_room_size } = 1 :- room(R).

% --- Coarse grid positions ---
% Rooms placed at cell origins (multiples of cell_size)
cell_x(C) :- C = 0..grid_cells_x-1.
cell_y(C) :- C = 0..grid_cells_y-1.

{ room_cell_x(R, C) : cell_x(C) } = 1 :- room(R).
{ room_cell_y(R, C) : cell_y(C) } = 1 :- room(R).

% Convert cell to pixel position
room_x(R, C * cell_size) :- room_cell_x(R, C).
room_y(R, C * cell_size) :- room_cell_y(R, C).

% --- Derived bounds ---
room_x2(R, X+W-1) :- room_x(R, X), room_w(R, W).
room_y2(R, Y+H-1) :- room_y(R, Y), room_h(R, H).

% Room center
room_cx(R, X+W/2) :- room_x(R, X), room_w(R, W).
room_cy(R, Y+H/2) :- room_y(R, Y), room_h(R, H).

% --- Non-overlap (cell level) ---
% Two rooms can't occupy the same cell
:- room(R1), room(R2), R1 < R2,
   room_cell_x(R1, CX), room_cell_y(R1, CY),
   room_cell_x(R2, CX), room_cell_y(R2, CY).

% --- Output ---
#show room_x/2.
#show room_y/2.
#show room_w/2.
#show room_h/2.
#show room_cx/2.
#show room_cy/2.
#show room_cell_x/2.
#show room_cell_y/2.
