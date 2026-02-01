import { useEffect, useState, FormEvent } from 'react';
import api from '../api';

interface Doc {
  id: string;
  title: string;
  content: string;
  created_at: string;
}

export default function KnowledgeBase() {
  const businessId = localStorage.getItem('businessId');
  const [docs, setDocs] = useState<Doc[]>([]);
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');

  async function load() {
    if (!businessId) return;
    const res = await api.get(`/businesses/${businessId}/knowledge-base`);
    setDocs(res.data);
  }

  useEffect(() => { load(); }, [businessId]);

  async function handleAdd(e: FormEvent) {
    e.preventDefault();
    await api.post(`/businesses/${businessId}/knowledge-base`, { title, content });
    setTitle('');
    setContent('');
    load();
  }

  async function handleDelete(docId: string) {
    await api.delete(`/businesses/${businessId}/knowledge-base/${docId}`);
    load();
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Knowledge Base</h1>
      <form onSubmit={handleAdd} className="bg-white rounded-lg shadow p-6 mb-6 max-w-2xl space-y-4">
        <input
          placeholder="Document title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className="w-full p-2 border rounded"
          required
        />
        <textarea
          placeholder="Document content"
          value={content}
          onChange={(e) => setContent(e.target.value)}
          className="w-full p-2 border rounded h-32"
          required
        />
        <button type="submit" className="bg-indigo-600 text-white px-6 py-2 rounded hover:bg-indigo-700">
          Add Document
        </button>
      </form>
      <div className="space-y-3">
        {docs.map((doc) => (
          <div key={doc.id} className="bg-white rounded-lg shadow p-4 flex justify-between items-start">
            <div>
              <h3 className="font-medium">{doc.title}</h3>
              <p className="text-sm text-gray-500 mt-1">{doc.content.slice(0, 200)}...</p>
            </div>
            <button onClick={() => handleDelete(doc.id)} className="text-red-500 hover:text-red-700 text-sm">
              Delete
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
