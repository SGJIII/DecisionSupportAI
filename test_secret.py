import os

# Get the FLASK_SECRET_KEY environment variable
flask_secret_key = os.environ.get('FLASK_SECRET_KEY')

# Print each character's unicode value to identify problematic characters
if flask_secret_key:
    for i, char in enumerate(flask_secret_key):
        try:
            print(f"Character {i}: '{char}' (Unicode: {ord(char)})")
        except UnicodeEncodeError as e:
            print(f"Character {i}: 'UnicodeEncodeError' ({e})")

# Use a safe way to print the FLASK_SECRET_KEY value
print("FLASK_SECRET_KEY (safe):", repr(flask_secret_key))
