import { useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { api } from "@/services/api";
import { LoadingSpinner } from "@/components/shared/LoadingSpinner";
import { StatusBadge } from "@/components/shared/StatusBadge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

export default function ItemDetailPage() {
  const { id } = useParams<{ id: string }>();

  const { data: item, isLoading } = useQuery({
    queryKey: ["item", id],
    queryFn: () => api.get(`/items/${id}`),
  });

  const { data: movements } = useQuery({
    queryKey: ["item-movements", id],
    queryFn: () => api.get(`/items/${id}/movements`),
  });

  const { data: batches } = useQuery({
    queryKey: ["item-batches", id],
    queryFn: () => api.get(`/items/${id}/batches`),
  });

  if (isLoading) return <LoadingSpinner />;
  if (!item) return <div>Item not found</div>;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">{item.name}</h1>
          <p className="text-muted-foreground">SKU: {item.sku}</p>
        </div>
        <StatusBadge
          status={
            item.current_qty <= item.min_stock_level ? "low_stock" : "active"
          }
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Current Stock</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{item.current_qty}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Min Level</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{item.min_stock_level}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Unit Price</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">${item.unit_price}</div>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="movements">
        <TabsList>
          <TabsTrigger value="movements">Movements</TabsTrigger>
          <TabsTrigger value="batches">Batches</TabsTrigger>
        </TabsList>

        <TabsContent value="movements">
          <Card>
            <CardHeader>
              <CardTitle>Stock Movements</CardTitle>
            </CardHeader>
            <CardContent>
              {movements && movements.length > 0 ? (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Date</TableHead>
                      <TableHead>Type</TableHead>
                      <TableHead>Qty</TableHead>
                      <TableHead>Reference</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {movements.map((m: any) => (
                      <TableRow key={m.id}>
                        <TableCell>
                          {new Date(m.created_at).toLocaleDateString()}
                        </TableCell>
                        <TableCell>
                          <StatusBadge status={m.movement_type} />
                        </TableCell>
                        <TableCell>{m.quantity}</TableCell>
                        <TableCell>{m.reference_no || "-"}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              ) : (
                <p className="text-muted-foreground">No movements recorded</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="batches">
          <Card>
            <CardHeader>
              <CardTitle>Batches</CardTitle>
            </CardHeader>
            <CardContent>
              {batches && batches.length > 0 ? (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Batch No</TableHead>
                      <TableHead>Qty</TableHead>
                      <TableHead>Location</TableHead>
                      <TableHead>Date</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {batches.map((b: any) => (
                      <TableRow key={b.id}>
                        <TableCell>{b.batch_number}</TableCell>
                        <TableCell>{b.quantity}</TableCell>
                        <TableCell>{b.location_name || "-"}</TableCell>
                        <TableCell>
                          {new Date(b.created_at).toLocaleDateString()}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              ) : (
                <p className="text-muted-foreground">No batches</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
