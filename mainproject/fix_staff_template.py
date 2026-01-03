import re

# Fix staff_profile.html
staff_file = r'C:\Users\HP\OneDrive\Desktop\HMS\Hospital_Management\mainproject\templates\staff_profile.html'

with open(staff_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the template syntax errors - add spaces around ==
content = re.sub(r'(\w+)\.id==(\w+)\.id', r'\1.id == \2.id', content)

with open(staff_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed staff_profile.html template syntax")
