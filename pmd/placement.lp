% Room placement using ASP
% Input: room sizes, connections
% Output: room positions satisfying constraints

#const min_gap = 2.

% Each room gets a position within bounds
{ room_x(R, X) : X = 0..bound_x } = 1 :- room(R).
{ room_y(R, Y) : Y = 0..bound_y } = 1 :- room(R).

% No overlap: for any two rooms, they must be separated on at least one axis
% Room R1 right edge + gap <= Room R2 left edge, OR vice versa, OR same for Y
separated_x(R1, R2) :- room_x(R1, X1), room_x(R2, X2), room_w(R1, W1),
                       X1 + W1 + min_gap <= X2, R1 < R2.
separated_x(R1, R2) :- room_x(R1, X1), room_x(R2, X2), room_w(R2, W2),
                       X2 + W2 + min_gap <= X1, R1 < R2.
separated_y(R1, R2) :- room_y(R1, Y1), room_y(R2, Y2), room_h(R1, H1),
                       Y1 + H1 + min_gap <= Y2, R1 < R2.
separated_y(R1, R2) :- room_y(R1, Y1), room_y(R2, Y2), room_h(R2, H2),
                       Y2 + H2 + min_gap <= Y1, R1 < R2.

% Must be separated on at least one axis
:- room(R1), room(R2), R1 < R2, not separated_x(R1, R2), not separated_y(R1, R2).

% Connected rooms: penalize distance (soft constraint via optimization)
% Manhattan distance between room centers
dist(R1, R2, D) :- connection(R1, R2),
                   room_x(R1, X1), room_x(R2, X2), room_w(R1, W1), room_w(R2, W2),
                   room_y(R1, Y1), room_y(R2, Y2), room_h(R1, H1), room_h(R2, H2),
                   CX1 = X1 + W1/2, CX2 = X2 + W2/2,
                   CY1 = Y1 + H1/2, CY2 = Y2 + H2/2,
                   D = |CX1 - CX2| + |CY1 - CY2|.

% Minimize total distance between connected rooms
#minimize { D,R1,R2 : dist(R1, R2, D) }.

#show room_x/2.
#show room_y/2.
