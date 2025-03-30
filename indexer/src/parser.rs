use crate::messages::{InitProposal, ProxyPayload, SkipperMessages, VoteForProposal};
use sea_orm::DatabaseConnection;
use tonapi::models::Trace;
use tonlib_core::cell::BagOfCells;
use tonlib_core::message::TonMessage;
use tonlib_core::TonAddress;
use tonstruct::fields::{Address, CellRef, Coins, Int, Uint};
use tonstruct::FromCell;

#[derive(Clone)]
pub struct Accumulator {
    skipper_address: TonAddress,
}

impl Accumulator {
    pub fn new(skipper_address: TonAddress) -> Accumulator {
        Accumulator { skipper_address }
    }
}

pub fn start_parsing(
    skipper_address: TonAddress,
    trace: Trace,
    db: &DatabaseConnection,
) -> anyhow::Result<Accumulator> {
    let accumulator = Accumulator::new(skipper_address);
    match_root(accumulator, trace, db)
}

fn childs_traversal(
    f: fn(Accumulator, Trace, &DatabaseConnection) -> anyhow::Result<Accumulator>,
    accumulator: Accumulator,
    childs: Option<Vec<Trace>>,
    db: &DatabaseConnection,
) -> anyhow::Result<Accumulator> {
    for child in childs.unwrap_or_default() {
        match f(accumulator.clone(), child, db) {
            Ok(acc) => return Ok(acc),
            Err(err) => {
                debug!("Reached leaf trace: {}", err);
            }
        };
    }

    Err(anyhow::anyhow!("No successful parses in current branch"))
}

fn match_root(
    mut accumulator: Accumulator,
    trace: Trace,
    db: &DatabaseConnection,
) -> anyhow::Result<Accumulator> {
    let current_address = TonAddress::from_hex_str(&trace.transaction.account.address)?;

    if current_address == accumulator.skipper_address {
        if let Some(in_msg) = trace.transaction.in_msg {
            let body = in_msg.raw_body.unwrap_or_default();

            let mut boc = BagOfCells::parse_hex(&body)?;
            let cell = boc.into_single_root()?.build()?;

            if let Ok(SkipperMessages::ProxyMessage(skipper_root_message)) =
                SkipperMessages::from_cell(cell)
            {
                return match skipper_root_message.payload.inner() {
                    ProxyPayload::RequestNewProposal(_) => childs_traversal(
                        match_request_new_proposal,
                        accumulator,
                        trace.children,
                        db,
                    ),
                    ProxyPayload::VoteForProposal(_) => {
                        childs_traversal(match_vote_for_proposal, accumulator, trace.children, db)
                    }
                };
            }
        }

        return Ok(accumulator);
    }

    childs_traversal(match_root, accumulator, trace.children, db)
}

fn match_request_new_proposal(
    mut accumulator: Accumulator,
    trace: Trace,
    db: &DatabaseConnection,
) -> anyhow::Result<Accumulator> {
    if let Some(in_msg) = trace.transaction.in_msg {
        let body = in_msg.raw_body.unwrap_or_default();

        let mut boc = BagOfCells::parse_hex(&body)?;
        let cell = boc.into_single_root()?.build()?;

        if let Ok(init_proposal) = InitProposal::from_cell(cell) {
            info!("New proposal: {:?}", init_proposal);
            // accumulator.proposal_address = Some(TonAddress::from_base64_std(
            //     &trace.transaction.account.address,
            // )?);
            return childs_traversal(match_success, accumulator, trace.children, db);
        }
    }

    childs_traversal(match_request_new_proposal, accumulator, trace.children, db)
}

fn match_vote_for_proposal(
    mut accumulator: Accumulator,
    trace: Trace,
    db: &DatabaseConnection,
) -> anyhow::Result<Accumulator> {
    if let Some(in_msg) = trace.transaction.in_msg {
        let body = in_msg.raw_body.unwrap_or_default();

        let mut boc = BagOfCells::parse_hex(&body)?;
        let cell = boc.into_single_root()?.build()?;

        if let Ok(vote_for_proposal) = VoteForProposal::from_cell(cell) {
            info!("Vote for proposal: {:?}", vote_for_proposal);
            // accumulator.proposal_address = Some(TonAddress::from_base64_std(
            //     &trace.transaction.account.address,
            // )?);
            return childs_traversal(match_success, accumulator, trace.children, db);
        }
    }

    childs_traversal(match_vote_for_proposal, accumulator, trace.children, db)
}

fn match_success(
    accumulator: Accumulator,
    trace: Trace,
    db: &DatabaseConnection,
) -> anyhow::Result<Accumulator> {
    if !trace.transaction.success {
        return Err(anyhow::anyhow!("Found failed transaction"));
    }

    if trace.children.is_some() {
        return childs_traversal(match_success, accumulator, trace.children, db);
    }

    Ok(accumulator)
}
