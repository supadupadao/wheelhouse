use crate::account::AccountTracesListener;
use crate::conf::conf;
use crate::parser::start_parsing;
use std::sync::Arc;
use std::time::Duration;
use tokio_utils::RateLimiter;
use tonapi::{Network, RestApiClientV2};
use tonlib_core::TonAddress;
use tracing_subscriber::layer::SubscriberExt;
use tracing_subscriber::util::SubscriberInitExt;
use tracing_subscriber::{fmt, EnvFilter};

#[macro_use]
extern crate tracing;

mod account;
mod conf;
mod parser;
mod traces;

#[inline(always)]
fn prepare_logs() {
    tracing_subscriber::registry()
        .with(fmt::layer())
        .with(EnvFilter::from_default_env())
        .init();
}

async fn run() {
    let c = conf();

    let skipper_address = TonAddress::from_base64_url(c.dao_address.as_str()).unwrap();

    let tonapi_client = RestApiClientV2::new(Network::Testnet, None);
    let rl = Arc::new(RateLimiter::new(Duration::from_secs(1)));
    let mut l = AccountTracesListener::new(skipper_address.clone());

    let mut last_trace = None;
    loop {
        let mut result = l.get_traces(rl.clone(), &tonapi_client).await.unwrap();

        while let Some(trace) = result.pop() {
            trace
                .handle(skipper_address.clone(), rl.clone(), &tonapi_client)
                .await
                .unwrap();
            last_trace = Some(trace.get_trace_id());
        }

        if let Some(ref t) = last_trace {
            l.set_last_trace_id(t.clone());
        }
    }
}

fn main() {
    prepare_logs();

    tokio::runtime::Builder::new_current_thread()
        .enable_all()
        .build()
        .unwrap()
        .block_on(run());

    info!("Hello");
}
