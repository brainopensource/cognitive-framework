import { useEffect, useState } from "react";
import type { RuntimeClient } from "@vanguard/client-core";
import { SlotFrame } from "./files";
export function WhySlot({ client }: { client?: RuntimeClient }) { const [message, setMessage] = useState("Select an artifact to explain."); useEffect(() => { if (!client) return; client.explainArtifact("selected-artifact").then(result => setMessage(result.ok ? result.value.prediction || "No evidence recorded." : result.error.code)); }, [client]); return <SlotFrame title="WHY"><p className="muted">{message}</p></SlotFrame>; }
