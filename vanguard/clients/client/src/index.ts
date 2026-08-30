export * from "./client.js";
export * from "./transports/transport.js";
export * from "./transports/socket.js";
export * from "./transports/http.js";
export * from "./transports/replay.js";
export * from "./signers/operator-signer.js";
export * from "./signers/web-signer.js";

import type { RuntimeClient } from "./client.js";
import { SocketRuntimeClient, type SocketTransportOptions } from "./transports/socket.js";
import { HttpRuntimeClient, type HttpTransportOptions } from "./transports/http.js";

export function createRuntimeClient(options?: {
  transport?: "socket" | "http";
  socketOptions?: SocketTransportOptions;
  httpOptions?: HttpTransportOptions;
}): RuntimeClient {
  if (options?.transport === "http") {
    return new HttpRuntimeClient(options.httpOptions);
  }
  return new SocketRuntimeClient(options?.socketOptions);
}
