import { createRuntimeClient } from "@aether/client";
import { DesktopApp } from "./components/App.js";

const client = createRuntimeClient({
  socketOptions: {
    socketPath: "/tmp/vanguard-runtime.sock",
  },
});

const app = new DesktopApp({ client });
const root = document.getElementById("root");
if (root) {
  app.mount(root);
}
