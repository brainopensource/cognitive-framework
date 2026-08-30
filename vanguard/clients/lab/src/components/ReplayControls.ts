import type { LabStore } from "../state/lab-store.js";
import type { ReplaySpeed } from "../state/replay-engine.js";
import { formatSeq } from "../util/formatting.js";

export function renderReplayControls(store: LabStore): HTMLElement {
  const container = document.createElement("div");
  container.className = "aether-replay-controls-bar";
  container.style.cssText = `
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 4px 10px;
    background: var(--lab-bg-panel);
    border: 1px solid var(--lab-border);
    border-radius: var(--lab-radius-sm);
    font-family: var(--lab-font-mono);
    font-size: 12px;
    user-select: none;
  `;

  const state = store.get();
  const replayState = store.replay.get();

  // Mode Toggle (Live vs Replay)
  const modeBtn = document.createElement("button");
  modeBtn.style.cssText = `
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 3px 8px;
    border-radius: var(--lab-radius-sm);
    font-size: 11px;
    font-weight: 600;
    cursor: pointer;
    background: ${state.mode === "live" ? "var(--lab-accent-muted)" : "var(--lab-bg-surface)"};
    color: ${state.mode === "live" ? "var(--lab-accent)" : "var(--lab-text-secondary)"};
    border: 1px solid ${state.mode === "live" ? "var(--lab-accent)" : "var(--lab-border)"};
  `;
  modeBtn.textContent = state.mode === "live" ? "● LIVE TAIL" : "⟲ REPLAY";
  modeBtn.onclick = () => {
    store.setMode(state.mode === "live" ? "replay" : "live");
  };
  container.appendChild(modeBtn);

  if (state.mode === "live") {
    // Live Status & Jump to Live if scrolled up
    const liveStatus = document.createElement("span");
    liveStatus.style.cssText = `
      font-size: 11px;
      color: ${state.liveTailState === "LIVE" ? "var(--lab-success)" : "var(--lab-warning)"};
    `;
    liveStatus.textContent = `[${state.liveTailState}]`;
    container.appendChild(liveStatus);

    if (state.unseenLiveCount > 0) {
      const jumpBtn = document.createElement("button");
      jumpBtn.style.cssText = `
        background: var(--lab-warning-bg);
        color: var(--lab-warning);
        border: 1px solid var(--lab-warning);
        border-radius: var(--lab-radius-sm);
        padding: 2px 6px;
        font-size: 11px;
        cursor: pointer;
        font-weight: 600;
      `;
      jumpBtn.textContent = `+${state.unseenLiveCount} new events — Jump to Live (L)`;
      jumpBtn.onclick = () => store.jumpToLive();
      container.appendChild(jumpBtn);
    }

    return container;
  }

  // REPLAY CONTROLS
  // 1. Jump Start
  const btnStart = document.createElement("button");
  btnStart.textContent = "⏮";
  btnStart.title = "Jump to beginning";
  btnStart.style.cssText = "background: none; border: none; color: var(--lab-text-primary); cursor: pointer; padding: 2px 4px;";
  btnStart.onclick = () => store.replay.jumpToBeginning();
  container.appendChild(btnStart);

  // 2. Step Backward
  const btnStepBack = document.createElement("button");
  btnStepBack.textContent = "⏴";
  btnStepBack.title = "Step backward";
  btnStepBack.style.cssText = "background: none; border: none; color: var(--lab-text-primary); cursor: pointer; padding: 2px 4px;";
  btnStepBack.onclick = () => store.replay.stepBackward();
  container.appendChild(btnStepBack);

  // 3. Play / Pause
  const btnPlay = document.createElement("button");
  btnPlay.textContent = replayState.isPlaying ? "⏸" : "▶";
  btnPlay.title = replayState.isPlaying ? "Pause" : "Play";
  btnPlay.style.cssText = `
    background: var(--lab-accent);
    color: var(--lab-bg);
    border: none;
    border-radius: 3px;
    padding: 2px 8px;
    font-weight: bold;
    cursor: pointer;
  `;
  btnPlay.onclick = () => store.replay.togglePlay();
  container.appendChild(btnPlay);

  // 4. Step Forward
  const btnStepFwd = document.createElement("button");
  btnStepFwd.textContent = "⏵";
  btnStepFwd.title = "Step forward";
  btnStepFwd.style.cssText = "background: none; border: none; color: var(--lab-text-primary); cursor: pointer; padding: 2px 4px;";
  btnStepFwd.onclick = () => store.replay.stepForward();
  container.appendChild(btnStepFwd);

  // 5. Jump End
  const btnEnd = document.createElement("button");
  btnEnd.textContent = "⏭";
  btnEnd.title = "Jump to end";
  btnEnd.style.cssText = "background: none; border: none; color: var(--lab-text-primary); cursor: pointer; padding: 2px 4px;";
  btnEnd.onclick = () => store.replay.jumpToEnd();
  container.appendChild(btnEnd);

  // 6. Scrubber Slider
  const slider = document.createElement("input");
  slider.type = "range";
  slider.min = "0";
  slider.max = String(Math.max(0, replayState.totalEvents - 1));
  slider.value = String(replayState.currentIndex);
  slider.style.cssText = "width: 120px; cursor: pointer;";
  slider.oninput = () => {
    const val = parseInt(slider.value, 10);
    store.replay.jumpToIndex(val);
  };
  container.appendChild(slider);

  // 7. Sequence / Index counter
  const counter = document.createElement("span");
  counter.style.cssText = "color: var(--lab-text-secondary); font-size: 11px;";
  counter.textContent = `${formatSeq(replayState.currentSeq)} (${replayState.currentIndex + 1}/${replayState.totalEvents})`;
  container.appendChild(counter);

  // 8. Speed Buttons
  const speedContainer = document.createElement("div");
  speedContainer.style.cssText = "display: flex; gap: 2px; margin-left: 6px;";
  const speeds: ReplaySpeed[] = [0.5, 1, 2, 5, 10, 100];

  for (const s of speeds) {
    const sBtn = document.createElement("button");
    sBtn.textContent = s === 100 ? "MAX" : `${s}x`;
    sBtn.style.cssText = `
      padding: 1px 4px;
      font-size: 10px;
      cursor: pointer;
      border: 1px solid var(--lab-border);
      border-radius: 2px;
      background: ${replayState.speed === s ? "var(--lab-accent-muted)" : "var(--lab-bg-surface)"};
      color: ${replayState.speed === s ? "var(--lab-accent)" : "var(--lab-text-muted)"};
    `;
    sBtn.onclick = () => store.replay.setSpeed(s);
    speedContainer.appendChild(sBtn);
  }
  container.appendChild(speedContainer);

  return container;
}
