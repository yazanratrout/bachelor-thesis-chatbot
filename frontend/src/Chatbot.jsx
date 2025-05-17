import React, { useState } from 'react';

function Chatbot() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await fetch(`/search?query=${encodeURIComponent(query)}`);
      const data = await response.json();
      setResults(data.results);
    } catch (err) {
      setResults(["Error fetching data"]);
    }
    setLoading(false);
  };

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <input value={query} onChange={(e) => setQuery(e.target.value)} />
        <button type="submit">Ask</button>
      </form>
      {loading ? <p>Loading...</p> : results.map((res, idx) => <p key={idx}>{res}</p>)}
    </div>
  );
}

export default Chatbot;
