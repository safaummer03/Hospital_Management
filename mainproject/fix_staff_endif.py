import re

# Fix staff_profile.html - add missing {% endif %}
staff_file = r'C:\Users\HP\OneDrive\Desktop\HMS\Hospital_Management\mainproject\templates\staff_profile.html'

with open(staff_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the problematic line around 354-356
for i, line in enumerate(lines[350:360], start=351):
    print(f"Line {i}: {line.rstrip()}")

# Fix: The department select option is missing proper closing
# Looking for pattern like: {% if staff_profile.department.id == dept.id %}selected{% endif
# Should be: {% if staff_profile.department.id == dept.id %}selected{% endif %}

content = ''.join(lines)

# Fix the broken if statement
content = re.sub(
    r'(\{%\s*if\s+staff_profile\.department\.id\s*==\s*dept\.id\s*%\})selected(\{%\s*endif)\s*%\}>',
    r'\1selected\2 %}>',
    content
)

# Also ensure proper spacing
content = re.sub(
    r'staff_profile\.department\.id==dept\.id',
    r'staff_profile.department.id == dept.id',
    content
)

with open(staff_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("\nFixed staff_profile.html template")
