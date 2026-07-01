import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select } from "@/components/ui/select";
import { stockApi, itemApi, locationApi } from "@/services/api";
import type { Item, Location } from "@/types";
import { Loader2, ArrowLeftRight } from "lucide-react";

export default function TransferPage() {
  const [items, setItems] = useState<Item[]>([]);
  const [locations, setLocations] = useState<Location[]>([]);
  const [itemId, setItemId] = useState("");
  const [fromLocation, setFromLocation] = useState("");
  const [toLocation, setToLocation] = useState("");
  const [quantity, setQuantity] = useState("1");
  const [notes, setNotes] = useState("");
  const [loading, setLoading] = useState(false);
  const [fetching, setFetching] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    async function load() {
      const [i, l] = await Promise.all([itemApi.list({}), locationApi.list()]);
      setItems(i.data.items || []);
      setLocations(l.data || []);
      setFetching(false);
    }
    load();
  }, []);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!itemId || !fromLocation || !toLocation || !quantity) return;
    if (fromLocation === toLocation) { alert("Source and destination must be different"); return; }
    setLoading(true);
    try {
      await stockApi.transfer({
        item_id: itemId,
        from_location_id: fromLocation,
        to_location_id: toLocation,
        quantity: parseInt(quantity),
        notes: notes || undefined,
      });
      navigate("/items");
    } catch (e: any) {
      alert(e.response?.data?.detail || "Transfer failed");
    }
    setLoading(false);
  }

  if (fetching) return <div className="p-8 text-center">Loading...</div>;

  return (
    <div className="mx-auto max-w-2xl space-y-4">
      <div className="flex items-center gap-3">
        <ArrowLeftRight size={28} className="text-purple-600" />
        <h2 className="text-2xl font-bold text-gray-800">Stock Transfer</h2>
      </div>
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
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>From Location *</Label>
                <Select value={fromLocation} onChange={(e) => setFromLocation(e.target.value)} required>
                  <option value="">Select</option>
                  {locations.filter((l) => l.is_active).map((l) => <option key={l.id} value={l.id}>{l.code}</option>)}
                </Select>
              </div>
              <div>
                <Label>To Location *</Label>
                <Select value={toLocation} onChange={(e) => setToLocation(e.target.value)} required>
                  <option value="">Select</option>
                  {locations.filter((l) => l.is_active).map((l) => <option key={l.id} value={l.id}>{l.code}</option>)}
                </Select>
              </div>
            </div>
            <div>
              <Label>Quantity *</Label>
              <Input type="number" min="1" value={quantity} onChange={(e) => setQuantity(e.target.value)} required />
            </div>
            <div>
              <Label>Notes</Label>
              <Input value={notes} onChange={(e) => setNotes(e.target.value)} placeholder="Optional" />
            </div>
            <div className="flex gap-3 pt-2">
              <Button type="submit" disabled={loading} className="bg-purple-600 hover:bg-purple-700">
                {loading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
                Transfer
              </Button>
              <Button type="button" variant="outline" onClick={() => navigate("/items")}>Cancel</Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
