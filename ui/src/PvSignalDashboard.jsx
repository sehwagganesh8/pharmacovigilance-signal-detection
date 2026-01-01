import React, { useEffect, useState } from "react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid
} from "recharts";

export default function PvSignalDashboard() {
  const [signals, setSignals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function load() {
      try {
        const res = await fetch("/signals_with_summaries.json");
        if (!res.ok) throw new Error("Failed to load JSON");
        const data = await res.json();
        setSignals(data.signals || []);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading) return <div>Loading dashboard...</div>;
  if (error) return <div>Error loading dashboard: {error}</div>;

  return (
    <div style={{ padding: 20 }}>
      <h1>PV Safety Signal Dashboard</h1>
      <h3>Total Signals: {signals.length}</h3>

      <ResponsiveContainer width="100%" height={400}>
        <BarChart data={signals.slice(0, 15)}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="drug" />
          <YAxis />
          <Tooltip />
          <Bar dataKey="count" />
        </BarChart>
      </ResponsiveContainer>

      <h2>Signal List</h2>
      <ul>
        {signals.slice(0, 20).map((s, i) => (
          <li key={i}>
            <b>{s.drug}</b> – {s.reaction} ({s.count})
          </li>
        ))}
      </ul>
    </div>
  );
}