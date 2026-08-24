/**
 * VANGUARD / AETHER — Meta-Harness Studio Frontend
 * Zero-dependency, high-performance UI client for composing, running,
 * and inspecting recursive-agency episodes.
 */

// Mock/Default State representing Vanguard runtime entities
const STATE = {
  activeTab: 'harness-tab',
  selectedPack: 'vg-code-default',
  selectedProfile: 'local',
  packs: {
    'vg-code-default': {
      id: 'vg-code-default',
      api: 'mhf.manifest/2',
      digest: 'sha256:4f8e91a27b848c7719c83602ab9273619280d52b6192bbfae0918c82b1328901',
      systemPrompt: `You are an autonomous senior software engineer operating within the Vanguard substrate.
Your task is to inspect the workspace, analyze failing tests or feature requests, formulate an execution plan, and apply minimal verified patches.
Always verify effect receipts before issuing follow-up edits. Never attempt actions outside your granted capabilities.`,
      components: [
        { name: 'planner', spi: 'IPlanner', role: 'Drive-Until-Green', isolation: 'in_process', status: 'ready' },
        { name: 'context', spi: 'IContextManager', role: 'Repo-Map + Compaction', isolation: 'in_process', status: 'ready' },
        { name: 'toolkit', spi: 'IToolkit', role: 'Filesystem + Patch + Exec', isolation: 'in_process', status: 'ready' },
        { name: 'evaluation', spi: 'IEvaluationGate', role: 'Coding-Oracle@3', isolation: 'subprocess', status: 'ready' },
        { name: 'memory', spi: 'IMemoryEngine', role: 'SQLite-KV + Evidence-Memo', isolation: 'in_process', status: 'ready' }
      ],
      capabilities: [
        { verb: 'fs.read', sink: 'observation', risk: 'low', selector: 'fs:/workspace', isolation: 'in_process' },
        { verb: 'fs.search', sink: 'observation', risk: 'low', selector: 'fs:/workspace', isolation: 'in_process' },
        { verb: 'patch.apply', sink: 'privileged', risk: 'medium', selector: 'fs:/workspace', isolation: 'in_process' },
        { verb: 'proc.exec', sink: 'privileged', risk: 'high', selector: 'proc://exec/allow/git,pytest,ruff,python3', isolation: 'container' }
      ],
      budget: {
        usd_micros: 250000,
        millis: 1800000,
        tokens: 64000,
        turns: 40
      }
    },
    'vg-code-explain': {
      id: 'vg-code-explain',
      api: 'mhf.manifest/2',
      digest: 'sha256:77bc09916dae988273901bca28e1892837482910fae829188091728371982736',
      systemPrompt: `You are an expert codebase comprehension and explanation agent.
Analyze the codebase thoroughly and answer the user's inquiry accurately.
You have read-only access to inspect files, search symbols, and examine repository structure.
Never attempt to modify files or execute arbitrary shell commands.
Explain code structure, control flow, design decisions, and potential issues clearly.`,
      components: [
        { name: 'context', spi: 'IContextManager', role: 'Repo-Map + Compaction', isolation: 'in_process', status: 'ready' },
        { name: 'toolkit', spi: 'IToolkit', role: 'Read-Only Filesystem', isolation: 'in_process', status: 'ready' },
        { name: 'memory', spi: 'IMemoryEngine', role: 'SQLite-KV Cache', isolation: 'in_process', status: 'ready' }
      ],
      capabilities: [
        { verb: 'fs.read', sink: 'observation', risk: 'low', selector: 'fs:/workspace', isolation: 'in_process' },
        { verb: 'fs.search', sink: 'observation', risk: 'low', selector: 'fs:/workspace', isolation: 'in_process' }
      ],
      budget: {
        usd_micros: 100000,
        millis: 600000,
        tokens: 32000,
        turns: 15
      }
    }
  },
  turns: [
    {
      turn: 1,
      model: 'deepseek/deepseek-v4-flash',
      action: 'fs.read',
      args: { path: 'calc.py' },
      status: 'executed',
      latency: '240ms',
      cost: '$0.0004'
    },
    {
      turn: 2,
      model: 'deepseek/deepseek-v4-flash',
      action: 'patch.apply',
      args: { path: 'calc.py', diff: '@@ -10,3 +10,3 @@\n- return a - b\n+ return a + b' },
      status: 'approval_required',
      latency: '310ms',
      cost: '$0.0007'
    }
  ],
  dispatchStages: [
    { stage: 'S0', name: 'Observe', desc: 'Read environmental signals & construct justification span.' },
    { stage: 'S1', name: 'Classify & Route', desc: 'StandardClassifier categorizes intent into Pure, Observation, or Privileged.' },
    { stage: 'S2', name: 'Scope & Ceilings', desc: 'Evaluate Monotonic Attenuation against active capability grant.' },
    { stage: 'S3', name: 'Reserve Budget', desc: 'Typed reservation across USD micros, tokens, and wall-clock time.' },
    { stage: 'S4', name: 'Policy Authority', desc: 'Fail-closed rule evaluation (deny unknown verbs or resource escapes).' },
    { stage: 'S5', name: 'Approval Gate', desc: 'Descriptor-bound operator signature verification (K-14).' },
    { stage: 'S6', name: 'Effect Pre-flight', desc: 'Pre-flight dry run and worktree collision isolation check.' },
    { stage: 'S7', name: 'Dispatch Execution', desc: 'Forward call to concrete environment / sandbox adapter.' },
    { stage: 'S8', name: 'Observe Point of Effect', desc: 'Capture SHA-256 post-digest and standard output streams.' },
    { stage: 'S9', name: 'Settle Budget', desc: 'Calculate actual resource delta and refund unused reservation.' },
    { stage: 'S10', name: 'Append Event', desc: 'Emit single-writer append-only event to SQLite-WAL ledger.' },
    { stage: 'S11', name: 'Evaluate Gate', desc: 'Exterior Ed25519 oracle evaluation (if hermetic/active).' },
    { stage: 'S12', name: 'Reconcile & Yield', desc: 'Return typed AdapterOutcome to EpisodeEngine turn loop.' }
  ],
  evidenceRows: [
    { row: 1, category: 'Model & Usage', proof: 'OpenRouter live invocation; 1,500 tokens recorded.', status: 'verified' },
    { row: 2, category: 'Grant & Budget', proof: 'Reservation matching descriptor grant:fs:read+patch:apply.', status: 'verified' },
    { row: 3, category: 'Point of Effect', proof: 'Pre/Post SHA-256 state delta captured on calc.py.', status: 'verified' },
    { row: 4, category: 'Containment Attestation', proof: 'Bubblewrap rootless probe (mount, egress, syscall denials).', status: 'verified' },
    { row: 5, category: 'Evaluation Signature', proof: 'Ed25519 verdict signed by UID 10002 evaluator daemon.', status: 'verified' },
    { row: 6, category: 'SQLite-WAL Lineage', proof: 'WAL journal mode verified; continuous prev_digest chain.', status: 'verified' },
    { row: 7, category: 'Trajectory Integrity', proof: 'Canonical mhf.trajectory/1 matches run_digest.', status: 'verified' },
    { row: 8, category: 'Preregistration Binding', proof: 'Immutable task & oracle pre-digest cross-signed before Turn 1.', status: 'verified' },
    { row: 9, category: 'Outcome Attribution', proof: 'Goal achieved without human-in-the-loop repair.', status: 'verified' }
  ]
};

// DOM Initialization
document.addEventListener('DOMContentLoaded', () => {
  renderPackList();
  renderHarnessDetails();
  renderLiveTurns();
  renderDispatchStages();
  renderEvidenceTable();
});

// Tab Switching
function switchTab(tabId) {
  STATE.activeTab = tabId;
  document.querySelectorAll('.tab-pane').forEach(el => el.classList.add('hidden'));
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.classList.remove('bg-card', 'text-accent');
    btn.classList.add('text-gray-400');
  });

  const activePane = document.getElementById(tabId);
  if (activePane) activePane.classList.remove('hidden');

  const activeBtn = document.getElementById(`nav-${tabId}`);
  if (activeBtn) {
    activeBtn.classList.add('bg-card', 'text-accent');
    activeBtn.classList.remove('text-gray-400');
  }
}

// Render Packs List
function renderPackList() {
  const container = document.getElementById('pack-list');
  container.innerHTML = '';

  Object.values(STATE.packs).forEach(pack => {
    const isSelected = pack.id === STATE.selectedPack;
    const item = document.createElement('div');
    item.className = `p-3 rounded-lg border cursor-pointer transition ${
      isSelected 
        ? 'bg-card border-accent text-white glow-accent' 
        : 'bg-panel border-border text-gray-400 hover:border-gray-600'
    }`;
    item.onclick = () => {
      STATE.selectedPack = pack.id;
      renderPackList();
      renderHarnessDetails();
    };

    item.innerHTML = `
      <div class="flex items-center justify-between mb-1">
        <span class="font-mono font-bold text-xs text-cyan-300">${pack.id}</span>
        <span class="badge ${isSelected ? 'bg-cyan-950 text-cyan-400 border border-cyan-800' : 'bg-canvas text-gray-500'}">v2</span>
      </div>
      <div class="text-[11px] text-gray-400 line-clamp-2">${pack.systemPrompt}</div>
    `;
    container.appendChild(item);
  });
}

// Render Harness Details View
function renderHarnessDetails() {
  const pack = STATE.packs[STATE.selectedPack];
  if (!pack) return;

  document.getElementById('current-harness-id').textContent = pack.id;
  document.getElementById('current-harness-digest').textContent = `D_H: ${pack.digest.slice(0, 18)}...`;
  document.getElementById('harness-system-prompt').textContent = pack.systemPrompt;

  // SPI Components
  const spiContainer = document.getElementById('spi-component-cards');
  spiContainer.innerHTML = '';
  pack.components.forEach(comp => {
    const card = document.createElement('div');
    card.className = 'bg-panel border border-border rounded-lg p-3 space-y-1.5';
    card.innerHTML = `
      <div class="flex items-center justify-between">
        <span class="font-mono font-bold text-xs text-sky-300">${comp.name}</span>
        <span class="badge bg-emerald-950 text-emerald-400 border border-emerald-800">${comp.status}</span>
      </div>
      <div class="text-[11px] text-gray-400 font-mono">${comp.spi}</div>
      <div class="text-[10px] text-gray-500 flex justify-between">
        <span>Role: ${comp.role}</span>
        <span>${comp.isolation}</span>
      </div>
    `;
    spiContainer.appendChild(card);
  });

  // Capability Ceilings Table
  const tableBody = document.getElementById('capability-table-body');
  tableBody.innerHTML = '';
  pack.capabilities.forEach(cap => {
    const row = document.createElement('tr');
    row.className = 'hover:bg-panel/50 transition';
    const riskBadge = cap.risk === 'high' 
      ? 'bg-rose-950 text-rose-400 border border-rose-800'
      : cap.risk === 'medium'
      ? 'bg-amber-950 text-amber-400 border border-amber-800'
      : 'bg-emerald-950 text-emerald-400 border border-emerald-800';

    row.innerHTML = `
      <td class="py-2.5 px-4 font-bold text-cyan-300">${cap.verb}</td>
      <td class="py-2.5 px-4 text-gray-300">${cap.sink}</td>
      <td class="py-2.5 px-4"><span class="badge ${riskBadge}">${cap.risk}</span></td>
      <td class="py-2.5 px-4 text-gray-400 font-mono text-[11px]">${cap.selector}</td>
      <td class="py-2.5 px-4 text-gray-500">${cap.isolation}</td>
    `;
    tableBody.appendChild(row);
  });

  // Budgets
  const budgetContainer = document.getElementById('budget-meters');
  budgetContainer.innerHTML = `
    <div class="bg-panel border border-border p-3 rounded">
      <div class="text-gray-400 text-[10px] uppercase">USD Limit</div>
      <div class="text-sm font-bold text-emerald-400">$${(pack.budget.usd_micros / 1000000).toFixed(2)}</div>
    </div>
    <div class="bg-panel border border-border p-3 rounded">
      <div class="text-gray-400 text-[10px] uppercase">Max Wall-Clock</div>
      <div class="text-sm font-bold text-sky-400">${pack.budget.millis / 1000}s</div>
    </div>
    <div class="bg-panel border border-border p-3 rounded">
      <div class="text-gray-400 text-[10px] uppercase">Token Ceiling</div>
      <div class="text-sm font-bold text-purple-400">${pack.budget.tokens.toLocaleString()}</div>
    </div>
    <div class="bg-panel border border-border p-3 rounded">
      <div class="text-gray-400 text-[10px] uppercase">Turn Depth</div>
      <div class="text-sm font-bold text-amber-400">${pack.budget.turns} Turns</div>
    </div>
  `;
}

// Render Live Turns & Feed
function renderLiveTurns() {
  const turnList = document.getElementById('turn-timeline-list');
  turnList.innerHTML = '';
  STATE.turns.forEach(t => {
    const el = document.createElement('div');
    el.className = 'p-3 bg-panel border border-border rounded text-xs space-y-1';
    el.innerHTML = `
      <div class="flex justify-between items-center font-bold">
        <span class="text-sky-400">Turn ${t.turn}</span>
        <span class="badge ${t.status === 'executed' ? 'bg-emerald-950 text-emerald-400' : 'bg-amber-950 text-amber-400'}">${t.status}</span>
      </div>
      <div class="font-mono text-gray-300">${t.action}</div>
      <div class="text-[10px] text-gray-500 flex justify-between">
        <span>${t.latency}</span>
        <span>${t.cost}</span>
      </div>
    `;
    turnList.appendChild(el);
  });

  const eventStream = document.getElementById('live-event-stream');
  eventStream.innerHTML = `
    <div class="p-3 bg-panel border border-border rounded">
      <span class="text-emerald-400">[00:00:01] EpisodeStarted:</span>
      <span class="text-gray-300">Initialized harness <code>${STATE.selectedPack}</code> under <code>${STATE.selectedProfile}</code> profile.</span>
    </div>
    <div class="p-3 bg-panel border border-border rounded">
      <span class="text-sky-400">[00:00:02] ModelInvoked:</span>
      <span class="text-gray-300">Prompting <code>deepseek/deepseek-v4-flash</code> with L1-L5 compiled context.</span>
    </div>
    <div class="p-3 bg-panel border border-border rounded">
      <span class="text-amber-400">[00:00:03] S5_ApprovalRequired:</span>
      <span class="text-gray-300">Privileged action <code>patch.apply</code> requested on <code>src/calc.py</code>. Awaiting operator signature.</span>
    </div>
  `;
}

// Render S0-S12 Kernel Pipeline
function renderDispatchStages() {
  const container = document.getElementById('dispatch-stages-grid');
  container.innerHTML = '';
  STATE.dispatchStages.forEach((s, idx) => {
    const card = document.createElement('div');
    card.className = 'bg-panel border border-border rounded-lg p-3.5 flex items-start space-x-3';
    card.innerHTML = `
      <div class="w-8 h-8 rounded bg-card border border-border flex items-center justify-center font-mono font-bold text-xs text-sky-400 shrink-0">
        ${s.stage}
      </div>
      <div>
        <div class="font-bold text-xs text-gray-200">${s.name}</div>
        <div class="text-[11px] text-gray-400 font-mono mt-0.5">${s.desc}</div>
      </div>
    `;
    container.appendChild(card);
  });
}

// Render Evidence 9-Rows Table
function renderEvidenceTable() {
  const tbody = document.getElementById('evidence-rows-body');
  tbody.innerHTML = '';
  STATE.evidenceRows.forEach(row => {
    const tr = document.createElement('tr');
    tr.className = 'hover:bg-panel/50 transition';
    tr.innerHTML = `
      <td class="py-2.5 px-4 font-bold text-sky-400">#0${row.row}</td>
      <td class="py-2.5 px-4 text-gray-200">${row.category}</td>
      <td class="py-2.5 px-4 text-gray-400 font-mono text-[11px]">${row.proof}</td>
      <td class="py-2.5 px-4"><span class="badge bg-emerald-950 text-emerald-400 border border-emerald-800">${row.status}</span></td>
    `;
    tbody.appendChild(tr);
  });
}

function updateSelectedProfile() {
  STATE.selectedProfile = document.getElementById('execution-profile-selector').value;
}

function renderJsonManifest() {
  const pack = STATE.packs[STATE.selectedPack];
  alert(JSON.stringify(pack, null, 2));
}
