:- module(categories, [ancestor/2, root/2, parent/2, conforms_to/2]).

% internally used predicates
transitive_is_a(A, C) :- is_a(A, C).
transitive_is_a(A, C) :-
    is_a(A, B),
    transitive_is_a(B, C).



% other user-level predicates

% get immediate parents of A
parent(A, Parent) :- is_a(Parent, A).

% get all ancestors of A
ancestor(A, Ancestor) :- transitive_is_a(Ancestor, A).

% get all ancestors of A which do not themselves have ancestors
root(A, Root) :-
    transitive_is_a(Root, A),
    \+ transitive_is_a(_, Root).  % Root should not have any ancestor


conforms_to(A, B) :- transitive_is_a(A, B).
