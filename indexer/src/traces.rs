use crate::parser::start_parsing;
use std::sync::Arc;
use tokio_utils::RateLimiter;
use tonapi::RestApiClientV2;
use tonlib_core::TonAddress;

pub enum UpdateType {
    // TODO IMPLEMENT HASH FOR HASHSET! TO AVOID DUPLICATED OPERATIONS
    NewProposal { proposal_id: u64 },
    ProposalVote { proposal_id: u64 },
}

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
        skipper_address: TonAddress,
        rate_limiter: Arc<RateLimiter>,
        ton_client: &RestApiClientV2,
    ) -> anyhow::Result<()> {
        let trace_info = rate_limiter
            .throttle(|| ton_client.get_trace(self.trace_id.as_str()))
            .await
            .map_err(|err| anyhow::Error::msg(err.to_string()))?;

        let _acc = start_parsing(skipper_address, trace_info)?;

        Ok(())
    }
}
