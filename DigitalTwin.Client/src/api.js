const BASE_URL = 'http://localhost:8000';

let activeRequests = 0;
function updateLoading(delta) {
  activeRequests += delta;
  if (activeRequests < 0) activeRequests = 0;
  window.dispatchEvent(new CustomEvent('api-loading', { detail: activeRequests > 0 }));
}

async function request(endpoint, options = {}) {
  updateLoading(1);
  const url = `${BASE_URL}${endpoint}`;
  
  // Prepare headers
  const headers = { ...options.headers };
  const token = localStorage.getItem('dt_token');
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  // Handle json payload automatically
  let body = options.body;
  if (body && !(body instanceof FormData)) {
    headers['Content-Type'] = 'application/json';
    body = JSON.stringify(body);
  }

  try {
    const res = await fetch(url, {
      ...options,
      headers,
      body,
    });

    if (res.status === 401) {
      localStorage.removeItem('dt_token');
      localStorage.removeItem('dt_user');
      window.dispatchEvent(new CustomEvent('api-auth-error'));
      throw new Error('Unauthorized');
    }

    if (!res.ok) {
      const errorText = await res.text();
      let errorJson;
      try {
        errorJson = JSON.parse(errorText);
      } catch (e) {}
      throw new Error(errorJson?.detail || errorText || 'Request failed');
    }

    return await res.json();
  } catch (error) {
    console.error(`API Error on ${endpoint}:`, error);
    throw error;
  } finally {
    updateLoading(-1);
  }
}

export const api = {
  // Auth
  auth: {
    login: async (email, password) => {
      const res = await request('/auth/login', {
        method: 'POST',
        body: { email, password }
      });
      if (res.access_token) {
        localStorage.setItem('dt_token', res.access_token);
        // Simple decode JWT to get user_id & email
        try {
          const payload = JSON.parse(atob(res.access_token.split('.')[1]));
          localStorage.setItem('dt_user', JSON.stringify({
            user_id: payload.user_id || payload.sub,
            email: payload.email || email,
            role: payload.role || 'user'
          }));
        } catch (e) {
          localStorage.setItem('dt_user', JSON.stringify({ email, role: 'user' }));
        }
      }
      return res;
    },
    register: async (fullName, email, password) => {
      return request('/auth/register', {
        method: 'POST',
        body: { full_name: fullName, email, password }
      });
    },
    logout: () => {
      localStorage.removeItem('dt_token');
      localStorage.removeItem('dt_user');
      window.dispatchEvent(new CustomEvent('api-auth-error'));
    },
    getCurrentUser: () => {
      try {
        return JSON.parse(localStorage.getItem('dt_user'));
      } catch (e) {
        return null;
      }
    },
    getUserFullName: async () => {
      const res = await request('/auth/fullname');
      return res;
    }
  },

  // Health Profile
  healthProfile: {
    get: async () => request('/health-profile/'),
    create: async (profile) => request('/health-profile/', { method: 'POST', body: profile }),
    update: async (profile) => request('/health-profile/', { method: 'PUT', body: profile }),
  },

  // Health Docs & Data
  healthDocs: {
    upload: async (file, noteText) => {
      const formData = new FormData();
      if (file) formData.append('file', file);
      if (noteText) formData.append('note', noteText);
      return request('/health-docs/upload', {
        method: 'POST',
        body: formData
      });
    },
    reports: async () => request('/health-docs/reports'),
    dashboard: async () => request('/health-docs/dashboard'),
    analyze: async (file, noteText) => {
      const formData = new FormData();
      if (file) formData.append('file', file);
      if (noteText) formData.append('note', noteText);
      // Wait, there's health-agent/analyze or health-docs/analyze
      // We will support both, but instruction says health-agent/analyze is used for uploads
      return request('/health-agent/analyze', {
        method: 'POST',
        body: formData
      });
    },
    ask: async (question) => request('/health-agent/ask', {
      method: 'POST',
      body: { question }
    }),
    trends: async () => request('/health-trends/'),
  },

  // Action Agent
  action: {
    execute: async (query) => request('/action/execute', {
      method: 'POST',
      body: { query }
    }),
    executeIntent: async (intent) => request('/action/execute-intent', {
      method: 'POST',
      body: intent
    }),
    // Emails
    emails: {
      inbox: async (query) => request(`/action/emails/inbox${query ? `?query=${encodeURIComponent(query)}` : ''}`),
      draft: async (to, topic, messageDetails, styleName) => request('/action/emails/draft', {
        method: 'POST',
        body: { to, topic, message_details: messageDetails, style_name: styleName }
      }),
      drafts: async () => request('/action/emails/drafts'),
      getDraft: async (id) => request(`/action/emails/drafts/${id}`),
      updateDraft: async (id, to, subject, body) => request(`/action/emails/drafts/${id}`, {
        method: 'PUT',
        body: { to, subject, body }
      }),
      deleteDraft: async (id) => request(`/action/emails/drafts/${id}`, {
        method: 'DELETE'
      }),
      send: async (to, subject, body) => request('/action/emails/send', {
        method: 'POST',
        body: { to, subject, body }
      }),
      sendEnhanced: async (to, subject, body, queryRequest, styleName) => request('/action/emails/send-enhanced', {
        method: 'POST',
        body: { to, subject, body, query_request: queryRequest, style_name: styleName }
      }),
      sent: async () => request('/action/emails/sent'),
    },
    // Calendar
    calendar: {
      events: async (startTime, endTime) => {
        let params = [];
        if (startTime) params.push(`startTime=${encodeURIComponent(startTime)}`);
        if (endTime) params.push(`endTime=${encodeURIComponent(endTime)}`);
        const queryStr = params.length ? `?${params.join('&')}` : '';
        return request(`/action/calendar/events${queryStr}`);
      },
      createEvent: async (title, start, end, description) => request('/action/calendar/events', {
        method: 'POST',
        body: { title, start, end, description }
      }),
      updateEvent: async (id, event) => request(`/action/calendar/events/${id}`, {
        method: 'PUT',
        body: event
      }),
      deleteEvent: async (id) => request(`/action/calendar/events/${id}`, {
        method: 'DELETE'
      }),
    },
    // Notifications
    notifications: {
      list: async () => request('/action/notifications'),
      create: async (message, level = 'info') => request('/action/notifications', {
        method: 'POST',
        body: { message, level }
      }),
    },
    // Style Profile
    style: {
      getManual: async () => request('/action/style-profile'),
      saveManual: async (profile) => request('/action/style-profile', {
        method: 'POST',
        body: profile
      }),
      generate: async () => request('/action/style/generate', {
        method: 'POST'
      }),
      profiles: async () => request('/action/style/profiles'),
      deleteProfile: async (name) => request(`/action/style/profiles/${encodeURIComponent(name)}`, {
        method: 'DELETE'
      }),
    },
    // Recommendations
    recommendations: async () => request('/action/proactive/recommendations'),
    // Google Integration
    google: {
      status: async () => request('/action/google/status'),
      connect: async (redirectUrl) => request(`/action/google/connect${redirectUrl ? `?redirect_url=${encodeURIComponent(redirectUrl)}` : ''}`),
      disconnect: async () => request('/action/google/disconnect',{method: 'POST'}),
    }
  }
};
