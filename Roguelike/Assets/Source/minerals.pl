
:- [ 'categories.pl' ].

is_a(hematite, mineral).
is_a(hematite, iron_ore).

is_a(iron_ore, metal_ore).

can_smelt(A) :- conforms_to(A, metal_ore).
