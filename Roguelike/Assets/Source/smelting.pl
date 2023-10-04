:- [ 'lcg.pl', 'rocks_and_minerals.pl' ].

:- asserta(is_a(anthracite, high_temperature_fuel)).
:- asserta(is_a(charcoal, high_temperature_fuel)).
:- asserta(is_a(wood, low_temperature_fuel)).

:- asserta(is_a(low_temperature_fuel, fuel)).
:- asserta(is_a(high_temperature_fuel, fuel)).


:- asserta(is_a(borax, sodium_borate_flux)).
:- asserta(is_a(calcite, calcium_carbonate_flux)).
:- asserta(is_a(chalk, calcium_carbonate_flux)).
:- asserta(is_a(dolomite, calcium_carbonate_flux)).
:- asserta(is_a(lead, lead_based_flux)).
:- asserta(is_a(limestone, calcium_carbonate_flux)).
:- asserta(is_a(magnesia, magnesium_carbonate_flux)).
:- asserta(is_a(marble, calcium_carbonate_flux)).
:- asserta(is_a(natron, sodium_carbonate_flux)).
:- asserta(is_a(oyster_shells, calcium_carbonate_flux)).
:- asserta(is_a(plant_ashes, sodium_carbonate_flux)).
:- asserta(is_a(potash, potassium_carbonate_flux)).
:- asserta(is_a(salt, sodium_chloride_flux)).
:- asserta(is_a(soda_ash, sodium_carbonate_flux)).



removes_with(alumina, [calcium_carbonate_flux, magnesium_carbonate_flux]).
removes_with(barium, [calcium_carbonate_flux]).
removes_with(base_metal_oxides, [sodium_borate_flux, sodium_chloride_flux]).
removes_with(lead_oxide, [sodium_carbonate_flux]).
removes_with(phosphorus, [calcium_carbonate_flux]).
removes_with(quartz, [calcium_carbonate_flux, magnesium_carbonate_flux]).
removes_with(silica, [calcium_carbonate_flux, magnesium_carbonate_flux, potassium_carbonate_flux, sodium_borate_flux, sodium_carbonate_flux]).
removes_with(sulfur, [calcium_carbonate_flux]).
removes_with(zinc, [lead_based_flux]).




% Find a combination of fluxes that removes a list of impurities
combination_to_remove([], []).
combination_to_remove([Impurity | RestImpurities], FluxCombination) :-
    removes_with(Impurity, FluxOptions),
    member(Flux, FluxOptions),
    combination_to_remove(RestImpurities, RestCombination),
    append([Flux], RestCombination, FluxCombinationUnfiltered),
    remove_duplicates(FluxCombinationUnfiltered, FluxCombination).

% Helper predicate to remove duplicates from a list
remove_duplicates([], []).
remove_duplicates([X | Xs], Ys) :-
    member(X, Xs),
    !,
    remove_duplicates(Xs, Ys).
remove_duplicates([X | Xs], [X | Ys]) :-
    remove_duplicates(Xs, Ys).





smelting_flux(Ore, Flux) :- conforms_to(Ore, iron_ore), conforms_to(Flux, calcium_carbonate_flux).
smelting_flux(Ore, Flux) :- conforms_to(Ore, tin_ore), conforms_to(Flux, calcium_carbonate_flux).
smelting_flux(Ore, Flux) :- conforms_to(Ore, lead_ore), conforms_to(Flux, calcium_carbonate_flux).
smelting_flux(Ore, Flux) :- conforms_to(Ore, gold_ore), conforms_to(Flux, sodium_borate_flux).
smelting_flux(Ore, Flux) :- conforms_to(Ore, gold_ore), conforms_to(Flux, sodium_carbonate_flux).

smelting_fuel(Ore, Fuel) :- conforms_to(Ore, iron_ore), conforms_to(Fuel, high_temperature_fuel).
smelting_fuel(Ore, Fuel) :- conforms_to(Ore, tin_ore), conforms_to(Fuel, fuel).
smelting_fuel(Ore, Fuel) :- conforms_to(Ore, lead_ore), conforms_to(Fuel, fuel).
smelting_fuel(Ore, Fuel) :- conforms_to(Ore, silver_ore), conforms_to(Fuel, fuel).

smelting_furnace(Ore, bloomery) :- smelting_fuel(Ore, Fuel), conforms_to(Fuel, high_temperature_fuel).
smelting_furnace(_, shaft_furnace).


smelting_charge(Ore, Fuel, Flux) :-
    is_a(Ore, metal_ore),
    smelting_flux(Ore, Flux),
    smelting_fuel(Ore, Fuel).


smelt([Ore, Fuel, Flux], Furnace, Products) :-
    smelting_charge(Ore, Fuel, Flux),
    smelting_furnace(Ore, Furnace),
    findall(Product, produces(Ore, Product), Products).
