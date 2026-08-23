use led_core::streaming::{ChatCompletionChunk, StreamJitterTracker};

#[test]
fn test_openai_chunk_format() {
    let chunk = ChatCompletionChunk::new_content("chatcmpl-test", "qwen2.5-coder:14b", "def");
    assert_eq!(chunk.id, "chatcmpl-test");
    assert_eq!(chunk.object, "chat.completion.chunk");
    assert_eq!(chunk.model, "qwen2.5-coder:14b");
    assert_eq!(chunk.choices[0].delta.content.as_deref(), Some("def"));
    assert_eq!(chunk.choices[0].finish_reason, None);

    let finish = ChatCompletionChunk::new_finish("chatcmpl-test", "qwen2.5-coder:14b", "stop");
    assert_eq!(finish.choices[0].finish_reason.as_deref(), Some("stop"));
    assert_eq!(finish.choices[0].delta.content, None);
}

#[tokio::test]
async fn test_jitter_tracker_metrics() {
    let tracker = StreamJitterTracker::new();
    tracker.record_delta(2000, true); // 2.0ms
    tracker.record_delta(2500, true); // 2.5ms
    tracker.record_delta(1800, true); // 1.8ms

    let metrics = tracker.get_metrics();
    assert_eq!(metrics.total_tokens, 3);
    assert!(metrics.avg_inter_token_ms > 0.0);
    assert!(metrics.p99_jitter_ms < 10.0);
    assert!(metrics.meets_slo); // SLO: P99 < 10ms
}
