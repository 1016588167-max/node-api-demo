const express = require('express');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');

const app = express();

app.use(express.json());

const users = new Map();
const JWT_SECRET = process.env.JWT_SECRET || 'dev_secret_change_me';

app.get('/', (req, res) => {
  res.json({ message: 'Auth API is running' });
});

app.post('/api/auth/register', async (req, res) => {
  const { username, email, password } = req.body;

  if (!username || !email || !password) {
    return res.status(400).json({ message: 'username, email and password are required' });
  }

  if (password.length < 6) {
    return res.status(400).json({ message: 'password must be at least 6 characters' });
  }

  const normalizedEmail = email.trim().toLowerCase();

  if (users.has(normalizedEmail)) {
    return res.status(409).json({ message: 'user already exists' });
  }

  const passwordHash = await bcrypt.hash(password, 10);
  const id = cryptoRandomId();

  users.set(normalizedEmail, {
    id,
    username,
    email: normalizedEmail,
    passwordHash
  });

  return res.status(201).json({
    message: 'registration successful',
    user: {
      id,
      username,
      email: normalizedEmail
    }
  });
});

app.post('/api/auth/login', async (req, res) => {
  const { email, password } = req.body;

  if (!email || !password) {
    return res.status(400).json({ message: 'email and password are required' });
  }

  const normalizedEmail = email.trim().toLowerCase();
  const user = users.get(normalizedEmail);

  if (!user) {
    return res.status(401).json({ message: 'invalid credentials' });
  }

  const matched = await bcrypt.compare(password, user.passwordHash);

  if (!matched) {
    return res.status(401).json({ message: 'invalid credentials' });
  }

  const token = jwt.sign(
    {
      sub: user.id,
      email: user.email,
      username: user.username
    },
    JWT_SECRET,
    { expiresIn: '1h' }
  );

  return res.json({
    message: 'login successful',
    token,
    user: {
      id: user.id,
      username: user.username,
      email: user.email
    }
  });
});

function cryptoRandomId() {
  return `${Date.now()}_${Math.random().toString(36).slice(2, 10)}`;
}

module.exports = { app, users };
