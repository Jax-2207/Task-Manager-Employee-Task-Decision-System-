const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:5000/api";

function authHeaders(token) {
  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  };
}

// --- Auth ---

export async function adminLogin(email, password) {
  const res = await fetch(`${API_BASE}/auth/admin/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.error || "Admin login failed");
  }
  return res.json(); // { token, user }
}

export async function registerGoogleUser(token) {
  const res = await fetch(`${API_BASE}/auth/google/register`, {
    method: "POST",
    headers: authHeaders(token),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.error || "Registration failed");
  }
  return res.json();
}

export async function getProfile(token) {
  const res = await fetch(`${API_BASE}/auth/me`, {
    headers: authHeaders(token),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.error || "Failed to get profile");
  }
  return res.json();
}

// --- Decisions ---

export async function fetchDecisions(token) {
  const res = await fetch(`${API_BASE}/decisions`, {
    headers: authHeaders(token),
  });
  if (!res.ok) throw new Error("Failed to fetch decisions");
  return res.json();
}

export async function fetchAssignedDecisions(token) {
  const res = await fetch(`${API_BASE}/decisions/assigned`, {
    headers: authHeaders(token),
  });
  if (!res.ok) throw new Error("Failed to fetch assigned decisions");
  return res.json();
}

export async function createDecision(title, description, token) {
  const res = await fetch(`${API_BASE}/decisions`, {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify({ title, description: description || null }),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(
      err.error ? JSON.stringify(err.error) : "Failed to create decision"
    );
  }
  return res.json();
}

export async function updateDecisionStatus(id, status, token) {
  const res = await fetch(`${API_BASE}/decisions/${id}/status`, {
    method: "PATCH",
    headers: authHeaders(token),
    body: JSON.stringify({ status }),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.error || "Failed to update status");
  }
  return res.json();
}

export async function assignDecision(decisionId, employeeId, token) {
  const res = await fetch(`${API_BASE}/decisions/${decisionId}/assign`, {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify({ employee_id: employeeId }),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.error || "Failed to assign decision");
  }
  return res.json();
}

export async function assignDecisionToAll(decisionId, token) {
  const res = await fetch(`${API_BASE}/decisions/${decisionId}/assign-all`, {
    method: "POST",
    headers: authHeaders(token),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.error || "Failed to assign to all");
  }
  return res.json();
}

export async function deleteDecision(id, token) {
  const res = await fetch(`${API_BASE}/decisions/${id}`, {
    method: "DELETE",
    headers: authHeaders(token),
  });
  if (!res.ok) throw new Error("Failed to delete decision");
  return res.json();
}
