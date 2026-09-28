with open('frontend/src/types/index.ts', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("status: 'CLEAR' | 'REVIEW REQUIRED' | 'HIGH RISK';", "status: 'CLEAR' | 'REQUIRE REVIEW' | 'REJECTED' | 'REVIEW REQUIRED' | 'HIGH RISK';\n  decision_reason?: string;")

with open('frontend/src/types/index.ts', 'w', encoding='utf-8') as f:
    f.write(content)
print("Patched types")
