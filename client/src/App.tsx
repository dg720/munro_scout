import { useEffect, useState } from 'react';
import axios from 'axios';

interface Munro {
  id: number;
  name: string;
  summary: string;
  distance: number;
  time: number;
  grade: number;
  bog: number;
  start: string;
}

export default function App() {
  const [munros, setMunros] = useState<Munro[]>([]);
  const [search, setSearch] = useState('');

  useEffect(() => {
    const query = search ? `?search=${encodeURIComponent(search)}` : '';
    axios
      .get(`http://localhost:5000/api/munros${query}`)
      .then((res) => setMunros(res.data))
      .catch((err) => console.error(err));
  }, [search]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-white">
      {/* Navbar */}
      <nav className="bg-blue-600 text-white py-4 shadow-md">
        <div className="max-w-6xl mx-auto px-6">
          <h1 className="text-2xl font-bold">🏔️ Munro Explorer</h1>
        </div>
      </nav>

      <main className="max-w-6xl mx-auto px-6 py-10">
        {/* PURPLE TEST TEXT */}
        <h2 className="text-3xl font-bold text-purple-600 underline mb-6 text-center">
          Tailwind is working!
        </h2>

        {/* Info Box */}
        <div className="bg-blue-100 border border-blue-300 rounded-xl p-6 mb-8 shadow-sm text-center">
          <h2 className="text-lg font-semibold text-blue-900 mb-2">About This Project</h2>
          <p className="text-sm text-gray-700">
            This tool lets you search and explore Munro mountains — peaks in Scotland over 3,000 ft. 
            The data was sourced from public hillwalking websites and curated into a structured dataset 
            including distance, time, terrain grade, and bogginess.
          </p>
        </div>

        {/* Search Box */}
        <div className="bg-white rounded-xl shadow-md p-6 mb-6 border border-blue-100">
          <input
            type="text"
            className="w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400"
            placeholder="Search by name..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>

        {/* Table */}
        <div className="bg-white border border-blue-100 shadow-lg rounded-2xl overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm text-left">
              <thead className="bg-blue-100 text-blue-900 text-sm uppercase">
                <tr>
                  <th className="px-6 py-4">Name</th>
                  <th className="px-4 py-4 text-center">Distance (km)</th>
                  <th className="px-4 py-4 text-center">Time (hrs)</th>
                  <th className="px-4 py-4 text-center">Grade</th>
                  <th className="px-4 py-4 text-center">Bog</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {munros.map((m) => (
                  <tr
                    key={m.id}
                    className="hover:bg-blue-50 transition-all duration-150"
                  >
                    <td className="px-6 py-4 font-semibold text-gray-800">{m.name}</td>
                    <td className="px-4 py-4 text-center text-gray-600">{m.distance}</td>
                    <td className="px-4 py-4 text-center text-gray-600">{m.time}</td>
                    <td className="px-4 py-4 text-center text-gray-600">{m.grade}</td>
                    <td className="px-4 py-4 text-center text-gray-600">{m.bog}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <footer className="mt-12 text-center text-sm text-gray-400">
          Built with Flask, React & Tailwind — demo project by Dhruv
        </footer>
      </main>
    </div>
  );
}
