import React, { useState } from 'react';

const Reports = () => {
  const [caseId, setCaseId] = useState('');
  const [callStats, setCallStats] = useState([]);
  const [dayNight, setDayNight] = useState({ day: [], night: [] });

  const fetchStats = async () => {
    const response = await fetch(`http://localhost:8000/api/cases/${caseId}/reports/call-stats`);
    if (response.ok) {
      const data = await response.json();
      setCallStats(data);
    }
  };

  const fetchDayNight = async () => {
    const response = await fetch(`http://localhost:8000/api/cases/${caseId}/reports/day-night`);
    if (response.ok) {
      const data = await response.json();
      setDayNight(data);
    }
  };

  return (
    <section>
      <h2>Reports</h2>
      <div className="card">
        <label>
          Case ID
          <input value={caseId} onChange={(event) => setCaseId(event.target.value)} />
        </label>
        <div className="actions">
          <button type="button" onClick={fetchStats}>Load Call Stats</button>
          <button type="button" onClick={fetchDayNight}>Load Day/Night</button>
          <a href={`http://localhost:8000/reports/${caseId}`} target="_blank" rel="noreferrer">
            HTML Reports
          </a>
        </div>
      </div>

      <h3>Call Statistics</h3>
      <div className="table">
        <div className="table-row header">
          <span>A Party</span>
          <span>B Party</span>
          <span>Count</span>
          <span>Duration</span>
        </div>
        {callStats.map((row) => (
          <div className="table-row" key={`${row.a_party}-${row.b_party}`}>
            <span>{row.a_party}</span>
            <span>{row.b_party}</span>
            <span>{row.call_count}</span>
            <span>{row.total_duration}</span>
          </div>
        ))}
      </div>

      <h3>Day Calls</h3>
      <div className="table">
        <div className="table-row header">
          <span>A Party</span>
          <span>B Party</span>
          <span>Count</span>
          <span>Duration</span>
        </div>
        {dayNight.day.map((row) => (
          <div className="table-row" key={`day-${row.a_party}-${row.b_party}`}>
            <span>{row.a_party}</span>
            <span>{row.b_party}</span>
            <span>{row.call_count}</span>
            <span>{row.total_duration}</span>
          </div>
        ))}
      </div>

      <h3>Night Calls</h3>
      <div className="table">
        <div className="table-row header">
          <span>A Party</span>
          <span>B Party</span>
          <span>Count</span>
          <span>Duration</span>
        </div>
        {dayNight.night.map((row) => (
          <div className="table-row" key={`night-${row.a_party}-${row.b_party}`}>
            <span>{row.a_party}</span>
            <span>{row.b_party}</span>
            <span>{row.call_count}</span>
            <span>{row.total_duration}</span>
          </div>
        ))}
      </div>
    </section>
  );
};

export default Reports;
