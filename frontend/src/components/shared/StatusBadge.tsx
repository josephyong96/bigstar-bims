import { badgeVariants } from "../ui/badge";
import { cn } from "../../lib/utils";

type Status =
  | "active"
  | "inactive"
  | "pending"
  | "completed"
  | "cancelled"
  | "draft"
  | "approved"
  | "rejected"
  | "in_progress"
  | "done"
  | "open"
  | "closed"
  | "low"
  | "medium"
  | "high";

const statusColorMap: Record<Status, string> = {
  active: "bg-green-100 text-green-800 hover:bg-green-100",
  inactive: "bg-gray-100 text-gray-800 hover:bg-gray-100",
  pending: "bg-yellow-100 text-yellow-800 hover:bg-yellow-100",
  completed: "bg-blue-100 text-blue-800 hover:bg-blue-100",
  cancelled: "bg-red-100 text-red-800 hover:bg-red-100",
  draft: "bg-gray-100 text-gray-800 hover:bg-gray-100",
  approved: "bg-green-100 text-green-800 hover:bg-green-100",
  rejected: "bg-red-100 text-red-800 hover:bg-red-100",
  in_progress: "bg-purple-100 text-purple-800 hover:bg-purple-100",
  done: "bg-blue-100 text-blue-800 hover:bg-blue-100",
  open: "bg-green-100 text-green-800 hover:bg-green-100",
  closed: "bg-gray-100 text-gray-800 hover:bg-gray-100",
  low: "bg-green-100 text-green-800 hover:bg-green-100",
  medium: "bg-yellow-100 text-yellow-800 hover:bg-yellow-100",
  high: "bg-red-100 text-red-800 hover:bg-red-100",
};

export function StatusBadge({ status }: { status: string }) {
  const colorClass = statusColorMap[status as Status] || statusColorMap.draft;
  return (
    <span className={cn(badgeVariants({ variant: "default" }), colorClass)}>
      {status.replace(/_/g, " ").toUpperCase()}
    </span>
  );
}
