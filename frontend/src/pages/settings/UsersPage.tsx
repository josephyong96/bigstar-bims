import { useState, useEffect } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "@/components/ui/table";
import { LoadingSpinner } from "@/components/shared/LoadingSpinner";
import { StatusBadge } from "@/components/shared/StatusBadge";
import { userApi } from "@/services/api";
import { Search } from "lucide-react";

const ROLE_LABELS: Record<string, string> = {
  management: "Management", project_manager: "Project Manager",
  sales: "Sales", warehouse: "Warehouse", technician: "Technician"
};

export default function UsersPage() {
  const [users, setUsers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [role, setRole] = useState("");

  useEffect(() => { load(); }, [search, role]);

  async function load() {
    setLoading(true);
    try {
      const res = await userApi.list({ search, role: role || undefined });
      setUsers(res.data.items || []);
    } catch (e) { console.error(e); }
    setLoading(false);
  }

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold text-gray-800">User Management</h2>
      <Card><CardContent className="p-4 flex gap-3">
        <div className="relative flex-1"><Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={16} /><Input placeholder="Search users..." value={search} onChange={(e) => setSearch(e.target.value)} className="pl-9" /></div>
        <Select value={role} onChange={(e) => setRole(e.target.value)} className="w-44">
          <option value="">All Roles</option>
          <option value="management">Management</option><option value="project_manager">Project Manager</option>
          <option value="sales">Sales</option><option value="warehouse">Warehouse</option><option value="technician">Technician</option>
        </Select>
      </CardContent></Card>
      <Card><CardContent className="p-0">
        {loading ? <LoadingSpinner className="flex justify-center p-8" /> : (
          <Table>
            <TableHeader><TableRow><TableHead>Username</TableHead><TableHead>Full Name</TableHead><TableHead>Email</TableHead><TableHead>Role</TableHead><TableHead>Status</TableHead></TableRow></TableHeader>
            <TableBody>
              {users.length === 0 && <TableRow><TableCell colSpan={5} className="text-center py-8 text-gray-500">No users found</TableCell></TableRow>}
              {users.map((u) => (
                <TableRow key={u.id}>
                  <TableCell className="font-medium">{u.username}</TableCell>
                  <TableCell>{u.full_name}</TableCell>
                  <TableCell>{u.email}</TableCell>
                  <TableCell>{ROLE_LABELS[u.role] || u.role}</TableCell>
                  <TableCell><StatusBadge status={u.is_active ? "active" : "inactive"} /></TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </CardContent></Card>
    </div>
  );
}
