"""
extract_data_structures: This method is the main entry point. It calls the _extract_variables method to extract all the variables from the data division of the COBOL program.

_extract_variables: A recursive function that looks for nodes with a nodeType of "variable" and collects them into the data_structures dictionary.

extract_dependencies: This method starts the process of identifying dependencies between data structures (e.g., variables). It looks for constructs like PERFORM_UNTIL or IF and calls _track_dependencies to follow their flow.

_track_dependencies: A recursive function that traces variable usage and assignment across different nodes in the AST, identifying which variables are used in which conditions or assigned new values.

serialize_data_structures: This method serializes the data structures into a JSON file for further analysis or visualization
"""
import json
import re

# class DataStructureExtractor:
#     def __init__(self, ast, data_division_node=None):
#         """
#         Initialize the DataStructureExtractor with AST and an optional data_division_node.

#         Args:
#             ast (dict): The abstract syntax tree (AST) of the COBOL program.
#             data_division_node (dict, optional): The data division node to start extraction. 
#                                                  If None, it will be determined automatically.
#         """
#         self.ast = ast
#         # If data_division_node is provided, use it; otherwise, fetch it using find_nodes_with_type
#         if data_division_node is None:
#             self.data_division_node = self.find_nodes_with_type(self.ast, node_type="dataDivision")
#         else:
#             self.data_division_node = [data_division_node]
        
#         self.data_structures = {}  # Initialize data structures dictionary

#     def find_nodes_with_type(self, node, node_type="dataDivision"):
#         """
#         Recursively search through the AST and return all nodes with the specified nodeType.
#         """
#         result = []
        
#         # Skip None nodes
#         if node is None:
#             return result
        
#         # Check if the current node matches the specified node_type
#         if node.get("nodeType") == node_type:
#             result.append(node)
        
#         # Recurse through all children of the current node
#         for child in node.get("children", []):
#             result.extend(self.find_nodes_with_type(child, node_type))  # Add any found nodes of the specified type
        
#         return result
#     def extract_data_structures(self):
#         """
#         Extracts variables and their attributes from the data division section of the AST.
#         Returns:
#             dict: A dictionary of extracted data structures, including variables.
#         """
#         data_structures = {}
#         print("Starting to extract data structures...")
#         self.recursive_traversal_for_data_division(self.data_division_node, data_structures)
#         print("Data structures extracted:", json.dumps(data_structures, indent=4))
#         return data_structures

#     def recursive_traversal_for_data_division(self, nodes, data_structures):
#         """
#         Recursively traverses nodes to find and extract data structures inside 'dataDivisionSection' and other relevant sections.
#         """
#         for section in nodes:
#             if section is None:
#                 continue
#             print(f"Checking section node: {section.get('nodeType')}")
            
#             # Always try to extract variables from any relevant section
#             if "children" in section:
#                 self.extract_variables_from_section(section, data_structures)  # Apply extraction to all children

#                 # Recursively check children of the current section node
#                 print(f"Recursively checking children of {section.get('nodeType')}")
#                 self.recursive_traversal_for_data_division(section["children"], data_structures)

#     def extract_variables_from_section(self, section, data_structures):
#         """
#         Extract variables from a section (like workingStorageSection or fileSection).
#         """
#         if not section.get("children"):
#             print(f"Section {section.get('nodeType')} has no children, skipping.")
#             return
        
#         for item in section.get("children", []):
#             if item is None:
#                 continue
#             print(f"Processing item: {item.get('nodeType')}")
#             self.extract_data_from_children(item, data_structures)

#     def extract_data_from_children(self, item, data_structures):
#         """
#         Extract data like dataName, levelNumber, or pictureClause from children of the section.
#         """
#         for child in item.get("children", []):
#             if child is None:
#                 continue
#             print(f"Checking child node: {child.get('nodeType')}")
#             # Extract dataName, levelNumber, or pictureClause if they exist
#             if child.get("nodeType") == "dataName":
#                 data_name = self.get_terminal_text(child)
#                 print(f"Found data name: {data_name}")
#                 if data_name:
#                     if data_name not in data_structures:
#                         data_structures[data_name] = {
#                             "level": None,
#                             "pictureClause": None,
#                             "dependencies": []
#                         }

#             elif child.get("nodeType") == "levelNumber":
#                 level_number = self.get_terminal_text(child)
#                 print(f"Found level number: {level_number}")
#                 if level_number:
#                     for name, structure in data_structures.items():
#                         if structure["level"] is None:
#                             structure["level"] = level_number

#             elif child.get("nodeType") == "dataPictureClause":
#                 picture_clause = self.get_terminal_text(child)
#                 print(f"Found picture clause: {picture_clause}")
#                 if picture_clause:
#                     for name, structure in data_structures.items():
#                         if structure["pictureClause"] is None:
#                             structure["pictureClause"] = picture_clause

#     def get_terminal_text(self, node):
#         """
#         Recursively get terminal text (skips None or invalid nodes).
#         """
#         if node and "text" in node and node["text"]:
#             return node["text"]
#         for child in node.get("children", []):
#             terminal_text = self.get_terminal_text(child)
#             if terminal_text:
#                 return terminal_text
#         return None
#     def serialize_data_structures(self, output_path):
#         """
#         Serialize the extracted data structures to a JSON file.

#         Args:
#             output_path (str): The path where the JSON file will be saved.
#         """
#         with open(output_path, 'w') as json_file:
#             json.dump(self.data_structures, json_file, indent=4)
#     def extract_dependencies(self):
#         """
#         Extract dependencies for variables used in conditions of control flow nodes (IF, PERFORM_UNTIL).
#         Updates the data structures with dependencies based on control flow analysis.
#         """
#         print("Starting to extract dependencies...")
        
#         # Start by traversing the AST to find control flow nodes and extract dependencies
#         self._extract_control_flow_dependencies(self.ast)

#         print("Dependency extraction complete.")

#     def _extract_control_flow_dependencies(self, node):
#         """
#         Traverse through the AST, identify control flow nodes (IF, PERFORM_UNTIL), and update data structures with dependencies.
#         """
#         if node is None:
#             return

#         # Ensure node is a valid dictionary before processing
#         if not isinstance(node, dict):
#             print(f"Skipping invalid node: {node} (Type: {type(node)})")
#             return

#         # Check for IF and PERFORM_UNTIL nodes and extract their conditions
#         if node.get("nodeType") in ["IF", "PERFORM_UNTIL"]:
#             print(f"Found control flow node: {node['nodeType']}")
#             condition = self._extract_condition(node)
#             if condition:
#                 self._update_dependencies(condition, node.get("nodeType"))

#         # Recursively process children of this node (if any)
#         if "children" in node:
#             for child in node["children"]:
#                 self._extract_control_flow_dependencies(child)

#     def extract_dependencies(self):
#         """
#         Extract dependencies for variables used in conditions of control flow nodes (IF, PERFORM_UNTIL).
#         Updates the data structures with dependencies based on control flow analysis.
#         """
#         print("Starting to extract dependencies...")
        
#         # Start by traversing the AST to find control flow nodes and extract dependencies
#         self._extract_control_flow_dependencies(self.ast)
        
#         print("Dependency extraction complete.")

#     def _extract_control_flow_dependencies(self, node):
#         """
#         Traverse through the AST, identify control flow nodes (IF, PERFORM_UNTIL), and update data structures with dependencies.
#         """
#         if node is None:
#             return
        
#         # Ensure node is a valid dictionary before processing
#         if not isinstance(node, dict):
#             print(f"Skipping invalid node: {node} (Type: {type(node)})")
#             return

#         # Check for IF and PERFORM_UNTIL nodes and extract their conditions
#         if node.get("nodeType") in ["IF", "PERFORM_UNTIL"]:
#             print(f"Found control flow node: {node['nodeType']}")
#             condition = self._extract_condition(node)
#             if condition:
#                 self._update_dependencies(condition, node.get("nodeType"))
        
#         # Recursively process children of this node (if any)
#         if "children" in node:
#             for child in node["children"]:
#                 self._extract_control_flow_dependencies(child)

#     def _extract_condition(self, node):
#         """
#         Extract the condition expression from control flow nodes (IF, PERFORM_UNTIL).
#         """
#         # Extract the condition for IF and PERFORM_UNTIL control flow nodes
#         if "condition" in node:
#             print(f"Condition found for {node['nodeType']}: {node['condition'].get('text')}")
#             return node["condition"]
#         return None

#     def _update_dependencies(self, condition, node_type):
#         """
#         Update the dependencies of variables involved in the given condition.
#         """
#         # Extract the text from the condition
#         condition_text = condition.get("text")
#         if not condition_text:
#             print(f"Skipping condition with no text: {condition}")
#             return

#         # Dynamically extract variables from condition text
#         variables_used = self.extract_variables_from_condition_text(condition_text)

#         #Hack : TODO
#         temp_variables = self.extract_variables_from_data_structures(condition_text)
#         print("hack:", condition_text, ":", temp_variables)
#         # Iterate over extracted variables and update dependencies
#         for variable in set(variables_used).union(temp_variables):
#             # Check if the variable already exists in data structures, if not, initialize it
#             if variable not in self.data_structures:
#                 self.data_structures[variable] = {"dependencies": []}
#             print("check1:", node_type)
#             # Update the dependencies for the variable
#             if node_type not in self.data_structures[variable]["dependencies"]:
#                 self.data_structures[variable]["dependencies"].append(node_type)
#                 print(f"Updated dependency for {variable}: {self.data_structures[variable]['dependencies']}")
#     def extract_variables_from_data_structures(self, condition_text):
#         """
#         This function extracts all the variables from the data_structures that are present in the condition text.
        
#         Args:
#             condition_text (str): The condition text from control flow nodes (e.g., IF or PERFORM_UNTIL).
            
#         Returns:
#             list: A list of variable names found in the condition text.
#         """
#         print(f"Extracting variables from condition text: {condition_text}")
        
#         variables_found = []
        
#         # Get all the variable names from data structures
#         all_variables = self.data_structures.keys()
        
#         # Iterate through the variables and check if they exist in the condition text
#         for variable in all_variables:
#             # Check if the variable is present in the condition text
#             if variable in condition_text:
#                 print(f"Variable {variable} found in condition text")
#                 variables_found.append(variable)
        
#         print(f"Variables found in condition text: {variables_found}")
#         return variables_found
#     def extract_variables_from_condition_text(self, condition_text):
#         """
#         Extract variable names from the condition text (simple variable extraction).
#         This function parses the condition and identifies variable-like strings.
        
#         Args:
#             condition_text (str): The condition text from the control flow node (e.g., IF or PERFORM_UNTIL).

#         Returns:
#             list: A list of variables used in the condition.
#         """
#         print(f"Parsing condition text: {condition_text}")
#         variables = []
        
#         # Split the condition text into words and look for uppercase alphanumeric words
#         for word in condition_text.split():
#             # We are assuming that variables are alphanumeric and in uppercase (standard for COBOL variables)
#             if word.isalnum() and word.isupper():  # Simple check for variable-like strings
#                 variables.append(word)

#         print(f"Extracted variables: {variables}")
#         return variables
    
# {
#   "END-OF-FILE": {
#     "level": "01",
#     "pictureClause": "PIC",
#     "dependencies": ["PERFORM_UNTIL"]
#   },
#   "ACCTFILE-STATUS": {
#     "level": "05",
#     "pictureClause": "PIC",
#     "dependencies": ["IF", "IF", "IF", "IF", "IF"]
#   },
#   "APPL-AOK": {
#     "level": "01",
#     "pictureClause": "PIC",
#     "dependencies": ["IF", "IF", "IF", "IF"]
#   },
#   "IO-STATUS": {
#     "level": "05",
#     "pictureClause": "PIC",
#     "dependencies": ["IF"]
#   },
#   "IO-STAT1": {
#     "level": "05",
#     "pictureClause": "PIC",
#     "dependencies": ["IF"]
#   }
# }

# import re
class DataStructureExtractor:
    def __init__(self, ast, data_division_node=None):
        """
        Initialize the DataStructureExtractor with AST and an optional data_division_node.

        Args:
            ast (dict): The abstract syntax tree (AST) of the COBOL program.
            data_division_node (dict, optional): The data division node to start extraction. 
                                                 If None, it will be determined automatically.
        """
        self.ast = ast
        # If data_division_node is provided, use it; otherwise, fetch it using find_nodes_with_type
        if data_division_node is None:
            self.data_division_node = self.find_nodes_with_type(self.ast, node_type="dataDivision")
        else:
            self.data_division_node = [data_division_node]
        
        self.data_structures = {}  # Initialize data structures dictionary

    def find_nodes_with_type(self, node, node_type="dataDivision"):
        """
        Recursively search through the AST and return all nodes with the specified nodeType.
        """
        result = []
        
        # Skip None nodes
        if node is None:
            return result
        
        # Check if the current node matches the specified node_type
        if node.get("nodeType") == node_type:
            result.append(node)
        
        # Recurse through all children of the current node
        for child in node.get("children", []):
            result.extend(self.find_nodes_with_type(child, node_type))  # Add any found nodes of the specified type
        
        return result
    def extract_data_structures(self):
        """
        Extracts variables and their attributes from the data division section of the AST.
        Returns:
            dict: A dictionary of extracted data structures, including variables.
        """
        data_structures = {}
        print("Starting to extract data structures...")
        self.recursive_traversal_for_data_division(self.data_division_node, data_structures)
        print("Data structures extracted:", json.dumps(data_structures, indent=4))
        return data_structures

    def recursive_traversal_for_data_division(self, nodes, data_structures):
        """
        Recursively traverses nodes to find and extract data structures inside 'dataDivisionSection' and other relevant sections.
        """
        for section in nodes:
            if section is None:
                continue
            print(f"Checking section node: {section.get('nodeType')}")
            
            # Always try to extract variables from any relevant section
            if "children" in section:
                self.extract_variables_from_section(section, data_structures)  # Apply extraction to all children

                # Recursively check children of the current section node
                print(f"Recursively checking children of {section.get('nodeType')}")
                self.recursive_traversal_for_data_division(section["children"], data_structures)

    def extract_variables_from_section(self, section, data_structures):
        """
        Extract variables from a section (like workingStorageSection or fileSection).
        """
        if not section.get("children"):
            print(f"Section {section.get('nodeType')} has no children, skipping.")
            return
        
        for item in section.get("children", []):
            if item is None:
                continue
            print(f"Processing item: {item.get('nodeType')}")
            self.extract_data_from_children(item, data_structures)

    def extract_data_from_children(self, item, data_structures):
        """
        Extract data like dataName, levelNumber, or pictureClause from children of the section.
        """
        for child in item.get("children", []):
            if child is None:
                continue
            print(f"Checking child node: {child.get('nodeType')}")
            # Extract dataName, levelNumber, or pictureClause if they exist
            if child.get("nodeType") == "dataName":
                data_name = self.get_terminal_text(child)
                print(f"Found data name: {data_name}")
                if data_name:
                    if data_name not in data_structures:
                        data_structures[data_name] = {
                            "level": None,
                            "pictureClause": None,
                            "dependencies": []
                        }

            elif child.get("nodeType") == "levelNumber":
                level_number = self.get_terminal_text(child)
                print(f"Found level number: {level_number}")
                if level_number:
                    for name, structure in data_structures.items():
                        if structure["level"] is None:
                            structure["level"] = level_number

            elif child.get("nodeType") == "dataPictureClause":
                picture_clause = self.get_terminal_text(child)
                print(f"Found picture clause: {picture_clause}")
                if picture_clause:
                    for name, structure in data_structures.items():
                        if structure["pictureClause"] is None:
                            structure["pictureClause"] = picture_clause

    def get_terminal_text(self, node):
        """
        Recursively get terminal text (skips None or invalid nodes).
        """
        if node and "text" in node and node["text"]:
            return node["text"]
        for child in node.get("children", []):
            terminal_text = self.get_terminal_text(child)
            if terminal_text:
                return terminal_text
        return None
    def serialize_data_structures(self, output_path):
        """
        Serialize the extracted data structures to a JSON file.

        Args:
            output_path (str): The path where the JSON file will be saved.
        """
        with open(output_path, 'w') as json_file:
            json.dump(self.data_structures, json_file, indent=4)
    def extract_dependencies(self):
        """
        Extract dependencies for variables used in conditions of control flow nodes (IF, PERFORM_UNTIL).
        Updates the data structures with dependencies based on control flow analysis.
        """
        print("Starting to extract dependencies...")
        
        # Start by traversing the AST to find control flow nodes and extract dependencies
        self._extract_control_flow_dependencies(self.ast)

        print("Dependency extraction complete.")

    def _extract_control_flow_dependencies(self, node):
        """
        Traverse through the AST, identify control flow nodes (IF, PERFORM_UNTIL), and update data structures with dependencies.
        """
        if node is None:
            return

        # Ensure node is a valid dictionary before processing
        if not isinstance(node, dict):
            print(f"Skipping invalid node: {node} (Type: {type(node)})")
            return

        # Check for IF and PERFORM_UNTIL nodes and extract their conditions
        if node.get("nodeType") in ["IF", "PERFORM_UNTIL"]:
            print(f"Found control flow node: {node['nodeType']}")
            condition = self._extract_condition(node)
            if condition:
                self._update_dependencies(condition, node.get("nodeType"))

        # Recursively process children of this node (if any)
        if "children" in node:
            for child in node["children"]:
                self._extract_control_flow_dependencies(child)

# {
#   "END-OF-FILE": {
#     "level": "01",
#     "pictureClause": "PIC",
#     "dependencies": ["PERFORM_UNTIL"]
#   },
#   "ACCTFILE-STATUS": {
#     "level": "05",
#     "pictureClause": "PIC",
#     "dependencies": ["IF", "IF", "IF", "IF", "IF"]
#   },
#   "APPL-AOK": {
#     "level": "01",
#     "pictureClause": "PIC",
#     "dependencies": ["IF", "IF", "IF", "IF"]
#   },
#   "IO-STATUS": {
#     "level": "05",
#     "pictureClause": "PIC",
#     "dependencies": ["IF"]
#   },
#   "IO-STAT1": {
#     "level": "05",
#     "pictureClause": "PIC",
#     "dependencies": ["IF"]
#   }
# }
    def extract_dependencies(self):
        """
        Extract dependencies for variables used in conditions of control flow nodes (IF, PERFORM_UNTIL).
        Updates the data structures with dependencies based on control flow analysis.
        """
        print("Starting to extract dependencies...")
        
        # Start by traversing the AST to find control flow nodes and extract dependencies
        self._extract_control_flow_dependencies(self.ast)
        
        print("Dependency extraction complete.")

    def _extract_control_flow_dependencies(self, node):
        """
        Traverse through the AST, identify control flow nodes (IF, PERFORM_UNTIL), and update data structures with dependencies.
        """
        if node is None:
            return
        
        # Ensure node is a valid dictionary before processing
        if not isinstance(node, dict):
            print(f"Skipping invalid node: {node} (Type: {type(node)})")
            return

        # Check for IF and PERFORM_UNTIL nodes and extract their conditions
        if node.get("nodeType") in ["IF", "PERFORM_UNTIL"]:
            print(f"Found control flow node: {node['nodeType']}")
            condition = self._extract_condition(node)
            if condition:
                self._update_dependencies(condition, node.get("nodeType"))
        
        # Recursively process children of this node (if any)
        if "children" in node:
            for child in node["children"]:
                self._extract_control_flow_dependencies(child)

    def _extract_condition(self, node):
        """
        Extract the condition expression from control flow nodes (IF, PERFORM_UNTIL).
        """
        # Extract the condition for IF and PERFORM_UNTIL control flow nodes
        if "condition" in node:
            print(f"Condition found for {node['nodeType']}: {node['condition'].get('text')}")
            return node["condition"]
        return None

    def _update_dependencies(self, condition, node_type):
        """
        Update the dependencies of variables involved in the given condition.
        """
        # Extract the text from the condition
        condition_text = condition.get("text")
        if not condition_text:
            print(f"Skipping condition with no text: {condition}")
            return

        # Dynamically extract variables from condition text
        variables_used = self.extract_variables_from_condition_text(condition_text)

        #Hack : TODO
        temp_variables = self.extract_variables_from_data_structures(condition_text)
        print("hack:", condition_text, ":", temp_variables)
        # Iterate over extracted variables and update dependencies
        for variable in set(variables_used).union(temp_variables):
            # Check if the variable already exists in data structures, if not, initialize it
            if variable not in self.data_structures:
                self.data_structures[variable] = {"dependencies": []}
            print("check1:", node_type)
            # Update the dependencies for the variable
            if node_type not in self.data_structures[variable]["dependencies"]:
                self.data_structures[variable]["dependencies"].append(node_type)
                print(f"Updated dependency for {variable}: {self.data_structures[variable]['dependencies']}")
    def extract_variables_from_data_structures(self, condition_text):
        """
        This function extracts all the variables from the data_structures that are present in the condition text.
        
        Args:
            condition_text (str): The condition text from control flow nodes (e.g., IF or PERFORM_UNTIL).
            
        Returns:
            list: A list of variable names found in the condition text.
        """
        print(f"Extracting variables from condition text: {condition_text}")
        
        variables_found = []
        
        # Get all the variable names from data structures
        all_variables = self.data_structures.keys()
        
        # Iterate through the variables and check if they exist in the condition text
        for variable in all_variables:
            # Check if the variable is present in the condition text
            if variable in condition_text:
                print(f"Variable {variable} found in condition text")
                variables_found.append(variable)
        
        print(f"Variables found in condition text: {variables_found}")
        return variables_found
    def extract_variables_from_condition_text(self, condition_text):
        """
        Extract variable names from the condition text (simple variable extraction).
        This function parses the condition and identifies variable-like strings.
        
        Args:
            condition_text (str): The condition text from the control flow node (e.g., IF or PERFORM_UNTIL).

        Returns:
            list: A list of variables used in the condition.
        """
        print(f"Parsing condition text: {condition_text}")
        variables = []
        
        # Split the condition text into words and look for uppercase alphanumeric words
        for word in condition_text.split():
            # We are assuming that variables are alphanumeric and in uppercase (standard for COBOL variables)
            if word.isalnum() and word.isupper():  # Simple check for variable-like strings
                variables.append(word)

        print(f"Extracted variables: {variables}")
        return variables
