import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "@/components/ui/table";
import { LoadingSpinner } from "@/components/shared/LoadingSpinner";
import { StatusBadge } from "@/components/shared/StatusBadge";
import { projectApi } from "@/services/api";
import { formatDate } from "@/lib/utils";
import { Plus, Search, Eye } from "lucide-react";

export default function ProjectsPage() {
  const [projects, setProjects] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("");
  const navigate = useNavigate();

  useEffect(() => { load(); }, [search, status]);

  async function load() {
    setLoading(true);
    try {
      const res = await projectApi.list({ search, status: status || undefined });
      setProjects(res.data.items || []);
    } catch (e) { console.error(e); }
    setLoading(false);
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-800">Projects</h2>
        <Button onClick={() => navigate("/projects/new")}><Plus size={16} className="mr-2"/> New Project</Button>
      </div>
      <Card><CardContent className="p-4 flex gap-3">
        <div className="relative flex-1"><Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={16} /><Input placeholder="Search projects..." value={search} onChange={(e) => setSearch(e.target.value)} className="pl-9" /></div>
        <Select value={status} onChange={(e) => setStatus(e.target.value)} className="w-40">
          <option value="">All Status</option><option value="planning">Planning</option><option value="active">Active</option><option value="on_hold">On Hold</option><option value="completed">Completed</option><option value="cancelled">Cancelled</option>
        </Select>
      </CardContent></Card>
      <Card><CardContent className="p-0">
        {loading ? <LoadingSpinner className="flex justify-center p-8" /> : (
          <Table>
            <TableHeader><TableRow><TableHead>Project Code</TableHead><TableHead>Name</TableHead><TableHead>Client</TableHead><TableHead>Status</TableHead><TableHead>Start Date</TableHead><TableHead className="text-right">Actions</TableHead></TableRow></TableHeader>
            <TableBody>
              {projects.length === 0 && <TableRow><TableCell colSpan={6} className="text-center py-8 text-gray-500">No projects found</TableCell></TableRow>}
              {projects.map((p) => (
                <TableRow key={p.id}>
                  <TableCell className="font-medium">{p.project_code}</TableCell>
                  <TableCell>{p.project_name}</TableCell>
                  <TableCell>{p.client_name}</TableCell>
                  <TableCell><StatusBadge status={p.status} /></TableCell>
                  <TableCell>{formatDate(p.start_date)}</TableCell>
                  <TableCell className="text-right"><Button size="sm" variant="ghost" onClick={() => navigate(`/projects/${p.id}`)}><Eye size={14} /></Button></TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </CardContent></Card>
    </div>
  );
}
