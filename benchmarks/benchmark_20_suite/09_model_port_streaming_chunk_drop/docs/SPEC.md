# Specification: SSE Stream Event Decoding and Flush (MOD-09)

The `SSEDecoder` MUST:
1. Decode incoming SSE chunks into JSON data events.
2. When `close()` is called at stream termination, process any pending `data: ` line in `self._buffer` and yield the final event before resetting.
