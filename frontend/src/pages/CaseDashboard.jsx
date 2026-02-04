import React, { useEffect, useState } from 'react';

const CaseDashboard = () => {
  const [cases, setCases] = useState([]);
  const [formData, setFormData] = useState({ case_id: '', police_station: '', case_date: '' });

  const fetchCases = async () => {
    const response = await fetch('http://localhost:8000/api/cases');
    if (response.ok) {
      const data = await response.json();
      setCases(data);
    }
  };

  useEffect(() => {
    fetchCases();
  }, []);

  const handleChange = (event) => {
    setFormData({ ...formData, [event.target.name]: event.target.value });
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    const payload = new FormData();
    payload.append('case_id', formData.case_id);
    payload.append('police_station', formData.police_station);
    payload.append('case_date', formData.case_date);
    const response = await fetch('http://localhost:8000/api/cases', {
      method: 'POST',
      body: payload
    });
    if (response.ok) {
      setFormData({ case_id: '', police_station: '', case_date: '' });
      fetchCases();
    }
  };

  return (
    <section>
      <h2>Case Management</h2>
      <form onSubmit={handleSubmit} className="card">
        <label>
          Case ID
          <input name="case_id" value={formData.case_id} onChange={handleChange} />
        </label>
        <label>
          Police Station
          <input name="police_station" value={formData.police_station} onChange={handleChange} />
        </label>
        <label>
          Case Date
          <input name="case_date" type="date" value={formData.case_date} onChange={handleChange} />
        </label>
        <button type="submit">Create Case</button>
      </form>
      <div className="table">
        <div className="table-row header">
          <span>Case ID</span>
          <span>Police Station</span>
          <span>Date</span>
          <span>Created</span>
        </div>
        {cases.map((entry) => (
          <div className="table-row" key={entry.case_id}>
            <span>{entry.case_id}</span>
            <span>{entry.police_station}</span>
            <span>{entry.case_date}</span>
            <span>{entry.created_at}</span>
          </div>
        ))}
      </div>
    </section>
  );
};

export default CaseDashboard;
