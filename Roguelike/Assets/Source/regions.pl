is_a(hematite, mineral).
is_a(magnetite, mineral).
is_a(chalcopyrite, mineral).
is_a(cassiterite, mineral).
is_a(lignite, mineral).


is_a(hematite, iron_ore).
is_a(magnetite, iron_ore).
is_a(chalcopyrite, copper_ore).
is_a(cassiterite, tin_ore).
is_a(lignite, coal).

is_a(iron_ore, metal_ore).
is_a(copper_ore, metal_ore).
is_a(tin_ore, metal_ore).
is_a(A, C) :-
    is_a(A, B),
    is_a(B, C).






alloy(bronze, [copper, tin]).


smelting_fuel(coal).
smelting_fuel(charcoal).

% Mining industry rule: Region should have the ore as a local resource
industry(Region, mining, Details) :-
    is_a(Mineral, mineral),
    local_resource(Region, Mineral),
    Details = [Mineral].
    
% Local resources
local_resource(alicetopia, hematite).
local_resource(alicetopia, lignite).

% Imported resources
imported_resource(alicetopia, copper_ore).
imported_resource(alicetopia, tin).

