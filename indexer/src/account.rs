//! Trace listener module
//!
//! # Example
//!
//! ```
//! let tonapi_client = RestApiClientV2::new(Network::Testnet, None);
//! let rate_limiter = Arc::new(RateLimiter::new(Duration::from_secs(1)));
//! let mut listener = AccountTracesListener::new(TonAddress::from_base64_std(c.dao_address.as_str()).unwrap());
//!
//! let mut last_trace = None;
//! loop {
//!     let mut result = listener.get_traces(rate_limiter.clone(), &tonapi_client).await.unwrap();
//!
//!     while let Some(trace) = result.pop() {
//!         last_trace = Some(trace);
//!     }
//!
//!     if let Some(ref t) = last_trace {
//!         listener.set_last_trace_id(t.clone());
//!     }
//! }
//! ```
use crate::traces::TraceHandler;
use std::sync::Arc;
use tokio_utils::RateLimiter;
use tonapi::RestApiClientV2;
use tonlib_core::TonAddress;

/// Struct for traces fetching by API.
///
/// It stores last fetched trace id to avoid duplicates and support pagination
pub struct AccountTracesListener {
    account: String,
    last_trace_id: String,
}

impl AccountTracesListener {
    /// Max allowed pagination page size in TONAPI
    const PAGINATION_MAX_LIMIT: u64 = 1000;

    /// Initiate new listener
    pub fn new(account: TonAddress) -> Self {
        Self {
            account: account.to_hex(),
            last_trace_id: Default::default(),
        }
    }

    /// Update stored last fetched trace
    pub fn set_last_trace_id(&mut self, trace_id: String) {
        self.last_trace_id = trace_id;
    }

    /// Fetch paginated traces
    pub async fn get_traces(
        &mut self,
        rate_limiter: Arc<RateLimiter>,
        ton_client: &RestApiClientV2,
    ) -> anyhow::Result<Vec<TraceHandler>> {
        let mut result = Vec::new();
        let mut before_lt = None;

        debug!("Starting tracing fetch");
        'root: loop {
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
            debug!("Getting traces page: {} items", traces_result.traces.len());

            if traces_result.traces.is_empty() {
                debug!("No traces found. Exiting.");
                break;
            }

            for trace in traces_result.traces {
                trace!("Trace id: {:?}", trace.id);
                if trace.id == self.last_trace_id {
                    debug!("Reached last trace id. Exiting.");
                    break 'root;
                }
                result.push(TraceHandler::new(trace.id));
                before_lt = Some(trace.utime);
            }
        }
        debug!("Finished fetching traces. {} items", result.len());

        Ok(result)
    }
}
