/**
 * @file AUTO-GENERATED
 */

export interface AuthoritativeSnapshot<T> {
  readonly state: T;
  readonly version: number;
  readonly timestamp: string;
}

export interface StateProjectionDelta<T> {
  readonly fromVersion: number;
  readonly toVersion: number;
  readonly patch: Partial<T>;
}

export interface DegradedState {
  readonly isDegraded: boolean;
  readonly reason?: string;
  readonly lastAuthoritativeVersion: number;
}

export function applyProjectionDelta<T>(
  snapshot: AuthoritativeSnapshot<T>,
  delta: StateProjectionDelta<T>
): AuthoritativeSnapshot<T> {
  if (snapshot.version !== delta.fromVersion) {
    throw new Error(`Version mismatch: expected ${delta.fromVersion}, got ${snapshot.version}`);
  }
  return {
    state: { ...snapshot.state, ...delta.patch },
    version: delta.toVersion,
    timestamp: new Date().toISOString()
  };
}

export function createSnapshot<T>(state: T, version: number): AuthoritativeSnapshot<T> {
  return {
    state,
    version,
    timestamp: new Date().toISOString()
  };
}

export function checkDegraded(
  currentVersion: number,
  authoritativeVersion: number,
  tolerance = 0
): DegradedState {
  const diff = currentVersion - authoritativeVersion;
  return {
    isDegraded: diff > tolerance,
    reason: diff > tolerance ? `Projection is ${diff} versions ahead of authoritative state` : undefined,
    lastAuthoritativeVersion: authoritativeVersion
  };
}
