#
# Scratchpad for Testing L-System Graph Generation
#
# This script serves as a complete, runnable example of the L-system-based
# graph generation pipeline. It demonstrates the following steps:
#
# PREREQUISITE:
#   This script now assumes that a 'settlement.rules' file exists in the
#   'Assets/Rulesets/' directory. The content for this file has been
#   provided in previous responses.
#
# 1.  Initialization: It imports and initializes the LSystemManager and the
#     GraphGenerator.
#
# 2.  Parsing and Generation: It loads the 'settlement' ruleset from the file,
#     uses a deterministically seeded random number generator, and iterates the
#     L-system to produce a string output.
#
# 3.  Graph Interpretation: The generated string is then fed into the
#     GraphGenerator, which parses the special syntax (#(label), ->(label), etc.)
#     to construct a directed graph.
#
# 4.  Display: Finally, it prints the L-system's raw output string and the
#     resulting graph data structure (nodes and edges) to the console in a
#     human-readable JSON format.
#
import os
import random
import json

# Assuming the necessary modules are in the parent directory
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import lsystem_parser
import graph_generator

def main():
    """Main execution function."""
    
    # --- 1. Define Environment ---
    # Note: Assumes script is run from the project's root 'Roguelike' directory
    rules_directory = os.path.join("Assets", "Rulesets")
    ruleset_name = "settlement"
    
    # Ensure the required file exists before proceeding
    rules_file_path = os.path.join(rules_directory, f"{ruleset_name}.rules")
    if not os.path.exists(rules_file_path):
        print(f"ERROR: Rules file not found at '{rules_file_path}'")
        print("Please ensure the 'settlement.rules' file exists in the 'Assets/Rulesets/' directory.")
        return

    # --- 2. Initialize Managers and Get L-System ---
    print("\nInitializing L-System Manager...")
    lsystem_manager = lsystem_parser.LSystemManager(rules_directory)
    settlement_lsystem = lsystem_manager.get_lsystem(ruleset_name)

    # --- DEBUG LOGGING: Print the parsed rules dictionary ---
    print("\n--- Parsed Rules Dictionary ---")
    # This will show us exactly what the parser extracted from the file.
    # If a rule is missing successors, it's a parsing error.
    try:
        # Convert functions to string representation for clean printing
        rules_for_printing = {k: str(v) for k, v in settlement_lsystem.rules.items()}
        print(json.dumps(rules_for_printing, indent=2))
    except Exception as e:
        print(f"Could not serialize rules for printing: {e}")
        print(settlement_lsystem.rules)
    print("-----------------------------\n")

    # --- 3. Generate L-System Output ---
    print("Generating L-System string step-by-step...")
    # Use a fixed seed for deterministic, repeatable results
    seed = 42
    rng = random.Random(seed)
    axiom = 'start'
    iterations = 3
    
    # --- DEBUG LOGGING: Manual iteration to trace expansion ---
    current_symbols = axiom.split()
    print(f"Iteration 0 (Axiom): {current_symbols}")

    for i in range(iterations):
        new_symbols = []
        for symbol in current_symbols:
            # We pass an empty context for this test
            expanded = settlement_lsystem.apply_rules(symbol, rng, {})
            new_symbols.extend(expanded.split())
        
        print(f"Iteration {i+1}: {new_symbols}")
        if current_symbols == new_symbols:
            print("L-System stabilized. No further changes.")
            break
        current_symbols = new_symbols

    output_string = " ".join(current_symbols)
    
    print("-" * 50)
    print(f"Final Generated L-System String (Seed: {seed}):")
    print(output_string)
    print("-" * 50)

    # --- 4. Generate Graph from String ---
    print("\nGenerating graph from string...")
    graph_gen = graph_generator.GraphGenerator()
    map_graph = graph_gen.generate(output_string)

    # --- 5. Display Result ---
    print("\nGenerated Graph Data:")
    # Use json.dumps for pretty printing the dictionary
    print(json.dumps(map_graph, indent=2))
    print("-" * 50)


if __name__ == "__main__":
    main()