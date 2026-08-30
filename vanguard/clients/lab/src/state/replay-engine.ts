import type { EventEnvelope } from "@aether/contracts";
import { createSignal, type Signal } from "./signals.js";

export type ReplaySpeed = 0.5 | 1 | 2 | 5 | 10 | 100;

export type ReplayState = {
  events: EventEnvelope[];
  currentIndex: number;
  totalEvents: number;
  isPlaying: boolean;
  speed: ReplaySpeed;
  currentSeq: string;
};

export class ReplayEngine {
  public readonly state: Signal<ReplayState>;
  private timer: any = null;
  private onStepCallback?: (visibleEvents: EventEnvelope[], currentEvent: EventEnvelope | null) => void;

  constructor(events: EventEnvelope[] = [], onStep?: (visibleEvents: EventEnvelope[], currentEvent: EventEnvelope | null) => void) {
    this.onStepCallback = onStep;
    const initialSeq = events.length > 0 ? events[0]?.seq ?? "0" : "0";
    this.state = createSignal<ReplayState>({
      events,
      currentIndex: 0,
      totalEvents: events.length,
      isPlaying: false,
      speed: 1,
      currentSeq: initialSeq,
    });
  }

  public setEvents(events: EventEnvelope[]): void {
    this.stopPlayback();
    const initialSeq = events.length > 0 ? events[0]?.seq ?? "0" : "0";
    this.state.set({
      events,
      currentIndex: 0,
      totalEvents: events.length,
      isPlaying: false,
      speed: this.state.get().speed,
      currentSeq: initialSeq,
    });
    this.notifyStep();
  }

  public get(): ReplayState {
    return this.state.get();
  }

  public setOnStep(cb: (visibleEvents: EventEnvelope[], currentEvent: EventEnvelope | null) => void): void {
    this.onStepCallback = cb;
  }

  public play(): void {
    const cur = this.get();
    if (cur.isPlaying) return;
    if (cur.currentIndex >= cur.totalEvents - 1) {
      // If at end, reset to start
      this.jumpToBeginning();
    }
    this.state.set((prev) => ({ ...prev, isPlaying: true }));
    this.scheduleNext();
  }

  public pause(): void {
    this.stopPlayback();
    this.state.set((prev) => ({ ...prev, isPlaying: false }));
  }

  public togglePlay(): void {
    if (this.get().isPlaying) {
      this.pause();
    } else {
      this.play();
    }
  }

  public setSpeed(speed: ReplaySpeed): void {
    this.state.set((prev) => ({ ...prev, speed }));
    if (this.get().isPlaying) {
      this.stopPlayback();
      this.scheduleNext();
    }
  }

  public stepForward(): void {
    const cur = this.get();
    if (cur.currentIndex < cur.totalEvents - 1) {
      const nextIndex = cur.currentIndex + 1;
      const nextEvent = cur.events[nextIndex];
      this.state.set((prev) => ({
        ...prev,
        currentIndex: nextIndex,
        currentSeq: nextEvent?.seq ?? prev.currentSeq,
      }));
      this.notifyStep();
    } else {
      this.pause();
    }
  }

  public stepBackward(): void {
    const cur = this.get();
    if (cur.currentIndex > 0) {
      const nextIndex = cur.currentIndex - 1;
      const nextEvent = cur.events[nextIndex];
      this.state.set((prev) => ({
        ...prev,
        currentIndex: nextIndex,
        currentSeq: nextEvent?.seq ?? prev.currentSeq,
      }));
      this.notifyStep();
    }
  }

  public jumpToSeq(seq: string | number): void {
    const targetSeq = String(seq);
    const cur = this.get();
    const index = cur.events.findIndex((e) => e.seq === targetSeq);
    if (index !== -1) {
      this.state.set((prev) => ({
        ...prev,
        currentIndex: index,
        currentSeq: targetSeq,
      }));
      this.notifyStep();
    }
  }

  public jumpToIndex(index: number): void {
    const cur = this.get();
    const clamped = Math.max(0, Math.min(cur.totalEvents - 1, index));
    const evt = cur.events[clamped];
    this.state.set((prev) => ({
      ...prev,
      currentIndex: clamped,
      currentSeq: evt?.seq ?? prev.currentSeq,
    }));
    this.notifyStep();
  }

  public jumpToBeginning(): void {
    this.jumpToIndex(0);
  }

  public jumpToEnd(): void {
    const cur = this.get();
    if (cur.totalEvents > 0) {
      this.jumpToIndex(cur.totalEvents - 1);
    }
  }

  public reset(): void {
    this.pause();
    this.jumpToBeginning();
  }

  private scheduleNext(): void {
    const cur = this.get();
    if (!cur.isPlaying) return;

    if (cur.currentIndex >= cur.totalEvents - 1) {
      this.pause();
      return;
    }

    const baseDelay = 300; // 300ms base
    const delay = cur.speed === 100 ? 5 : Math.max(10, baseDelay / cur.speed);

    this.timer = setTimeout(() => {
      this.stepForward();
      if (this.get().isPlaying) {
        this.scheduleNext();
      }
    }, delay);
  }

  private stopPlayback(): void {
    if (this.timer) {
      clearTimeout(this.timer);
      this.timer = null;
    }
  }

  private notifyStep(): void {
    if (!this.onStepCallback) return;
    const cur = this.get();
    if (cur.totalEvents === 0) {
      this.onStepCallback([], null);
      return;
    }
    const visible = cur.events.slice(0, cur.currentIndex + 1);
    const current = cur.events[cur.currentIndex] ?? null;
    this.onStepCallback(visible, current);
  }
}
