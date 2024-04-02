
% If none is with me and I am hungry, I am sad to eat alone
sad(X) :- alone(true), people(X).

% If I am with someone and we both want to eat the same food, we can go together
can_go_togheter(X, Y, Z) :- people(X), people(Y), X != Y, want_food(X, Z), want_food(Y, Z), not can_go_togheter(Y, X, Z).
can_go_togheter(X, Y, Z) :- people(X), people(Y), X != Y, cuisine_preferences(X, Z), cuisine_preferences(Y, Z), not can_go_togheter(Y, X, Z).

#show sad/1.
#show can_go_togheter/3.
