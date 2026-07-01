import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select } from "@/components/ui/select";
import { stockApi, itemApi, locationApi } from "@/services/api";
import type { Item, Location } from "@/types";
import { Loader2, ArrowDownCircle } from "lucide-react";

export default function StockInPage() {
  const [items, setItems] = useState<Item[]>([]);
  const [locations, setLocations] = useState<Location[]>([]);
  const [itemId, setItemId] = useState("");
  const [locationId, setLocationId] = useState("");
  const [quantity, setQuantity] = useState("1");
  const [serialNumbers, setSerialNumbers] = useState("");
  const [batchNumber, setBatchNumber] = useState("");
  const [poRef, setPoRef] = useState("");
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

  const selectedItem = items.find((i) => i.id === itemId);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!itemId || !locationId || !quantity) return;
    setLoading(true);
    try {
      const payload: any = {
        item_id: itemId,
        to_location_id: locationId,
        quantity: parseInt(quantity),
        reference_number: poRef || undefined,
        notes: notes || undefined,
      };
      if (serialNumbers.trim()) {
        payload.serial_numbers = serialNumbers.split("\n").map((s) => s.trim()).filter(Boolean);
      }
      if (batchNumber.trim()) {
        payload.batch_number = batchNumber.trim();
      }
      await stockApi.stockIn(payload);
      navigate("/items");
    } catch (e: any) {
      alert(e.response?.data?.detail || "Stock in failed");
    }
    setLoading(false);
  }

  if (fetching) return <div className="p-8 text-center">Loading...</div>;

  return (
    <div className="mx-auto max-w-2xl space-y-4">
      <div className="flex items-center gap-3">
        <ArrowDownCircle size={28} className="text-green-600" />
        <h2 className="text-2xl font-bold text-gray-800">Stock In (Goods Receive)</h2>
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
            <div>
              <Label>Destination Location *</Label>
              <Select value={locationId} onChange={(e) => setLocationId(e.target.value)} required>
                <option value="">Select location</option>
                {locations.filter((l) => l.is_active).map((l) => <option key={l.id} value={l.id}>{l.code} - {l.name}</option>)}
              </Select>
            </div>
            <div>
              <Label>Quantity *</Label>
              <Input type="number" min="1" value={quantity} onChange={(e) => setQuantity(e.target.value)} required />
            </div>
            {selectedItem?.tracking_type === "serial" || selectedItem?.tracking_type === "both" ? (
              <div>
                <Label>Serial Numbers (one per line)</Label>
                <textarea
                  className="flex min-h-[100px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                  value={serialNumbers}
                  onChange={(e) => setSerialNumbers(e.target.value)}
                  placeholder="SN001&#10;SN002&#10;SN003"
                />
                <p className="text-xs text-gray-500 mt-1">{serialNumbers.split("\n").filter(Boolean).length} serial(s) entered</p>
              </div>
            ) : null}
            {selectedItem?.tracking_type === "batch" || selectedItem?.tracking_type === "both" ? (
              <div>
                <Label>Batch Number</Label>
                <Input value={batchNumber} onChange={(e) => setBatchNumber(e.target.value)} placeholder="BATCH-2024-001" />
              </div>
            ) : null}
            <div>
              <Label>PO Reference</Label>
              <Input value={poRef} onChange={(e) => setPoRef(e.target.value)} placeholder="PO-2024-001" />
            </div>
            <div>
              <Label>Notes</Label>
              <Input value={notes} onChange={(e) => setNotes(e.target.value)} placeholder="Optional notes" />
            </div>
            <div className="flex gap-3 pt-2">
              <Button type="submit" disabled={loading} className="bg-green-600 hover:bg-green-700">
                {loading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
                Receive Stock
              </Button>
              <Button type="button" variant="outline" onClick={() => navigate("/items")}>Cancel</Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
