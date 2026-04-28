import type { ReactNode } from "react"

import { cn } from "@/lib/utils"

interface DashboardPageHeaderProps {
  title: string
  actions?: ReactNode
  className?: string
  titleClassName?: string
}

export function DashboardPageHeader({
  title,
  actions,
  className,
  titleClassName,
}: DashboardPageHeaderProps) {
  return (
    <div className={cn("flex items-center justify-between gap-4", className)}>
      <p className={cn("text-sm text-muted-foreground", titleClassName)}>{title}</p>
      {actions ? <div className="flex items-center gap-2">{actions}</div> : null}
    </div>
  )
}

export default DashboardPageHeader
