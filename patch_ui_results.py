with open('frontend/src/app/screen/results/page.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

old_block = """              <div className="flex flex-col gap-2">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm font-medium text-muted-foreground uppercase tracking-wider">Screening Decision</span>
                  <Badge variant={isClear ? 'success' : isHighRisk ? 'destructive' : 'warning'} className="text-xs uppercase px-2 py-0.5">
                    {report.status}
                  </Badge>
                </div>
                <h3 className="text-xl font-semibold text-foreground">
                  {isClear ? "Identity verified successfully" : "Further review recommended"}
                </h3>
                <p className="text-sm text-muted-foreground leading-relaxed max-w-lg">
                  This risk assessment is based on multiple deterministic forensic and validation signals. {isClear ? "No significant anomalies were detected during the screening pipeline." : "The pipeline detected anomalies requiring manual verification."}
                </p>
              </div>"""

new_block = """              <div className="flex flex-col gap-2">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm font-medium text-muted-foreground uppercase tracking-wider">Screening Decision</span>
                  <Badge variant={report.status === 'CLEAR' ? 'success' : report.status === 'REJECTED' || report.status === 'HIGH RISK' ? 'destructive' : 'warning'} className="text-xs uppercase px-2 py-0.5">
                    {report.status}
                  </Badge>
                </div>
                <h3 className="text-xl font-semibold text-foreground">
                  {report.status === 'CLEAR' ? 'CLEAR' : report.status === 'REJECTED' ? 'REJECTED' : 'REQUIRE REVIEW'}
                </h3>
                <p className="text-sm text-muted-foreground leading-relaxed max-w-lg">
                  {report.decision_reason || (report.status === 'CLEAR' ? "Identity verification completed successfully. No significant anomalies were detected." : "Manual review required. One or more verification signals could not establish sufficient confidence.")}
                </p>
              </div>"""

content = content.replace(old_block, new_block)

with open('frontend/src/app/screen/results/page.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
print("Patched results UI")
