const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export async function uploadDocument(file, tags = []) {
  const formData = new FormData();
  formData.append('file', file);
  tags.forEach(tag => formData.append('tags', tag));

  const response = await fetch(`${API_BASE}/documents`, {
    method: 'POST',
    body: formData,
  });
  return response.json();
}

export async function getDocuments(tag = null) {
  const url = tag
    ? `${API_BASE}/documents?tag=${encodeURIComponent(tag)}`
    : `${API_BASE}/documents`;
  const response = await fetch(url);
  return response.json();
}

export async function getDocument(id) {
  const response = await fetch(`${API_BASE}/documents/${id}`);
  return response.json();
}

export async function deleteDocument(id) {
  const response = await fetch(`${API_BASE}/documents/${id}`, {
    method: 'DELETE',
  });
  return response.json();
}

export async function searchDocuments(query, tag = null) {
  let url = `${API_BASE}/search?q=${encodeURIComponent(query)}`;
  if (tag) {
    url += `&tag=${encodeURIComponent(tag)}`;
  }
  const response = await fetch(url);
  return response.json();
}

export async function getTags() {
  const response = await fetch(`${API_BASE}/tags`);
  return response.json();
}
