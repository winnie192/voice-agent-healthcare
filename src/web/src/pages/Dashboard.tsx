import { useEffect, useState } from 'react';
import api from '../api';

interface Stats {
  totalCalls: number;
  totalBookings: number;
  totalServices: number;
}

export default function Dashboard() {
  const [stats, setStats] = useState<Stats>({ totalCalls: 0, totalBookings: 0, totalServices: 0 });
  const businessId = localStorage.getItem('businessId');

  useEffect(() => {
    async function load() {
      if (!businessId) return;
      const [calls, bookings, services] = await Promise.all([
        api.get(`/businesses/${businessId}/call-logs`),
        api.get(`/businesses/${businessId}/bookings`),
        api.get(`/businesses/${businessId}/services`),
      ]);
      setStats({
        totalCalls: calls.data.length,
        totalBookings: bookings.data.length,
        totalServices: services.data.length,
      });
    }
    load();
  }, [businessId]);

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Dashboard</h1>
      <div className="grid grid-cols-3 gap-6">
        {[
          { label: 'Total Calls', value: stats.totalCalls, color: 'bg-blue-500' },
          { label: 'Bookings', value: stats.totalBookings, color: 'bg-green-500' },
          { label: 'Services', value: stats.totalServices, color: 'bg-purple-500' },
        ].map((card) => (
          <div key={card.label} className="bg-white rounded-lg shadow p-6">
            <div className={`inline-block px-3 py-1 rounded-full text-white text-xs ${card.color} mb-2`}>
              {card.label}
            </div>
            <p className="text-3xl font-bold">{card.value}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
