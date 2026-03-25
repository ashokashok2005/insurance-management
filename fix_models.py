import os

file_path = r'c:\Users\ELCOT\Insurance\app\models.py'
with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

# Fix set_password
old_func = """def set_password(self, password):
    self.password_hash = generate_password_hash(password)"""

new_func = """def set_password(self, password):
    from werkzeug.security import generate_password_hash
    self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')"""

if old_func in text:
    text = text.replace(old_func, new_func)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(text)
    print("models.py updated successfully.")
else:
    # Try with different line endings or slightly different spacing
    print("Target content not found in models.py. Checking variations...")
    # Just replace the line
    if "self.password_hash = generate_password_hash(password)" in text:
        text = text.replace("self.password_hash = generate_password_hash(password)", "from werkzeug.security import generate_password_hash\n        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(text)
        print("models.py updated successfully (variation).")
    else:
        print("Still not found.")
