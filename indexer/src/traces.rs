use crate::parser::{start_parsing, Ops};
use sea_orm::DatabaseConnection;
use std::sync::Arc;
use tokio_utils::RateLimiter;
use tonapi::RestApiClientV2;
use tonlib_core::TonAddress;

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
        db: &DatabaseConnection,
    ) -> anyhow::Result<()> {
        let trace_info = rate_limiter
            .throttle(|| ton_client.get_trace(self.trace_id.as_str()))
            .await
            .map_err(|err| anyhow::Error::msg(err.to_string()))?;

        let acc = start_parsing(skipper_address, trace_info, db)?;

        match acc.op {
            Some(Ops::NewProposal {}) => {
                // TODO
                info!("New proposal created");
            }
            Some(Ops::VoteForProposal {}) => {
                // TODO
                info!("Vote proposal created");
            }

            None => {}
        }

        Ok(())
    }
}
