import type { Value } from "@vanguard/domain/value";

export interface Api {
  read(): Value;
}

