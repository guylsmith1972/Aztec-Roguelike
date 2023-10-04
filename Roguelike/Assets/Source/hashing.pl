hash_string(String, Hash) :-
	atom_codes(String, Codes),
	hash_codes(Codes, Hash).

hash_codes([], 0, _).
hash_codes([X|Xs], Hash, MaxValue) :-
	hash_codes(Xs, SubHash),
	Hash is (SubHash * 31 + X) mod MaxValue.
