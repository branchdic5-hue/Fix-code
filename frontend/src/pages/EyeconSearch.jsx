import React, { useState } from 'react';

const EyeconSearch = () => {
  const [caseId, setCaseId] = useState('');
  const [numbers, setNumbers] = useState('');
  const [results, setResults] = useState([]);

  const handleSearch = async () => {
    const payload = new FormData();
    payload.append('numbers', numbers);
    const response = await fetch(`http://localhost:8000/api/cases/${caseId}/eyecon`, {
      method: 'POST',
      body: payload
    });
    if (response.ok) {
      const data = await response.json();
      setResults(data.results || []);
    }
  };

  return (
    <section>
      <h2>Eyecon Enrichment</h2>
      <div className="card">
        <label>
          Case ID
          <input value={caseId} onChange={(event) => setCaseId(event.target.value)} />
        </label>
        <label>
          Numbers (comma separated)
          <textarea value={numbers} onChange={(event) => setNumbers(event.target.value)} />
        </label>
        <button type="button" onClick={handleSearch}>Search</button>
      </div>
      <div className="table">
        <div className="table-row header">
          <span>Number</span>
          <span>Primary Name</span>
          <span>Alt Name 1</span>
          <span>Alt Name 2</span>
          <span>Alt Name 3</span>
          <span>Facebook</span>
          <span>Status</span>
        </div>
        {results.map((entry) => (
          <div className="table-row" key={entry.number}>
            <span>{entry.number}</span>
            <span>{entry.primary_name}</span>
            <span>{entry.alternate_name_1}</span>
            <span>{entry.alternate_name_2}</span>
            <span>{entry.alternate_name_3}</span>
            <span>{entry.facebook_profile_link}</span>
            <span>{entry.status}</span>
          </div>
        ))}
      </div>
    </section>
  );
};

export default EyeconSearch;
