from L_system import LSystem

import random


class PopulationCenter:
    resource_lsystem = LSystem({'resources': [('farmland(0.9) minerals(0.7)', 1)],
                                'farmland': [('wheat(0.5) flax(0.5) barley(0.5) hops(0.5)', 1)],
                                'minerals': [('iron(0.9) copper(0.1) silver(0.01) gold(0.001)', 1)]
                                })
    
    def __init__(self, name, location, rng):
        self.name = name
        self.location = location
        self.resources = PopulationCenter.resource_lsystem.iterate('resources', max_iterations=3, rng=rng).split(' ')


if __name__ == '__main__':
    for _ in range(20):
        pop = PopulationCenter('Farmtopia', 'paradise', random.Random())
        print(pop.resources)
