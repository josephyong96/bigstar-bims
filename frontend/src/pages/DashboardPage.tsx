import { useQuery } from "@tanstack/react-query";
import { Package, FolderKanban, Wrench, AlertTriangle } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { LoadingSpinner } from "../components/shared/LoadingSpinner";
import { getDashboardStats, getDashboardActivities, getDashboardAlerts } from "../services/api";

export function DashboardPage() {
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ["dashboard-stats"],
    queryFn: getDashboardStats,
  });
  const { data: activities, isLoading: activitiesLoading } = useQuery({
    queryKey: ["dashboard-activities"],
    queryFn: getDashboardActivities,
  });
  const { data: alerts, isLoading: alertsLoading } = useQuery({
    queryKey: ["dashboard-alerts"],
    queryFn: getDashboardAlerts,
  });

  if (statsLoading) return <LoadingSpinner />;

  const statCards = [
    { title: "Total Items", value: stats?.data?.total_items || 0, icon: Package },
    { title: "Active Projects", value: stats?.data?.active_projects || 0, icon: FolderKanban },
    { title: "Pending Repairs", value: stats?.data?.pending_repairs || 0, icon: Wrench },
    { title: "Low Stock Alerts", value: stats?.data?.low_stock_count || 0, icon: AlertTriangle },
  ];

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Dashboard</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((stat) => {
          const Icon = stat.icon;
          return (
            <Card key={stat.title}>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-gray-500">
                  {stat.title}
                </CardTitle>
                <Icon className="w-4 h-4 text-gray-400" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stat.value}</div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Recent Activities</CardTitle>
          </CardHeader>
          <CardContent>
            {activitiesLoading ? (
              <LoadingSpinner />
            ) : (
              <div className="space-y-3">
                {activities?.data?.map((activity: { id: number; description: string; created_at: string }) => (
                  <div
                    key={activity.id}
                    className="flex items-center justify-between py-2 border-b last:border-0"
                  >
                    <span className="text-sm">{activity.description}</span>
                    <span className="text-xs text-gray-400">
                      {new Date(activity.created_at).toLocaleDateString()}
                    </span>
                  </div>
                )) || <p className="text-sm text-gray-500">No recent activities</p>}
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Alerts</CardTitle>
          </CardHeader>
          <CardContent>
            {alertsLoading ? (
              <LoadingSpinner />
            ) : (
              <div className="space-y-3">
                {alerts?.data?.map((alert: { id: number; message: string; severity: string }) => (
                  <div
                    key={alert.id}
                    className={`p-3 rounded-lg text-sm ${
                      alert.severity === "high"
                        ? "bg-red-50 text-red-700"
                        : alert.severity === "medium"
                        ? "bg-yellow-50 text-yellow-700"
                        : "bg-blue-50 text-blue-700"
                    }`}
                  >
                    {alert.message}
                  </div>
                )) || <p className="text-sm text-gray-500">No alerts</p>}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
