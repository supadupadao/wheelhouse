use std::sync::Arc;
use tokio_utils::RateLimiter;
use tonapi::RestApiClientV2;

pub struct TraceHandler {
    trace_id: String,
}

impl TraceHandler {
    pub fn new(trace_id: String) -> Self {
        Self { trace_id }
    }

    pub fn get_trace_id(&self) -> String {
        self.trace_id.clone()
    }

    pub async fn handle(
        &self,
        rate_limiter: Arc<RateLimiter>,
        ton_client: &RestApiClientV2,
    ) -> anyhow::Result<()> {
        let trace_info = rate_limiter
            .throttle(|| ton_client.get_trace(self.trace_id.as_str()))
            .await
            .map_err(|err| anyhow::Error::msg(err.to_string()))?;

        info!("Parsing transaction {:?}", trace_info);

        Ok(())
    }
}
