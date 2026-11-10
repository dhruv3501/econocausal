import { useState, useEffect } from "react";
import "./App.css";
import Plot from "react-plotly.js";
function App() {
const [file, setFile] = useState(null);
const [budget, setBudget] = useState("5000");
const [message, setMessage] = useState("");
const [campaignResult, setCampaignResult ] = useState(null);
const [page, setPage] = useState("setup");
const [modelResults, setModelResults] = useState([]);
const [validation, setValidation] = useState(null);
const [qiniResults, setQiniResults] = useState([])
useEffect(() => {
  async function loadResults() {
    try {
      const [resultsResponse, validationResponse, qiniResponse] = await Promise.all([
        fetch("/data/corrected_causal_forest_results.csv"),
        fetch("/data/week2_validation_summary.csv"),
        fetch("/data/qini_curve_results.csv")
      ]);
      if (!resultsResponse.ok || !validationResponse.ok || !qiniResponse.ok) {
        throw new Error("Could not load model results.");
      }
      const resultsText = await resultsResponse.text();
      const validationText = await validationResponse.text();
      const qiniText =await qiniResponse.text();
      const parseCSV = (text) => {
        const lines = text.trim().split(/\r?\n/);
        const headers = lines[0].split(",").map(h => h.trim());
        return lines.slice(1).map(line => {
          const values = line.split(",");
          return Object.fromEntries(
            headers.map((header, i) => [header, values[i]?.trim()])
          );
        });
      };
      setModelResults(parseCSV(resultsText));
      setValidation(parseCSV(validationText)[0]);
      setQiniResults(parseCSV(qiniText));

    } catch (error) {
      console.error(error);
      setMessage("Could not load model results. Check the CSV files.");
    }
  }
  loadResults();
}, []);
async function handleSubmit(event) {
  event.preventDefault();

  if (!file || !budget) {
    setMessage("Please select a CSV and enter a budget.");
    return;
  }

  const formData = new FormData();
  formData.append("file", file);
  formData.append("budget", budget);

  const response = await fetch("http://127.0.0.1:8000/upload-csv", {
    method: "POST",
    body: formData,
  });

  const data = await response.json();
  setCampaignResult(data);
  setMessage(
    `Campaign ready: ${data.total_customers} customers | Budget: $${data.budget}`
  );
}
return (
<main className="dashboard">
<header className="header">
<h1>EconoCausal</h1>
<p>Dynamic Pricing via Causal AI</p>
</header>
   <nav className="navigation">
    <button 
      className={page === "setup" ? "active" : ""}
      onClick={() => setPage("setup")}
    >
      Campaign Setup
    </button>
    <button 
      className={page === "uplift" ? "active" : ""}
      onClick={() => setPage("uplift")}
    >
      Uplift Curves
    </button>
    <button 
      className={page === "allocation" ? "active" : ""}
      onClick={() => setPage("allocation")}
    >
      Allocation Matrix
    </button>
    <button
  className={page === "qini" ? "active" : ""}
  onClick={() => setPage("qini")}
>
  Qini Analysis
</button>
  </nav>
  {page === "setup" && (
    <section className="panel">
      <h2>Campaign Setup</h2>
      <p>Upload customer data and set your promotional budget.</p>
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
      {campaignResult && (
  <div className="campaign-results">
    <p>High Uplift: {campaignResult.high_uplift.customers} customers → ${campaignResult.high_uplift.budget}</p>
    <p>Medium Uplift: {campaignResult.medium_uplift.customers} customers → ${campaignResult.medium_uplift.budget}</p>
    <p>Low Uplift: {campaignResult.low_uplift.customers} customers → ${campaignResult.low_uplift.budget}</p>
  </div>
)}
    </section>
  )}
   {page === "uplift" && (
  <section className="panel">
    <h2>Uplift Curves</h2>
   <p>Individual treatment effects predicted by your Causal Forest model.</p>
{modelResults.length > 0 ? (
  <Plot
    data={[
      {
        x: modelResults.map((_, i) => i + 1),
        y: modelResults.map(row => Number(row.estimated_ite)),
        type: "scatter",
        mode: "lines",
        name: "Estimated ITE",
        line: { color: "#2f8f83", width: 2 },
      },
    ]}
    layout={{
      autosize: true,
      title: { text: "Predicted Treatment Effects by Test Customer" },
      xaxis: { title: "Test customer (CSV row order)" },
      yaxis: { title: "Estimated treatment effect" },
      margin: { l: 65, r: 25, t: 60, b: 60 },
    }}
    useResizeHandler
    style={{ width: "100%", height: "380px" }}
    config={{ responsive: true, displayModeBar: false }}
  />
) : (
  <p className="message">Loading model results...</p>
)}
{validation && (
  <p className="message">
    Test customers: {validation.test_customers} |
    MAE: {validation.MAE} |
    RMSE: {validation.RMSE} |
    Spearman correlation: {validation.spearman_correlation}
  </p>
)}
  </section>
)}
   {page === "allocation" && (
  <section className="panel">
    <h2>Allocation Matrix</h2>
    <p>Customer groups ranked using predicted treatment effects.</p>
    <table>
      <thead>
        <tr>
          <th>Customer Group</th>
          <th>Discount</th>
          <th>Budget Share</th>
          <th>Customers</th>
        </tr>
      </thead>
      <tbody>
        {modelResults.length > 0 ? (() => {
          const sorted = [...modelResults].sort(
            (a, b) => Number(b.estimated_ite) - Number(a.estimated_ite)
          );
          const highCount = campaignResult
  ? campaignResult.high_uplift.customers
  : Math.ceil(sorted.length * 0.6);
const mediumCount = campaignResult
  ? campaignResult.medium_uplift.customers
  : Math.ceil(sorted.length * 0.3);
          const groups = [
  {
    name: "High uplift",
    discount: "20%",
    share: campaignResult ? `$${campaignResult.high_uplift.budget}` : "60%",
    count: highCount,
  },
  {
    name: "Medium uplift",
    discount: "10%",
    share: campaignResult ? `$${campaignResult.medium_uplift.budget}` : "30%",
    count: mediumCount,
  },
  {
    name: "Low uplift",
    discount: "0%",
    share: campaignResult ? `$${campaignResult.low_uplift.budget}` : "10%",
    count: sorted.length - highCount - mediumCount,
  },
];
          return groups.map(group => (
            <tr key={group.name}>
              <td>{group.name}</td>
              <td>{group.discount}</td>
              <td>{group.share}</td>
              <td>{group.count}</td>
            </tr>
          ));
        })() : (
          <tr>
            <td colSpan="4">Loading model results...</td>
          </tr>
        )}
      </tbody>
    </table>
    <p className="message">
      Customer counts and budget allocations are calculated from the campaign analysis.
    </p>
  </section>
)}
  {page === "qini" && (
  <section className="panel">
    <h2>Qini Curve Analysis</h2>
    <p>
      Cumulative uplift achieved by targeting customers
      according to their estimated treatment effects.
    </p>
    {qiniResults.length > 0 ? (
      <Plot
        data={[
          {
            x: qiniResults.map(row =>
              Number(row.fraction_targeted)
            ),
            y: qiniResults.map(row =>
              Number(row.qini_curve)
            ),
            type: "scatter",
            mode: "lines",
            name: "Qini Curve",
            line: { color: "#2f8f83", width: 3 }
          }
        ]}
        layout={{
          autosize: true,
          title: { text: "Cumulative Qini Curve" },
          xaxis: {
            title: "Fraction of Customers Targeted",
            tickformat: ".0%"
          },
          yaxis: {
            title: "Cumulative Uplift"
          },
          margin: { l: 65, r: 25, t: 60, b: 60 }
        }}
        useResizeHandler
        style={{ width: "100%", height: "400px" }}
        config={{ responsive: true, displayModeBar: false }}
      />
    ) : (
      <p className="message">Loading Qini results...</p>
    )}
  </section>
)}
  <footer>
    EconoCausal | Causal Inference &amp; Budget Planning
  </footer>
</main>
);
}
export default App;