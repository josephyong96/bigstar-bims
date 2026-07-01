import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select } from "@/components/ui/select";
import { stockApi, itemApi, locationApi, projectApi } from "@/services/api";
import type { Item, Location, Project } from "@/types";
import { Loader2, ArrowUpCircle } from "lucide-react";

export default function StockOutPage() {
  const [items, setItems] = useState<Item[]>([]);
  const [locations, setLocations] = useState<Location[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [itemId, setItemId] = useState("");
  const [locationId, setLocationId] = useState("");
  const [quantity, setQuantity] = useState("1");
  const [projectId, setProjectId] = useState("");
  const [reason, setReason] = useState("");
  const [notes, setNotes] = useState("");
  const [loading, setLoading] = useState(false);
  const [fetching, setFetching] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    async function load() {
      const [i, l, p] = await Promise.all([itemApi.list({}), locationApi.list(), projectApi.list({ status: "active" })]);
      setItems(i.data.items || []);
      setLocations(l.data || []);
      setProjects(p.data.items || []);
      setFetching(false);
    }
    load();
  }, []);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!itemId || !locationId || !quantity) return;
    setLoading(true);
    try {
      await stockApi.stockOut({
        item_id: itemId,
        from_location_id: locationId,
        quantity: parseInt(quantity),
        project_id: projectId || undefined,
        notes: notes || undefined,
      });
      navigate("/items");
    } catch (e: any) {
      alert(e.response?.data?.detail || "Stock out request failed");
    }
    setLoading(false);
  }

  if (fetching) return <div className="p-8 text-center">Loading...</div>;

  return (
    <div className="mx-auto max-w-2xl space-y-4">
      <div className="flex items-center gap-3">
        <ArrowUpCircle size={28} className="text-orange-500" />
        <h2 className="text-2xl font-bold text-gray-800">Stock Out Request</h2>
      </div>
      <p className="text-sm text-gray-500">Stock out requests require approval from management.</p>
      <Card>
        <CardContent className="p-6">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Label>Item *</Label>
              <Select value={itemId} onChange={(e) => setItemId(e.target.value)} required>
                <option value="">Select item</option>
                {items.map((i) => <option key={i.id} value={i.id}>{i.sku} - {i.name}</option>)}
              </Select>
            </div>
            <div>
              <Label>Source Location *</Label>
              <Select value={locationId} onChange={(e) => setLocationId(e.target.value)} required>
                <option value="">Select location</option>
                {locations.filter((l) => l.is_active).map((l) => <option key={l.id} value={l.id}>{l.code} - {l.name}</option>)}
              </Select>
            </div>
            <div>
              <Label>Quantity *</Label>
              <Input type="number" min="1" value={quantity} onChange={(e) => setQuantity(e.target.value)} required />
            </div>
            <div>
              <Label>Project (optional)</Label>
              <Select value={projectId} onChange={(e) => setProjectId(e.target.value)}>
                <option value="">Select project</option>
                {projects.map((p) => <option key={p.id} value={p.id}>{p.project_code} - {p.project_name}</option>)}
              </Select>
            </div>
            <div>
              <Label>Reason</Label>
              <Input value={reason} onChange={(e) => setReason(e.target.value)} placeholder="Project installation, etc." />
            </div>
            <div>
              <Label>Notes</Label>
              <Input value={notes} onChange={(e) => setNotes(e.target.value)} placeholder="Optional notes" />
            </div>
            <div className="flex gap-3 pt-2">
              <Button type="submit" disabled={loading} className="bg-orange-500 hover:bg-orange-600">
                {loading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
                Submit Request
              </Button>
              <Button type="button" variant="outline" onClick={() => navigate("/items")}>Cancel</Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
