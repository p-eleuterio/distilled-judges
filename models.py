from transformers import AutoTokenizer, AutoModelForCausalLM
from huggingface_hub import login
from dotenv import load_dotenv
import os
import torch

#Load environment variables from .env file
load_dotenv()

#Authenticate with Hugging Face
huggingface_token = os.getenv("HUGGINGFACE_TOKEN")
if not huggingface_token:
    raise ValueError("HUGGINGFACE_TOKEN not found in .env file. Please add it.")
login(token=huggingface_token)

#Load Falcon-7B model and tokenizer
model_name = "tiiuae/falcon-7b"  # Open-access model
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float16,  # Use FP16 for faster inference
    device_map="auto",          # Automatically load the model on GPU if available
)

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

#Define the prompt template
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

#Parse the output
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

#Generate classification and explanation
def evaluate_text(text, rules_path):
    # Create the prompt
    prompt = create_prompt(text, rules_path)

    # Tokenize the input
    inputs = tokenizer(prompt, return_tensors="pt")

    # Generate the output
    outputs = model.generate(
        **inputs,
        max_length=300,  # Adjust based on your needs
        temperature=0.7,  # Adjust for creativity vs. determinism
        top_k=50,         # Limit to top-k tokens
        top_p=0.9,        # Use nucleus sampling
        do_sample=True,   # Enable sampling
    )

    # Decode the output
    output = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print("Raw Output:", output)  # Debugging: Print the raw output
    return parse_output(output)

#Test the system
if __name__ == "__main__":
    # Example text to evaluate
    text = "This post contains personal information about another user."

    # Evaluate the text
    result = evaluate_text(text, rules_path)

    # Print the results
    print("Text:", text)
    print("Classification:", result["classification"])
    print("Explanation:", result["explanation"])