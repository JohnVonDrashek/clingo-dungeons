% ============================================================================
% ROOM PLACEMENT
% Places rooms in 2D grid space
% Expects room/1 and connects/2 facts from graph layer
% ============================================================================

% --- Configuration ---
#const grid_width = 40.
#const grid_height = 40.
#const min_room_size = 5.
#const max_room_size = 9.
#const room_padding = 2.  % Min gap between rooms

% --- Room dimensions ---
% Each room chooses a width and height
{ room_w(R, W) : W = min_room_size..max_room_size } = 1 :- room(R).
{ room_h(R, H) : H = min_room_size..max_room_size } = 1 :- room(R).

% --- Room positions ---
% Each room chooses a position (top-left corner)
{ room_x(R, X) : X = 0..grid_width } = 1 :- room(R).
{ room_y(R, Y) : Y = 0..grid_height } = 1 :- room(R).

% Room must fit within grid
:- room(R), room_x(R, X), room_w(R, W), X + W > grid_width.
:- room(R), room_y(R, Y), room_h(R, H), Y + H > grid_height.

% --- Derived bounds ---
room_x2(R, X+W-1) :- room_x(R, X), room_w(R, W).
room_y2(R, Y+H-1) :- room_y(R, Y), room_h(R, H).

% Room center (for corridor routing)
room_cx(R, X+W/2) :- room_x(R, X), room_w(R, W).
room_cy(R, Y+H/2) :- room_y(R, Y), room_h(R, H).

% --- Output ---
#show room_x/2.
#show room_y/2.
#show room_w/2.
#show room_h/2.
#show room_cx/2.
#show room_cy/2.
