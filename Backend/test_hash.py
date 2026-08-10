import bcrypt

salt = b'$2b$12$0h3/KkE30sHn9g7Gf7oI.O'  # Just generating a fixed length hash
print("New Hash:", bcrypt.hashpw(b'password123', bcrypt.gensalt()).decode())
