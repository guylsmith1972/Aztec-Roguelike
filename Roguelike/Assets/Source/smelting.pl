:- [ 'rocks_and_minerals.pl' ].

:- asserta(is_a(anthracite, high_temperature_fuel)).
:- asserta(is_a(charcoal, high_temperature_fuel)).
:- asserta(is_a(wood, low_temperature_fuel)).

:- asserta(is_a(low_temperature_fuel, fuel)).
:- asserta(is_a(high_temperature_fuel, fuel)).


:- asserta(is_a(limestone, calcium_carbonate_flux)).
:- asserta(is_a(dolomite, calcium_carbonate_flux)).
:- asserta(is_a(calcite, calcium_carbonate_flux)).
:- asserta(is_a(marble, calcium_carbonate_flux)).
:- asserta(is_a(oyster_shells, calcium_carbonate_flux)).

:- asserta(is_a(borax, sodium_borate_flux)).
:- asserta(is_a(soda_ash, sodium_carbonate_flux)).
:- asserta(is_a(fluorspar, calcium_fluoride_flux)).
:- asserta(is_a(silica, silicon_dioxide_flux)).

smelting_flux(Ore, Flux) :- conforms_to(Ore, iron_ore), conforms_to(Flux, calcium_carbonate_flux).
smelting_flux(Ore, Flux) :- conforms_to(Ore, tin_ore), conforms_to(Flux, calcium_carbonate_flux).
smelting_flux(Ore, Flux) :- conforms_to(Ore, lead_ore), conforms_to(Flux, calcium_carbonate_flux).
smelting_flix(Ore, Flux) :- conforms_to(Ore, gold_ore), conforms_to(Flux, sodium_borate_flux).
smelting_flix(Ore, Flux) :- conforms_to(Ore, gold_ore), conforms_to(Flux, sodium_carbonate_flux).

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
