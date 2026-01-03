
import os

file_path = r'c:\Users\HP\OneDrive\Desktop\HMS\Hospital_Management\mainproject\templates\appointment_list.html'

print(f"Inspecting: {file_path}")

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    found_error = False
    for i, line in enumerate(lines):
        if "status_filter=='CONFIRMED'" in line or "status_filter=='PENDING'" in line or "status_filter=='COMPLETED'" in line:
            print(f"Line {i+1} HAS ERROR: {repr(line)}")
            found_error = True
            
            # Fix it in memory
            lines[i] = line.replace("status_filter=='CONFIRMED'", "status_filter == 'CONFIRMED'")
            lines[i] = lines[i].replace("status_filter=='PENDING'", "status_filter == 'PENDING'")
            lines[i] = lines[i].replace("status_filter=='COMPLETED'", "status_filter == 'COMPLETED'")
            print(f"Fixed line {i+1}: {repr(lines[i])}")

    if not found_error:
        print("No syntax error pattern found in file!")
        # Search specifically for the block to see what IS there
        for i, line in enumerate(lines):
            if "CONFIRMED" in line and "option" in line:
                print(f"Line {i+1} content: {repr(line)}")

    # Write back only if we found something or just to be safe
    print("Overwriting file with fixed content...")
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print("File written successfully.")

    # Verification
    with open(file_path, 'r', encoding='utf-8') as f:
        new_content = f.read()
        if "status_filter == 'CONFIRMED'" in new_content:
            print("VERIFICATION SUCCESS: Found correct syntax in file.")
        else:
            print("VERIFICATION FAILED: Correct syntax NOT found.")

except Exception as e:
    print(f"Error: {e}")
