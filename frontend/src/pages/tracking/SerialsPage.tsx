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
import { StatusBadge } from "@/components/shared/StatusBadge";
import { Search } from "lucide-react";

export default function SerialsPage() {
  const [search, setSearch] = useState("");
  const { data: serials, isLoading } = useQuery({
    queryKey: ["serials"],
    queryFn: () => api.get("/serials"),
  });

  const filtered = serials?.filter((s: any) =>
    s.serial_number?.toLowerCase().includes(search.toLowerCase())
  );

  if (isLoading) return <LoadingSpinner />;

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Serial Number Tracking</h1>

      <div className="flex items-center gap-2">
        <Search className="h-4 w-4 text-muted-foreground" />
        <Input
          placeholder="Search serial numbers..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="max-w-sm"
        />
      </div>

      <div className="border rounded-lg">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Serial Number</TableHead>
              <TableHead>Item</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Location</TableHead>
              <TableHead>Warranty Expiry</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filtered?.map((serial: any) => (
              <TableRow key={serial.id}>
                <TableCell className="font-medium">{serial.serial_number}</TableCell>
                <TableCell>{serial.item_name || "-"}</TableCell>
                <TableCell>
                  <StatusBadge status={serial.status} />
                </TableCell>
                <TableCell>{serial.location_name || "-"}</TableCell>
                <TableCell>
                  {serial.warranty_expiry
                    ? new Date(serial.warranty_expiry).toLocaleDateString()
                    : "-"}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
