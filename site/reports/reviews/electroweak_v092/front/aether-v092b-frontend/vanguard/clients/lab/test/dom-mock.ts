export function setupDomMock() {
  if (typeof globalThis.document === "undefined" || (globalThis as any).__isMockDom) {
    class MockElement {
      public style: Record<string, string> = {};
      public children: MockElement[] = [];
      public parentNode: MockElement | null = null;
      private _textContent: string = "";
      private _innerHTML: string = "";
      public className: string = "";
      public type: string = "";
      public placeholder: string = "";
      public value: string = "";
      public title: string = "";
      public id: string = "";
      public tagName: string = "DIV";
      public clientHeight: number = 500;
      public scrollTop: number = 0;
      public scrollHeight: number = 1000;
      public attributes: Record<string, string> = {};
      public isContentEditable: boolean = false;

      public onclick: any = null;
      public oninput: any = null;
      public onchange: any = null;
      public onkeydown: any = null;
      public onmouseenter: any = null;
      public onmouseleave: any = null;
      public onmousedown: any = null;

      get textContent(): string {
        if (this.children.length === 0) return this._textContent;
        return this._textContent + this.children.map((c) => c.textContent).join(" ");
      }

      set textContent(val: string) {
        this._textContent = val;
        this.children = [];
      }

      get innerHTML(): string {
        return this._innerHTML;
      }

      set innerHTML(val: string) {
        this._innerHTML = val;
        if (val === "") {
          this.children = [];
          this._textContent = "";
        }
      }

      appendChild(child: MockElement) {
        child.parentNode = this;
        this.children.push(child);
        return child;
      }

      removeChild(child: MockElement) {
        const idx = this.children.indexOf(child);
        if (idx !== -1) {
          this.children.splice(idx, 1);
          child.parentNode = null;
        }
        return child;
      }

      replaceChild(newChild: MockElement, oldChild: MockElement) {
        const idx = this.children.indexOf(oldChild);
        if (idx !== -1) {
          this.children[idx] = newChild;
          newChild.parentNode = this;
          oldChild.parentNode = null;
        }
        return oldChild;
      }

      setAttribute(name: string, value: string) {
        this.attributes[name] = value;
      }

      getAttribute(name: string): string | null {
        return this.attributes[name] ?? null;
      }

      addEventListener(event: string, handler: any) {
        // mock
      }

      removeEventListener(event: string, handler: any) {
        // mock
      }

      querySelector(selector: string): MockElement | null {
        const check = (node: MockElement): MockElement | null => {
          if (selector.startsWith(".") && node.className.includes(selector.slice(1))) return node;
          if (selector.startsWith("#") && node.id === selector.slice(1)) return node;
          if (node.tagName.toLowerCase() === selector.toLowerCase()) return node;
          for (const c of node.children) {
            const found = check(c);
            if (found) return found;
          }
          return null;
        };
        return check(this);
      }

      querySelectorAll(selector: string): MockElement[] {
        const results: MockElement[] = [];
        const check = (node: MockElement) => {
          if (selector.startsWith(".") && node.className.includes(selector.slice(1))) results.push(node);
          if (node.tagName.toLowerCase() === selector.toLowerCase()) results.push(node);
          for (const c of node.children) {
            check(c);
          }
        };
        check(this);
        return results;
      }

      focus() {}
      blur() {}
      select() {}
    }

    const doc: any = {
      createElement: (tag: string) => {
        const el = new MockElement();
        el.tagName = tag.toUpperCase();
        return el;
      },
      createElementNS: (_ns: string, tag: string) => {
        const el = new MockElement();
        el.tagName = tag.toUpperCase();
        return el;
      },
      head: new MockElement(),
      body: new MockElement(),
      getElementById: (id: string) => {
        const el = new MockElement();
        el.id = id;
        return el;
      },
      querySelector: () => new MockElement(),
      querySelectorAll: () => [],
      activeElement: null,
      execCommand: () => true,
    };

    (globalThis as any).document = doc;
    (globalThis as any).window = {
      addEventListener: () => {},
      removeEventListener: () => {},
      dispatchEvent: () => true,
      location: { hash: "#runs" },
      history: { replaceState: () => {} },
    };
    (globalThis as any).__isMockDom = true;
  }
}
