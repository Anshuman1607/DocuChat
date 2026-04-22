const API = 'http://localhost:8000';


const uploadZone   = document.getElementById('uploadZone');
const uploadInner  = document.getElementById('uploadInner');
const uploadProgress = document.getElementById('uploadProgress');
const progressFill = document.getElementById('progressFill');
const progressLabel= document.getElementById('progressLabel');
const fileInput    = document.getElementById('fileInput');
const browseBtn    = document.getElementById('browseBtn');
const docsList     = document.getElementById('docsList');
const docsCount    = document.getElementById('docsCount');
const statusDot    = document.getElementById('statusDot');
const statusLabel  = document.getElementById('statusLabel');
const chatArea     = document.getElementById('chatArea');
const welcome      = document.getElementById('welcome');
const questionInput= document.getElementById('questionInput');
const sendBtn      = document.getElementById('sendBtn');
const clearBtn     = document.getElementById('clearBtn');
const toast        = document.getElementById('toast');

// ── TOAST ──
let toastTimer;
function showToast(msg, type = '') {
  clearTimeout(toastTimer);
  toast.textContent = msg;
  toast.className = 'toast show ' + type;
  toastTimer = setTimeout(() => { toast.className = 'toast'; }, 3200);
}


async function checkHealth() {
  try {
    const r = await fetch(`${API}/health`);
    const d = await r.json();
    if (d.qdrant === 'connected') {
      statusDot.className = 'status-dot online';
      statusLabel.textContent = 'API connected';
    } else {
      statusDot.className = 'status-dot offline';
      statusLabel.textContent = 'Qdrant offline';
    }
  } catch {
    statusDot.className = 'status-dot offline';
    statusLabel.textContent = 'API offline';
  }
}


async function loadDocuments() {
  try {
    const r = await fetch(`${API}/documents`);
    const d = await r.json();
    const docs = d.documents || [];
    docsCount.textContent = docs.length;

    if (docs.length === 0) {
      docsList.innerHTML = '<li class="docs-empty">No documents yet</li>';
      return;
    }

    docsList.innerHTML = docs.map(doc => `
      <li class="doc-item">
        <span class="doc-icon">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <polyline points="14 2 14 8 20 8"/>
          </svg>
        </span>
        <span class="doc-name" title="${doc.filename}">${doc.filename}</span>
        <button class="doc-delete" onclick="deleteDoc('${doc.filename}')" title="Delete">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </button>
      </li>
    `).join('');
  } catch {
    showToast('Could not load documents', 'error');
  }
}


async function deleteDoc(filename) {
  try {
    const r = await fetch(`${API}/document/${encodeURIComponent(filename)}`, { method: 'DELETE' });
    if (r.ok) {
      showToast(`Deleted ${filename}`, 'success');
      loadDocuments();
    } else {
      const d = await r.json();
      showToast(d.detail || 'Delete failed', 'error');
    }
  } catch {
    showToast('API not reachable', 'error');
  }
}


function showUploadProgress(label, pct) {
  uploadInner.style.display = 'none';
  uploadProgress.style.display = 'block';
  progressFill.style.width = pct + '%';
  progressLabel.textContent = label;
}

function resetUploadZone() {
  uploadInner.style.display = 'block';
  uploadProgress.style.display = 'none';
  progressFill.style.width = '0%';
  fileInput.value = '';
}

async function uploadFile(file) {
  if (!file) return;
  if (!file.name.endsWith('.pdf')) { showToast('Only PDF files are allowed', 'error'); return; }

  showUploadProgress('Reading file…', 15);

  const formData = new FormData();
  formData.append('file', file);

  try {
    showUploadProgress('Uploading…', 40);
    const r = await fetch(`${API}/upload`, { method: 'POST', body: formData });
    showUploadProgress('Processing chunks…', 75);
    const d = await r.json();

    if (r.ok) {
      showUploadProgress('Done!', 100);
      setTimeout(() => {
        resetUploadZone();
        if (d.message && d.message.toLowerCase().includes('already')) {
          showToast(`${file.name} already uploaded`, '');
        } else {
          showToast(`${file.name} · ${d.chunks} chunks indexed`, 'success');
        }
        loadDocuments();
      }, 600);
    } else {
      resetUploadZone();
      showToast(d.detail || 'Upload failed', 'error');
    }
  } catch {
    resetUploadZone();
    showToast('API not reachable', 'error');
  }
}


uploadZone.addEventListener('dragover', e => { e.preventDefault(); uploadZone.classList.add('drag-over'); });
uploadZone.addEventListener('dragleave', () => uploadZone.classList.remove('drag-over'));
uploadZone.addEventListener('drop', e => {
  e.preventDefault();
  uploadZone.classList.remove('drag-over');
  const file = e.dataTransfer.files[0];
  uploadFile(file);
});
uploadZone.addEventListener('click', () => fileInput.click());
browseBtn.addEventListener('click', e => { e.stopPropagation(); fileInput.click(); });
fileInput.addEventListener('change', () => uploadFile(fileInput.files[0]));


function hideWelcome() {
  if (welcome) welcome.style.display = 'none';
}

function appendMessage(role, text, sources) {
  hideWelcome();

  const wrap = document.createElement('div');
  wrap.className = `msg msg-${role}`;

  const roleLabel = document.createElement('div');
  roleLabel.className = 'msg-role';
  roleLabel.textContent = role === 'user' ? 'You' : 'DocuChat';

  const bubble = document.createElement('div');
  bubble.className = 'msg-bubble';
  bubble.textContent = text;

  wrap.appendChild(roleLabel);
  wrap.appendChild(bubble);

  if (role === 'bot' && sources && sources.length > 0) {
    const toggle = document.createElement('button');
    toggle.className = 'sources-toggle';
    toggle.innerHTML = `
      <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
        <polyline points="9 18 15 12 9 6"/>
      </svg>
      ${sources.length} source${sources.length > 1 ? 's' : ''}
    `;

    const sourcesList = document.createElement('div');
    sourcesList.className = 'sources-list';

    sources.forEach(src => {
      const card = document.createElement('div');
      card.className = 'source-card';

      const filename = (src.source || '').split(/[\\/]/).pop();
      const page = src.page != null ? `p. ${src.page + 1}` : '';

      card.innerHTML = `
        <div class="source-meta">
          <span class="source-file">${filename}</span>
          ${page ? `<span class="source-page">${page}</span>` : ''}
        </div>
        <div class="source-content">${src.content || ''}</div>
      `;
      sourcesList.appendChild(card);
    });

    toggle.addEventListener('click', () => {
      const open = sourcesList.classList.toggle('visible');
      toggle.classList.toggle('open', open);
    });

    wrap.appendChild(toggle);
    wrap.appendChild(sourcesList);
  }

  chatArea.appendChild(wrap);
  chatArea.scrollTop = chatArea.scrollHeight;
}

function appendTyping() {
  const wrap = document.createElement('div');
  wrap.className = 'msg msg-bot';
  wrap.id = 'typingMsg';

  const roleLabel = document.createElement('div');
  roleLabel.className = 'msg-role';
  roleLabel.textContent = 'DocuChat';

  const bubble = document.createElement('div');
  bubble.className = 'msg-bubble';
  bubble.innerHTML = `<div class="typing"><span></span><span></span><span></span></div>`;

  wrap.appendChild(roleLabel);
  wrap.appendChild(bubble);
  chatArea.appendChild(wrap);
  chatArea.scrollTop = chatArea.scrollHeight;
}

function removeTyping() {
  const t = document.getElementById('typingMsg');
  if (t) t.remove();
}

async function sendQuestion() {
  const q = questionInput.value.trim();
  if (!q) return;

  appendMessage('user', q);
  questionInput.value = '';
  questionInput.style.height = 'auto';
  sendBtn.disabled = true;
  appendTyping();

  try {
    const r = await fetch(`${API}/ask`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: q })
    });

    const d = await r.json();
    removeTyping();

    if (r.ok) {
      appendMessage('bot', d.answer, d.sources);
    } else {
      appendMessage('bot', d.detail || 'Something went wrong.', []);
    }
  } catch {
    removeTyping();
    appendMessage('bot', 'Could not reach the API. Make sure the server is running.', []);
  }

  sendBtn.disabled = false;
  chatArea.scrollTop = chatArea.scrollHeight;
}


questionInput.addEventListener('input', () => {
  questionInput.style.height = 'auto';
  questionInput.style.height = Math.min(questionInput.scrollHeight, 140) + 'px';
});

questionInput.addEventListener('keydown', e => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendQuestion();
  }
});

sendBtn.addEventListener('click', sendQuestion);


clearBtn.addEventListener('click', () => {
  chatArea.innerHTML = '';
  chatArea.appendChild(welcome);
  welcome.style.display = 'flex';
  welcome.style.flexDirection = 'column';
});


checkHealth();
loadDocuments();
setInterval(checkHealth, 30000);