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
    prolog_engine = PrologInterface(['minerals.pl'])
    # prolog_engine.assert_fact('is_a(a, b)')
    # prolog_engine.assert_fact('is_a(b, c)')
    # prolog_engine.assert_fact('is_a(d, c)')
    # print(prolog_engine.query('ancestor(c, Ancestor)'))
    # print(prolog_engine.query('root(c, Root)'))
    # print(prolog_engine.query('parent(c, Parent)'))
    print(prolog_engine.query('can_smelt(hematite)'))
    

if __name__ == '__main__':
    main()
    