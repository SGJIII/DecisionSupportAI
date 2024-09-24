import base64

secret_key = "KzDSPin_FGL7KUThpiFOi9IZdF0FvOzrvy3I3Hfo7Ao="
try:
    # Decode the base64 key to ensure it's valid
    decoded_key = base64.urlsafe_b64decode(secret_key + '==')  # Adding '==' to ensure proper padding
    print("Decoded Key:", decoded_key)
except Exception as e:
    print("Failed to decode key:", e)