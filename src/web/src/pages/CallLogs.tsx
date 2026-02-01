import { useEffect, useState } from 'react';
import api from '../api';

interface CallLog {
  id: string;
  caller_phone: string | null;
  intent: string | null;
  outcome: string | null;
  duration_seconds: number | null;
  created_at: string;
}

export default function CallLogs() {
  const businessId = localStorage.getItem('businessId');
  const [logs, setLogs] = useState<CallLog[]>([]);

  useEffect(() => {
    if (!businessId) return;
    api.get(`/businesses/${businessId}/call-logs`).then((res) => setLogs(res.data));
  }, [businessId]);

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Call Logs</h1>
      {logs.length === 0 ? (
        <p className="text-gray-500">No calls recorded yet.</p>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Phone</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Intent</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Outcome</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Duration</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {logs.map((log) => (
                <tr key={log.id}>
                  <td className="px-6 py-4 text-sm">{log.caller_phone || 'Unknown'}</td>
                  <td className="px-6 py-4 text-sm">{log.intent || '-'}</td>
                  <td className="px-6 py-4 text-sm">{log.outcome || '-'}</td>
                  <td className="px-6 py-4 text-sm">{log.duration_seconds ? `${log.duration_seconds}s` : '-'}</td>
                  <td className="px-6 py-4 text-sm">{new Date(log.created_at).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
