/**
 * A DOM mock with the surface the desktop components actually touch.
 *
 * The two previous inline mocks stopped at `createElement`/`appendChild`, so
 * any component that reached for an attribute or moved focus crashed the test
 * rather than failing an assertion. Focus preservation is exactly that kind of
 * behaviour, so it needs attributes, a queryable tree, and an `activeElement`
 * that `focus()` actually moves.
 */

export class MockElement {
  public tagName: string;
  public style: Record<string, string> & { cssText: string };
  public children: MockElement[] = [];
  public parentNode: MockElement | null = null;
  public textContent = "";
  public className = "";
  public type = "";
  public placeholder = "";
  public value = "";
  public scrollTop = 0;
  public selectionStart: number | null = 0;
  public selectionEnd: number | null = 0;
  public onclick: any = null;
  public oninput: any = null;
  public onkeydown: any = null;
  public onblur: any = null;
  public onchange: any = null;
  private attributes = new Map<string, string>();
  private ownerDoc: MockDocument;

  constructor(tagName: string, ownerDocument: MockDocument) {
    this.tagName = tagName.toUpperCase();
    this.ownerDoc = ownerDocument;
    this.style = new Proxy({ cssText: "" } as any, {
      get: (target, key) => target[key] ?? "",
      set: (target, key, val) => {
        target[key] = val;
        return true;
      },
    });
  }

  get ownerDocument(): MockDocument {
    return this.ownerDoc;
  }

  set innerHTML(_value: string) {
    // Assigning innerHTML discards the subtree, which is precisely the moment
    // focus is lost in the real application.
    this.children = [];
  }

  get innerHTML(): string {
    return "";
  }

  appendChild(child: MockElement): MockElement {
    child.parentNode = this;
    this.children.push(child);
    return child;
  }

  setAttribute(name: string, value: string): void {
    this.attributes.set(name, value);
  }

  getAttribute(name: string): string | null {
    return this.attributes.get(name) ?? null;
  }

  hasAttribute(name: string): boolean {
    return this.attributes.has(name);
  }

  focus(): void {
    this.ownerDoc.activeElement = this;
  }

  blur(): void {
    if (this.ownerDoc.activeElement === this) this.ownerDoc.activeElement = null;
  }

  setSelectionRange(start: number, end: number): void {
    this.selectionStart = start;
    this.selectionEnd = end;
  }

  /** Supports only the `[attr="value"]` form the focus helper emits. */
  querySelector(selector: string): MockElement | null {
    const match = /^\[([\w-]+)="(.*)"\]$/.exec(selector);
    for (const node of this.descendants()) {
      if (match && node.getAttribute(match[1]) === match[2]) return node;
    }
    return null;
  }

  querySelectorAll(selector: string): MockElement[] {
    const match = /^\[([\w-]+)="(.*)"\]$/.exec(selector);
    if (!match) return [];
    return [...this.descendants()].filter(
      (node) => node.getAttribute(match[1]) === match[2],
    );
  }

  *descendants(): Generator<MockElement> {
    for (const child of this.children) {
      yield child;
      yield* child.descendants();
    }
  }
}

export class MockDocument {
  public activeElement: MockElement | null = null;
  public head: MockElement;
  public body: MockElement;

  constructor() {
    this.head = new MockElement("head", this);
    this.body = new MockElement("body", this);
  }

  createElement(tagName: string): MockElement {
    return new MockElement(tagName, this);
  }

  querySelector(selector: string): MockElement | null {
    return this.body.querySelector(selector);
  }

  querySelectorAll(selector: string): MockElement[] {
    return this.body.querySelectorAll(selector);
  }
}

/** Install the mock globals the components expect. Idempotent. */
export function installMockDom(): MockDocument {
  const doc = new MockDocument();
  (globalThis as any).document = doc;
  (globalThis as any).HTMLElement = MockElement;
  (globalThis as any).HTMLInputElement = MockElement;
  (globalThis as any).HTMLTextAreaElement = MockElement;
  (globalThis as any).CSS = { escape: (value: string) => value };
  if (typeof (globalThis as any).window === "undefined") {
    (globalThis as any).window = {
      addEventListener: () => {},
      removeEventListener: () => {},
    };
  }
  return doc;
}
