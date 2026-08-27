import React from "react";
import { Box, Text } from "ink";
import { theme } from "../theme/tokens.js";

export type TimelineEntry = {
  seq: string;
  kind: string;
  lineageId?: string;
  writer?: string;
  summary: string;
  status: "committed" | "projected" | "telemetry";
  timestamp?: string;
};

export type EventTimelineProps = {
  events: readonly TimelineEntry[];
  selectedSeq?: string;
  onSelectEvent: (seq: string) => void;
  filter?: { kind?: string; lineage?: string; writer?: string };
  height: number;
};

export const EventTimeline: React.FC<EventTimelineProps> = (props) => {
  const { events, selectedSeq, height } = props;
  const displayEvents = events.slice(-height);
  
  return (
    <Box flexDirection="column" height={height}>
      {displayEvents.map((event) => {
        const isSelected = event.seq === selectedSeq;
        const color = event.status === "telemetry" ? "gray" : event.status === "projected" ? theme.warning : undefined;
        return (
          <Box key={event.seq}>
            <Text color={isSelected ? theme.accent : color} backgroundColor={isSelected ? "gray" : undefined}>
              {event.seq.padEnd(5)} {event.kind.padEnd(15)} {event.summary}
            </Text>
          </Box>
        );
      })}
    </Box>
  );
};
