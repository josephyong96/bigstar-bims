import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/services/api";
import { LoadingSpinner } from "@/components/shared/LoadingSpinner";
import { Plus, Trash2 } from "lucide-react";

interface StockOutLine {
  item_id: string;
  quantity: number;
  location_id?: string;
}

export default function StockOutPage() {
  const queryClient = useQueryClient();
  const [referenceNo, setReferenceNo] = useState("");
  const [reason, setReason] = useState("");
  const [lines, setLines] = useState<StockOutLine[]>([
    { item_id: "", quantity: 1 },
  ]);

  const { data: items, isLoading: itemsLoading } = useQuery({
    queryKey: ["items"],
    queryFn: () => api.get("/items"),
  });

  const { data: locations } = useQuery({
    queryKey: ["locations"],
    queryFn: () => api.get("/locations"),
  });

  const stockOutMutation = useMutation({
    mutationFn: (data: any) => api.post("/stock-out", data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["items"] });
      setReferenceNo("");
      setReason("");
      setLines([{ item_id: "", quantity: 1 }]);
    },
  });

  const addLine = () => {
    setLines([...lines, { item_id: "", quantity: 1 }]);
  };

  const removeLine = (index: number) => {
    setLines(lines.filter((_, i) => i !== index));
  };

  const updateLine = (index: number, field: keyof StockOutLine, value: any) => {
    const updated = [...lines];
    updated[index] = { ...updated[index], [field]: value };
    setLines(updated);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    stockOutMutation.mutate({
      reference_no: referenceNo,
      reason,
      items: lines,
    });
  };

  if (itemsLoading) return <LoadingSpinner />;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Stock Out</h1>

      <form onSubmit={handleSubmit} className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>Header</CardTitle>
          </CardHeader>
          <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="reference">Reference No</Label>
              <Input
                id="reference"
                value={referenceNo}
                onChange={(e) => setReferenceNo(e.target.value)}
                placeholder="e.g., SO-2024-001"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="reason">Reason</Label>
              <Input
                id="reason"
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                placeholder="Reason for stock out"
              />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>Items</CardTitle>
            <Button type="button" variant="outline" size="sm" onClick={addLine}>
              <Plus className="h-4 w-4 mr-1" />
              Add Line
            </Button>
          </CardHeader>
          <CardContent className="space-y-4">
            {lines.map((line, index) => (
              <div
                key={index}
                className="grid grid-cols-1 md:grid-cols-4 gap-4 items-end p-4 border rounded-lg"
              >
                <div className="md:col-span-2 space-y-2">
                  <Label>Item</Label>
                  <Select
                    value={line.item_id}
                    onValueChange={(v) => updateLine(index, "item_id", v)}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select item" />
                    </SelectTrigger>
                    <SelectContent>
                      {items?.map((item: any) => (
                        <SelectItem key={item.id} value={String(item.id)}>
                          {item.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>Qty</Label>
                  <Input
                    type="number"
                    min={1}
                    value={line.quantity}
                    onChange={(e) =>
                      updateLine(index, "quantity", parseInt(e.target.value))
                    }
                  />
                </div>
                <div className="space-y-2">
                  <Label>Location</Label>
                  <Select
                    value={line.location_id}
                    onValueChange={(v) => updateLine(index, "location_id", v)}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select" />
                    </SelectTrigger>
                    <SelectContent>
                      {locations?.map((loc: any) => (
                        <SelectItem key={loc.id} value={String(loc.id)}>
                          {loc.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  {lines.length > 1 && (
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={() => removeLine(index)}
                    >
                      <Trash2 className="h-4 w-4 text-red-500" />
                    </Button>
                  )}
                </div>
              </div>
            ))}
          </CardContent>
        </Card>

        <Button
          type="submit"
          disabled={stockOutMutation.isPending}
          className="w-full md:w-auto"
        >
          {stockOutMutation.isPending ? "Submitting..." : "Submit Stock Out"}
        </Button>
      </form>
    </div>
  );
}
