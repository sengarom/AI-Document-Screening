with open('frontend/src/services/api.ts', 'r', encoding='utf-8') as f:
    content = f.read()

old_str = "documentNumberValid: hasPassedCheck('passport_number_format'),"
new_str = "documentNumberValid: hasPassedCheck('passport_number_format') || hasPassedCheck('aadhaar_number_format') || hasPassedCheck('pan_number_format'),"

if old_str in content:
    content = content.replace(old_str, new_str)
    with open('frontend/src/services/api.ts', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Patched api.ts')
else:
    print('Could not find string in api.ts')
