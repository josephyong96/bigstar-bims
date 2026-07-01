import { useState, useEffect } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "@/components/ui/table";
import { LoadingSpinner } from "@/components/shared/LoadingSpinner";
import { StatusBadge } from "@/components/shared/StatusBadge";
import { locationApi } from "@/services/api";
import type { Location } from "@/types";
import { Search } from "lucide-react";

export default function LocationsPage() {
  const [locations, setLocations] = useState<Location[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");

  useEffect(() => {
    async function load() {
      try {
        const res = await locationApi.list();
        setLocations(res.data || []);
      } catch (e) { console.error(e); }
      setLoading(false);
    }
    load();
  }, []);

  const filtered = locations.filter((l) =>
    !search || l.name.toLowerCase().includes(search.toLowerCase()) || l.code.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold text-gray-800">Locations</h2>
      <Card><CardContent className="p-4">
        <div className="relative"><Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={16} /><Input placeholder="Search locations..." value={search} onChange={(e) => setSearch(e.target.value)} className="pl-9" /></div>
      </CardContent></Card>
      <Card><CardContent className="p-0">
        {loading ? <LoadingSpinner className="flex justify-center p-8" /> : (
          <Table>
            <TableHeader><TableRow><TableHead>Code</TableHead><TableHead>Name</TableHead><TableHead>Type</TableHead><TableHead>Contact</TableHead><TableHead>Status</TableHead></TableRow></TableHeader>
            <TableBody>
              {filtered.length === 0 && <TableRow><TableCell colSpan={5} className="text-center py-8 text-gray-500">No locations found</TableCell></TableRow>}
              {filtered.map((l) => (
                <TableRow key={l.id}>
                  <TableCell className="font-medium">{l.code}</TableCell>
                  <TableCell>{l.name}</TableCell>
                  <TableCell className="capitalize">{l.location_type.replace(/_/g, " ")}</TableCell>
                  <TableCell>{l.contact_person || "-"}</TableCell>
                  <TableCell><StatusBadge status={l.is_active ? "active" : "inactive"} /></TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </CardContent></Card>
    </div>
  );
}
