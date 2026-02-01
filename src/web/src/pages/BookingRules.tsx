import { useEffect, useState, FormEvent } from 'react';
import api from '../api';

export default function BookingRules() {
  const businessId = localStorage.getItem('businessId');
  const [form, setForm] = useState({
    advance_notice_hours: 24,
    max_advance_days: 30,
    cancellation_hours: 24,
  });
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    if (!businessId) return;
    api.get(`/businesses/${businessId}/booking-rules`).then((res) => {
      if (res.data) setForm(res.data);
    });
  }, [businessId]);

  async function handleSave(e: FormEvent) {
    e.preventDefault();
    await api.put(`/businesses/${businessId}/booking-rules`, form);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Booking Rules</h1>
      <form onSubmit={handleSave} className="bg-white rounded-lg shadow p-6 max-w-2xl space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Advance Notice (hours)</label>
          <input type="number" value={form.advance_notice_hours} onChange={(e) => setForm({ ...form, advance_notice_hours: +e.target.value })} className="w-full p-2 border rounded" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Max Advance Booking (days)</label>
          <input type="number" value={form.max_advance_days} onChange={(e) => setForm({ ...form, max_advance_days: +e.target.value })} className="w-full p-2 border rounded" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Cancellation Notice (hours)</label>
          <input type="number" value={form.cancellation_hours} onChange={(e) => setForm({ ...form, cancellation_hours: +e.target.value })} className="w-full p-2 border rounded" />
        </div>
        <button type="submit" className="bg-indigo-600 text-white px-6 py-2 rounded hover:bg-indigo-700">Save</button>
        {saved && <span className="ml-4 text-green-600">Saved!</span>}
      </form>
    </div>
  );
}
