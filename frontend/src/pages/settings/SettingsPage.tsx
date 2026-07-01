import { Card, CardContent } from "@/components/ui/card";
export default function SettingsPage() {
  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold text-gray-800">Settings</h2>
      <Card><CardContent className="p-6 space-y-4">
        <div>
          <h3 className="text-lg font-semibold">Bigstar Optoelectronics (M) Sdn Bhd</h3>
          <p className="text-sm text-gray-500">Inventory Management System v1.0</p>
        </div>
        <div className="border-t pt-4">
          <p className="text-sm text-gray-600">Contact: support@bigstarled.com.my</p>
          <p className="text-sm text-gray-600">Website: www.bigstarled.com.my</p>
        </div>
      </CardContent></Card>
    </div>
  );
}
