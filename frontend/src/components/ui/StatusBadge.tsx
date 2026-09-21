import { Badge } from "@/components/ui/Badge"
import { CheckCircle2, AlertTriangle, XCircle } from "lucide-react"

type StatusType = "VERIFIED" | "REVIEW REQUIRED" | "HIGH RISK" | string

interface StatusBadgeProps {
  status: StatusType
}

export function StatusBadge({ status }: StatusBadgeProps) {
  let variant: "success" | "warning" | "destructive" | "default" = "default"
  let Icon = null

  if (status === "VERIFIED") {
    variant = "success"
    Icon = CheckCircle2
  } else if (status === "REVIEW REQUIRED") {
    variant = "warning"
    Icon = AlertTriangle
  } else if (status === "HIGH RISK") {
    variant = "destructive"
    Icon = XCircle
  }

  return (
    <Badge variant={variant} className="gap-1.5 py-1 px-3">
      {Icon && <Icon className="w-3.5 h-3.5" />}
      {status}
    </Badge>
  )
}
