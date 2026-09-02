/**
 * Keep keyboard focus alive across a full re-render.
 *
 * `DesktopApp.render` rebuilds the entire tree and swaps it in, so every
 * element the operator was interacting with is a different object afterwards.
 * The browser drops focus when the focused node leaves the document, which is
 * why typing produced one character per click: the `input` handler wrote to the
 * store, the store notified, the tree was rebuilt, and the textarea the
 * keystroke came from no longer existed.
 *
 * The real fix is to stop rebuilding the world on every state change, but that
 * is a rewrite of nine components. This restores the two things the operator
 * can actually perceive -- which field has focus, and where the caret sits --
 * by matching elements across renders on a stable author-assigned key.
 *
 * Elements opt in with `data-focus-key`. Anything without one is not restored,
 * because guessing at identity by DOM position moves focus to the wrong field
 * as soon as the layout changes.
 */

export const FOCUS_KEY_ATTRIBUTE = "data-focus-key";

export type CapturedFocus = {
  key: string;
  selectionStart: number | null;
  selectionEnd: number | null;
  scrollTop: number;
};

type TextEntry = HTMLInputElement | HTMLTextAreaElement;

function isTextEntry(element: Element | null): element is TextEntry {
  return (
    element instanceof HTMLInputElement || element instanceof HTMLTextAreaElement
  );
}

/** Record what has focus now, or null when focus is not on a keyed field. */
export function captureFocus(root: Document | ShadowRoot = document): CapturedFocus | null {
  const active = root.activeElement;
  if (!active) return null;
  const key = active.getAttribute?.(FOCUS_KEY_ATTRIBUTE);
  if (!key) return null;

  if (isTextEntry(active)) {
    return {
      key,
      // Reading selection on an input whose type forbids it throws in some
      // browsers (email, number); those fields simply restore without a caret.
      selectionStart: safeSelection(active, "selectionStart"),
      selectionEnd: safeSelection(active, "selectionEnd"),
      scrollTop: active.scrollTop,
    };
  }
  return { key, selectionStart: null, selectionEnd: null, scrollTop: 0 };
}

function safeSelection(element: TextEntry, field: "selectionStart" | "selectionEnd"): number | null {
  try {
    return element[field];
  } catch {
    return null;
  }
}

/** Put focus and caret back on the element carrying `captured.key`. */
export function restoreFocus(
  captured: CapturedFocus | null,
  container: ParentNode = document,
): boolean {
  if (!captured) return false;
  const selector = `[${FOCUS_KEY_ATTRIBUTE}="${CSS.escape(captured.key)}"]`;
  const target = container.querySelector(selector);
  if (!(target instanceof HTMLElement)) return false;

  target.focus({ preventScroll: true });

  if (isTextEntry(target) && captured.selectionStart !== null) {
    // Clamp: the value may be shorter than it was when focus was captured,
    // and an out-of-range caret silently snaps to 0 rather than the end.
    const limit = target.value.length;
    const start = Math.min(captured.selectionStart, limit);
    const end = Math.min(captured.selectionEnd ?? start, limit);
    try {
      target.setSelectionRange(start, end);
    } catch {
      /* selection is unsupported on this input type; focus alone is enough */
    }
    target.scrollTop = captured.scrollTop;
  }
  return true;
}
