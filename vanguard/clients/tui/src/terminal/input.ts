export type KeyEvent = {
  name: string;
  ctrl?: boolean;
  meta?: boolean;
  shift?: boolean;
  sequence: string;
  isPaste?: boolean;
  pasteText?: string;
};

export class KeyParser {
  private pasteBuffer: string = "";
  private inBracketedPaste: boolean = false;

  public parse(chunk: Buffer | string): KeyEvent[] {
    const raw = typeof chunk === "string" ? chunk : chunk.toString("utf-8");
    const events: KeyEvent[] = [];
    let i = 0;

    while (i < raw.length) {
      if (this.inBracketedPaste) {
        const endIdx = raw.indexOf("\x1b[201~", i);
        if (endIdx !== -1) {
          this.pasteBuffer += raw.slice(i, endIdx);
          events.push({
            name: "paste",
            sequence: "",
            isPaste: true,
            pasteText: this.pasteBuffer,
          });
          this.pasteBuffer = "";
          this.inBracketedPaste = false;
          i = endIdx + 6;
          continue;
        } else {
          this.pasteBuffer += raw.slice(i);
          break;
        }
      }

      if (raw.startsWith("\x1b[200~", i)) {
        this.inBracketedPaste = true;
        this.pasteBuffer = "";
        i += 6;
        continue;
      }

      // Check single character / escape sequences
      const code = raw.charCodeAt(i);

      // Ctrl + C (0x03)
      if (code === 3) {
        events.push({ name: "c", ctrl: true, sequence: "\x03" });
        i++;
        continue;
      }
      // Ctrl + D (0x04)
      if (code === 4) {
        events.push({ name: "d", ctrl: true, sequence: "\x04" });
        i++;
        continue;
      }
      // Ctrl + U (0x15)
      if (code === 21) {
        events.push({ name: "u", ctrl: true, sequence: "\x15" });
        i++;
        continue;
      }
      // Ctrl + K (0x0b)
      if (code === 11) {
        events.push({ name: "k", ctrl: true, sequence: "\x0b" });
        i++;
        continue;
      }
      // Ctrl + A (0x01)
      if (code === 1) {
        events.push({ name: "a", ctrl: true, sequence: "\x01" });
        i++;
        continue;
      }
      // Ctrl + E (0x05)
      if (code === 5) {
        events.push({ name: "e", ctrl: true, sequence: "\x05" });
        i++;
        continue;
      }

      // Backspace (0x7f or 0x08)
      if (code === 127 || code === 8) {
        events.push({ name: "backspace", sequence: raw[i]! });
        i++;
        continue;
      }

      // Tab (0x09)
      if (code === 9) {
        events.push({ name: "tab", sequence: "\t" });
        i++;
        continue;
      }

      // Return / Enter (0x0d or 0x0a)
      if (code === 13 || code === 10) {
        events.push({ name: "return", sequence: "\n" });
        i++;
        continue;
      }

      // Escape sequence
      if (code === 27) {
        if (i + 1 >= raw.length) {
          events.push({ name: "escape", sequence: "\x1b" });
          i++;
          continue;
        }

        const next = raw[i + 1];

        // CSI sequences (\x1b[)
        if (next === "[") {
          const rest = raw.slice(i + 2);
          if (rest.startsWith("A")) {
            events.push({ name: "up", sequence: "\x1b[A" });
            i += 3;
            continue;
          }
          if (rest.startsWith("B")) {
            events.push({ name: "down", sequence: "\x1b[B" });
            i += 3;
            continue;
          }
          if (rest.startsWith("C")) {
            events.push({ name: "right", sequence: "\x1b[C" });
            i += 3;
            continue;
          }
          if (rest.startsWith("D")) {
            events.push({ name: "left", sequence: "\x1b[D" });
            i += 3;
            continue;
          }
          if (rest.startsWith("H")) {
            events.push({ name: "home", sequence: "\x1b[H" });
            i += 3;
            continue;
          }
          if (rest.startsWith("F")) {
            events.push({ name: "end", sequence: "\x1b[F" });
            i += 3;
            continue;
          }
          if (rest.startsWith("Z")) {
            events.push({ name: "tab", shift: true, sequence: "\x1b[Z" });
            i += 3;
            continue;
          }
          if (rest.startsWith("3~")) {
            events.push({ name: "delete", sequence: "\x1b[3~" });
            i += 4;
            continue;
          }
          if (rest.startsWith("5~")) {
            events.push({ name: "pageup", sequence: "\x1b[5~" });
            i += 4;
            continue;
          }
          if (rest.startsWith("6~")) {
            events.push({ name: "pagedown", sequence: "\x1b[6~" });
            i += 4;
            continue;
          }
          // Shift+Enter / Alt+Enter escape variants (e.g. \x1b[13;2u, \x1b\r)
          if (rest.startsWith("13;2u") || rest.startsWith("13;5u")) {
            events.push({ name: "return", shift: true, sequence: "\x1b[13;2u" });
            i += 7;
            continue;
          }
        }

        // Alt + Enter (\x1b\r)
        if (next === "\r" || next === "\n") {
          events.push({ name: "return", meta: true, sequence: "\x1b\r" });
          i += 2;
          continue;
        }

        // Alt + key
        events.push({ name: next!, meta: true, sequence: `\x1b${next}` });
        i += 2;
        continue;
      }

      // Regular character (including multi-byte UTF-8)
      const cp = raw.codePointAt(i);
      if (cp !== undefined) {
        const char = String.fromCodePoint(cp);
        events.push({ name: char, sequence: char });
        i += char.length;
      } else {
        i++;
      }
    }

    return events;
  }
}
