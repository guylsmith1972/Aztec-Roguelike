
conforms_to(A, C) :- is_a(A, C).
conforms_to(A, C) :-
    is_a(A, B),
    conforms_to(B, C).

% get immediate parents of A
parent(A, Parent) :- is_a(Parent, A).

% get all ancestors of A
ancestor(A, Ancestor) :- conforms_to(Ancestor, A).

% get all ancestors of A which do not themselves have ancestors
root(A, Root) :-
    conforms_to(Root, A),
    \+ conforms_to(_, Root).  % Root should not have any ancestor

% get immediate children of A
children(A, Child) :- is_a(A, Child).

% get all descentants of A
descendant(A, Descendant) :- conforms_to(A, Descendant).

% get all descendants of A which do not themselves have descendants
leaf(A, Leaf) :-
    conforms_to(A, Leaf),
    \+ conforms_to(Leaf, _).  % Leaf should not have any descendant

