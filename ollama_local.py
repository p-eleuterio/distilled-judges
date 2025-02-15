import ollama
from dotenv import load_dotenv
import os
from datetime import datetime

# Step 1: Load environment variables from .env file
load_dotenv()

# Path to the rules file
rules_path = "rules.txt"

# Path to the output folder
output_folder = "output"  # Folder where responses will be saved

# Ensure the output folder exists
os.makedirs(output_folder, exist_ok=True)

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

# Step 5: Function to ask for user input
def get_user_input():
    print("Enter the text you want to evaluate (press Enter when done):")
    user_input = input()  # Read input from the console
    return user_input

# Step 6: Function to save the response to a file
def save_response(text, result, output_folder):
    # Generate a unique filename using the current timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"response_{timestamp}.txt"
    filepath = os.path.join(output_folder, filename)

    # Write the response to the file
    with open(filepath, "w", encoding="utf-8") as file:
        file.write(f"Text: {text}\n")
        file.write(f"Classification: {result['classification']}\n")
        file.write(f"Explanation: {result['explanation']}\n")

    print(f"Response saved to: {filepath}")

# Step 7: Test the system
if __name__ == "__main__":
    # Ask the user for input
    text = get_user_input()

    # Evaluate the text
    result = evaluate_text(text, rules_path)

    # Print the results
    print("\nResults:")
    print("Text:", text)
    print("Classification:", result["classification"])
    print("Explanation:", result["explanation"])

    # Save the response to a file
    save_response(text, result, output_folder)