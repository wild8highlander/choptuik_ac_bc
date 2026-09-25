import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

const badgeVariants = cva(
  "inline-flex items-center rounded-md border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-1 focus:ring-teal-500",
  {
    variants: {
      variant: {
        default: "border-transparent bg-teal-600 text-white shadow",
        secondary: "border-transparent bg-navy-700 text-gray-300",
        destructive: "border-transparent bg-red-600 text-white shadow",
        outline: "border-navy-600 text-gray-300",
        success: "border-transparent bg-emerald-600 text-white shadow",
        warning: "border-transparent bg-amber-600 text-white shadow",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
)

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant }), className)} {...props} />
  )
}

export { Badge, badgeVariants }
