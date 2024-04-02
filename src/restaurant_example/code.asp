
%If none is with me and I am hungry, I am sad to eat alone
sad(X) :- alone, people(X).

%If I am with someone and we both want to eat the same food, we can go together
cangotogheter(X, Y, Z) :- people(X), people(Y), X != Y, want_food(X, Z), want_food(Y, Z), not cangotogheter(Y, X, Z).
cangotogheter(X, Y, Z) :- people(X), people(Y), X != Y, cuisine_preferences(X, Z), cuisine_preferences(Y, Z), not cangotogheter(Y, X, Z).

#show sad/1.
#show cangotogheter/3.
