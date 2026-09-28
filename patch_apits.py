with open('frontend/src/services/api.ts', 'r', encoding='utf-8') as f:
    content = f.read()

old_status = """    let uiStatus: 'CLEAR' | 'REVIEW REQUIRED' | 'HIGH RISK' = 'REVIEW REQUIRED';
    if (backendReport.overall_status === 'clear') uiStatus = 'CLEAR';
    if (backendReport.overall_status === 'high_risk') uiStatus = 'HIGH RISK';"""

new_status = """    let uiStatus: 'CLEAR' | 'REQUIRE REVIEW' | 'REJECTED' | 'REVIEW REQUIRED' | 'HIGH RISK' = 'REQUIRE REVIEW';
    
    // Support new backend deterministic decision
    if (backendReport.decision) {
        if (backendReport.decision === 'clear') uiStatus = 'CLEAR';
        else if (backendReport.decision === 'require_review') uiStatus = 'REQUIRE REVIEW';
        else if (backendReport.decision === 'rejected') uiStatus = 'REJECTED';
    } else {
        if (backendReport.overall_status === 'clear') uiStatus = 'CLEAR';
        if (backendReport.overall_status === 'high_risk') uiStatus = 'HIGH RISK';
    }
    
    const decision_reason = backendReport.decision_reason || '';
"""

content = content.replace(old_status, new_status)

old_return = """      status: uiStatus,
      ocr: {"""

new_return = """      status: uiStatus,
      decision_reason: decision_reason,
      ocr: {"""

content = content.replace(old_return, new_return)

with open('frontend/src/services/api.ts', 'w', encoding='utf-8') as f:
    f.write(content)
print("Patched api.ts")
