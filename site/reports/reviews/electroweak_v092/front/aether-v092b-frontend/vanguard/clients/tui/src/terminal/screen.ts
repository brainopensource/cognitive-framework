import type { Writable } from "node:stream";
import { type ColorMode, detectColorMode, type SemanticStyle, styleToAnsi } from "../theme.js";
import { charWidth, stringWidth, type TerminalCell } from "./cell.js";

export type ScreenOptions = {
  stdout?: Writable & { columns?: number; rows?: number; isTTY?: boolean };
  colorMode?: ColorMode;
};

export class TerminalScreen {
  public width: number;
  public height: number;
  public readonly colorMode: ColorMode;
  private readonly out: Writable & { columns?: number; rows?: number; isTTY?: boolean };
  private frontBuffer: TerminalCell[][];
  private backBuffer: TerminalCell[][];
  private isRaw: boolean = false;
  private cursorRow: number = 0;
  private cursorCol: number = 0;
  private cursorVisible: boolean = false;

  constructor(options: ScreenOptions = {}) {
    this.out = options.stdout ?? process.stdout;
    this.colorMode = options.colorMode ?? detectColorMode();
    this.width = this.out.columns || 80;
    this.height = this.out.rows || 24;
    this.frontBuffer = this.createBuffer();
    this.backBuffer = this.createBuffer();
  }

  private createBuffer(): TerminalCell[][] {
    const buf: TerminalCell[][] = [];
    for (let r = 0; r < this.height; r++) {
      const row: TerminalCell[] = [];
      for (let c = 0; c < this.width; c++) {
        row.push({ char: " ", width: 1 });
      }
      buf.push(row);
    }
    return buf;
  }

  public resize(newWidth: number, newHeight: number): void {
    this.width = Math.max(10, newWidth);
    this.height = Math.max(5, newHeight);
    this.frontBuffer = this.createBuffer();
    this.backBuffer = this.createBuffer();
  }

  public enterRawMode(): void {
    if (process.stdin.isTTY) {
      process.stdin.setRawMode(true);
      process.stdin.resume();
      this.isRaw = true;
    }
    // Enter alternate screen and hide cursor
    this.out.write("\x1b[?1049h\x1b[?25l\x1b[2J\x1b[H");
  }

  public exitRawMode(): void {
    if (this.isRaw && process.stdin.isTTY) {
      process.stdin.setRawMode(false);
      process.stdin.pause();
      this.isRaw = false;
    }
    // Exit alternate screen and show cursor
    this.out.write("\x1b[?25h\x1b[?1049l");
  }

  public clear(): void {
    for (let r = 0; r < this.height; r++) {
      for (let c = 0; c < this.width; c++) {
        this.backBuffer[r]![c] = { char: " ", width: 1 };
      }
    }
  }

  public writeString(row: number, col: number, text: string, style?: SemanticStyle): void {
    if (row < 0 || row >= this.height || col >= this.width) return;

    let c = col;
    let i = 0;
    while (i < text.length && c < this.width) {
      // Check for ANSI escapes inside text
      if (text.charCodeAt(i) === 0x1b && text[i + 1] === "[") {
        let end = i + 2;
        while (end < text.length && !/[a-zA-Z]/.test(text[end]!)) end++;
        if (end < text.length) end++;
        i = end;
        continue;
      }

      const cp = text.codePointAt(i);
      if (cp === undefined) break;
      const char = String.fromCodePoint(cp);
      const w = charWidth(cp);
      i += char.length;

      if (c + w > this.width) break;

      this.backBuffer[row]![c] = { char, width: w, style };
      if (w === 2 && c + 1 < this.width) {
        this.backBuffer[row]![c + 1] = { char: "", width: 0, style };
      }
      c += Math.max(1, w);
    }
  }

  public setCursor(row: number, col: number, visible: boolean = true): void {
    this.cursorRow = Math.max(0, Math.min(this.height - 1, row));
    this.cursorCol = Math.max(0, Math.min(this.width - 1, col));
    this.cursorVisible = visible;
  }

  public render(): void {
    let output = "";
    let lastStyleKey = "";

    for (let r = 0; r < this.height; r++) {
      let rowDiff = false;
      for (let c = 0; c < this.width; c++) {
        const front = this.frontBuffer[r]![c]!;
        const back = this.backBuffer[r]![c]!;
        if (front.char !== back.char || front.style !== back.style) {
          rowDiff = true;
          break;
        }
      }

      if (rowDiff) {
        output += `\x1b[${r + 1};1H`;
        for (let c = 0; c < this.width; c++) {
          const cell = this.backBuffer[r]![c]!;
          if (cell.width === 0) continue; // skipped 2nd half of wide char

          const styleKey = cell.style ? JSON.stringify(cell.style) : "";
          if (styleKey !== lastStyleKey) {
            output += "\x1b[0m";
            if (cell.style) {
              const { open } = styleToAnsi(cell.style, this.colorMode);
              output += open;
            }
            lastStyleKey = styleKey;
          }
          output += cell.char;
          this.frontBuffer[r]![c] = { ...cell };
        }
      }
    }

    if (lastStyleKey) output += "\x1b[0m";

    if (this.cursorVisible) {
      output += `\x1b[${this.cursorRow + 1};${this.cursorCol + 1}H\x1b[?25h`;
    } else {
      output += "\x1b[?25l";
    }

    if (output) {
      this.out.write(output);
    }
  }
}
