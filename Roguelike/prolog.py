from swiplserver import PrologMQI


class PrologInterface:
    def __init__(self, prolog_source_filename):
        self.mqi = PrologMQI()
        self.prolog_thread = self.mqi.create_thread()
        self.prolog_thread.query(f'consult("Assets/Source/{prolog_source_filename}")')
    
    def query(self, prolog_query):
        return self.prolog_thread.query(prolog_query)
    
    def __del__(self):
        # Cleanup resources if necessary
        self.prolog_thread.stop()
        # self.mqi.close()


def main():
    prolog_engine = PrologInterface('regions.pl')
    print(prolog_engine.query('industry(alicetopia, X).'))
    

if __name__ == '__main__':
    main()
    