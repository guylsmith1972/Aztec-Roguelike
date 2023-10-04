:- [ 'hashing.pl', 'lcg.pl' ].


has_resource(Region, Resource) :- has_manufactured_resource(Region, Resource).
has_resource(Region, Resource) :- has_imported_resource(Region, Resource).
has_resource(Region, Resource) :- has_harvested_resource(Region, Resource). 

has_resources(Region, []).
has_resources(Region, [X|Xs]) :-
    has_resource(Region, X),
    has_resources(Region, Xs).


:- table has_natural_resource/2
has_natural_resource(Region, Resource) :-
    natural_resource(Resource, _),
    resource_frequency(Resource, Probability),
    atom_concat(Region, "__", Resource),
    hash_string(RegionResource, Hash, 4294967296),
    lcg(Hash, Result),
    Result < Probability.

has_harvested_resource(Region, Resource) :-
    natural_resource(RawResource, Resource),
    has_natural_resource(Region, RawResource),
    has_manufactured_resource(Region, Resource).

has_manufactured_resource(Region, Resource) :-
    industry_produces(Industry, Resource),
    has_industry(Region, Industry).
    
has_imported_resource(Region, Resource) :-
    trade_route(_, Region, Resource).


