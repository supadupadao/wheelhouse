use crate::account::AccountTracesListener;
use crate::conf::conf;
use sea_orm::sea_query::Expr;
use sea_orm::{ColumnTrait, Database, EntityTrait, QueryFilter};
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
mod consts;
mod messages;
mod parser;
mod traces;

#[inline(always)]
fn prepare_logs() {
    tracing_subscriber::registry()
        .with(fmt::layer())
        .with(EnvFilter::from_default_env())
        .init();
}

async fn run() -> anyhow::Result<()> {
    let c = conf();

    let db = Database::connect(&c.db).await?;

    let skipper_address = TonAddress::from_base64_url(c.dao_address.as_str()).unwrap();

    let dao_db = {
        let db_result = entities::dao::Entity::find()
            .filter(entities::dao::Column::Address.eq(skipper_address.hash_part.to_vec()))
            .one(&db)
            .await?;
        match db_result {
            None => {
                let model = entities::dao::Model {
                    address: skipper_address.hash_part.to_vec(),
                    jetton_address: vec![],
                    trace_id: None,
                };
                let result = entities::dao::Entity::insert::<entities::dao::ActiveModel>(
                    model.clone().into(),
                )
                .exec(&db)
                .await?;
                model
            }
            Some(dao) => dao,
        }
    };

    let tonapi_client = RestApiClientV2::new(Network::Testnet, None);
    let rl = Arc::new(RateLimiter::new(Duration::from_secs(1)));
    let mut l = AccountTracesListener::new(skipper_address.clone());

    let mut last_trace = dao_db.trace_id;
    loop {
        let mut result = l.get_traces(rl.clone(), &tonapi_client).await.unwrap();

        if result.is_empty() {
            debug!("No traces");
            continue;
        }

        while let Some(trace) = result.pop() {
            info!("Started parsing trace {:?}", trace.get_trace_id());
            let result = trace
                .handle(skipper_address.clone(), rl.clone(), &tonapi_client, &db)
                .await;
            match result {
                Ok(_) => {
                    info!("Successfuly parsed trace")
                }
                Err(_) => {
                    error!("Failed to parse the trace")
                }
            }
            last_trace = Some(trace.get_trace_id());
        }

        if let Some(ref t) = last_trace {
            entities::dao::Entity::update_many()
                .col_expr(entities::dao::Column::TraceId, Expr::value(t))
                .filter(entities::dao::Column::Address.eq(skipper_address.hash_part.to_vec()))
                .exec(&db)
                .await?;

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
        .block_on(run())
        .unwrap();
}
