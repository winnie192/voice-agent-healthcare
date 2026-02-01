import { useEffect, useState, FormEvent } from 'react';
import api from '../api';

interface Service {
  id: string;
  name: string;
  description: string | null;
  duration_minutes: number;
  price: number | null;
}

export default function Services() {
  const businessId = localStorage.getItem('businessId');
  const [services, setServices] = useState<Service[]>([]);
  const [name, setName] = useState('');
  const [duration, setDuration] = useState(30);
  const [price, setPrice] = useState('');
  const [description, setDescription] = useState('');

  async function load() {
    if (!businessId) return;
    const res = await api.get(`/businesses/${businessId}/services`);
    setServices(res.data);
  }

  useEffect(() => { load(); }, [businessId]);

  async function handleAdd(e: FormEvent) {
    e.preventDefault();
    await api.post(`/businesses/${businessId}/services`, {
      name,
      duration_minutes: duration,
      price: price ? parseFloat(price) : null,
      description: description || null,
    });
    setName(''); setDuration(30); setPrice(''); setDescription('');
    load();
  }

  async function handleDelete(id: string) {
    await api.delete(`/businesses/${businessId}/services/${id}`);
    load();
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Services</h1>
      <form onSubmit={handleAdd} className="bg-white rounded-lg shadow p-6 mb-6 max-w-2xl space-y-4">
        <input placeholder="Service name" value={name} onChange={(e) => setName(e.target.value)} className="w-full p-2 border rounded" required />
        <input placeholder="Description" value={description} onChange={(e) => setDescription(e.target.value)} className="w-full p-2 border rounded" />
        <div className="flex space-x-4">
          <input type="number" placeholder="Duration (min)" value={duration} onChange={(e) => setDuration(+e.target.value)} className="w-1/2 p-2 border rounded" required />
          <input type="number" step="0.01" placeholder="Price" value={price} onChange={(e) => setPrice(e.target.value)} className="w-1/2 p-2 border rounded" />
        </div>
        <button type="submit" className="bg-indigo-600 text-white px-6 py-2 rounded hover:bg-indigo-700">Add Service</button>
      </form>
      <div className="space-y-3">
        {services.map((s) => (
          <div key={s.id} className="bg-white rounded-lg shadow p-4 flex justify-between">
            <div>
              <h3 className="font-medium">{s.name}</h3>
              <p className="text-sm text-gray-500">{s.duration_minutes} min {s.price ? `· $${s.price}` : ''}</p>
            </div>
            <button onClick={() => handleDelete(s.id)} className="text-red-500 text-sm">Delete</button>
          </div>
        ))}
      </div>
    </div>
  );
}
