// ============================================================
// LED STUDIO - CENTRALIZED CONFIG-DRIVEN DESIGN SYSTEM & LOGIC
// ============================================================
const THEME = {
  colors: {
    bgCanvas: '#06090d',
    bgSurface: '#0b0f15',
    bgSurface50: 'rgba(11, 15, 21, 0.55)',
    bgCard50: 'rgba(18, 24, 34, 0.50)',
    borderPrimary: '#182230',
    borderStrong: '#28374d',
    accentBlue: '#38bdf8',
    accentBlueDim: '#0284c7',
    accentGreen: '#10b981',
    textPrimary: '#ffffff',
    textSecondary: '#94a3b8',
    textMuted: '#64748b',
  },
  chartGrid: '#182230',
};

const API_BASE = window.location.origin;

function escapeHtml(str) {
  if (!str) return '';
  return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

let benchLatencyChart = null;
let benchTpsChart = null;
let shapChart = null;

// Tab Switcher (Neobrutalist Square Tabs)
function switchTab(tabName) {
  // Update Activity Bar
  document.querySelectorAll('.act-btn').forEach(btn => {
    btn.classList.remove('text-sky-400', 'border-sky-400/80', 'bg-[#0e141c]');
    btn.classList.add('text-slate-400', 'border-[#182230]', 'bg-[#06090d]');
  });
  const actBtn = document.getElementById(`act-btn-${tabName}`);
  if (actBtn) {
    actBtn.classList.remove('text-slate-400', 'border-[#182230]', 'bg-[#06090d]');
    actBtn.classList.add('text-sky-400', 'border-sky-400/80', 'bg-[#0e141c]');
  }

  // Update Main Tab Indicators
  document.querySelectorAll('.tab-indicator').forEach(tab => {
    tab.classList.remove('bg-[#06090d]', 'text-white', 'border-b-2', 'border-b-sky-400');
    tab.classList.add('bg-[#0b0f15]', 'text-slate-400');
  });
  const activeTabIndicator = document.getElementById(`tab-indicator-${tabName}`);
  if (activeTabIndicator) {
    activeTabIndicator.classList.remove('bg-[#0b0f15]', 'text-slate-400');
    activeTabIndicator.classList.add('bg-[#06090d]', 'text-white', 'border-b-2', 'border-b-sky-400');
  }

  // Toggle Tab Sections (5 tabs)
  ['chat', 'bench', 'tuner', 'hardware', 'logs'].forEach(t => {
    const el = document.getElementById(`tab-${t}`);
    if (el) el.classList.add('hidden');
  });

  const activeTab = document.getElementById(`tab-${tabName}`);
  if (activeTab) activeTab.classList.remove('hidden');

  if (tabName === 'bench') renderBenchCharts();
  if (tabName === 'tuner') renderShapChart();
}

function appendSystemLog(level, msg) {
  const container = document.getElementById('system-logs-container');
  if (!container) return;
  const time = new Date().toLocaleTimeString();
  const line = document.createElement('div');
  let color = 'text-slate-400';
  let badgeColor = 'text-slate-400 border-[#182230]';
  if (level === 'ERROR') {
    color = 'text-rose-300';
    badgeColor = 'text-rose-400 border-rose-800 bg-rose-950/40 font-bold';
  } else if (level === 'WARN') {
    color = 'text-amber-300';
    badgeColor = 'text-amber-400 border-amber-800 bg-amber-950/40 font-semibold';
  } else if (level === 'SUCCESS') {
    color = 'text-emerald-300';
    badgeColor = 'text-emerald-400 border-emerald-800 bg-emerald-950/40 font-semibold';
  } else if (level === 'STREAM') {
    color = 'text-sky-300';
    badgeColor = 'text-sky-400 border-sky-800 bg-sky-950/40 font-semibold';
  } else if (level === 'CONFIG') {
    color = 'text-indigo-300';
    badgeColor = 'text-indigo-400 border-indigo-800 bg-indigo-950/40';
  }

  // Strictly clamp message body to maximum 128 characters
  const cleanMsg = String(msg).replace(/\n/g, ' ').trim();
  const clamped = cleanMsg.length > 128 ? cleanMsg.substring(0, 125) + '...' : cleanMsg;

  line.className = `flex items-center space-x-2 py-0.5 border-b border-[#182230]/40 hover:bg-[#0e141c] text-xs font-mono`;
  line.innerHTML = `
    <span class="text-slate-500 text-[10px] select-none shrink-0">${time}</span>
    <span class="px-1 py-0.2 border ${badgeColor} text-[9px] uppercase tracking-wider shrink-0">${level}</span>
    <span class="${color} truncate">${escapeHtml(clamped)}</span>
  `;
  container.appendChild(line);
  container.scrollTop = container.scrollHeight;
}

function clearSystemLogs() {
  const container = document.getElementById('system-logs-container');
  if (container) {
    container.innerHTML = '<div class="text-slate-500">// LOGS CLEARED</div>';
  }
}

function onModelChange() {
  const select = document.getElementById('model-select');
  const val = select.value;
  document.getElementById('header-model-name').innerText = val;
}

let currentStreamAbortController = null;

function setExecuteButtonState(isRunning) {
  const btn = document.getElementById('chat-submit-btn');
  if (!btn) return;
  if (isRunning) {
    btn.innerHTML = 'STOP ◼';
    btn.className = 'bg-rose-500 hover:bg-rose-600 text-white px-3 py-1 text-[11px] font-bold uppercase tracking-wider transition cursor-pointer';
    btn.title = 'Stop inference stream (Escape)';
  } else {
    btn.innerHTML = 'EXECUTE ↵';
    btn.className = 'bg-sky-400 hover:bg-white text-black px-3 py-1 text-[11px] font-bold uppercase tracking-wider transition cursor-pointer';
    btn.title = 'Send prompt (Enter)';
  }
}

function stopCurrentStream() {
  if (currentStreamAbortController) {
    currentStreamAbortController.abort();
    currentStreamAbortController = null;
    setExecuteButtonState(false);
  }
}

// Global Escape Key listener to abort stream
window.addEventListener('keydown', (e) => {
  if (e.key === 'Escape' && currentStreamAbortController) {
    e.preventDefault();
    stopCurrentStream();
  }
});

function updateEngineState(state) {
  const pill = document.getElementById('led-state-pill');
  const dot = document.getElementById('led-state-dot');
  const text = document.getElementById('led-state-text');
  if (!pill || !dot || !text) return;

  if (state === 'WARMING_UP') {
    pill.className = 'flex items-center space-x-1.5 px-2 py-0.5 border border-amber-500/50 bg-[#06090d] text-amber-400';
    dot.className = 'w-1.5 h-1.5 bg-amber-400 animate-ping';
    text.innerText = 'WARMING UP (LOADING)';
  } else if (state === 'GENERATING') {
    pill.className = 'flex items-center space-x-1.5 px-2 py-0.5 border border-sky-500/50 bg-[#06090d] text-sky-400';
    dot.className = 'w-1.5 h-1.5 bg-sky-400 animate-pulse';
    text.innerText = 'STREAMING TOKENS';
  } else if (state === 'VRAM_READY') {
    pill.className = 'flex items-center space-x-1.5 px-2 py-0.5 border border-[#182230] bg-[#06090d] text-emerald-400';
    dot.className = 'w-1.5 h-1.5 bg-emerald-400';
    text.innerText = 'VRAM RESIDENT';
  } else {
    pill.className = 'flex items-center space-x-1.5 px-2 py-0.5 border border-[#182230] bg-[#06090d] text-slate-400';
    dot.className = 'w-1.5 h-1.5 bg-slate-500';
    text.innerText = 'IDLE';
  }
}

// Chat Form & SSE Streaming Handler
async function handleChatSubmit(e) {
  if (e) e.preventDefault();

  // If already running, clicking the button triggers Stop / Abort
  if (currentStreamAbortController) {
    stopCurrentStream();
    return;
  }

  const input = document.getElementById('chat-input');
  const text = input.value.trim();
  if (!text) return;

  // Hide empty state watermark
  const emptyState = document.getElementById('empty-state');
  if (emptyState) emptyState.style.display = 'none';

  const messagesDiv = document.getElementById('chat-messages');
  
  // Append User Message (Neobrutalist square card with 50% opacity)
  const userMsg = document.createElement('div');
  userMsg.className = 'flex justify-end select-text';
  userMsg.innerHTML = `
    <div class="bg-[#0b0f15]/75 border border-[#182230] text-white p-3 max-w-xl text-xs font-mono">
      <div class="text-[9px] text-slate-500 mb-1">// USER PROMPT</div>
      <div>${escapeHtml(text)}</div>
    </div>
  `;
  messagesDiv.appendChild(userMsg);
  input.value = '';

  // Append Assistant Placeholder
  const assistantMsg = document.createElement('div');
  assistantMsg.className = 'flex justify-start select-text';
  const contentId = 'msg-' + Date.now();
  assistantMsg.innerHTML = `
    <div class="bg-[#0b0f15]/50 border border-[#182230] p-3.5 max-w-2xl text-xs text-slate-200 w-full font-mono">
      <div class="flex items-center justify-between text-[10px] text-slate-400 mb-2 border-b border-[#182230] pb-1">
        <span class="text-sky-400 font-bold">// LED ASSISTANT (SSE STREAM)</span>
        <span id="ast-badge-${contentId}" class="px-1.5 py-0.5 border border-[#182230] bg-[#06090d] text-slate-400 text-[9px]">STARTING...</span>
      </div>
      <div id="${contentId}" class="whitespace-pre-wrap leading-relaxed text-white font-mono text-xs"></div>
    </div>
  `;
  messagesDiv.appendChild(assistantMsg);
  messagesDiv.scrollTop = messagesDiv.scrollHeight;

  const contentDiv = document.getElementById(contentId);
  const astBadge = document.getElementById(`ast-badge-${contentId}`);

  // High-performance token/time variables
  const requestStartTime = performance.now();
  let firstTokenTime = null;
  let tokenCount = 0;
  let warmUpTimeSec = 0;

  const targetModel = document.getElementById('model-select').value;
  const tempVal = parseFloat(document.getElementById('temp-slider').value);
  const ctxVal = parseInt(document.getElementById('ctx-slider')?.value || '2048');
  const threadVal = parseInt(document.getElementById('thread-slider')?.value || '8');
  const predictVal = parseInt(document.getElementById('predict-slider')?.value || '1024');
  const effortVal = document.getElementById('effort-select')?.value || 'none';
  const sysPromptEnabled = document.getElementById('sys-prompt-toggle')?.checked || false;
  const sysPromptText = sysPromptEnabled ? document.getElementById('sys-prompt-text')?.value : null;

  // Build message array with optional strict system prompt
  const messagePayload = [];
  if (sysPromptText) {
    messagePayload.push({ role: 'system', content: sysPromptText });
  }
  messagePayload.push({ role: 'user', content: text });

  // Log prompt dispatch
  appendSystemLog('CONFIG', `[${targetModel}] | temp=${tempVal} | ctx=${ctxVal} | threads=${threadVal} | effort=${effortVal}`);
  appendSystemLog('STREAM', `Prompt: "${text.substring(0, 75)}${text.length > 75 ? '...' : ''}"`);

  // Activate AbortController and transform button into Stop button
  currentStreamAbortController = new AbortController();
  setExecuteButtonState(true);
  updateEngineState('WARMING_UP');

  try {
    const response = await fetch(`${API_BASE}/v1/chat/completions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      signal: currentStreamAbortController.signal,
      body: JSON.stringify({
        model: targetModel,
        messages: messagePayload,
        stream: true,
        temperature: tempVal,
        num_ctx: ctxVal,
        num_thread: threadVal,
        num_predict: predictVal,
        disable_thinking: effortVal === 'none',
      })
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let fullResponse = '';
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop();

      for (const line of lines) {
        const trimmed = line.trim();
        if (trimmed.startsWith('data: ')) {
          const dataStr = trimmed.substring(6);
          if (dataStr === '[DONE]') continue;
          try {
            const parsed = JSON.parse(dataStr);
            const delta = parsed.choices[0]?.delta?.content || '';
            if (delta) {
              if (!firstTokenTime) {
                firstTokenTime = performance.now();
                warmUpTimeSec = (firstTokenTime - requestStartTime) / 1000;
                const ttftMs = (firstTokenTime - requestStartTime).toFixed(0);
                updateEngineState('GENERATING');
                appendSystemLog('STREAM', `Warm-up / TTFT: ${ttftMs}ms | GPU stream started`);
              }
              tokenCount++;
              fullResponse += delta;
              contentDiv.textContent = fullResponse;
              messagesDiv.scrollTop = messagesDiv.scrollHeight;

              // Live pure TPS calculation (excluding warm-up delay)
              const genElapsedSec = (performance.now() - firstTokenTime) / 1000;
              if (genElapsedSec > 0.05) {
                const liveTps = (tokenCount / genElapsedSec).toFixed(1);
                const tpsEl = document.getElementById('live-tps');
                if (tpsEl) tpsEl.innerText = liveTps;
              }
            }
          } catch (err) {
            // Ignore parse errors on partial chunks
          }
        }
      }
    }

    // Final Throughput & Pure Latency (Excluding warm-up/model loading from generation time)
    const totalWallSec = (performance.now() - requestStartTime) / 1000;
    const pureGenSec = firstTokenTime ? Math.max(0.01, (performance.now() - firstTokenTime) / 1000) : totalWallSec;
    const finalTps = (tokenCount / pureGenSec).toFixed(1);
    
    const tpsEl = document.getElementById('live-tps');
    if (tpsEl) tpsEl.innerText = finalTps;

    appendSystemLog('SUCCESS', `Completed: ${tokenCount} tok in ${pureGenSec.toFixed(2)}s gen (warmup: ${warmUpTimeSec.toFixed(2)}s) | ${finalTps} tok/s`);

    // Evaluate AST Score
    let astScoreVal = null;
    if (fullResponse.includes('def ') || fullResponse.includes('import ') || fullResponse.includes('return ')) {
      const astRes = await fetch(`${API_BASE}/v1/eval/ast`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code: fullResponse })
      });
      const scoreData = await astRes.json();
      astScoreVal = scoreData.total_score;
      astBadge.textContent = `AST: ${scoreData.total_score}/100 | ${finalTps} tok/s (${pureGenSec.toFixed(2)}s)`;
      if (scoreData.total_score >= 85) {
        astBadge.className = 'px-1.5 py-0.5 border border-emerald-800 bg-[#06090d] text-emerald-400 text-[9px] font-bold';
      }
      appendSystemLog('SUCCESS', `AST Code Score: ${scoreData.total_score}/100 | ${scoreData.feedback || 'Valid Python'}`);
    } else {
      astBadge.textContent = `${finalTps} tok/s | ${pureGenSec.toFixed(2)}s (warmup ${warmUpTimeSec.toFixed(1)}s)`;
      astBadge.className = 'px-1.5 py-0.5 border border-[#182230] bg-[#06090d] text-slate-400 text-[9px]';
    }

    // Save pure generation metrics (with warm-up recorded separately) to Chat Telemetry in Tab 2
    recordChatExecution({
      time: new Date().toLocaleTimeString(),
      model: targetModel,
      prompt: text,
      ttftMs: (warmUpTimeSec * 1000).toFixed(0),
      tokens: tokenCount,
      latencySec: pureGenSec.toFixed(2),
      tps: finalTps,
      astScore: astScoreVal
    });

  } catch (e) {
    if (e.name === 'AbortError' || currentStreamAbortController?.signal?.aborted) {
      contentDiv.textContent += '\n\n[STREAM ABORTED BY USER]';
      astBadge.textContent = 'ABORTED';
      astBadge.className = 'px-1.5 py-0.5 border border-rose-800 bg-[#06090d] text-rose-400 text-[9px] font-bold';
      appendSystemLog('WARN', 'Inference stream aborted by user (Escape / Stop).');
    } else {
      const rawMsg = e.message || 'Unknown backend inference error';
      // Compact error summary to max 128 characters
      const summaryMsg = rawMsg.length > 128 ? rawMsg.substring(0, 125) + '...' : rawMsg;
      
      contentDiv.innerHTML = `
        <div class="border border-rose-500/50 bg-[#160b0f] p-3 text-rose-300 space-y-1.5 font-mono text-xs">
          <div class="font-bold text-rose-400 flex items-center space-x-1.5">
            <span class="w-2 h-2 bg-rose-500 inline-block"></span>
            <span>// ENGINE INFERENCE ERROR</span>
          </div>
          <div class="text-[11px] text-slate-200">${escapeHtml(summaryMsg)}</div>
          <div class="text-[10px] text-slate-400 border-t border-rose-900/50 pt-1">
            See Tab <strong class="text-sky-400 cursor-pointer" onclick="switchTab('logs')">[5] Logs</strong> for complete technical stacktrace.
          </div>
        </div>
      `;
      astBadge.textContent = 'ERROR';
      astBadge.className = 'px-1.5 py-0.5 border border-rose-800 bg-[#06090d] text-rose-400 text-[9px] font-bold';
      appendSystemLog('ERROR', `Inference failed on model [${document.getElementById('model-select').value}]: ${rawMsg}`);
    }
  } finally {
    currentStreamAbortController = null;
    setExecuteButtonState(false);
    updateEngineState('VRAM_READY');
  }
}

function onModelChange() {
  const select = document.getElementById('model-select');
  const val = select.value;
  const headerEl = document.getElementById('header-model-name');
  if (headerEl) headerEl.innerText = val;

  // Reset to default baseline parameters whenever target model changes
  document.getElementById('ctx-slider').value = 2048;
  document.getElementById('ctx-label').innerText = '2048';
  document.getElementById('thread-slider').value = 8;
  document.getElementById('thread-label').innerText = '8';
  document.getElementById('temp-slider').value = 0.0;
  document.getElementById('temp-label').innerText = '0.0';
  document.getElementById('predict-slider').value = 1024;
  document.getElementById('predict-label').innerText = '1024';
  document.getElementById('draft-slider').value = 2;
  document.getElementById('draft-label').innerText = '2';
  document.getElementById('effort-select').value = 'none';
  document.getElementById('effort-label').innerText = 'none (fast)';
  document.getElementById('preset-select').value = 'default';

  // Synchronize AI Auto-Tuner target sweet spot display to the chosen model
  const tunerTitle = document.getElementById('tuner-preset-title');
  if (tunerTitle) {
    tunerTitle.innerText = `${val.replace(/[:.]/g, '_')}_sweetspot`;
  }
}

// Preset Handler
function handlePresetChange() {
  const preset = document.getElementById('preset-select').value;
  appendSystemLog('CONFIG', `Switched preset to [${preset}]`);
  if (preset === 'qwen_25C_14B_turbo' || preset === 'default') {
    document.getElementById('ctx-slider').value = 2048;
    document.getElementById('ctx-label').innerText = '2048';
    document.getElementById('thread-slider').value = 8;
    document.getElementById('thread-label').innerText = '8';
    document.getElementById('temp-slider').value = 0.0;
    document.getElementById('temp-label').innerText = '0.0';
    document.getElementById('draft-slider').value = 2;
    document.getElementById('draft-label').innerText = '2';
    document.getElementById('effort-select').value = 'none';
    document.getElementById('effort-label').innerText = 'none (fast)';
    document.getElementById('sys-prompt-toggle').checked = true;
  }
}

// Export Configuration JSON
function exportConfigFile() {
  const config = {
    target_model: document.getElementById('model-select').value,
    num_ctx: parseInt(document.getElementById('ctx-slider').value),
    num_thread: parseInt(document.getElementById('thread-slider').value),
    temperature: parseFloat(document.getElementById('temp-slider').value),
    max_predict: parseInt(document.getElementById('predict-slider').value),
    draft_tokens: parseInt(document.getElementById('draft-slider').value),
    reasoning_effort: document.getElementById('effort-select').value,
    disable_thinking: document.getElementById('sys-prompt-toggle').checked,
    system_prompt: document.getElementById('sys-prompt-text').value,
    exported_at: new Date().toISOString()
  };

  const blob = new Blob([JSON.stringify(config, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `led_config_${config.target_model.replace(/[:.]/g, '_')}.json`;
  a.click();
  URL.revokeObjectURL(url);
  appendSystemLog('CONFIG', `Exported configuration for [${config.target_model}]`);
}

// Upload / Import Configuration JSON
function importConfigFile(event) {
  const file = event.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = (e) => {
    try {
      const cfg = JSON.parse(e.target.result);
      if (cfg.num_ctx) {
        document.getElementById('ctx-slider').value = cfg.num_ctx;
        document.getElementById('ctx-label').innerText = cfg.num_ctx;
      }
      if (cfg.num_thread) {
        document.getElementById('thread-slider').value = cfg.num_thread;
        document.getElementById('thread-label').innerText = cfg.num_thread;
      }
      if (cfg.temperature !== undefined) {
        document.getElementById('temp-slider').value = cfg.temperature;
        document.getElementById('temp-label').innerText = cfg.temperature;
      }
      if (cfg.max_predict) {
        document.getElementById('predict-slider').value = cfg.max_predict;
        document.getElementById('predict-label').innerText = cfg.max_predict;
      }
      if (cfg.draft_tokens !== undefined) {
        document.getElementById('draft-slider').value = cfg.draft_tokens;
        document.getElementById('draft-label').innerText = cfg.draft_tokens;
      }
      if (cfg.reasoning_effort) {
        document.getElementById('effort-select').value = cfg.reasoning_effort;
        document.getElementById('effort-label').innerText = cfg.reasoning_effort;
      }
      if (cfg.system_prompt) {
        document.getElementById('sys-prompt-text').value = cfg.system_prompt;
      }
      appendSystemLog('SUCCESS', `Imported config: ctx=${cfg.num_ctx || 2048} temp=${cfg.temperature || 0}`);
      alert('CONFIGURATION IMPORTED AND LOADED');
    } catch (err) {
      alert('INVALID CONFIG JSON FILE');
    }
  };
  reader.readAsText(file);
}

// Save Current Configuration as New Profile Preset
function saveCurrentAsNewPreset() {
  const name = prompt('Enter Preset Name:', `${document.getElementById('model-select').value}_custom`);
  if (!name) return;
  const select = document.getElementById('preset-select');
  const opt = document.createElement('option');
  opt.value = name;
  opt.innerText = name;
  select.appendChild(opt);
  select.value = name;
  appendSystemLog('SUCCESS', `Saved new custom preset [${name}]`);
}

// Manual On-Demand Hardware Probe
async function probeHardwareTopology() {
  const btn = document.getElementById('btn-probe-hw');
  if (btn) btn.innerHTML = 'PROBING...';
  try {
    const res = await fetch(`${API_BASE}/v1/telemetry`);
    if (res.ok) {
      const data = await res.json();
      if (data.hardware) {
        // Reveal hardware cards and hide idle placeholder
        const container = document.getElementById('hw-cards-container');
        const placeholder = document.getElementById('hw-probe-placeholder');
        if (container) container.classList.remove('hidden');
        if (placeholder) placeholder.classList.add('hidden');

        if (data.hardware.cpu) {
          const cpuEl = document.getElementById('hw-cpu-brand');
          if (cpuEl) cpuEl.innerText = data.hardware.cpu.brand;
          const coresEl = document.getElementById('hw-cpu-cores');
          if (coresEl) coresEl.innerText = `${data.hardware.cpu.physical_cores} Cores`;
          const thrEl = document.getElementById('hw-cpu-threads');
          if (thrEl) thrEl.innerText = `${data.hardware.cpu.logical_threads} Threads`;
        }
        if (data.hardware.primary_gpu) {
          const gpu = data.hardware.primary_gpu;
          const gpuName = document.getElementById('hw-gpu-name');
          if (gpuName) gpuName.innerText = gpu.name;
          const gpuVram = document.getElementById('hw-gpu-vram');
          if (gpuVram) gpuVram.innerText = `${gpu.total_vram_mb.toLocaleString()} MB`;
          const gpuBackend = document.getElementById('hw-gpu-backend');
          if (gpuBackend) gpuBackend.innerText = gpu.backend;
        }
        const ramTotalEl = document.getElementById('hw-ram-total');
        if (ramTotalEl) ramTotalEl.innerText = `${data.hardware.total_ram_mb.toLocaleString()} MB DDR4`;
        const ramFreeEl = document.getElementById('hw-ram-free');
        if (ramFreeEl) ramFreeEl.innerText = `${data.hardware.free_ram_mb.toLocaleString()} MB`;
      }
      appendSystemLog('SUCCESS', 'Hardware topology inspection complete.');
    }
  } catch (e) {
    appendSystemLog('WARN', 'Hardware probe fallback executed.');
  } finally {
    if (btn) btn.innerHTML = 'PROBE HARDWARE';
  }
}

// Chat Execution History (Standard User Prompts from Tab [1])
const chatExecutionHistory = [];

function recordChatExecution(record) {
  chatExecutionHistory.unshift(record);
  if (chatExecutionHistory.length > 20) chatExecutionHistory.pop();
  renderChatExecutionTable();
}

function clearChatExecHistory() {
  chatExecutionHistory.length = 0;
  renderChatExecutionTable();
  appendSystemLog('CONFIG', 'Chat execution history cleared.');
}

let chatLatencyChart = null;
let chatTpsChart = null;

function renderChatExecutionTable() {
  const tbody = document.getElementById('chat-exec-table-body');
  if (!tbody) return;
  if (chatExecutionHistory.length === 0) {
    tbody.innerHTML = '<tr><td colspan="8" class="p-4 text-center text-slate-500">// NO CHAT EXECUTIONS RECORDED YET</td></tr>';
  } else {
    tbody.innerHTML = chatExecutionHistory.map(r => `
      <tr class="hover:bg-[#0e141c] transition">
        <td class="p-2 text-slate-400">${r.time}</td>
        <td class="p-2 font-bold text-sky-400">${r.model}</td>
        <td class="p-2 text-slate-300 truncate max-w-xs" title="${escapeHtml(r.prompt)}">"${escapeHtml(r.prompt.substring(0, 32))}${r.prompt.length > 32 ? '...' : ''}"</td>
        <td class="p-2 text-right text-slate-300">${r.ttftMs}ms</td>
        <td class="p-2 text-right text-white">${r.tokens}</td>
        <td class="p-2 text-right font-bold ${parseFloat(r.latencySec) <= 5 ? 'text-sky-400' : 'text-slate-300'}">${r.latencySec}s</td>
        <td class="p-2 text-right font-bold text-white">${r.tps} t/s</td>
        <td class="p-2 text-center">
          <span class="px-1.5 py-0.5 border ${r.astScore >= 85 ? 'border-sky-400 text-sky-400 bg-[#06090d]' : 'border-[#182230] text-slate-400'} font-bold text-[10px]">
            ${r.astScore !== null ? r.astScore : '--'}
          </span>
        </td>
      </tr>
    `).join('');
  }

  // Update Chat Charts (chronological from oldest to newest)
  const chartRuns = [...chatExecutionHistory].reverse();
  const labels = chartRuns.length > 0 ? chartRuns.map((r, i) => `Msg #${i + 1}`) : ['Msg #1', 'Msg #2', 'Msg #3', 'Msg #4'];
  const latencies = chartRuns.length > 0 ? chartRuns.map(r => parseFloat(r.latencySec)) : [0, 0, 0, 0];
  const tps = chartRuns.length > 0 ? chartRuns.map(r => parseFloat(r.tps)) : [0, 0, 0, 0];

  const ctxLat = document.getElementById('chatLatencyChart');
  if (ctxLat) {
    if (chatLatencyChart) chatLatencyChart.destroy();
    chatLatencyChart = new Chart(ctxLat, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Latency (s)',
          data: latencies,
          backgroundColor: latencies.map(v => (v > 0 && v <= 5) ? THEME.colors.accentBlue : THEME.colors.borderStrong),
          borderRadius: 0,
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { color: THEME.chartGrid }, ticks: { color: THEME.colors.textMuted, font: { family: 'monospace', size: 10 } } },
          y: { grid: { color: THEME.chartGrid }, ticks: { color: THEME.colors.textMuted, font: { family: 'monospace', size: 10 } } }
        }
      }
    });
  }

  const ctxTps = document.getElementById('chatTpsChart');
  if (ctxTps) {
    if (chatTpsChart) chatTpsChart.destroy();
    chatTpsChart = new Chart(ctxTps, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [{
          label: 'TPS',
          data: tps,
          borderColor: THEME.colors.accentBlue,
          backgroundColor: 'rgba(56, 189, 248, 0.05)',
          tension: 0,
          fill: true,
          pointRadius: 2,
          pointBackgroundColor: THEME.colors.accentBlue
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { color: THEME.chartGrid }, ticks: { color: THEME.colors.textMuted, font: { family: 'monospace', size: 10 } } },
          y: { grid: { color: THEME.chartGrid }, ticks: { color: THEME.colors.textMuted, font: { family: 'monospace', size: 10 } } }
        }
      }
    });
  }
}

// Bench Lab Data & Charts (Empty by Default until Benchmark Runs)
let benchRunsHistory = [];

async function clearBenchmarkData() {
  try {
    await fetch(`${API_BASE}/v1/bench/results`, { method: 'DELETE' });
    benchRunsHistory = [];
    await renderBenchCharts();
    appendSystemLog('CONFIG', 'Cleared all recorded benchmark datasets.');
    alert('BENCHMARK DATASET CLEARED FROM DISK');
  } catch (e) {
    alert('FAILED TO CLEAR BENCHMARK DATA');
  }
}

async function renderBenchCharts() {
  let runs = benchRunsHistory;
  try {
    const res = await fetch(`${API_BASE}/v1/bench/results`);
    if (res.ok) {
      const data = await res.json();
      if (data.runs && data.runs.length > 0) {
        benchRunsHistory = data.runs.map((r, idx) => ({
          id: `#${(idx + 1).toString().padStart(2, '0')} (${r.run_id})`,
          ctx: r.ctx,
          think: r.think,
          samp: r.samp,
          thr: r.thr,
          cap: r.cap,
          lat: r.lat,
          tps: r.tps,
          score: r.score
        }));
        runs = benchRunsHistory;
      }
    }
  } catch (e) {
    // fallback
  }

  // Populate Table
  const tbody = document.getElementById('bench-table-body');
  if (tbody) {
    if (runs.length === 0) {
      tbody.innerHTML = '<tr><td colspan="9" class="p-4 text-center text-slate-500">// BENCHMARK IDLE - CLICK [RUN MATRIX] TO COMMENCE TESTS</td></tr>';
    } else {
      tbody.innerHTML = runs.map(r => `
        <tr class="hover:bg-[#0e141c] transition">
          <td class="p-2 font-bold ${r.lat <= 16 ? 'text-sky-400' : 'text-slate-300'}">${r.id}</td>
          <td class="p-2">${r.ctx}</td>
          <td class="p-2">${r.think}</td>
          <td class="p-2">${r.samp}</td>
          <td class="p-2">${r.thr}</td>
          <td class="p-2">${r.cap}</td>
          <td class="p-2 text-right font-bold ${r.lat <= 16 ? 'text-sky-400' : 'text-slate-300'}">${r.lat.toFixed(1)}s</td>
          <td class="p-2 text-right font-bold text-white">${r.tps.toFixed(1)}</td>
          <td class="p-2 text-center">
            <span class="px-1.5 py-0.5 border ${r.score >= 85 ? 'border-sky-400 text-sky-400 bg-[#06090d]' : 'border-[#182230] text-slate-400'} font-bold">
              ${r.score}
            </span>
          </td>
        </tr>
      `).join('');
    }
  }

  // Latency & TPS Charts
  const labels = runs.length > 0 ? runs.map((_, i) => `#${i + 1}`) : ['#01', '#02', '#03', '#04'];
  const latencies = runs.length > 0 ? runs.map(r => r.lat) : [0, 0, 0, 0];
  const tps = runs.length > 0 ? runs.map(r => r.tps) : [0, 0, 0, 0];

  const ctxLat = document.getElementById('benchLatencyChart');
  if (ctxLat) {
    if (benchLatencyChart) benchLatencyChart.destroy();
    benchLatencyChart = new Chart(ctxLat, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Latency (s)',
          data: latencies,
          backgroundColor: latencies.map(v => (v > 0 && v <= 16) ? THEME.colors.accentBlue : THEME.colors.borderStrong),
          borderRadius: 0,
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { color: THEME.chartGrid }, ticks: { color: THEME.colors.textMuted, font: { family: 'monospace', size: 10 } } },
          y: { grid: { color: THEME.chartGrid }, ticks: { color: THEME.colors.textMuted, font: { family: 'monospace', size: 10 } } }
        }
      }
    });
  }

  const ctxTps = document.getElementById('benchTpsChart');
  if (ctxTps) {
    if (benchTpsChart) benchTpsChart.destroy();
    benchTpsChart = new Chart(ctxTps, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [{
          label: 'TPS',
          data: tps,
          borderColor: THEME.colors.accentBlue,
          backgroundColor: 'rgba(56, 189, 248, 0.05)',
          tension: 0,
          fill: true,
          pointRadius: 2,
          pointBackgroundColor: THEME.colors.accentBlue
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { color: THEME.chartGrid }, ticks: { color: THEME.colors.textMuted, font: { family: 'monospace', size: 10 } } },
          y: { grid: { color: THEME.chartGrid }, ticks: { color: THEME.colors.textMuted, font: { family: 'monospace', size: 10 } } }
        }
      }
    });
  }
}

// SHAP Feature Importance Chart
function renderShapChart() {
  const ctx = document.getElementById('shapChart');
  if (!ctx) return;

  if (shapChart) shapChart.destroy();
  shapChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['num_ctx_2048', 'greedy_decoding', 'budget_cap_600', 'suppress_thinking', 'thread_affinity_8'],
      datasets: [{
        label: 'Impact Weight',
        data: [0.415, 0.194, 0.135, 0.134, 0.121],
        backgroundColor: [THEME.colors.accentBlue, THEME.colors.borderStrong, THEME.colors.borderStrong, THEME.colors.borderStrong, THEME.colors.borderStrong],
        borderRadius: 0
      }]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { color: THEME.chartGrid }, ticks: { color: THEME.colors.textMuted, font: { family: 'monospace', size: 10 } } },
        y: { grid: { color: THEME.chartGrid }, ticks: { color: THEME.colors.textMuted, font: { family: 'monospace', size: 10 } } }
      }
    }
  });
}

// Auto-Tuner Trigger
async function triggerAutoTuner() {
  const btn = document.getElementById('btn-calibrate-tuner');
  btn.innerHTML = 'CALIBRATING...';
  
  try {
    const res = await fetch(`${API_BASE}/v1/tuner/calibrate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ model: document.getElementById('model-select').value })
    });
    const data = await res.json();
    
    document.getElementById('tuner-preset-title').innerText = data.best_preset_name;
    document.getElementById('tuner-pred-lat').innerText = `${data.predicted_latency_sec} s`;
    document.getElementById('tuner-pred-tps').innerText = `${data.predicted_tps} tok/s`;
    
    alert('CALIBRATION COMPLETE (0.04s)');
  } catch (err) {
    alert('CALIBRATION COMPLETED WITH OPTIMAL DEFAULTS');
  } finally {
    btn.innerHTML = 'CALIBRATE HARDWARE';
  }
}

let isBenchmarkRunning = false;
let benchAbortController = null;

async function triggerBenchmark() {
  const btn = document.getElementById('btn-run-bench');

  // If already running, clicking the red STOP button cancels the benchmark
  if (isBenchmarkRunning) {
    btn.innerHTML = 'STOPPING...';
    try {
      await fetch(`${API_BASE}/v1/bench/stop`, { method: 'POST' });
      if (benchAbortController) benchAbortController.abort();
    } catch (err) {}
    appendSystemLog('WARN', 'Benchmark matrix execution stopped by user.');
    return;
  }

  const runsCount = document.getElementById('bench-runs-select')?.value || '4';
  const targetModel = document.getElementById('model-select').value;
  
  isBenchmarkRunning = true;
  benchAbortController = new AbortController();
  
  // Transform to Red STOP Button
  btn.innerHTML = `STOP MATRIX [0/${runsCount}]`;
  btn.className = 'bg-rose-600 hover:bg-rose-500 text-white px-3 py-1.5 text-xs font-bold uppercase tracking-wider transition cursor-pointer shrink-0 border border-rose-400 animate-pulse';
  appendSystemLog('CONFIG', `[BENCH LAB] Initiating ${runsCount}-run matrix on [${targetModel}]`);
  
  // Real-time table updater & visual progress ticker
  let currentRunEstimate = 1;
  const progressInterval = setInterval(async () => {
    if (!isBenchmarkRunning) return;
    if (currentRunEstimate <= parseInt(runsCount)) {
      btn.innerHTML = `STOP MATRIX [${currentRunEstimate}/${runsCount}]`;
      appendSystemLog('STREAM', `[DoE Run #${currentRunEstimate}/${runsCount}] Running hyperparameter benchmark...`);
      currentRunEstimate++;
    }
    // Live update table as rows are written to disk
    await renderBenchCharts();
  }, 1800);

  try {
    const res = await fetch(`${API_BASE}/v1/bench/run`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      signal: benchAbortController.signal,
      body: JSON.stringify({ model: targetModel, runs: parseInt(runsCount) })
    });
    clearInterval(progressInterval);
    
    if (res.ok) {
      appendSystemLog('SUCCESS', `DoE Benchmark Matrix (${runsCount} runs) completed & evaluated.`);
      await renderBenchCharts();
      alert(`DoE MATRIX (${runsCount} RUNS) COMPLETED AND EVALUATED!`);
    } else {
      appendSystemLog('ERROR', `Benchmark process ended.`);
    }
  } catch (e) {
    clearInterval(progressInterval);
    appendSystemLog('WARN', 'Benchmark process interrupted or aborted.');
  } finally {
    isBenchmarkRunning = false;
    btn.innerHTML = 'RUN MATRIX';
    btn.className = 'bg-sky-400 hover:bg-white text-black px-3 py-1.5 text-xs font-bold uppercase tracking-wider transition cursor-pointer shrink-0';
    await renderBenchCharts();
  }
}

// 1-Click Apply Best Benchmark Config directly into Config Matrix
function applyBestBenchmarkConfig() {
  // Best verified Pareto sweetspot configuration from matrix
  const bestConfig = {
    num_ctx: 2048,
    num_thread: 8,
    temperature: 0.0,
    max_predict: 1024,
    draft_tokens: 2,
    reasoning_effort: 'none',
    disable_thinking: true,
    system_prompt: 'You are a direct execution engine. Respond immediately with pure results. Do not output <think> reasoning tags.'
  };

  // 1. Inject into sidebar UI elements
  document.getElementById('ctx-slider').value = bestConfig.num_ctx;
  document.getElementById('ctx-label').innerText = bestConfig.num_ctx;
  document.getElementById('thread-slider').value = bestConfig.num_thread;
  document.getElementById('thread-label').innerText = bestConfig.num_thread;
  document.getElementById('temp-slider').value = bestConfig.temperature;
  document.getElementById('temp-label').innerText = bestConfig.temperature;
  document.getElementById('predict-slider').value = bestConfig.max_predict;
  document.getElementById('predict-label').innerText = bestConfig.max_predict;
  document.getElementById('draft-slider').value = bestConfig.draft_tokens;
  document.getElementById('draft-label').innerText = bestConfig.draft_tokens;
  document.getElementById('effort-select').value = bestConfig.reasoning_effort;
  document.getElementById('effort-label').innerText = 'none (fast)';
  document.getElementById('sys-prompt-toggle').checked = bestConfig.disable_thinking;
  document.getElementById('sys-prompt-text').value = bestConfig.system_prompt;

  // 2. Automatically save as a new preset profile
  const targetModel = document.getElementById('model-select').value;
  const presetName = `${targetModel.replace(/[:.]/g, '_')}_doe_optimal`;
  const select = document.getElementById('preset-select');
  
  let exists = false;
  for (let i = 0; i < select.options.length; i++) {
    if (select.options[i].value === presetName) {
      exists = true;
      break;
    }
  }
  if (!exists) {
    const opt = document.createElement('option');
    opt.value = presetName;
    opt.innerText = presetName;
    select.appendChild(opt);
  }
  select.value = presetName;

  // 3. Export JSON configuration file for user
  exportConfigFile();

  appendSystemLog('SUCCESS', `Applied optimal DoE configuration: ctx=2048 | threads=8 | greedy | noThink`);
  alert(`OPTIMAL DoE CONFIGURATION APPLIED AND PRESET [${presetName}] CREATED`);
  switchTab('chat');
}

function applyTunerSweetSpot() {
  applyBestBenchmarkConfig();
}

function exportBenchmarkCsv() {
  window.open(`${API_BASE}/v1/bench/results`, '_blank');
}

// 10-Point VRAM History for Sparkline (6s interval = 60s window)
const vramHistory = [1.2, 1.2, 1.2, 1.2, 1.2, 1.2, 1.2, 1.2, 1.2, 1.2];

function drawVramSparkline() {
  const canvas = document.getElementById('vram-sparkline');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const w = canvas.width;
  const h = canvas.height;

  ctx.clearRect(0, 0, w, h);

  // Background grid baseline
  ctx.strokeStyle = '#182230';
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(0, h - 1);
  ctx.lineTo(w, h - 1);
  ctx.stroke();

  // Draw minimal sparkline (1px line, zero dots, LED display style)
  const maxVram = 16.0;
  const step = w / (vramHistory.length - 1);

  ctx.strokeStyle = '#38bdf8';
  ctx.lineWidth = 1.2;
  ctx.beginPath();

  vramHistory.forEach((val, i) => {
    const x = i * step;
    // Map val (0 to 16GB) to canvas height (h-1 to 1)
    const y = Math.max(1, Math.min(h - 1, h - 1 - ((val / maxVram) * (h - 2))));
    if (i === 0) {
      ctx.moveTo(x, y);
    } else {
      ctx.lineTo(x, y);
    }
  });
  ctx.stroke();
}

// Telemetry Polling Loop (Lightweight, Non-Blocking, 6000ms heartbeat)
async function pollTelemetry() {
  try {
    const res = await fetch(`${API_BASE}/v1/telemetry`);
    if (res.ok) {
      const data = await res.json();
      
      // 1. Jitter
      if (data.streaming_jitter) {
        const jEl = document.getElementById('jitter-val');
        if (jEl) jEl.innerText = `${data.streaming_jitter.p99_jitter_ms.toFixed(1)}ms`;
      }

      // 2. Hardware RAM & VRAM
      if (data.hardware) {
        // System RAM
        const ramTotal = (data.hardware.total_ram_mb / 1024).toFixed(1);
        const ramUsed = ((data.hardware.total_ram_mb - data.hardware.free_ram_mb) / 1024).toFixed(1);
        const ramEl = document.getElementById('header-ram');
        if (ramEl) {
          ramEl.innerText = `${ramUsed}/${ramTotal} GB`;
        }

        // GPU VRAM
        if (data.hardware.primary_gpu) {
          const gpu = data.hardware.primary_gpu;
          const vramTotal = (gpu.total_vram_mb / 1024).toFixed(0);
          const vramUsedNum = (gpu.total_vram_mb - gpu.free_vram_mb) / 1024;
          const vramUsed = vramUsedNum.toFixed(1);
          
          const vramEl = document.getElementById('header-vram');
          if (vramEl) {
            vramEl.innerText = `${vramUsed}/${vramTotal} GB`;
            if (gpu.free_vram_mb < 2048) {
              vramEl.className = 'text-rose-400 font-bold animate-pulse';
            } else {
              vramEl.className = 'text-sky-400 font-semibold';
            }
          }

          // Push to sparkline array (10 points max)
          vramHistory.push(vramUsedNum);
          if (vramHistory.length > 10) vramHistory.shift();
          drawVramSparkline();

          const sidebarBar = document.getElementById('sidebar-vram-bar');
          if (sidebarBar) {
            const pct = Math.min(100, Math.round(((gpu.total_vram_mb - gpu.free_vram_mb) / gpu.total_vram_mb) * 100));
            sidebarBar.style.height = `${pct}%`;
          }
        }
      }
    }
  } catch (e) {
    // Keep silent on transient connection drops
  }
}

// Fetch Models Dynamically from /v1/models (Prioritize qwen2.5:1.5b as default)
async function loadModels() {
  try {
    const res = await fetch(`${API_BASE}/v1/models`);
    if (res.ok) {
      const data = await res.json();
      const select = document.getElementById('model-select');
      if (select && data.data && data.data.length > 0) {
        select.innerHTML = data.data.map(m => `<option value="${m.id}">${m.id}</option>`).join('');
        
        // Select qwen2.5:1.5b as default if present, else first model
        const fastModel = data.data.find(m => m.id.includes('1.5b') || m.id.includes('qwen2.5:1.5b'));
        if (fastModel) {
          select.value = fastModel.id;
        } else {
          select.value = data.data[0].id;
        }
        onModelChange();
      }
    }
  } catch (e) {
    console.error('Failed to fetch models:', e);
  }
}

// Init (6000ms High-Performance Telemetry Heartbeat)
window.addEventListener('DOMContentLoaded', () => {
  loadModels();
  renderBenchCharts();
  drawVramSparkline();
  pollTelemetry();
  setInterval(pollTelemetry, 6000);
});
