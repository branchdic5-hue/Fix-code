import React, { useState } from 'react';

const Login = () => {
  const [formData, setFormData] = useState({ username: '', password: '' });
  const [message, setMessage] = useState('');

  const handleChange = (event) => {
    setFormData({ ...formData, [event.target.name]: event.target.value });
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    const payload = new FormData();
    payload.append('username', formData.username);
    payload.append('password', formData.password);

    const response = await fetch('http://localhost:8000/api/login', {
      method: 'POST',
      body: payload
    });

    if (response.ok) {
      const data = await response.json();
      setMessage(`Welcome ${data.username} (${data.role})`);
    } else {
      setMessage('Login failed');
    }
  };

  return (
    <section>
      <h2>Admin Login</h2>
      <form onSubmit={handleSubmit} className="card">
        <label>
          Username
          <input name="username" value={formData.username} onChange={handleChange} />
        </label>
        <label>
          Password
          <input name="password" type="password" value={formData.password} onChange={handleChange} />
        </label>
        <button type="submit">Login</button>
      </form>
      {message && <p className="message">{message}</p>}
    </section>
  );
};

export default Login;
