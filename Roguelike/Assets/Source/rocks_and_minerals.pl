
:- [ 'categories.pl' ].


:- assertz(is_a(metal_ore, mineral)).
:- assertz(is_a(mineral, rock)).


define_metal_ore(_, [], _, _).
define_metal_ore(Name, [Head|Tail], Impurities, AlternateNames) :-
    define_metal_ore(Name, Tail, Impurities, AlternateNames),
    atom_concat(Head, '_ore', Ore),
    asserta(produces(Name, Head)),
    asserta(produces(Ore, Head)),
    asserta(is_a(Name, metal_ore)),
    asserta(is_a(Name, Ore)),
    asserta(has_impurities(Name, Impurities)),
    asserta(also_known_as(Name, AlternateNames)).


:- define_metal_ore(argentite, [silver], ['silica', 'barium', 'base_metal_oxides'], ['argentum']).
:- define_metal_ore(azurite, [copper], ['silica', 'iron', 'base_metal_oxides'], ['caeruleum', 'kuanos']).
:- define_metal_ore(bismuthinite, [bismuth], ['sulfur'], []).
:- define_metal_ore(bornite, [copper, silver], ['silica', 'iron', 'base_metal_oxides'], []).
:- define_metal_ore(cassiterite, [tin], ['silica', 'iron'], ['stannum']).
:- define_metal_ore(cerussite, [lead], ['silica', 'barium', 'lead_oxide'], ['cerussa', 'psimythion']).
:- define_metal_ore(chalcocite, [copper], ['silica', 'iron', 'base_metal_oxides'], ['chalcos']).
:- define_metal_ore(chalcopyrite, [copper, gold, silver], ['silica', 'iron', 'base_metal_oxides'], ['chalcopyros']).
:- define_metal_ore(cinnabar, [mercury], ['silica', 'sulfur'], ['dragyde', 'minium']).
:- define_metal_ore(cuprite, [copper], ['silica', 'iron', 'base_metal_oxides'], ['chalcos']).
:- define_metal_ore(galena, [lead, silver], ['silica', 'lead_oxide'], ['galene', 'plumbum nigrum']).
:- define_metal_ore(goethite, [iron], ['silica', 'alumina', 'phosphorus', 'sulfur'], ['sideros']).
:- define_metal_ore(hematite, [iron], ['silica', 'alumina', 'phosphorus', 'sulfur'], ['sideritis', 'haimatites']).
:- define_metal_ore(hemimorphite, [zinc], ['silica', 'iron'], []).
:- define_metal_ore(limonite, [iron], ['silica', 'alumina', 'phosphorus', 'sulfur'], ['sideros']).
:- define_metal_ore(magnetite, [iron], ['silica', 'alumina', 'phosphorus', 'sulfur'], ['magnes', 'heracleian stone']).
:- define_metal_ore(malachite, [copper], ['silica', 'iron', 'base_metal_oxides'], ['molochitis']).
:- define_metal_ore(native_copper, [copper], ['silica', 'iron', 'base_metal_oxides'], ['chalcos']).
:- define_metal_ore(native_gold, [gold], ['quartz', 'iron', 'base_metal_oxides'], ['chrysos']).
:- define_metal_ore(native_silver, [silver], ['quartz', 'base_metal_oxides'], ['argentum']).
:- define_metal_ore(orpiment, [arsenic], ['sulfur', 'iron'], ['orpimentum']).
:- define_metal_ore(realgar, [arsenic], ['sulfur', 'iron'], ['sandaracha']).
:- define_metal_ore(siderite, [iron], ['silica', 'alumina', 'phosphorus', 'sulfur'], ['sideros']).
:- define_metal_ore(smithsonite, [zinc], ['silica', 'iron'], []).
:- define_metal_ore(sphalerite, [zinc], ['silica', 'iron'], ['zincum']).
:- define_metal_ore(stibnite, [antimony], ['silica', 'sulfur'], ['stibium']).


