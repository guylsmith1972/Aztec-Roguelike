#
# L-System Parser and Manager
#
# This module provides the tools to load L-system rules from external `.rules`
# files. This decouples the generative grammar from the game's source code,
# allowing for easier editing and expansion of content.
#
# --- How to Use ---
#
# 1. Create `.rules` Files:
#    Create text files (e.g., 'items.rules', 'quests.rules') in a dedicated
#    directory (e.g., 'Assets/Rulesets/'). The syntax is as follows:
#
#    // Comments start with double slashes.
#    rule_name:
#        successor_string_1 @weight1
#        successor_string_2 @weight2
#
#    # To link to a dynamic Python function:
#    dynamic_rule_name:
#        dynamic: name_of_registered_function
#
# 2. Use the LSystemManager:
#    (Usage remains the same)
#
import os
import re
from L_system import LSystem

class LSystemParser:
    """Parses a .rules file into a dictionary format for the LSystem class."""

    def __init__(self, function_registry=None):
        self.function_registry = function_registry if function_registry else {}

    def parse(self, file_path):
        rules = {}
        current_rule = None
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                stripped_line = line.strip()

                # FIX: Use '//' for comments for unambiguous parsing.
                if not stripped_line or stripped_line.startswith('//'):
                    continue

                is_indented = len(line) > len(line.lstrip())

                if is_indented:
                    if current_rule: # It's a successor for the current rule
                        if stripped_line.startswith('dynamic:'):
                            func_name = stripped_line.split(':')[1].strip()
                            if func_name in self.function_registry:
                                rules[current_rule] = self.function_registry[func_name]
                            else:
                                raise ValueError(f"Dynamic function '{func_name}' not found in registry for rule '{current_rule}'.")
                            continue

                        # Static rule with optional weight
                        parts = stripped_line.split('@')
                        successor = parts[0].strip()
                        weight = int(parts[1].strip()) if len(parts) > 1 else 1
                        
                        if isinstance(rules.get(current_rule), list):
                            rules[current_rule].append((successor, weight))
                else: # It's a new rule definition
                    current_rule = stripped_line.strip(':')
                    rules[current_rule] = []
        return rules

class LSystemManager:
    """Manages the loading, parsing, and caching of L-system rulesets."""

    def __init__(self, rules_directory):
        self.rules_directory = rules_directory
        self.lsystem_cache = {}
        self.function_registry = {}
        self.parser = LSystemParser(self.function_registry)

    def register_function(self, name, func):
        """
        Registers a Python function to be used as a dynamic rule.
        The name must match the one used in the .rules file.
        """
        self.function_registry[name] = func

    def get_lsystem(self, name):
        """
        Gets an LSystem instance for a given ruleset name.
        Loads from file and caches the result.
        """
        if name in self.lsystem_cache:
            return self.lsystem_cache[name]

        file_path = os.path.join(self.rules_directory, f"{name}.rules")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Rules file not found: {file_path}")

        rules_dict = self.parser.parse(file_path)
        lsystem_instance = LSystem(rules_dict)
        self.lsystem_cache[name] = lsystem_instance
        
        return lsystem_instance