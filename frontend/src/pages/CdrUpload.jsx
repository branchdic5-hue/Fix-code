import React, { useState } from 'react';

const CdrUpload = () => {
  const [formData, setFormData] = useState({ case_id: '', operator: 'zong' });
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState('');

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!file) {
      setMessage('Please select an Excel file.');
      return;
    }
    const payload = new FormData();
    payload.append('operator', formData.operator);
    payload.append('file', file);
    const response = await fetch(`http://localhost:8000/api/cases/${formData.case_id}/upload`, {
      method: 'POST',
      body: payload
    });
    if (response.ok) {
      const data = await response.json();
      setMessage(`Uploaded ${data.rows} rows.`);
    } else {
      const error = await response.json();
      setMessage(error.detail || 'Upload failed.');
    }
  };

  return (
    <section>
      <h2>Upload CDR</h2>
      <form onSubmit={handleSubmit} className="card">
        <label>
          Case ID
          <input
            name="case_id"
            value={formData.case_id}
            onChange={(event) => setFormData({ ...formData, case_id: event.target.value })}
          />
        </label>
        <label>
          Operator
          <select
            name="operator"
            value={formData.operator}
            onChange={(event) => setFormData({ ...formData, operator: event.target.value })}
          >
            <option value="zong">Zong</option>
            <option value="jazz">Jazz</option>
            <option value="warid">Warid</option>
            <option value="mobilink">Mobilink</option>
            <option value="telenor">Telenor</option>
            <option value="ufone">Ufone</option>
          </select>
        </label>
        <label>
          Excel File
          <input type="file" onChange={(event) => setFile(event.target.files[0])} />
        </label>
        <button type="submit">Upload</button>
      </form>
      {message && <p className="message">{message}</p>}
    </section>
  );
};

export default CdrUpload;
