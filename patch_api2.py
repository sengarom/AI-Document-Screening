with open('frontend/src/services/api.ts', 'r', encoding='utf-8') as f:
    content = f.read()

old_str = "const datesValid = evaluateChecks(['date_of_birth_logic', 'issue_date_logic', 'expiry_date_logic']);"
new_str = "const datesValid = evaluateChecks(['date_of_birth_logic', 'issue_date_logic', 'expiry_date_logic', 'date_of_birth']);"

if old_str in content:
    content = content.replace(old_str, new_str)
    with open('frontend/src/services/api.ts', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Patched api.ts datesValid')
else:
    print('Could not find datesValid string in api.ts')
