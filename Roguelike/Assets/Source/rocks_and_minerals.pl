
:- [ 'categories.pl' ].


:- asserta(is_a(metal_ore, mineral)).
:- asserta(is_a(mineral, rock)).


define_metal_ore(_, [], _, _, _).
define_metal_ore(Name, [Head|Tail], Impurities, AlternateNames, Frequency) :-
    define_metal_ore(Name, Tail, Impurities, AlternateNames),
    atom_concat(Head, '_ore', Ore),
    asserta(produces(Name, Head)),
    asserta(produces(Ore, Head)),
    asserta(is_a(Name, metal_ore)),
    asserta(is_a(Name, Ore)),
    asserta(has_impurities(Name, Impurities)),
    asserta(also_known_as(Name, AlternateNames)),
    asserta(resource_frequency(Name, Frequency)),
    atom_concat(Name, "_deposit", MineralDeposit),
    asserta(natural_resource(MineralDeposit, Name)).    


:- define_metal_ore(argentite, [silver], [silica, barium, base_metal_oxides], [argentum], 0.01).
:- define_metal_ore(azurite, [copper], [silica, base_metal_oxides], [caeruleum, kuanos], 0.02).
:- define_metal_ore(bismuthinite, [bismuth], [sulfur], [], 0.03).
:- define_metal_ore(bornite, [copper, silver], [silica, base_metal_oxides], [], 0.01).
:- define_metal_ore(cassiterite, [tin], [silica], [stannum], 0.1).
:- define_metal_ore(cerussite, [lead], [silica, barium, lead_oxide], [cerussa, psimythion], 0.1).
:- define_metal_ore(chalcocite, [copper], [silica, base_metal_oxides], [chalcos], 0.02).
:- define_metal_ore(chalcopyrite, [copper, gold, silver], [silica, base_metal_oxides], [chalcopyros], 0.01).
:- define_metal_ore(cinnabar, [mercury], [silica, sulfur], [dragyde, minium], 0.02).
:- define_metal_ore(cuprite, [copper], [silica, base_metal_oxides], [chalcos], 0.02).
:- define_metal_ore(galena, [lead, silver], [silica, lead_oxide], [galene, plumbum_nigrum], 0.02).
:- define_metal_ore(goethite, [iron], [silica, alumina, phosphorus, sulfur], [sideros], 0.2).
:- define_metal_ore(hematite, [iron], [silica, alumina, phosphorus, sulfur], [sideritis, haimatites], 0.2).
:- define_metal_ore(hemimorphite, [zinc], [silica], [calamine], 0.05).
:- define_metal_ore(limonite, [iron], [silica, alumina, phosphorus, sulfur], [sideros], 0.2).
:- define_metal_ore(magnetite, [iron], [silica, alumina, phosphorus, sulfur], [magnes, heracleian_stone], 0.2).
:- define_metal_ore(malachite, [copper], [silica, base_metal_oxides], [molochitis], 0.02).
:- define_metal_ore(native_copper, [copper], [silica, base_metal_oxides], [chalcos], 0.003).
:- define_metal_ore(native_gold, [gold], [quartz, base_metal_oxides], [chrysos], 0.001).
:- define_metal_ore(native_silver, [silver], [quartz, base_metal_oxides], [argentum], 0.002).
:- define_metal_ore(orpiment, [arsenic], [sulfur], [orpimentum], 0.05).
:- define_metal_ore(realgar, [arsenic], [sulfur], [sandaracha], 0.05).
:- define_metal_ore(siderite, [iron], [silica, alumina, phosphorus, sulfur], [sideros], 0.2).
:- define_metal_ore(smithsonite, [zinc], [silica], [calamine], 0.05).
:- define_metal_ore(sphalerite, [zinc], [silica], [zincum], 0.05).
:- define_metal_ore(stibnite, [antimony], [silica, sulfur], [stibium], 0.05).
