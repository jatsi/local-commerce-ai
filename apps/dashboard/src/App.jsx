import { useEffect, useState } from "react";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export function App() {
  const [summary, setSummary] = useState({ jobs: 0, pending_approvals: 0 });
  const [jobs, setJobs] = useState([]);

  useEffect(() => {
    fetch(`${API_URL}/dashboard/summary`).then((r) => r.json()).then(setSummary);
    fetch(`${API_URL}/jobs`).then((r) => r.json()).then(setJobs);
  }, []);

  return (
    <main className="container">
      <h1>Local Commerce AI Dashboard</h1>
      <section className="stats">
        <article><h2>Jobs</h2><p>{summary.jobs}</p></article>
        <article><h2>Pending approvals</h2><p>{summary.pending_approvals}</p></article>
      </section>
      <section>
        <h2>Recent Jobs</h2>
        <ul>
          {jobs.map((job) => (
            <li key={job.id}>{job.name} - {job.status}</li>
          ))}
        </ul>
      </section>
    </main>
  );
}
