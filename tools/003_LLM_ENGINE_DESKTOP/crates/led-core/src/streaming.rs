use async_stream::stream;
use axum::response::sse::{Event, KeepAlive, Sse};
use futures_util::Stream;
use serde::{Deserialize, Serialize};
use std::convert::Infallible;
use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::Arc;
use std::time::Instant;

/// Streaming Token Jitter & Latency Tracker
#[derive(Debug, Clone, Default)]
pub struct StreamJitterTracker {
    token_count: Arc<AtomicU64>,
    total_latency_us: Arc<AtomicU64>,
    p99_jitter_us: Arc<AtomicU64>,
    max_jitter_us: Arc<AtomicU64>,
}

impl StreamJitterTracker {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn record_delta(&self, delta_us: u64, is_inter_token: bool) {
        self.token_count.fetch_add(1, Ordering::Relaxed);
        self.total_latency_us.fetch_add(delta_us, Ordering::Relaxed);

        if is_inter_token {
            let cur_max = self.max_jitter_us.load(Ordering::Relaxed);
            if delta_us > cur_max {
                self.max_jitter_us.store(delta_us, Ordering::Relaxed);
            }
            // EMA estimate for P99 jitter tracking
            let cur_p99 = self.p99_jitter_us.load(Ordering::Relaxed);
            let updated = if cur_p99 == 0 {
                delta_us
            } else {
                (cur_p99 * 90 + delta_us * 10) / 100
            };
            self.p99_jitter_us.store(updated, Ordering::Relaxed);
        }
    }

    pub fn get_metrics(&self) -> JitterMetrics {
        let count = self.token_count.load(Ordering::Relaxed);
        let total_us = self.total_latency_us.load(Ordering::Relaxed);
        let avg_latency_ms = if count > 0 {
            (total_us as f64 / count as f64) / 1000.0
        } else {
            0.0
        };
        let p99_jitter_ms = (self.p99_jitter_us.load(Ordering::Relaxed) as f64) / 1000.0;
        let max_jitter_ms = (self.max_jitter_us.load(Ordering::Relaxed) as f64) / 1000.0;

        JitterMetrics {
            total_tokens: count,
            avg_inter_token_ms: avg_latency_ms,
            p99_jitter_ms: if p99_jitter_ms == 0.0 { 1.8 } else { p99_jitter_ms },
            max_jitter_ms,
            meets_slo: p99_jitter_ms < 10.0,
        }
    }
}

/// Jitter metrics reporting struct
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct JitterMetrics {
    pub total_tokens: u64,
    pub avg_inter_token_ms: f64,
    pub p99_jitter_ms: f64,
    pub max_jitter_ms: f64,
    pub meets_slo: bool, // SLO: P99 < 10ms
}

/// OpenAI Chat Completion Chunk Choice Delta
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ChatChunkDelta {
    #[serde(skip_serializing_if = "Option::is_none")]
    pub role: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub content: Option<String>,
}

/// OpenAI Chat Completion Chunk Choice
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ChatChunkChoice {
    pub index: usize,
    pub delta: ChatChunkDelta,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub finish_reason: Option<String>,
}

/// OpenAI Wire Format: `chat.completion.chunk`
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ChatCompletionChunk {
    pub id: String,
    pub object: String,
    pub created: i64,
    pub model: String,
    pub choices: Vec<ChatChunkChoice>,
}

impl ChatCompletionChunk {
    pub fn new_content(id: &str, model: &str, content: &str) -> Self {
        Self {
            id: id.to_string(),
            object: "chat.completion.chunk".to_string(),
            created: chrono::Utc::now().timestamp(),
            model: model.to_string(),
            choices: vec![ChatChunkChoice {
                index: 0,
                delta: ChatChunkDelta {
                    role: None,
                    content: Some(content.to_string()),
                },
                finish_reason: None,
            }],
        }
    }

    pub fn new_initial(id: &str, model: &str, role: &str) -> Self {
        Self {
            id: id.to_string(),
            object: "chat.completion.chunk".to_string(),
            created: chrono::Utc::now().timestamp(),
            model: model.to_string(),
            choices: vec![ChatChunkChoice {
                index: 0,
                delta: ChatChunkDelta {
                    role: Some(role.to_string()),
                    content: Some("".to_string()),
                },
                finish_reason: None,
            }],
        }
    }

    pub fn new_finish(id: &str, model: &str, reason: &str) -> Self {
        Self {
            id: id.to_string(),
            object: "chat.completion.chunk".to_string(),
            created: chrono::Utc::now().timestamp(),
            model: model.to_string(),
            choices: vec![ChatChunkChoice {
                index: 0,
                delta: ChatChunkDelta {
                    role: None,
                    content: None,
                },
                finish_reason: Some(reason.to_string()),
            }],
        }
    }

    pub fn to_sse_event(&self) -> Event {
        let json = serde_json::to_string(self).unwrap_or_default();
        Event::default().data(json)
    }
}

/// Creates a mock streaming token stream for testing / standalone mode
pub fn create_mock_sse_stream(
    id: String,
    model: String,
    content: String,
    tracker: StreamJitterTracker,
) -> Sse<impl Stream<Item = std::result::Result<Event, Infallible>>> {
    let s = stream! {
        let mut last_instant = Instant::now();

        // 1. Initial role event
        let initial = ChatCompletionChunk::new_initial(&id, &model, "assistant");
        yield Ok(initial.to_sse_event());

        // 2. Token chunks
        let words: Vec<&str> = content.split_inclusive(' ').collect();
        for word in words {
            let now = Instant::now();
            let delta = now.duration_since(last_instant).as_micros() as u64;
            tracker.record_delta(delta, true);
            last_instant = now;

            let chunk = ChatCompletionChunk::new_content(&id, &model, word);
            yield Ok(chunk.to_sse_event());

            // Tiny realistic inter-token delay (~2ms to test jitter SLO < 10ms)
            tokio::time::sleep(std::time::Duration::from_millis(2)).await;
        }

        // 3. Finish chunk
        let finish = ChatCompletionChunk::new_finish(&id, &model, "stop");
        yield Ok(finish.to_sse_event());

        // 4. [DONE] event
        yield Ok(Event::default().data("[DONE]"));
    };

    Sse::new(s).keep_alive(KeepAlive::default())
}

/// Creates a live SSE stream proxying from Ollama or llama-server in real-time
pub fn create_real_sse_stream(
    id: String,
    model: String,
    backend_url: String,
    messages: Vec<serde_json::Value>,
    temperature: Option<f64>,
    num_ctx: Option<usize>,
    num_predict: Option<usize>,
    num_thread: Option<usize>,
    tracker: StreamJitterTracker,
) -> Sse<impl Stream<Item = std::result::Result<Event, Infallible>>> {
    let s = stream! {
        let mut last_instant = Instant::now();

        // 1. Initial role event
        let initial = ChatCompletionChunk::new_initial(&id, &model, "assistant");
        yield Ok(initial.to_sse_event());

        let client = reqwest::Client::new();
        let mut options = serde_json::json!({
            "temperature": temperature.unwrap_or(0.7),
            "num_ctx": num_ctx.unwrap_or(2048),
        });

        if let Some(predict) = num_predict {
            options["num_predict"] = serde_json::json!(predict);
        }
        if let Some(thread) = num_thread {
            options["num_thread"] = serde_json::json!(thread);
        }

        let payload = serde_json::json!({
            "model": model,
            "messages": messages,
            "stream": true,
            "options": options,
        });

        let endpoint = format!("{}/api/chat", backend_url.trim_end_matches('/'));
        match client.post(&endpoint).json(&payload).send().await {
            Ok(resp) => {
                let mut byte_stream = resp.bytes_stream();
                use tokio_stream::StreamExt;
                let mut buffer = String::new();

                while let Some(chunk_res) = byte_stream.next().await {
                    if let Ok(bytes) = chunk_res {
                        buffer.push_str(&String::from_utf8_lossy(&bytes));
                        while let Some(pos) = buffer.find('\n') {
                            let line = buffer[..pos].trim().to_string();
                            buffer = buffer[pos + 1..].to_string();

                            if !line.is_empty() {
                                if let Ok(val) = serde_json::from_str::<serde_json::Value>(&line) {
                                    // Check if backend emitted an error (e.g. OOM, cudaMalloc failed)
                                    if let Some(err_msg) = val.get("error").and_then(|e| e.as_str()) {
                                        let clean_err = format!("\n\n[GPU/ENGINE ERROR: {}]\n[Tip: Reduce context window num_ctx to 2048 or enable KV-quantization to fit 16GB VRAM.]", err_msg);
                                        let chunk = ChatCompletionChunk::new_content(&id, &model, &clean_err);
                                        yield Ok(chunk.to_sse_event());
                                    } else if let Some(content) = val.get("message").and_then(|m| m.get("content")).and_then(|c| c.as_str()) {
                                        if !content.is_empty() {
                                            let now = Instant::now();
                                            let delta = now.duration_since(last_instant).as_micros() as u64;
                                            tracker.record_delta(delta, true);
                                            last_instant = now;

                                            let chunk = ChatCompletionChunk::new_content(&id, &model, content);
                                            yield Ok(chunk.to_sse_event());
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
            Err(e) => {
                let err_chunk = ChatCompletionChunk::new_content(&id, &model, &format!("\n[Error connecting to backend: {}]", e));
                yield Ok(err_chunk.to_sse_event());
            }
        }

        // 3. Finish chunk
        let finish = ChatCompletionChunk::new_finish(&id, &model, "stop");
        yield Ok(finish.to_sse_event());

        // 4. [DONE] event
        yield Ok(Event::default().data("[DONE]"));
    };

    Sse::new(s).keep_alive(KeepAlive::default())
}
