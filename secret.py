from cryptography.fernet import Fernet

# Generate secret key
key = Fernet.generate_key()

# Save the key in a secure file or environment variable
with open("secret.key", "wb") as key_file:
    key_file.write(key)

print(f"Generated Key: {key}")
