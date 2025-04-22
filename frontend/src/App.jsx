
import { useState } from "react";

function App() {
  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState([]);

  const sendMessage = async () => {
    const res = await fetch(`http://localhost:8000/ask?query=${encodeURIComponent(query)}`);
    const data = await res.json();
    setMessages([...messages, { role: "user", text: query }, { role: "bot", text: data.answer }]);
    setQuery("");
  };

  return (
    <div className="p-4 max-w-xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Chatbot</h1>
      <div className="space-y-2">
        {messages.map((msg, idx) => (
          <div key={idx} className={msg.role === "user" ? "text-right" : "text-left"}>
            <span className="inline-block bg-gray-200 p-2 rounded">{msg.text}</span>
          </div>
        ))}
      </div>
      <div className="mt-4 flex gap-2">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="flex-1 border p-2 rounded"
          placeholder="Ask something..."
        />
        <button onClick={sendMessage} className="bg-blue-500 text-white p-2 rounded">Send</button>
      </div>
    </div>
  );
}

export default App;
