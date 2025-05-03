use crate::parser::{start_parsing, Ops};
use clap::builder::TypedValueParser;
use sea_orm::{ActiveModelTrait, ColumnTrait, DatabaseConnection, EntityTrait, QueryFilter, Set};
use std::sync::Arc;
use tokio_utils::RateLimiter;
use tonapi::models::TvmStackRecord;
use tonapi::RestApiClientV2;
use tonlib_core::cell::BagOfCells;
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

        let acc = start_parsing(skipper_address.clone(), trace_info, db)?;

        match acc.op {
            Some(Ops::NewProposal { proposal_address }) => {
                let hex_address = proposal_address.to_hex();
                let proposal_info = rate_limiter
                    .throttle(|| {
                        ton_client.exec_get_method_for_blockchain_account(
                            hex_address.as_str(),
                            "get_proposal_data",
                            None,
                        )
                    })
                    .await
                    .map_err(|err| anyhow::Error::msg(err.to_string()))?;
                if proposal_info.success {
                    let mut stack_iter = proposal_info.stack.into_iter();

                    let stack_item = stack_iter
                        .next()
                        .ok_or_else(|| anyhow::Error::msg("empty stack"))?;
                    let cell = match stack_item {
                        TvmStackRecord::Tuple { tuple: Some(tuple) } => {
                            let mut sub_stack_iter = tuple.into_iter();

                            let sub_stack_item = sub_stack_iter
                                .next()
                                .ok_or_else(|| anyhow::Error::msg("empty stack"))?;

                            match sub_stack_item {
                                TvmStackRecord::Cell { cell: Some(cell) } => {
                                    let mut boc = BagOfCells::parse_hex(&cell)
                                        .map_err(|err| anyhow::Error::msg(err.to_string()))?;
                                    boc.into_single_root()
                                        .map_err(|err| anyhow::Error::msg(err.to_string()))?
                                }

                                _ => {
                                    return Err(anyhow::Error::msg(format!(
                                        "Invalid stack type: {:?}",
                                        sub_stack_item
                                    )))
                                }
                            }
                        }
                        _ => {
                            return Err(anyhow::Error::msg(format!(
                                "Invalid stack type: {:?}",
                                stack_item
                            )))
                        }
                    };
                    let mut parser = cell.parser();

                    let proposal_id = parser.load_u64(64)?.reverse_bits();
                    info!("New proposal {:?}", proposal_id);

                    let proposals = entities::proposal::Entity::find()
                        .filter(entities::proposal::Column::Id.eq(proposal_id as i64))
                        .filter(
                            entities::proposal::Column::DaoAddress
                                .eq(skipper_address.hash_part.to_vec()),
                        )
                        .all(db)
                        .await?;
                    if proposals.is_empty() {
                        let proposal = entities::proposal::ActiveModel {
                            dao_address: Set(skipper_address.hash_part.to_vec()),
                            id: Set(proposal_id as i64),
                        };
                        proposal.insert(db).await?;
                        info!("New proposal created: {:?}", proposal_id);
                    }
                }
            }
            Some(Ops::VoteForProposal { proposal_id }) => {
                // TODO
                info!("Vote proposal created: {:?}", proposal_id);
            }

            None => {}
        }

        Ok(())
    }
}
