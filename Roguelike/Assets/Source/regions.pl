:- style_check(-discontiguous).


% A region with iron and coal deposits, and a moderate or larger population, should have a smelting industry.
industry(Region, smelting) :-
    resource(Region, iron),
    resource(Region, coal),
    (population(Region, moderate); population(Region, large)).

% Regions with any mineral deposit should have a mining industry as long as there is at least some population.
industry(Region, mining) :-
    (resource(Region, iron); resource(Region, coal); resource(Region, gold); resource(Region, stone)),
    \+ population(Region, none).

% If a region lacks iron, but has coal and population, it should have trade connections supplying iron.
trade(Region, OtherRegion) :-
    \+ resource(Region, iron),
    resource(Region, coal),
    \+ population(Region, none),
    resource(OtherRegion, iron).

% In late antiquity, coastal regions with wood resources might have a shipbuilding industry.
resource(Region, coast). % Represents regions that are coastal
industry(Region, shipbuilding) :-
    resource(Region, coast),
    resource(Region, wood).

% Regions with significant food resources and large populations might have a monarchy.
politics(Region, monarchy) :-
    resource(Region, food),
    population(Region, large).

% Regions with stone and moderate population might have structures and can be considered as republics.
politics(Region, republic) :-
    resource(Region, stone),
    population(Region, moderate).

% Regions with significant gold resources may be major trade hubs.
industry(Region, trade) :-
    resource(Region, gold).

% If a region lacks food but has some population, it should have trade connections supplying food.
trade(Region, OtherRegion) :-
    \+ resource(Region, food),
    \+ population(Region, none),
    resource(OtherRegion, food).


resource(alicetopia, iron).
resource(alicetopia, coal).
population(alicetopia, moderate).
