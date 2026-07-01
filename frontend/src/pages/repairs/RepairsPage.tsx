import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { api } from "@/services/api";
import { StatusBadge } from "@/components/shared/StatusBadge";
import { LoadingSpinner } from "@/components/shared/LoadingSpinner";
import { Plus, Search } from "lucide-react";

export default function RepairsPage() {
  const [search, setSearch] = useState("");
  const { data: repairs, isLoading } = useQuery({
    queryKey: ["repairs"],
    queryFn: () => api.get("/repairs"),
  });

  const filtered = repairs?.filter((r: any) =>
    r.item_name?.toLowerCase().includes(search.toLowerCase()) ||
    r.repair_no?.toLowerCase().includes(search.toLowerCase())
  );

  if (isLoading) return <LoadingSpinner />;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Repairs</h1>
        <Link to="/repairs/new">
          <Button>
            <Plus className="h-4 w-4 mr-2" />
            New Repair
          </Button>
        </Link>
      </div>

      <div className="flex items-center gap-2">
        <Search className="h-4 w-4 text-muted-foreground" />
        <Input
          placeholder="Search repairs..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="max-w-sm"
        />
      </div>

      <div className="border rounded-lg">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Repair No</TableHead>
              <TableHead>Item</TableHead>
              <TableHead>Issue</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filtered?.map((repair: any) => (
              <TableRow key={repair.id}>
                <TableCell className="font-medium">{repair.repair_no}</TableCell>
                <TableCell>{repair.item_name || "-"}</TableCell>
                <TableCell className="max-w-xs truncate">{repair.issue_description}</TableCell>
                <TableCell>
                  <StatusBadge status={repair.status} />
                </TableCell>
                <TableCell>
                  <Link to={`/repairs/${repair.id}`}>
                    <Button variant="ghost" size="sm">View</Button>
                  </Link>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
