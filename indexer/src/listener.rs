//! Trace listener module

use std::sync::Arc;
use tokio_utils::RateLimiter;
use tonapi::RestApiClientV2;
use tonlib_core::TonAddress;

pub struct Listener {
    account: String,
    last_trace_id: String,
}

impl Listener {
    const PAGINATION_MAX_LIMIT: u64 = 1000;

    pub fn new(account: TonAddress) -> Self {
        Self {
            account: account.to_hex(),
            last_trace_id: Default::default(),
        }
    }

    pub async fn get_traces(
        &mut self,
        rate_limiter: Arc<RateLimiter>,
        ton_client: &RestApiClientV2,
    ) -> anyhow::Result<Vec<String>> {
        let mut result = Vec::new();
        let mut before_lt = None;

        loop {
            let traces_result = rate_limiter
                .throttle(|| {
                    ton_client.get_account_traces(
                        &self.account,
                        before_lt,
                        Some(Self::PAGINATION_MAX_LIMIT),
                    )
                })
                .await
                .map_err(|err| anyhow::Error::msg(err.to_string()))?;

            if traces_result.traces.is_empty() {
                break;
            }

            for trace in traces_result.traces {
                result.push(trace.id);
                before_lt = Some(trace.utime);
            }
        }

        Ok(result)
    }
}
