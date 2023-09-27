
% Define the relationships between specific materials and their categories.
is_a(hematite, iron_ore).
is_a(magnetite, iron_ore).

% Define the relationships for high_temperature_fuel
is_a(coal, high_temperature_fuel).
is_a(charcoal, high_temperature_fuel).

% Define lignite as a type of coal
is_a(lignite, coal).

% Recipe for iron_ingot
recipe([iron_ore, high_temperature_fuel], iron_ingot).

% Predicate to determine if a given material can be used for a recipe.
can_use(Material, RequiredMaterial) :-
    is_a(Material, RequiredMaterial).
can_use(Material, Material).

% Predicate to determine what can be produced from a list of materials.
can_produce(Materials, Product) :-
    recipe(RequiredMaterials, Product),
    maplist(can_use(Materials), RequiredMaterials).

% Predicate to find all the permutations of materials that can be used to produce a given product.
materials_needed(Product, MaterialList) :-
    recipe(RequiredCategories, Product),
    find_materials(RequiredCategories, MaterialList).

% Predicate to map each required category to its specific materials.
find_materials([], []).
find_materials([Category|RestCategories], [Material|RestMaterials]) :-
    is_specific(Material, Category),
    find_materials(RestCategories, RestMaterials).

% Predicate to determine if a given material is the most specific in its category.
is_specific(Material, Category) :-
    (is_a(Material, Category) ; Material = Category),
    \+ (is_a(AnotherMaterial, Material), AnotherMaterial \= Material, is_a(AnotherMaterial, Category)).
