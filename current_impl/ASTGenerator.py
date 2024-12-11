import json
from antlr4.tree.Tree import ParseTree, TerminalNodeImpl


class ASTGenerator:
    def __init__(self, parse_tree: ParseTree, parser):
        """
        Initialize the ASTGenerator with a parse tree and parser.

        Args:
            parse_tree (ParseTree): The root node of the parse tree.
            parser: The parser instance to retrieve rule names.
        """
        self.parse_tree = parse_tree
        self.rule_names = parser.ruleNames

    def _traverse_tree(self, node):
        """
        Recursively traverse the parse tree to build the refined AST.

        Args:
            node (ParseTree): The current node in the parse tree.

        Returns:
            dict: A dictionary representing the refined AST node.
        """
        # Handle terminal nodes (tokens)
        if isinstance(node, TerminalNodeImpl):
            # Skip punctuation like '.'
            if node.getText() in [".", "END-IF", "END-PERFORM"]:
                # print(f"Skipping punctuation node: {node.getText()}")  # Debug log
                return None
            return {
                "nodeType": f"TOKEN_{node.getText().upper()}" if node.getText() else "UNKNOWN",
                "text": node.getText(),
            }

        # Retrieve node type using grammar rule names
        node_type = (
            self.rule_names[node.getRuleIndex()]
            if hasattr(node, "getRuleIndex") else
            "UNKNOWN"
        )

        # Handle specific constructs
        if node_type == "performStatement":
            ## Differentiate between PERFORM and PERFORM_UNTIL
            perform_node = {}

            # Check if this is a PERFORM_UNTIL statement
            if self._is_perform_until(node):
                # Handle PERFORM_UNTIL specifically
                # print(f"Processing PERFORM_UNTIL node")
                perform_node["nodeType"] = "PERFORM_UNTIL"
                perform_node["condition"] = self._extract_condition(node)
                perform_node["body"] = [self._traverse_tree(node.getChild(i)) for i in range(node.getChildCount())],
            else:
                # Handle simple PERFORM statement
                # print(f"Processing simple PERFORM node")
                perform_node["nodeType"] = "PERFORM"
                # perform_node["condition"] = None  # No condition for a simple PERFORM
                perform_node["body"] = [self._traverse_tree(node.getChild(i)) for i in range(node.getChildCount())],

            # Process body of the perform statement (children)
            perform_node["body"] = [
                self._traverse_tree(node.getChild(i)) for i in range(node.getChildCount())
            ]

            return perform_node

        elif node_type == "ifStatement":
            # Abstract IF_THEN construct
            if_node = {
                "nodeType": "IF",
                "condition": self._extract_condition(node),  # Corrected `_extract_condition`
                "then": [self._traverse_tree(node.getChild(i)) for i in range(node.getChildCount())],
            }
            
            return if_node

        # Default case: Traverse and process children
        children = [self._traverse_tree(node.getChild(i)) for i in range(node.getChildCount()) if node.getChild(i)] #Skip None Results

        return {
            "nodeType": node_type,
            "text": None,  # Non-leaf nodes have no direct text
            "children": children,
        }

    def _is_perform_until(self, node):
        """
        Check if the current node represents a PERFORM_UNTIL statement.

        Args:
            node (ParseTree): The current node in the parse tree.

        Returns:
            bool: True if the node represents a PERFORM_UNTIL statement, False otherwise.
        """
        # Check if the node is of type 'performStatement' and contains 'UNTIL'
        # print(f"Checking node: {node.getText()}")  # Debug log
        # print("Node structure:")
        # node_dict = self._node_to_dict(node)  # Convert node to dict for serialization
        # print(json.dumps(node_dict, indent=4))  # Print the JSON structure of the node
        for i in range(node.getChildCount()):
            child = node.getChild(i)
            # print(f"Checking child node: {child.getText()}")  # Debug log
            
            if  child.getText().upper() == "UNTIL" or "UNTIL" in node.getText():
            # if isinstance(child, TerminalNodeImpl) and child.getText() == "UNTIL":
                return True
        # We may have to recursively look deeper into sub-children if it's a nested statement
        if child.getChildCount() > 0:
            return self._is_perform_until(child)  # Recursive call for deeper nodes

        return False
    def _node_to_dict(self, node):
        """
        Convert a ParseTree node into a serializable dictionary for logging purposes.

        Args:
            node (ParseTree): The current node to convert.

        Returns:
            dict: A dictionary representation of the node.
        """
        if isinstance(node, TerminalNodeImpl):
            return {
                "nodeType": f"TOKEN_{node.getText().upper()}" if node.getText() else "UNKNOWN",
                "text": node.getText(),
            }

        # Handle internal nodes
        children = []
        for i in range(node.getChildCount()):
            child = node.getChild(i)
            children.append(self._node_to_dict(child))  # Recursively convert children

        node_type = self.rule_names[node.getRuleIndex()] if hasattr(node, "getRuleIndex") else "UNKNOWN"
        return {
            "nodeType": node_type,
            "text": None,  # Non-leaf nodes have no direct text
            "children": children,
        }
    def _extract_condition(self, node):
        """
        Extract and simplify condition constructs into a single expression.

        Args:
            node (ParseTree): Current AST node representing a condition.

        Returns:
            dict: Simplified condition node.
        """
        if node is None or node.getChildCount() == 0:
            return None

        # Base case: Check if the node type corresponds to a condition
        node_type = self.rule_names[node.getRuleIndex()]
        # print(f"node_type", node_type)
        # Handle nodes that represent specific conditions
        if node_type == "performStatement":
            # If it's a PERFORM_UNTIL, extract the condition from the UNTIL clause
            # print(f"Extracting condition for PERFORM_UNTIL node {node_type}", "total children", node.PERFORM(), node.performProcedureStatement, 
            #       node.performInlineStatement, node.getRuleIndex)
            for i in range(node.getChildCount()):
                child = node.getChild(i)
                if child.getText() == "UNTIL":
                    # We found the UNTIL node, now look for the sibling condition
                    for j in range(node.getChildCount()):
                        sibling = node.getChild(j)
                        if sibling.getText() == "condition":
                            # Extract the actual condition text from the "condition" node's children
                            condition_text = " ".join(
                                sibling.getChild(k).getText() for k in range(sibling.getChildCount())
                                if sibling.getChild(k).getText()  # Skip empty or irrelevant nodes
                            )
                            print(f"Condition extracted from PERFORM_UNTIL: {condition_text}")
                            
        
        # # Handle specific conditions for PERFORM (could be body or a nested PERFORM_UNTIL)
        # elif node_type == "PERFORM":
        #     print(f"Extracting condition for PERFORM node {node_type}")
        #     # Check for condition within the body of the PERFORM statement
        #     for child in node.get("children", []):
        #         condition = self._extract_condition(child)
        #         if condition:
        #             return condition
        if node_type.lower() in ["performuntil", "condition", "ifcondition", "perform"]:
            condition_text = " ".join(
                child.getText() for child in [node.getChild(i) for i in range(node.getChildCount())] 
                if child.getText() # Skip empty or irrelevant nodes
            )
            return {"nodeType": "EXPRESSION", "text": condition_text}
        # Recursive case: Traverse children to locate condition
        for i in range(node.getChildCount()):
            child_condition = self._extract_condition(node.getChild(i))
            if child_condition:
                return child_condition

        return None



    def generate_ast(self) -> dict:
        """
        Generate the AST from the parse tree.

        Returns:
            dict: The AST as a Python dictionary.
        """
        return self._traverse_tree(self.parse_tree)

    def serialize_ast(self, output_path: str):
        """
        Serialize the AST to a JSON file.

        Args:
            output_path (str): Path to the output JSON file.
        """
        ast = self.generate_ast()
        with open(output_path, "w") as json_file:
            json.dump(ast, json_file, indent=4)
