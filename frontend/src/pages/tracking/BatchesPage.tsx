import { useState, useEffect } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "@/components/ui/table";
import { LoadingSpinner } from "@/components/shared/LoadingSpinner";
import { StatusBadge } from "@/components/shared/StatusBadge";
import { batchApi } from "@/services/api";
import { Search } from "lucide-react";

export default function BatchesPage() {
  const [batches, setBatches] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");

  useEffect(() => { load(); }, [search]);

  async function load() {
    setLoading(true);
    try {
      const res = await batchApi.list({ search });
      setBatches(res.data.items || []);
    } catch (e) { console.error(e); }
    setLoading(false);
  }

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold text-gray-800">Batch Numbers</h2>
      <Card><CardContent className="p-4">
        <div className="relative"><Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={16} /><Input placeholder="Search batch numbers..." value={search} onChange={(e) => setSearch(e.target.value)} className="pl-9" /></div>
      </CardContent></Card>
      <Card><CardContent className="p-0">
        {loading ? <LoadingSpinner className="flex justify-center p-8" /> : (
          <Table>
            <TableHeader><TableRow><TableHead>Batch #</TableHead><TableHead>Item</TableHead><TableHead>Location</TableHead><TableHead>Qty</TableHead><TableHead>Status</TableHead></TableRow></TableHeader>
            <TableBody>
              {batches.length === 0 && <TableRow><TableCell colSpan={5} className="text-center py-8 text-gray-500">No batches found</TableCell></TableRow>}
              {batches.map((b) => (
                <TableRow key={b.id}>
                  <TableCell className="font-medium">{b.batch_number}</TableCell>
                  <TableCell>{b.item?.name || b.item_id}</TableCell>
                  <TableCell>{b.location?.name || "-"}</TableCell>
                  <TableCell>{b.quantity}</TableCell>
                  <TableCell><StatusBadge status={b.status} /></TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </CardContent></Card>
    </div>
  );
}
