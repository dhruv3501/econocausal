import { useState } from "react";
import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [budget, setBudget] = useState("5000");
  const [message, setMessage] = useState("");

  function handleSubmit(event) {
    event.preventDefault();

    if (!file) {
      setMessage("Please upload a campaign CSV file.");
      return;
    }

    if (Number(budget) <= 0 || budget.trim() === "") {
      setMessage("Please enter a valid budget.");
      return;
    }
    
    setMessage(
      `Campaign file: ${file.name} | Budget: $${budget}`
    );
  }

  return (
    <main className="dashboard">
      <header className="header">
        <h1>EconoCausal</h1>
        <p>Dynamic Pricing via Causal AI</p>
      </header>

      <section className="panel">
        <h2>Campaign Setup</h2>
        <p>
          Upload customer data and set your promotional budget.
        </p>

        <form onSubmit={handleSubmit}>
          <label>Historical Campaign Data (CSV)</label>
          <input
            type="file"
            accept=".csv,text/csv"
            onChange={(event) => {
              setFile(event.target.files[0] || null);
              setMessage("");
            }}
          />

          <label>Marketing Budget ($)</label>
          <input
            type="number"
            min="1"
            step="0.01"
            value={budget}
            onChange={(event) => setBudget(event.target.value)}
            required
          />

          <button type="submit">Prepare Campaign</button>
        </form>

        {message && <p className="message">{message}</p>}
      </section>

      <footer>
        EconoCausal | Causal Inference & Budget Planning
      </footer>
    </main>
  );
}

export default App;