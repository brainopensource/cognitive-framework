import { strict as assert } from "node:assert";
import { describe, it } from "node:test";
import { DesktopStore, createSignal } from "../src/state/desktop-store.js";

/**
 * Regression cover for the "one letter per click" defect.
 *
 * Typing produced a full application re-render per keystroke, and the rebuild
 * discarded the focused textarea. Two independent notifiers caused it: the
 * store signal, and the controller's own subscriber list reached through
 * `setConversationDraft`. Both are asserted here, because silencing either one
 * alone leaves the bug intact.
 */
describe("@aether/desktop — composer draft does not force a re-render", () => {
  it("signal setSilent updates the value without notifying", () => {
    const signal = createSignal({ text: "" });
    let notifications = 0;
    signal.subscribe(() => notifications++);

    signal.setSilent({ text: "a" });
    signal.setSilent({ text: "ab" });

    assert.equal(signal.get().text, "ab");
    assert.equal(notifications, 0, "setSilent must not notify subscribers");
  });

  it("signal set still notifies, so ordinary state changes keep rendering", () => {
    const signal = createSignal({ text: "" });
    let notifications = 0;
    signal.subscribe(() => notifications++);

    signal.set({ text: "a" });

    assert.equal(notifications, 1);
  });

  it("typing a word notifies zero times", () => {
    const store = new DesktopStore();
    let renders = 0;
    store.state.subscribe(() => renders++);

    for (const draft of ["h", "he", "hel", "hell", "hello"]) {
      store.setComposerDraft(draft);
    }

    assert.equal(store.get().composerText, "hello");
    assert.equal(renders, 0, `typing caused ${renders} re-renders`);
  });

  it("does not persist a draft to the controller on every keystroke", () => {
    const store = new DesktopStore();
    let controllerNotifications = 0;
    store.controller.subscribe(() => controllerNotifications++);

    for (const draft of ["a", "ab", "abc"]) {
      store.setComposerDraft(draft);
    }

    assert.equal(
      controllerNotifications,
      0,
      "controller.setConversationDraft must be debounced, not per-keystroke",
    );
  });

  it("flush persists the pending draft to the controller", () => {
    const store = new DesktopStore();
    store.setComposerDraft("kept");

    store.flushComposerDraft();

    const active = store.controller
      .getState()
      .conversations.find((c) => c.id === store.controller.getState().activeConversationId);
    assert.equal(active?.draft, "kept");
  });

  it("submitting flushes immediately rather than waiting for the debounce", () => {
    const store = new DesktopStore();
    store.setComposerDraft("typed");
    store.setComposerDraft("", { flush: true });

    const state = store.controller.getState();
    const active = state.conversations.find((c) => c.id === state.activeConversationId);
    assert.equal(active?.draft, "");
  });

  it("a later flush does not resurrect superseded text", () => {
    const store = new DesktopStore();
    store.setComposerDraft("first");
    store.setComposerDraft("second");
    store.flushComposerDraft();

    const state = store.controller.getState();
    const active = state.conversations.find((c) => c.id === state.activeConversationId);
    assert.equal(active?.draft, "second");
  });
});
