import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
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
import { LoadingSpinner } from "@/components/shared/LoadingSpinner";
import { Search } from "lucide-react";

export default function BatchesPage() {
  const [search, setSearch] = useState("");
  const { data: batches, isLoading } = useQuery({
    queryKey: ["batches"],
    queryFn: () => api.get("/batch-numbers"),
  });

  const filtered = batches?.filter((b: any) =>
    b.batch_number?.toLowerCase().includes(search.toLowerCase())
  );

  if (isLoading) return <LoadingSpinner />;

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Batch Tracking</h1>

      <div className="flex items-center gap-2">
        <Search className="h-4 w-4 text-muted-foreground" />
        <Input
          placeholder="Search batches..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="max-w-sm"
        />
      </div>

      <div className="border rounded-lg">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Batch No</TableHead>
              <TableHead>Item</TableHead>
              <TableHead>Qty</TableHead>
              <TableHead>Location</TableHead>
              <TableHead>Date</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filtered?.map((batch: any) => (
              <TableRow key={batch.id}>
                <TableCell className="font-medium">{batch.batch_number}</TableCell>
                <TableCell>{batch.item_name || "-"}</TableCell>
                <TableCell>{batch.quantity}</TableCell>
                <TableCell>{batch.location_name || "-"}</TableCell>
                <TableCell>
                  {new Date(batch.created_at).toLocaleDateString()}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
