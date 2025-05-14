import React, { useState } from 'react';

function Chatbot() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    try {
      const response = await fetch(`http://localhost:8000/search?query=${encodeURIComponent(query)}`);
      if (!response.ok) throw new Error('Backend error');
      const data = await response.json();
      setResults(data.results || []);
    } catch (error) {
      console.error('Search failed:', error);
      setResults(["Something went wrong. Please try again."]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-4">
      <form onSubmit={handleSubmit} className="mb-4 flex gap-2">
        <input
          className="flex-1 p-2 border border-gray-300 rounded"
          type="text"
          placeholder="Ask your question..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button className="bg-blue-500 text-white px-4 py-2 rounded" type="submit">
          Ask
        </button>
      </form>

      {loading && <p>Loading...</p>}

      <div className="space-y-2">
        {results.map((res, idx) => (
          <div key={idx} className="p-3 bg-gray-100 rounded shadow-sm">
            {res}
          </div>
        ))}
      </div>
    </div>
  );
}

export default Chatbot;