import ollama
from dotenv import load_dotenv
import os

# Step 1: Load environment variables from .env file
load_dotenv()

# Path to the rules file
rules_path = "rules.txt"

# Function to extract text from a file
def extract_text(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
        return text
    except FileNotFoundError:
        return "File not found. Please check the file path."
    except Exception as e:
        return f"An error occurred: {e}"

# Step 2: Define the prompt template
def create_prompt(text, rules_path):
    rules = extract_text(rules_path)  # Load rules from a file or define them directly
    return f"""
    You are a moderator for a Reddit forum. Your task is to evaluate whether the following text complies with the forum's rules. Follow these steps:
    1. Classify the text as either "compliant" or "non-compliant".
    2. Explain your reasoning step by step, referencing specific rules if applicable.
    3. Refer to these rules:
    {rules}

    Text: {text}

    Your response must follow this format exactly:
    Classification: <compliant or non-compliant>
    Explanation: <your explanation here>

    Example:
    Classification: non-compliant
    Explanation: The text was classified as non-compliant because it contains personal information, which violates Rule 2 of the forum's guidelines. The mention of identifiable details about another user is a clear breach of privacy guidelines.
    """

# Step 3: Parse the output
def parse_output(output):
    # Split the output into classification and explanation
    lines = output.split("\n")
    classification = None
    explanation = []

    for line in lines:
        if "classification:" in line.lower():
            classification = line.split(":")[1].strip().lower()
        elif "explanation:" in line.lower():
            explanation.append(line.split(":")[1].strip())
        elif explanation:  # Continue appending explanation lines
            explanation.append(line.strip())
        elif classification is None:  # Handle single-word output
            classification = line.strip().lower()

    explanation = " ".join(explanation).strip()

    return {
        "classification": classification,
        "explanation": explanation,
    }

# Step 4: Generate classification and explanation using Ollama
def evaluate_text(text, rules_path):
    # Create the prompt
    prompt = create_prompt(text, rules_path)

    # Use the Ollama Python package to generate a response
    response = ollama.generate(
        model="llama3.2",  # Use Llama 3.2 model
        prompt=prompt,
    )

    # Decode the output
    output = response["response"].strip()
    print("Raw Output:", output)  # Debugging: Print the raw output
    return parse_output(output)

# Step 5: Test the system
if __name__ == "__main__":
    # Example text to evaluate
    text = "This post contains personal information about another user."

    # Evaluate the text
    result = evaluate_text(text, rules_path)

    # Print the results
    print("Text:", text)
    print("Classification:", result["classification"])
    print("Explanation:", result["explanation"])