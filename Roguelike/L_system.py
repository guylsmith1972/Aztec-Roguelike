import random
import re


class LSystem:
    def __init__(self, rules):
        self.rules = rules

    def apply_productions(self, rule_string, rng):
        # Check if the rule_string starts with a word (updated regex to include square brackets)
        initial_symbol_matches = re.findall(r'^[\w\[\]]+', rule_string)
        
        if initial_symbol_matches:
            # Initialize the intermediate result with the main symbol (ignoring any operators)
            intermediate_result = initial_symbol_matches[0]
            # Move the pointer to the end of the main symbol
            pointer = len(intermediate_result)
        else:
            intermediate_result = ""
            pointer = 0
        
        while pointer < len(rule_string):
            # Apply {} operator
            if rule_string[pointer] == '{':
                min_count, max_count = map(int, re.findall(r'\{(\d+),(\d+)\}', rule_string[pointer:])[0])
                count = rng.randint(min_count, max_count)
                intermediate_result = ' '.join([intermediate_result] * count)
                pointer += len(f"{{{min_count},{max_count}}}")
            # Apply () operator
            elif rule_string[pointer] == '(':
                prob = float(re.findall(r'\((0\.\d+|1)\)', rule_string[pointer:])[0])
                if rng.random() > prob:
                    intermediate_result = ""
                pointer += len(f"({prob})")
            else:
                break
        
        return intermediate_result

    def apply_rules(self, symbol, rng):
        # Fetch the rules for the symbol
        possible_rules = self.rules.get(symbol, [(symbol, 1)])
        
        # Split the rules and weights
        successors, weights = zip(*possible_rules)
        
        # Randomly select a rule based on the weights
        chosen_rule = rng.choices(successors, weights=weights)[0]
        
        # Updated the regex to split rule based on spaces or non-snake-case symbols and to include square brackets
        rule_symbols = re.findall(r'[\w\[\]]+(?:\{\d+,\d+\})?(?:\(\d+\.\d+\))?', chosen_rule)
        
        # Apply the productions to each symbol in the rule
        result_symbols = [self.apply_productions(rule_symbol, rng) for rule_symbol in rule_symbols]
        
        # Filter out any empty strings before joining
        result = ' '.join(filter(None, result_symbols))
        
        return result

    def iterate(self, start_string, max_iterations=1, rng=random, max_length=200):
        '''Iterate the L-system.'''
        # Splitting the start string into symbols based on spaces or non-snake-case symbols
        symbols = re.findall(r'[\w\[\]]+|[^a-zA-Z_ ]', start_string)
        
        for _ in range(max_iterations):
            new_symbols = []
            for symbol in symbols:
                expanded = self.apply_rules(symbol, rng)
                new_symbols.extend(expanded.split())
            if new_symbols == symbols or len(' '.join(new_symbols)) > max_length:
                break
            symbols = new_symbols
        
        return ' '.join(symbols)


def main():
    ruleset = {'resources': [('farmland(0.9) minerals(0.7)', 1)],
               'farmland': [('wheat(0.5) flax(0.5) barley(0.5) hops(0.5)', 1)],
               'minerals': [('iron(0.9) copper(0.1) silver(0.01) gold(0.001)', 1)]
               }
    lsystem = LSystem(ruleset)
    print(lsystem.iterate('resources', max_iterations=3))


if __name__ == '__main__':
    main()