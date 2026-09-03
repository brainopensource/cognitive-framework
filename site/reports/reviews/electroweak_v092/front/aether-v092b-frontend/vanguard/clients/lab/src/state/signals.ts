export type Signal<T> = {
  get(): T;
  set(value: T | ((prev: T) => T)): void;
  subscribe(fn: (value: T) => void): () => void;
};

let inBatch = false;
const pendingSubscribers = new Set<() => void>();

export function batch<T>(fn: () => T): T {
  const prevBatch = inBatch;
  inBatch = true;
  try {
    return fn();
  } finally {
    inBatch = prevBatch;
    if (!inBatch) {
      const copy = Array.from(pendingSubscribers);
      pendingSubscribers.clear();
      for (const subscriber of copy) {
        subscriber();
      }
    }
  }
}

export function createSignal<T>(initialValue: T): Signal<T> {
  let current = initialValue;
  const listeners = new Set<(val: T) => void>();

  return {
    get() {
      return current;
    },
    set(val) {
      const next = typeof val === "function" ? (val as (prev: T) => T)(current) : val;
      if (next !== current) {
        current = next;
        if (inBatch) {
          for (const listener of listeners) {
            pendingSubscribers.add(() => listener(current));
          }
        } else {
          for (const listener of listeners) {
            listener(current);
          }
        }
      }
    },
    subscribe(fn) {
      listeners.add(fn);
      return () => listeners.delete(fn);
    },
  };
}

export function createMemo<T>(fn: () => T, dependencies: Signal<any>[]): () => T {
  let cachedValue = fn();
  let dirty = false;

  for (const dep of dependencies) {
    dep.subscribe(() => {
      dirty = true;
    });
  }

  return () => {
    if (dirty) {
      cachedValue = fn();
      dirty = false;
    }
    return cachedValue;
  };
}
