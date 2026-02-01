import { useEffect, useState, FormEvent } from 'react';
import api from '../api';

export default function BusinessSettings() {
  const businessId = localStorage.getItem('businessId');
  const [form, setForm] = useState({ name: '', phone: '', timezone: '', location: '', policies: '' });
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    if (!businessId) return;
    api.get(`/businesses/${businessId}`).then((res) => setForm(res.data));
  }, [businessId]);

  async function handleSave(e: FormEvent) {
    e.preventDefault();
    await api.patch(`/businesses/${businessId}`, form);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Business Settings</h1>
      <form onSubmit={handleSave} className="bg-white rounded-lg shadow p-6 max-w-2xl space-y-4">
        {(['name', 'phone', 'timezone', 'location'] as const).map((field) => (
          <div key={field}>
            <label className="block text-sm font-medium text-gray-700 capitalize mb-1">{field}</label>
            <input
              value={(form as Record<string, string>)[field] || ''}
              onChange={(e) => setForm({ ...form, [field]: e.target.value })}
              className="w-full p-2 border rounded"
            />
          </div>
        ))}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Policies</label>
          <textarea
            value={form.policies || ''}
            onChange={(e) => setForm({ ...form, policies: e.target.value })}
            className="w-full p-2 border rounded h-32"
          />
        </div>
        <button type="submit" className="bg-indigo-600 text-white px-6 py-2 rounded hover:bg-indigo-700">
          Save
        </button>
        {saved && <span className="ml-4 text-green-600">Saved!</span>}
      </form>
    </div>
  );
}
