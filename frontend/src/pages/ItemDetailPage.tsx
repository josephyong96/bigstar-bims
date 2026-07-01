import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { StatusBadge } from "@/components/shared/StatusBadge";
import { LoadingSpinner } from "@/components/shared/LoadingSpinner";
import { itemApi } from "@/services/api";
import { formatDate, formatCurrency } from "@/lib/utils";
import type { Item } from "@/types";
import { ArrowLeft, Package, Barcode } from "lucide-react";

export default function ItemDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [item, setItem] = useState<Item | null>(null);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState("overview");

  useEffect(() => {
    if (id) loadItem();
  }, [id]);

  async function loadItem() {
    try {
      const res = await itemApi.get(id!);
      setItem(res.data);
    } catch (e) { console.error(e); }
    setLoading(false);
  }

  if (loading) return <LoadingSpinner className="flex justify-center p-8" />;
  if (!item) return <div className="p-8 text-center text-gray-500">Item not found</div>;

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-4">
        <Button variant="outline" size="sm" onClick={() => navigate("/items")}><ArrowLeft size={16} /></Button>
        <div>
          <h2 className="text-2xl font-bold text-gray-800">{item.name}</h2>
          <p className="text-sm text-gray-500">{item.sku} {item.barcode && `| Barcode: ${item.barcode}`}</p>
        </div>
      </div>

      <Tabs value={tab} onValueChange={setTab}>
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="stock">Stock</TabsTrigger>
          <TabsTrigger value="specs">Specifications</TabsTrigger>
        </TabsList>

        <TabsContent value="overview">
          <Card>
            <CardContent className="p-6">
              <div className="grid gap-4 md:grid-cols-2">
                <div><Label label="SKU" value={item.sku} /></div>
                <div><Label label="Barcode" value={item.barcode || "-"} /></div>
                <div><Label label="Name" value={item.name} /></div>
                <div><Label label="Type" value={<span className="capitalize">{item.inventory_type.replace(/_/g, " ")}</span>} /></div>
                <div><Label label="Brand" value={item.brand || "-"} /></div>
                <div><Label label="Model" value={item.model || "-"} /></div>
                <div><Label label="Tracking" value={<span className="capitalize">{item.tracking_type.replace(/_/g, " ")}</span>} /></div>
                <div><Label label="UOM" value={item.unit_of_measure} /></div>
                <div><Label label="Unit Cost" value={formatCurrency(item.unit_cost)} /></div>
                <div><Label label="Selling Price" value={item.selling_price ? formatCurrency(item.selling_price) : "-"} /></div>
                <div><Label label="Reorder Level" value={item.reorder_level.toString()} /></div>
                <div><Label label="Status" value={<StatusBadge status={item.is_active ? "active" : "inactive"} />} /></div>
                <div className="md:col-span-2"><Label label="Description" value={item.description || "-"} /></div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="stock">
          <Card>
            <CardContent className="p-6">
              {item.stock_summary && item.stock_summary.length > 0 ? (
                <div className="space-y-3">
                  {item.stock_summary.map((s: any) => (
                    <div key={s.id} className="flex items-center justify-between rounded-lg border p-4">
                      <div className="flex items-center gap-3">
                        <Package size={20} className="text-blue-600" />
                        <div>
                          <p className="font-medium">{s.location?.name || s.location_id}</p>
                          <p className="text-sm text-gray-500">Available: {s.available_qty} | Reserved: {s.reserved_qty}</p>
                        </div>
                      </div>
                      <p className="text-lg font-bold">{s.quantity}</p>
                    </div>
                  ))}
                </div>
              ) : <p className="text-gray-500">No stock recorded</p>}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="specs">
          <Card>
            <CardContent className="p-6">
              {item.specifications ? (
                <div className="grid gap-3 md:grid-cols-2">
                  {Object.entries(item.specifications).map(([key, val]) => (
                    <div key={key} className="rounded-lg border p-3">
                      <p className="text-xs text-gray-500 uppercase">{key.replace(/_/g, " ")}</p>
                      <p className="font-medium">{Array.isArray(val) ? val.join(", ") : String(val)}</p>
                    </div>
                  ))}
                </div>
              ) : <p className="text-gray-500">No specifications recorded</p>}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}

function Label({ label, value }: { label: string; value: React.ReactNode }) {
  return <div><p className="text-xs text-gray-500">{label}</p><p className="font-medium">{value}</p></div>;
}
