from mcp.server.fastmcp import FastMCP
import sys
from evaluation_model import evaluate_rows

mcp = FastMCP("server", version="0.0.1")

@mcp.tool()
def add(a: int, b: int) -> int:
    """
    Adds two integer numbers together and returns their sum.
    
    Args:
        a (int): First integer to add
        b (int): Second integer to add
        
    Returns:
        int: The sum of a and b
        
    Example:
        >>> result = add(5, 3)
        >>> print(result)
        8
    """
    return a + b

@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """
    Generates a personalized greeting message for the given name.
    This resource follows the pattern 'greeting://{name}' where {name} is the person to greet.
    
    Args:
        name (str): The name of the person to greet
        
    Returns:
        str: A formatted greeting message
        
    Example:
        >>> message = get_greeting("Alice")
        >>> print(message)
        "Hello, Alice!"
    """
    return f"Hello, {name}!"

@mcp.tool()
def get_profile_info(a: int, b: int) -> str:
    """
    Retrieves detailed profile information about Jake from Alaska.
    This is a demonstration tool to show how Claude Desktop can access and use profile information.
    
    Note: Currently returns a hardcoded profile for demonstration purposes.
    
    Args:
        a (int): Placeholder parameter (not used)
        b (int): Placeholder parameter (not used)
        
    Returns:
        str: A string containing Jake's profile information including:
            - Age
            - Location
            - Hobbies
            - Other personal details
            
    Example:
        >>> info = get_profile_info(1, 2)
        >>> print(info)
        "Jake is from Alaska. He is 25 years old and lives in Anchorage. He likes to ski and play guitar."
    """
    return "Jake is from Alaska. He is 25 years old and lives in Anchorage. He likes to ski and play guitar."

@mcp.tool()
def evaluation_model(file_path: str):
    """
    Processes a CSV file and generates random evaluation scores for each row.
    This tool serves as an interface to the evaluation_rows function from the evaluation_model module.
    
    Args:
        file_path (str): Path to the CSV file to evaluate, relative to the project root
                        or an absolute path.
        
    Returns:
        list: A list of random integers between 0 and 4, where:
             - Each integer corresponds to a row in the input CSV
             - 0 represents the lowest score
             - 4 represents the highest score
              
    Example:
        >>> scores = evaluation_model("datasets/samples.csv")
        >>> print(scores)
        [2, 4, 1, 3, 0]
    """
    return evaluate_rows(file_path)

@mcp.tool()
def calculate_bmi(weight_kg: float, height_m: float) -> float:
    """Calculate BMI given weight in kg and height in meters"""
    return weight_kg / (height_m**2)

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')