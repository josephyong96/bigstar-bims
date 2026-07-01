import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { StatusBadge } from "@/components/shared/StatusBadge";
import { LoadingSpinner } from "@/components/shared/LoadingSpinner";
import { itemApi } from "@/services/api";
import { format } from "date-fns";
import { ArrowLeft, Edit } from "lucide-react";
import type { Item } from "@/types";

export function ItemDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [item, setItem] = useState<Item | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchItem = async () => {
      try {
        const res = await itemApi.getById(Number(id));
        setItem(res.data);
      } catch (err) {
        console.error("Failed to fetch item:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchItem();
  }, [id]);

  if (loading) return <LoadingSpinner />;
  if (!item) return <div className="p-8 text-center">Item not found</div>;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="outline" size="sm" onClick={() => navigate(-1)}>
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back
          </Button>
          <h1 className="text-2xl font-bold">{item.name}</h1>
        </div>
        <Button size="sm" onClick={() => navigate(`/items/${id}/edit`)}>
          <Edit className="w-4 h-4 mr-2" />
          Edit
        </Button>
      </div>

      <Tabs defaultValue="details">
        <TabsList>
          <TabsTrigger value="details">Details</TabsTrigger>
          <TabsTrigger value="stock">Stock History</TabsTrigger>
          <TabsTrigger value="batches">Batches</TabsTrigger>
        </TabsList>

        <TabsContent value="details">
          <Card>
            <CardHeader>
              <CardTitle>Item Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm text-gray-500">Item Code</label>
                  <p className="font-medium">{item.item_code}</p>
                </div>
                <div>
                  <label className="text-sm text-gray-500">Category</label>
                  <p className="font-medium">{item.category?.name || "-"}</p>
                </div>
                <div>
                  <label className="text-sm text-gray-500">Unit</label>
                  <p className="font-medium">{item.unit}</p>
                </div>
                <div>
                  <label className="text-sm text-gray-500">Barcode</label>
                  <p className="font-medium">{item.barcode || "-"}</p>
                </div>
                <div>
                  <label className="text-sm text-gray-500">Status</label>
                  <p><StatusBadge status={item.status} /></p>
                </div>
                <div>
                  <label className="text-sm text-gray-500">Current Stock</label>
                  <p className="font-medium">{item.current_stock}</p>
                </div>
                <div>
                  <label className="text-sm text-gray-500">Min Stock Level</label>
                  <p className="font-medium">{item.min_stock_level}</p>
                </div>
                <div>
                  <label className="text-sm text-gray-500">Created</label>
                  <p className="font-medium">{format(new Date(item.created_at), "PPP")}</p>
                </div>
              </div>
              {item.description && (
                <div>
                  <label className="text-sm text-gray-500">Description</label>
                  <p className="mt-1">{item.description}</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="stock">
          <Card>
            <CardHeader>
              <CardTitle>Stock Movement History</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-500">Stock history coming soon...</p>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="batches">
          <Card>
            <CardHeader>
              <CardTitle>Batch Numbers</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-500">Batch numbers coming soon...</p>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
