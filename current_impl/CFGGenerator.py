import json
from collections import defaultdict

class CFGGenerator:
    def __init__(self, ast: dict):
        """
        Initialize the CFGGenerator with an AST.

        Args:
            ast (dict): The Abstract Syntax Tree of the COBOL program.
        """
        self.ast = ast
        self.graph = defaultdict(list)  # Adjacency list for the CFG
        self.node_counter = 0  # Unique ID for nodes
        self.nodes = {}  # Store nodes with metadata

    def _create_node(self, label, node_type, ast_node=None):
        """
        Create a new node in the CFG.

        Args:
            label (str): Human-readable label for the node.
            node_type (str): Type of the node (e.g., PERFORM, IF, DISPLAY).
            ast_node (dict): Corresponding AST node, if any.

        Returns:
            dict: The created node.
        """
        self.node_counter += 1
        node = {
            "id": self.node_counter,
            "label": label,
            "type": node_type,
            "astNode": ast_node,
        }
        self.nodes[self.node_counter] = node
        return node
    
    
    def _extract_condition(self, node):
        """
        Extract and simplify condition constructs into a structured representation.

        Args:
            node (dict): Current AST node representing a condition.

        Returns:
            dict: Structured representation of the condition or None if no condition exists.
        """
        if not node:  # Handle None or invalid nodes
            return None

        # Handle PERFORM_UNTIL - Look for the condition node after 'UNTIL'
        # if node["nodeType"] == "PERFORM_UNTIL":
        #     # Iterate over the body of PERFORM_UNTIL
        #     for child in node.get("body", []):  # Look through the body for the UNTIL condition
        #         if child and "children" in child:
        #             for subchild in child.get("children", []):
        #                 if subchild and subchild["nodeType"] == "condition":
        #                     print(f"PERFORM_UNTIL Condition extracted: {subchild.get('text')}")
        #                     return subchild  # Return the condition directly

        # Handle IF - Direct condition after 'IF'
        if node["nodeType"] in ["IF","PERFORM_UNTIL"]  and "condition" in node:
            print(f"IF Condition extracted: {node['condition'].get('text')}")
            return node["condition"]  # Return the 'condition' node from IF

        # Recursively search children for condition nodes
        for child in node.get("children", []):
            if child and child["nodeType"] in ["condition", "simpleCondition"]:
                print(f"Condition extracted from child: {child.get('text')}")
                return self._extract_condition(child)

        # Fallback: Concatenate the text from children if no condition found
        condition_text = " ".join(
            str(child.get("text", "")) for child in node.get("children", []) if child and "text" in child
        )
        if condition_text:
            print(f"Fallback condition constructed: {condition_text}")
            return {"nodeType": "EXPRESSION", "text": condition_text}

        # If no condition was found, log and return None
        print(f"Condition extraction failed for nodeType: {node['nodeType']}, node ID: {node.get('id', 'Unknown')}")
        return None
    def _extract_condition(self, node):
        """
        Extract and simplify condition constructs into a structured representation.

        Args:
            node (dict): Current AST node representing a condition.

        Returns:
            dict: Structured representation of the condition or None if no condition exists.
        """
        if not node:  # Handle None or invalid nodes
            return None

        # Handle IF and PERFORM_UNTIL - Look for the condition node
        if node["nodeType"] in ["IF", "PERFORM_UNTIL"] and "condition" in node:
            # Extract the condition for IF or PERFORM_UNTIL
            condition = node["condition"]
            print(f"{node['nodeType']} Condition extracted: {condition.get('text')}")

            # Ensure 'children' exists and wrap the condition inside it
            if "children" not in condition:
                condition["children"] = []  # Add children if missing
            condition["children"].append({
                "nodeType": "EXPRESSION",
                "text": condition.get("text", "")  # Make sure 'text' is populated
            })

            return condition  # Return the structured condition directly

        # Recursively search children for condition nodes
        for child in node.get("children", []):
            if child and child["nodeType"] in ["condition", "simpleCondition"]:
                print(f"Condition extracted from child: {child.get('text')}")
                return self._extract_condition(child)

        # Fallback: Concatenate the text from children if no condition found
        condition_text = " ".join(
            str(child.get("text", "")) for child in node.get("children", []) if child and "text" in child
        )
        if condition_text:
            print(f"Fallback condition constructed: {condition_text}")
            return {"nodeType": "EXPRESSION", "text": condition_text, "children": []}

        # If no condition was found, log and return None
        print(f"Condition extraction failed for nodeType: {node['nodeType']}, node ID: {node.get('id', 'Unknown')}")
        return None



    # def _extract_control_flow(self, node, parent_node=None):
    #     """
    #     Recursively extract control flow from the AST.

    #     Args:
    #         node (dict): Current AST node.
    #         parent_node (dict): Parent CFG node, if any.
    #     """
    #     if node is None:
    #         return 
    #     # Configuration for control flow types
    #     control_flow_config = {
    #         "PERFORM_UNTIL": {"extract_condition": True},
    #         "IF": {"extract_condition": True},
    #         "DISPLAY": {"extract_condition": False},
    #         "PERFORM": {"extract_condition": False},
    #         "CALL": {"extract_condition": False},
    #     }
        
    #     if "nodeType" not in node:
    #         return

    #     # Check if the node is a control flow type
    #     node_type = node["nodeType"]
        
    #     if node_type in control_flow_config:
    #         # Extract condition dynamically
    #         condition = self._extract_condition(node)
    #         if condition is None:
    #             print(f"Condition extraction failed for nodeType: {node_type}, node ID: {self.node_counter}")
    #             # print(f"AST Node Subtree: {json.dumps(node, indent=4)}")  # Log full AST subtree

    #         # Create a new CFG node
    #         cfg_node = self._create_node(
    #             label=node.get("text", node_type),
    #             node_type=node_type,
    #             ast_node={**node, "condition": condition},  # Include condition in AST node
    #         )

    #         # Add edge from parent to this node if parent exists
    #         if parent_node:
    #             print(f"Adding edge from {parent_node['id']} to {cfg_node['id']}")  # Debug log
    #             self.graph[parent_node["id"]].append(cfg_node["id"])
    #         else:
    #             print(f"Root node created: {cfg_node['id']}")  # Debug log for root nodes
    #         # # Process children (body of PERFORM_UNTIL or IF)
    #         # if "children" in node:
    #         #     for child in node["children"]:
    #         #         if child:
    #         #             self._extract_control_flow(child, cfg_node)  # Recursively process children

    #         # # Pass the current node as the new parent
    #         parent_node = cfg_node
    #     # print(parent_node, node)
    #     # Recurse for children
    #     # if "children" in node:
    #     #     for child in node["children"]:
    #     #         print("recursive check for child", child)
    #     #         if child:
    #     #             self._extract_control_flow(child, parent_node)
    #     for child in node.get("children", []):
    #         print('----1---', parent_node)
    #         self._extract_control_flow(child, parent_node)
                
    def _extract_control_flow(self, node, parent_node=None):
        """
        Recursively extract control flow from the AST and create CFG nodes and edges.

        Args:
            node (dict): Current AST node.
            parent_node (dict): Parent CFG node, if any.
        """
        if not node:
            return
        # Configuration for control flow types
        control_flow_config = {
            "PERFORM_UNTIL": {"extract_condition": True},
            "IF": {"extract_condition": True},
            "DISPLAY": {"extract_condition": False},
            "PERFORM": {"extract_condition": False},
            "CALL": {"extract_condition": False},
        }

        if "nodeType" not in node:
            return parent_node  # If there's no nodeType, return the parent node (nothing to do)

        node_type = node["nodeType"]

        # Check if node is of a type requiring control flow handling
        if node_type in control_flow_config:
            # Extract condition dynamically
            condition = self._extract_condition(node)

            if condition is None:
                print(f"Condition extraction failed for nodeType: {node_type}, node ID: {self.node_counter}")

            # Create a new CFG node for the current node
            cfg_node = self._create_node(
                label=node.get("text", node_type),
                node_type=node_type,
                ast_node={**node, "condition": condition},  # Include condition in AST node
            )

            # If there is a parent, create an edge
            if parent_node:
                print(f"Adding edge from {parent_node['id']} to {cfg_node['id']}")  # Debug log
                self.graph[parent_node["id"]].append(cfg_node["id"])
            else:
                print(f"Root node created: {cfg_node['id']}")  # Debug log for root nodes

            # The new node (cfg_node) becomes the parent for its children
            parent_node = cfg_node

        # Recurse for children, passing the current node as the parent
        if "children" in node:
            for child in node["children"]:
                parent_node = self._extract_control_flow(child, parent_node)  # Pass and update parent_node

        return parent_node  # Return the parent node for next recursion level


    def build_cfg(self):
        """
        Build the Control Flow Graph (CFG) from the AST.

        Returns:
            dict: The CFG represented as an adjacency list.
        """
        # Start from the root node of the AST
        self._extract_control_flow(self.ast)
        return {"nodes": self.nodes, "edges": dict(self.graph)}

    def serialize_cfg(self, output_path):
        """
        Serialize the CFG to a JSON file.

        Args:
            output_path (str): Path to the output JSON file.
        """
        cfg = self.build_cfg()
        with open(output_path, "w") as json_file:
            json.dump(cfg, json_file, indent=4)
