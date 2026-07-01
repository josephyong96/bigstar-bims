import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "@/components/ui/table";
import { LoadingSpinner } from "@/components/shared/LoadingSpinner";
import { StatusBadge } from "@/components/shared/StatusBadge";
import { poApi } from "@/services/api";
import { formatDate, formatCurrency } from "@/lib/utils";
import { Plus, Search, Eye } from "lucide-react";

export default function PurchaseOrdersPage() {
  const [orders, setOrders] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("");
  const navigate = useNavigate();

  useEffect(() => { load(); }, [search, status]);

  async function load() {
    setLoading(true);
    try {
      const res = await poApi.list({ search, status: status || undefined });
      setOrders(res.data.items || []);
    } catch (e) { console.error(e); }
    setLoading(false);
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-800">Purchase Orders</h2>
        <Button onClick={() => navigate("/purchase-orders/new")}><Plus size={16} className="mr-2"/> New PO</Button>
      </div>
      <Card><CardContent className="p-4 flex gap-3">
        <div className="relative flex-1"><Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={16} /><Input placeholder="Search POs..." value={search} onChange={(e) => setSearch(e.target.value)} className="pl-9" /></div>
        <Select value={status} onChange={(e) => setStatus(e.target.value)} className="w-40">
          <option value="">All Status</option><option value="draft">Draft</option><option value="sent">Sent</option><option value="partial">Partial</option><option value="received">Received</option><option value="cancelled">Cancelled</option>
        </Select>
      </CardContent></Card>
      <Card><CardContent className="p-0">
        {loading ? <LoadingSpinner className="flex justify-center p-8" /> : (
          <Table>
            <TableHeader><TableRow><TableHead>PO Number</TableHead><TableHead>Supplier</TableHead><TableHead>Order Date</TableHead><TableHead>Amount</TableHead><TableHead>Status</TableHead><TableHead className="text-right">Actions</TableHead></TableRow></TableHeader>
            <TableBody>
              {orders.length === 0 && <TableRow><TableCell colSpan={6} className="text-center py-8 text-gray-500">No purchase orders found</TableCell></TableRow>}
              {orders.map((o) => (
                <TableRow key={o.id}>
                  <TableCell className="font-medium">{o.po_number}</TableCell>
                  <TableCell>{o.supplier_name}</TableCell>
                  <TableCell>{formatDate(o.order_date)}</TableCell>
                  <TableCell>{formatCurrency(o.total_amount)}</TableCell>
                  <TableCell><StatusBadge status={o.status} /></TableCell>
                  <TableCell className="text-right"><Button size="sm" variant="ghost" onClick={() => navigate(`/purchase-orders/${o.id}`)}><Eye size={14} /></Button></TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </CardContent></Card>
    </div>
  );
}
