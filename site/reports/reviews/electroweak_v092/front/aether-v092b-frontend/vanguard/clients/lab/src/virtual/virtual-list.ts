export type VirtualListOptions<T> = {
  items: T[];
  itemHeight: number;
  containerHeight?: number;
  overscan?: number;
  renderItem: (item: T, index: number) => HTMLElement;
  onScroll?: (info: { scrollTop: number; isAtBottom: boolean; isScrolledUp: boolean }) => void;
};

export class VirtualList<T> {
  private container: HTMLElement;
  private contentWrapper: HTMLElement;
  private topSpacer: HTMLElement;
  private itemsWrapper: HTMLElement;
  private bottomSpacer: HTMLElement;

  private items: T[] = [];
  private itemHeight: number;
  private overscan: number;
  private renderItem: (item: T, index: number) => HTMLElement;
  private onScrollCallback?: (info: { scrollTop: number; isAtBottom: boolean; isScrolledUp: boolean }) => void;
  private isStickToBottom: boolean = false;
  private scrollListener: () => void;

  constructor(options: VirtualListOptions<T>) {
    this.items = options.items;
    this.itemHeight = options.itemHeight;
    this.overscan = options.overscan ?? 5;
    this.renderItem = options.renderItem;
    this.onScrollCallback = options.onScroll;

    this.container = document.createElement("div");
    this.container.className = "aether-virtual-list-container";
    this.container.style.cssText = `
      position: relative;
      overflow-y: auto;
      overflow-x: hidden;
      width: 100%;
      height: 100%;
      contain: strict;
    `;

    this.contentWrapper = document.createElement("div");
    this.contentWrapper.className = "aether-virtual-content-wrapper";
    this.contentWrapper.style.cssText = "position: relative; width: 100%; min-height: 100%;";

    this.topSpacer = document.createElement("div");
    this.topSpacer.style.cssText = "width: 100%; height: 0px;";

    this.itemsWrapper = document.createElement("div");
    this.itemsWrapper.style.cssText = "width: 100%;";

    this.bottomSpacer = document.createElement("div");
    this.bottomSpacer.style.cssText = "width: 100%; height: 0px;";

    this.contentWrapper.appendChild(this.topSpacer);
    this.contentWrapper.appendChild(this.itemsWrapper);
    this.contentWrapper.appendChild(this.bottomSpacer);
    this.container.appendChild(this.contentWrapper);

    this.scrollListener = () => this.handleScroll();
    this.container.addEventListener("scroll", this.scrollListener, { passive: true });
  }

  public getElement(): HTMLElement {
    return this.container;
  }

  public setItems(items: T[], stickToBottomIfAtBottom: boolean = false): void {
    const wasAtBottom = this.isAtBottom();
    this.items = items;
    this.render();

    if (stickToBottomIfAtBottom && wasAtBottom) {
      this.scrollToBottom();
    }
  }

  public render(): void {
    const totalCount = this.items.length;
    const scrollTop = this.container.scrollTop || 0;
    const clientHeight = this.container.clientHeight || 400;

    const startIndex = Math.max(0, Math.floor(scrollTop / this.itemHeight) - this.overscan);
    const visibleCount = Math.ceil(clientHeight / this.itemHeight) + 2 * this.overscan;
    const endIndex = Math.min(totalCount, startIndex + visibleCount);

    const topHeight = startIndex * this.itemHeight;
    const bottomHeight = Math.max(0, (totalCount - endIndex) * this.itemHeight);

    this.topSpacer.style.height = `${topHeight}px`;
    this.bottomSpacer.style.height = `${bottomHeight}px`;

    // Clear and rebuild visible DOM items
    this.itemsWrapper.innerHTML = "";
    for (let i = startIndex; i < endIndex; i++) {
      const item = this.items[i];
      if (item !== undefined) {
        const el = this.renderItem(item, i);
        this.itemsWrapper.appendChild(el);
      }
    }
  }

  public scrollToIndex(index: number): void {
    if (index < 0 || index >= this.items.length) return;
    const targetTop = index * this.itemHeight;
    this.container.scrollTop = targetTop;
    this.render();
  }

  public scrollToBottom(): void {
    const totalHeight = this.items.length * this.itemHeight;
    this.container.scrollTop = Math.max(0, totalHeight - (this.container.clientHeight || 400));
    this.render();
  }

  public isAtBottom(): boolean {
    const threshold = 40;
    const scrollTop = this.container.scrollTop || 0;
    const clientHeight = this.container.clientHeight || 0;
    const scrollHeight = this.container.scrollHeight || 0;
    return scrollHeight - (scrollTop + clientHeight) <= threshold;
  }

  private handleScroll(): void {
    const atBottom = this.isAtBottom();
    const scrollTop = this.container.scrollTop || 0;
    const isScrolledUp = !atBottom;

    if (this.onScrollCallback) {
      this.onScrollCallback({
        scrollTop,
        isAtBottom: atBottom,
        isScrolledUp,
      });
    }

    this.render();
  }

  public destroy(): void {
    this.container.removeEventListener("scroll", this.scrollListener);
  }
}
