import { useState, useEffect } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "@/components/ui/table";
import { LoadingSpinner } from "@/components/shared/LoadingSpinner";
import { StatusBadge } from "@/components/shared/StatusBadge";
import { serialApi } from "@/services/api";
import { Search } from "lucide-react";

export default function SerialsPage() {
  const [serials, setSerials] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("");

  useEffect(() => { load(); }, [search, status]);

  async function load() {
    setLoading(true);
    try {
      const res = await serialApi.list({ search, status: status || undefined });
      setSerials(res.data.items || []);
    } catch (e) { console.error(e); }
    setLoading(false();
  }

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold text-gray-800">Serial Numbers</h2>
      <Card><CardContent className="p-4 flex gap-3">
        <div className="relative flex-1"><Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={16} /><Input placeholder="Search serial numbers..." value={search} onChange={(e) => setSearch(e.target.value)} className="pl-9" /></div>
        <Select value={status} onChange={(e) => setStatus(e.target.value)} className="w-40">
          <option value="">All Status</option><option value="in_stock">In Stock</option><option value="reserved">Reserved</option><option value="deployed">Deployed</option><option value="in_repair">In Repair</option><option value="scrapped">Scrapped</option><option value="rented">Rented</option>
        </Select>
      </CardContent></Card>
      <Card><CardContent className="p-0">
        {loading ? <LoadingSpinner className="flex justify-center p-8" /> : (
          <Table>
            <TableHeader><TableRow><TableHead>Serial #</TableHead><TableHead>Item</TableHead><TableHead>Location</TableHead><TableHead>Status</TableHead><TableHead>Condition</TableHead></TableRow></TableHeader>
            <TableBody>
              {serials.length === 0 && <TableRow><TableCell colSpan={5} className="text-center py-8 text-gray-500">No serial numbers found</TableCell></TableRow>}
              {serials.map((s) => (
                <TableRow key={s.id}>
                  <TableCell className="font-medium">{s.serial_number}</TableCell>
                  <TableCell>{s.item?.name || s.item_id}</TableCell>
                  <TableCell>{s.location?.name || "-"}</TableCell>
                  <TableCell><StatusBadge status={s.status} /></TableCell>
                  <TableCell><StatusBadge status={s.condition} /></TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </CardContent></Card>
    </div>
  );
}
