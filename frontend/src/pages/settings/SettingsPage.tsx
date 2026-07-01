import { Link } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Users, MapPin } from "lucide-react";

export default function SettingsPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Settings</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <Link to="/settings/users">
          <Card className="hover:bg-gray-50 transition-colors cursor-pointer">
            <CardHeader className="flex flex-row items-center gap-4">
              <Users className="h-8 w-8 text-primary" />
              <div>
                <CardTitle>Users</CardTitle>
                <p className="text-sm text-muted-foreground">
                  Manage system users
                </p>
              </div>
            </CardHeader>
          </Card>
        </Link>

        <Link to="/settings/locations">
          <Card className="hover:bg-gray-50 transition-colors cursor-pointer">
            <CardHeader className="flex flex-row items-center gap-4">
              <MapPin className="h-8 w-8 text-primary" />
              <div>
                <CardTitle>Locations</CardTitle>
                <p className="text-sm text-muted-foreground">
                  Manage storage locations
                </p>
              </div>
            </CardHeader>
          </Card>
        </Link>
      </div>
    </div>
  );
}
