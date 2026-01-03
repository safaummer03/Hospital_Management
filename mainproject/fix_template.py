import re

file_path = r'C:\Users\HP\OneDrive\Desktop\HMS\Hospital_Management\mainproject\templates\appointment_list.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the template syntax errors
content = content.replace("status_filter=='CONFIRMED'", "status_filter == 'CONFIRMED'")
content = content.replace("status_filter=='PENDING'", "status_filter == 'PENDING'")
content = content.replace("status_filter=='COMPLETED'", "status_filter == 'COMPLETED'")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed appointment_list.html template syntax")
