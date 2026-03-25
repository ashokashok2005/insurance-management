import os

file_path = r'c:\Users\ELCOT\Insurance\app\routes\auth.py'
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if "new_agent = Agent(email=email, name=name, role='agent')" in line:
        new_lines.append(line.replace("Agent(email=email, name=name, role='agent')", "Agent(email=email, name=name, role='agent', agency_id=1)"))
    elif "return jsonify({'message': 'Agent registered successfully'}), 201" in line:
        new_lines.append(line.replace("'message': 'Agent registered successfully'}", "'message': 'Agent registered successfully', 'agency_id': 1}"))
    else:
        new_lines.append(line)

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
print("auth.py updated successfully.")
