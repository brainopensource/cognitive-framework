import { createRuntimeClient } from "@aether/client";
import { LabApp } from "./components/LabApp.js";

const client = createRuntimeClient({
  socketOptions: {
    socketPath: "/tmp/vanguard-runtime.sock",
  },
});

const app = new LabApp({ client });

if (typeof document !== "undefined") {
  const root = document.getElementById("root");
  if (root) {
    app.mount(root);
  }
}
