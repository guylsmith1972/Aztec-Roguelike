:- [ 'resources.pl' ].


has_industry(Region, IndustryName) :-
    required_resources(IndustryName, RequiredResources),
    has_resources(Region, RequiredResources).


has_industry(Region, IndustryName) :-
    % TODO - a region can have an industry if it has a supply of all of the required materials for the industry.
    % required materials could be
