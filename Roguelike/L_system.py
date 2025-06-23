#
# L-System Generation Engine
#
# This module provides a flexible L-system (Lindenmayer system) engine capable of
# generating complex strings from a simple axiom and a set of rules. It is designed
# to be used for a wide range of procedural generation tasks within the game.
#
# --- How to Use ---
#
# 1. Initialization:
#    lsystem = LSystem(rules)
#    - 'rules' is a dictionary where keys are symbols (str) and values define
#      the rewriting rule for that symbol.
#
# 2. Rule Types:
#
#    a) Static, Weighted Rules:
#       Provide a list of (successor, weight) tuples. A successor is chosen
#       randomly based on its weight.
#       'A': [('AB', 1), ('AC', 2)]  # 'AC' is twice as likely as 'AB'
#
#    b) Dynamic, Context-Sensitive Rules:
#       Provide a callable function that accepts 'context' and 'rng' arguments.
#       The function should return a successor string. This allows generation to
#       be influenced by external game state (e.g., location, wealth).
#       def my_rule(context, rng):
#           if context.get('wealth') == 'rich':
#               return 'gold_coin'
#           return 'copper_coin'
#       'coin': my_rule
#
# 3. Production Operators in Rule Strings:
#
#    a) Probabilistic Operator `(p)`:
#       A symbol followed by `(probability)` will only be included if a random
#       number is less than the probability.
#       Example: 'treasure(0.1)' -> "treasure" appears 10% of the time.
#
#    b) Repetition Operator `{min,max}`:
#       A symbol followed by `{min,max}` will be repeated a random number of
#       times within that inclusive range.
#       Example: 'goblin{1,5}' -> "goblin goblin goblin" (or any count from 1 to 5).
#
# 4. Generating Output:
#
#    lsystem.iterate(axiom, iterations, rng, context)
#    - axiom (str): The starting symbol string (e.g., 'start').
#    - iterations (int): How many times to apply the rules.
#    - rng (random.Random): A seeded random number generator for deterministic output.
#    - context (dict): An optional dictionary containing external state to be used
#      by dynamic rules.
#
import random
import re


class LSystem:
    def __init__(self, rules):
        self.rules = rules

    def apply_productions(self, rule_string, rng):
        # Check if the rule_string starts with a word
        initial_symbol_matches = re.findall(r'^[\w\[\]\(\)->#]+', rule_string)
        
        if initial_symbol_matches:
            # Initialize the intermediate result with the main symbol
            intermediate_result = initial_symbol_matches[0]
            # Move the pointer to the end of the main symbol
            pointer = len(intermediate_result)
        else:
            intermediate_result = ""
            pointer = 0
        
        while pointer < len(rule_string):
            # Apply {} operator for repetition
            if rule_string[pointer] == '{':
                min_count, max_count = map(int, re.findall(r'\{(\d+),(\d+)\}', rule_string[pointer:])[0])
                count = rng.randint(min_count, max_count)
                intermediate_result = ' '.join([intermediate_result] * count)
                pointer += len(f"{{{min_count},{max_count}}}")
            # Apply () operator for probability
            elif rule_string[pointer] == '(':
                # Updated regex to handle floats like 0.1 and integers like 1
                prob_match = re.search(r'\((0\.\d+|1|1\.0)\)', rule_string[pointer:])
                if prob_match:
                    prob = float(prob_match.group(1))
                    if rng.random() > prob:
                        intermediate_result = ""
                    pointer += len(prob_match.group(0))
                else:
                    break # No valid probability found
            else:
                break
        
        return intermediate_result

    def apply_rules(self, symbol, rng, context):
        """Applies rules to a single symbol."""
        rule_definition = self.rules.get(symbol)
        chosen_rule = None

        if callable(rule_definition):
            # Dynamic rule: execute the function
            chosen_rule = rule_definition(context, rng)
        elif isinstance(rule_definition, list):
            # FIX: Handle terminal symbols (empty rule list) gracefully.
            if not rule_definition:
                return symbol
            # Static rule: choose a successor based on weight
            successors, weights = zip(*rule_definition)
            chosen_rule = rng.choices(successors, weights=weights)[0]

        if chosen_rule is None:
            # If no rule is found, the symbol is terminal
            return symbol

        # FIX: Safeguard against simple infinite recursion (e.g., "well: well")
        if chosen_rule.strip() == symbol:
            return symbol

        # Use split() for robust tokenization, assuming space separation in rules files
        rule_symbols = chosen_rule.split()
        
        # Apply productions to each symbol in the chosen rule
        result_symbols = [self.apply_productions(rule_symbol, rng) for rule_symbol in rule_symbols]
        
        # Filter out any empty strings that resulted from probabilistic operators
        result = ' '.join(filter(None, result_symbols))
        
        return result

    def iterate(self, start_string, max_iterations=1, rng=None, max_length=1000, context=None):
        """Iterate the L-system for a number of generations."""
        if rng is None:
            rng = random.Random()
        if context is None:
            context = {}

        # Use split() for robust initial tokenization
        symbols = start_string.split()
        
        for _ in range(max_iterations):
            new_symbols = []
            for symbol in symbols:
                expanded = self.apply_rules(symbol, rng, context)
                # Ensure the expanded result is also tokenized correctly
                new_symbols.extend(expanded.split())
            
            # Stop if the system is stable or exceeds max length
            if new_symbols == symbols or len(' '.join(new_symbols)) > max_length:
                break
            symbols = new_symbols
        
        return ' '.join(symbols)