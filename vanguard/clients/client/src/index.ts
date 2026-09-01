export * from "./client.js";
export * from "./transports/transport.js";
export * from "./transports/socket.js";
export * from "./transports/http.js";
export * from "./transports/replay.js";
export * from "./transports/fake.js";
export * from "./application/run-view.js";
export * from "./application/trace-graph.js";
export * from "./application/budget.js";
export * from "./application/coding-types.js";
export * from "./application/graph-model.js";
export * from "./application/mcnemar.js";
export * from "./application/projection-model.js";
export * from "./application/approvals.js";
export * from "./application/subscribe-run.js";
export * from "./application/selectors.js";
export * from "./application/coding-receipts.js";
export * from "./application/corrections.js";
export * from "./application/why.js";
export * from "./application/resume.js";
export * from "./application/commands.js";
export * from "./signers/operator-signer.js";
export * from "./signers/web-signer.js";
export * from "./application/app-controller.js";
export * from "./persistence/persistence-port.js";
export * from "./product/paths.js";
export * from "./product/compatibility.js";
export * from "./product/configuration.js";
export * from "./runtime/managed-runtime.js";

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
