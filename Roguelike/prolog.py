from swiplserver import PrologMQI


class PrologInterface:
    def __init__(self, prolog_source_filenames):
        self.mqi = PrologMQI()
        self.prolog_thread = self.mqi.create_thread()
        for prolog_source_filename in prolog_source_filenames:
            self.prolog_thread.query(f'consult("Assets/Source/{prolog_source_filename}")')
    
    def query(self, prolog_query):
        return self.prolog_thread.query(prolog_query)
    
    def assert_fact(self, fact):
        '''Assert a new fact into the Prolog knowledge base.'''
        return self.prolog_thread.query(f'assert({fact})')
    
    def retract_fact(self, fact):
        '''Retract a fact from the Prolog knowledge base.'''
        return self.prolog_thread.query(f'retract({fact})')
    
    def __del__(self):
        # Cleanup resources if necessary
        # self.prolog_thread.stop()
        self.mqi.stop()


def main():
    prolog_engine = PrologInterface(['smelting.pl'])
    # print(prolog_engine.query('smelt([cassiterite, Fuel, Flux], Furnace, Products)'))
    print(prolog_engine.query('combination_to_remove([alumina, barium], FluxCombination)'))
    print(prolog_engine.query('combination_to_remove(Impurities, [calcium_carbonate_flux])'))

if __name__ == '__main__':
    main()
    