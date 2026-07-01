import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "@/components/ui/table";
import { LoadingSpinner } from "@/components/shared/LoadingSpinner";
import { StatusBadge } from "@/components/shared/StatusBadge";
import { repairApi } from "@/services/api";
import { formatDateTime } from "@/lib/utils";
import { Plus, Search, Eye } from "lucide-react";

export default function RepairsPage() {
  const [tickets, setTickets] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("");
  const navigate = useNavigate();

  useEffect(() => { load(); }, [search, status]);

  async function load() {
    setLoading(true);
    try {
      const res = await repairApi.list({ search, status: status || undefined });
      setTickets(res.data.items || []);
    } catch (e) { console.error(e); }
    setLoading(false);
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-800">Repair Center</h2>
        <Button onClick={() => navigate("/repairs/new")}><Plus size={16} className="mr-2"/> New Ticket</Button>
      </div>
      <Card><CardContent className="p-4 flex gap-3">
        <div className="relative flex-1"><Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={16} /><Input placeholder="Search tickets..." value={search} onChange={(e) => setSearch(e.target.value)} className="pl-9" /></div>
        <Select value={status} onChange={(e) => setStatus(e.target.value)} className="w-40">
          <option value="">All Status</option><option value="received">Received</option><option value="diagnosing">Diagnosing</option><option value="waiting_parts">Waiting Parts</option><option value="in_repair">In Repair</option><option value="completed">Completed</option><option value="returned">Returned</option>
        </Select>
      </CardContent></Card>
      <Card><CardContent className="p-0">
        {loading ? <LoadingSpinner className="flex justify-center p-8" /> : (
          <Table>
            <TableHeader><TableRow><TableHead>Ticket #</TableHead><TableHead>Item</TableHead><TableHead>Client</TableHead><TableHead>Type</TableHead><TableHead>Status</TableHead><TableHead>Received</TableHead><TableHead className="text-right">Actions</TableHead></TableRow></TableHeader>
            <TableBody>
              {tickets.length === 0 && <TableRow><TableCell colSpan={7} className="text-center py-8 text-gray-500">No repair tickets found</TableCell></TableRow>}
              {tickets.map((t) => (
                <TableRow key={t.id}>
                  <TableCell className="font-medium">{t.ticket_number}</TableCell>
                  <TableCell>{t.item?.name || t.item_id}</TableCell>
                  <TableCell>{t.client_name}</TableCell>
                  <TableCell className="capitalize">{t.repair_type.replace(/_/g, " ")}</TableCell>
                  <TableCell><StatusBadge status={t.status} /></TableCell>
                  <TableCell>{formatDateTime(t.received_at)}</TableCell>
                  <TableCell className="text-right"><Button size="sm" variant="ghost" onClick={() => navigate(`/repairs/${t.id}`)}><Eye size={14} /></Button></TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </CardContent></Card>
    </div>
  );
}
