import React from "react";
import { Box, Text } from "ink";
import { theme } from "../theme/tokens.js";

export const GapIndicator: React.FC<{
  isLive: boolean;
  hasGap: boolean;
  gapRange?: { from: string; to: string };
  reconnecting: boolean;
}> = (props) => {
  return (
    <Box marginLeft={2}>
      {props.reconnecting ? (
        <Text color={theme.warning}>[Reconnecting...]</Text>
      ) : props.hasGap ? (
        <Text color={theme.danger}>
          [GAP: {props.gapRange?.from} - {props.gapRange?.to}]
        </Text>
      ) : props.isLive ? (
        <Text color="green">[LIVE]</Text>
      ) : (
        <Text dimColor>[DISCONNECTED]</Text>
      )}
    </Box>
  );
};
