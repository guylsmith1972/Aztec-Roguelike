
lcg(Seed, PsuedoRandomResult) :-
    % Use your desired LCG parameters (Multiplier, Increment, Modulus)
    Multiplier = 1664525,
    Increment = 1013904223,
    Modulus = 4294967296, % 2^32
    NewSeed is (Multiplier * Seed + Increment) mod Modulus,
    PsuedoRandomResult is NewSeed / Modulus.
