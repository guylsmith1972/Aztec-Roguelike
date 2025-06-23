:- [ 'resources.pl' ]


can_build_mine(Region, MineType, Ore) :-
    has_natural_resource(Region, MineralDeposit),
    atom_concat(Ore, "_deposit", MineralDeposit),
    atom_concat(Ore, "_mine", MineType).

can_build_farm(Region, FarmType, SeedType) :-
    has_natural_resource(Region, arable_land),
    (has_natural_resource(Region, fresh_water_irrigation_source); (climate_annual_rainfall(Region, AnnualRainfall), AnnualRainfall > 10) ),
    has_resource(Region, SeedType),
    atom_concat(SeedType, "_farm", FarmType).

can_build_facility(Region, charcoal_manufactory, _) :- % TODO
can_build_facility(Region, FarmType, SeedType) :- can_build_farm(Region, FarmType, SeedType)
can_build_facility(Region, FoundryType, MetalType) :- % TODO
can_build_facility(Region, lumber_mill, _) :- % TODO
can_build_facility(Region, MineType, Ore) :- can_build_mine(Region, MineType).
can_build_facility(Region, pottery, _) :- % TODO
can_build_facility(Region, QuarryType, StoneType) :- % TODO
can_build_facility(Region, seaport, _) :- has_natural_resource(Region, coastline).
can_build_facility(Region, shipyard, _) :- % TODO
can_build_facility(Region, smeltery, OreType) :- % TODO
can_build_facility(Region, SmithyType, MetalType) :- % TODO
can_build_facility(Region, tannery, _) :- % TODO
can_build_facility(Region, textile_mill, _) :- % TODO

% TODO: Add additional facilities common in late antiquity Europe
