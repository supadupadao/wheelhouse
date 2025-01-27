use crate::listener::Listener;
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

mod listener;

#[inline(always)]
fn prepare_logs() {
    tracing_subscriber::registry()
        .with(fmt::layer())
        .with(EnvFilter::from_default_env())
        .init();
}

async fn run() {
    let tonapi_client = RestApiClientV2::new(Network::Testnet, None);
    let rl = Arc::new(RateLimiter::new(Duration::from_secs(1)));
    let mut l = Listener::new(
        TonAddress::from_base64_std("0QCMsvusl1rl4rZemB3wtZgcqEB4vLftEFmWsAmEvDErsb00").unwrap(),
    );

    loop {
        let result = l.get_traces(rl.clone(), &tonapi_client).await.unwrap();

        println!("{:?}", result);
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
