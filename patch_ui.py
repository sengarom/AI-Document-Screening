import re

with open('frontend/src/app/screen/results/page.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace generateFlags logic
old_flag = "!report.documentType.includes('PAN') && !report.documentType.includes('Aadhaar')"
new_flag = "report.documentType.toUpperCase() !== 'PAN' && report.documentType.toUpperCase() !== 'AADHAAR'"
content = content.replace(old_flag, new_flag)

new_content = """<CardContent className="p-4 space-y-4">
                {report.documentType.toUpperCase() === 'AADHAAR' && (
                  <>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">Required identity fields</span>
                      {report.validation.checks.requiredFieldsDetected ? <Check className="w-4 h-4 text-success"/> : <X className="w-4 h-4 text-destructive"/>}
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">Aadhaar number format</span>
                      {report.validation.checks.documentNumberValid ? <Check className="w-4 h-4 text-success"/> : <X className="w-4 h-4 text-destructive"/>}
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">Date/field consistency</span>
                      {report.validation.checks.datesValid === 'NOT_ASSESSED' ? <Minus className="w-4 h-4 text-muted-foreground" /> : report.validation.checks.datesValid ? <Check className="w-4 h-4 text-success"/> : <X className="w-4 h-4 text-destructive"/>}
                    </div>
                  </>
                )}
                {report.documentType.toUpperCase() === 'PAN' && (
                  <>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">Required identity fields</span>
                      {report.validation.checks.requiredFieldsDetected ? <Check className="w-4 h-4 text-success"/> : <X className="w-4 h-4 text-destructive"/>}
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">PAN format</span>
                      {report.validation.checks.documentNumberValid ? <Check className="w-4 h-4 text-success"/> : <X className="w-4 h-4 text-destructive"/>}
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">Date/field consistency</span>
                      {report.validation.checks.datesValid === 'NOT_ASSESSED' ? <Minus className="w-4 h-4 text-muted-foreground" /> : report.validation.checks.datesValid ? <Check className="w-4 h-4 text-success"/> : <X className="w-4 h-4 text-destructive"/>}
                    </div>
                  </>
                )}
                {report.documentType.toUpperCase() !== 'AADHAAR' && report.documentType.toUpperCase() !== 'PAN' && (
                  <>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">Logically valid dates</span>
                      {report.validation.checks.datesValid === 'NOT_ASSESSED' ? <Minus className="w-4 h-4 text-muted-foreground" /> : report.validation.checks.datesValid ? <Check className="w-4 h-4 text-success"/> : <X className="w-4 h-4 text-destructive"/>}
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">MRZ checksums</span>
                      {report.mrz.checksumPassed ? <Check className="w-4 h-4 text-success"/> : <X className="w-4 h-4 text-destructive"/>}
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">Visual & MRZ consistency</span>
                      {report.validation.checks.visualMrzConsistency === 'NOT_ASSESSED' ? <Minus className="w-4 h-4 text-muted-foreground" /> : report.validation.checks.visualMrzConsistency ? <Check className="w-4 h-4 text-success"/> : <X className="w-4 h-4 text-destructive"/>}
                    </div>
                  </>
                )}
              </CardContent>"""

parts = content.split('<CardContent className="p-4 space-y-4">')
for i, p in enumerate(parts):
    if 'Logically valid dates' in p:
        end_idx = p.find('</CardContent>')
        if end_idx != -1:
            parts[i] = new_content.replace('<CardContent className="p-4 space-y-4">\n', '') + p[end_idx + len('</CardContent>'):]
        break
        
content = '<CardContent className="p-4 space-y-4">'.join(parts)
with open('frontend/src/app/screen/results/page.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
print('Patched successfully via split')
