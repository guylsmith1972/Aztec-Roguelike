#
# L-System Graph Generator
#
# This module provides an interpreter for L-system output strings to generate
# directed graphs. It is designed to work with an L-system that has been
# augmented with special syntax for labeling nodes and creating edges.
#
# --- How to Use ---
#
# 1. Grammar Syntax:
#    Your L-system grammar should produce strings containing special operators:
#
#    a) Node Labeling `#(label_name)`:
#       Creates a named node that can be referenced later. The node's type will be
#       the symbol immediately preceding the label.
#       Example: `plaza #(main_plaza)` -> This syntax is no longer supported directly.
#       The new syntax requires the label to come *after* the node it labels.
#       Example: `town_square #(gate)` is interpreted as a node of type 'town_square'
#       which is then given the label 'gate'.
#
#    b) Directed Edge `->(label_name)`:
#       Creates a directed edge from the most recently created node to the node
#       with the specified label.
#       Example: `market ->(gate)` -> Creates a 'market' node connected to the
#       current branch, and then draws an edge from that market node back to the
#       node previously labeled 'gate'.
#
#    c) Branching `[` and `]`:
#       These are used to create branches in the graph, similar to turtle graphics.
#       `[` pushes the current node onto a stack and `]` pops it off, allowing
#       generation to return to an earlier branching point.
#
# 2. Generating a Graph:
#
#    graph_gen = GraphGenerator()
#    map_graph = graph_gen.generate(lsystem_output_string)
#    - 'lsystem_output_string' is the string produced by the LSystem.iterate() method.
#    - The `generate` method returns a dictionary:
#      {
#          "nodes": [{"id": 0, "type": "root"}, ...],
#          "edges": [{"source": 0, "target": 1}, ...]
#      }
#      This structure can then be used to build a game map, quest chain, etc.
#
#
# L-System Graph Generator
#
# This module provides an interpreter for L-system output strings to generate
# directed graphs. It is designed to work with an L-system that has been
# augmented with special syntax for labeling nodes and creating edges.
#
# --- How to Use ---
#
# 1. Grammar Syntax:
#    Your L-system grammar should produce strings containing special operators:
#
#    a) Node Labeling `label(name)`:
#       Creates a named node that can be referenced later.
#
#    b) Directed Edge `connect(name)`:
#       Creates a directed edge from the most recently created node to the node
#       with the specified label.
#
#    c) Branching `[` and `]`:
#       (Usage remains the same)
#
# 2. Generating a Graph:
#    (Usage remains the same)
#
import re

class GraphGenerator:
    def __init__(self):
        self.nodes = []
        self.edges = []
        self.named_nodes = {}
        self.node_counter = 0
        self.state_stack = []

    def add_node(self, node_type, parent_node=None):
        """Adds a new node and an edge from the parent, returning the new node."""
        node_id = self.node_counter
        new_node = {'id': node_id, 'type': node_type}
        self.nodes.append(new_node)
        
        if parent_node is not None:
            self.edges.append({'source': parent_node['id'], 'target': node_id})
            
        self.node_counter += 1
        return new_node

    def add_edge(self, source_node, target_label):
        """Adds an edge from the source node to a named node."""
        if source_node and target_label in self.named_nodes:
            target_node = self.named_nodes[target_label]
            new_edge = {'source': source_node['id'], 'target': target_node['id']}
            if new_edge not in self.edges:
                self.edges.append(new_edge)
            
    def generate(self, lsystem_string):
        """Parses an L-system string to build a graph data structure."""
        self.nodes, self.edges, self.named_nodes = [], [], {}
        self.node_counter, self.state_stack = 0, []

        current_node = self.add_node('root')
        self.state_stack.append(current_node)
        
        parts = lsystem_string.split()
        
        for part in parts:
            if part == '[':
                self.state_stack.append(current_node)
            elif part == ']':
                if len(self.state_stack) > 1:
                    current_node = self.state_stack.pop()
            # FIX: Check for new label() syntax
            elif part.startswith('label(') and part.endswith(')'):
                label = part[6:-1]
                self.named_nodes[label] = current_node
            # FIX: Check for new connect() syntax
            elif part.startswith('connect(') and part.endswith(')'):
                label = part[8:-1]
                self.add_edge(current_node, label)
            else: # It's a normal symbol/node type
                parent = self.state_stack[-1]
                current_node = self.add_node(part, parent_node=parent)
        
        return {"nodes": self.nodes, "edges": self.edges}