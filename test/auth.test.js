const test = require('node:test');
const assert = require('node:assert/strict');

const { app, users } = require('../src/app');

let server;
let baseUrl;

test.before(async () => {
  users.clear();
  server = app.listen(0);
  await new Promise((resolve) => server.once('listening', resolve));
  const { port } = server.address();
  baseUrl = `http://127.0.0.1:${port}`;
});

test.after(async () => {
  if (!server) return;
  await new Promise((resolve, reject) => {
    server.close((error) => (error ? reject(error) : resolve()));
  });
});

test('registers a user and allows login', async () => {
  const registerResponse = await fetch(`${baseUrl}/api/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      username: 'alice',
      email: 'alice@example.com',
      password: 'mypassword'
    })
  });

  assert.equal(registerResponse.status, 201);
  const registerJson = await registerResponse.json();
  assert.equal(registerJson.user.email, 'alice@example.com');

  const loginResponse = await fetch(`${baseUrl}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      email: 'alice@example.com',
      password: 'mypassword'
    })
  });

  assert.equal(loginResponse.status, 200);
  const loginJson = await loginResponse.json();
  assert.ok(loginJson.token);
  assert.equal(loginJson.user.username, 'alice');
});

test('rejects duplicate registration', async () => {
  const response = await fetch(`${baseUrl}/api/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      username: 'alice-2',
      email: 'alice@example.com',
      password: 'mypassword2'
    })
  });

  assert.equal(response.status, 409);
});

test('rejects invalid login', async () => {
  const response = await fetch(`${baseUrl}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      email: 'alice@example.com',
      password: 'wrongpassword'
    })
  });

  assert.equal(response.status, 401);
});
