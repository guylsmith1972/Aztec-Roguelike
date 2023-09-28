
:- [ 'categories.pl' ].


:- assertz(is_a(metal_ore, mineral)).
:- assertz(is_a(mineral, rock)).

metal_ore(_, []).
metal_ore(Name, [Head|Tail]) :-
    metal_ore(Name, Tail),
    atom_concat(Head, '_ore', Ore),
    asserta(produces(Name, Head)),
    asserta(produces(Ore, Head)),
    asserta(is_a(Name, metal_ore)),
    asserta(is_a(Name, Ore)).

% Iron
:- metal_ore(hematite, [iron]).
:- metal_ore(magnetite, [iron]).
:- metal_ore(goethite, [iron]).
:- metal_ore(limonite, [iron]).
:- metal_ore(siderite, [iron]).

% Lead and Silver
:- metal_ore(galena, [lead, silver]).
:- metal_ore(argentite, [silver]).
:- metal_ore(cerussite, [lead]).

% Copper, Gold, and Silver
:- metal_ore(chalcopyrite, [copper, gold, silver]).
:- metal_ore(bornite, [copper, silver]).
:- metal_ore(chalcocite, [copper]).
:- metal_ore(malachite, [copper]).
:- metal_ore(azurite, [copper]).
:- metal_ore(cuprite, [copper]).
:- metal_ore(native_copper, [copper]).
:- metal_ore(native_gold, [gold]).
:- metal_ore(native_silver, [silver]).
:- metal_ore(native_electrum, [gold, silver]).

% Tin
:- metal_ore(cassiterite, [tin]).

% Zinc
:- metal_ore(sphalerite, [zinc]).
:- metal_ore(smithsonite, [zinc]).
:- metal_ore(hemimorphite, [zinc]).

% Mercury
:- metal_ore(cinnabar, [mercury]).



% Rare metals
% Antimony
:- metal_ore(stibnite, [antimony]).

% Arsenic
:- metal_ore(realgar, [arsenic]).
:- metal_ore(orpiment, [arsenic]).

% Bismuth
:- metal_ore(bismuthinite, [bismuth]).

% Platinum
:- metal_ore(native_platinum, [platinum]).

% Stream Tin (additional source for tin)
:- metal_ore(stream_tin, [tin]).



