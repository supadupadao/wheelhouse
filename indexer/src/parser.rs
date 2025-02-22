use crate::consts;
use crate::messages::SkipperMessages;
use clap::Parser;
use tonapi::models::Trace;
use tonlib_core::cell::{BagOfCells, Cell, CellParser};
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

pub fn start_parsing(skipper_address: TonAddress, trace: Trace) -> anyhow::Result<Accumulator> {
    let accumulator = Accumulator::new(skipper_address);
    match_root(accumulator, trace)
}

fn childs_traversal(
    f: fn(Accumulator, Trace) -> anyhow::Result<Accumulator>,
    accumulator: Accumulator,
    childs: Option<Vec<Trace>>,
) -> anyhow::Result<Accumulator> {
    for child in childs.unwrap_or_default() {
        match f(accumulator.clone(), child) {
            Ok(acc) => return Ok(acc),
            Err(_) => {
                info!("Reached leaf trace");
            }
        };
    }

    Err(anyhow::anyhow!("No successful parses in current branch"))
}

fn match_root(mut accumulator: Accumulator, trace: Trace) -> anyhow::Result<Accumulator> {
    let current_address = TonAddress::from_hex_str(&trace.transaction.account.address)?;

    if current_address == accumulator.skipper_address {
        if let Some(in_msg) = trace.transaction.in_msg {
            let op_code = in_msg.op_code.unwrap_or_default();
            let body = in_msg.raw_body.unwrap_or_default();

            info!("OP_CODE: {}", op_code);

            let mut boc = BagOfCells::parse_hex(&body)?;
            let cell = boc.into_single_root()?.build()?;

            let p = SkipperMessages::from_cell(Cell::from(cell))?;

            info!("PARSED {:?}", p)
        }

        return Ok(accumulator);
    }

    childs_traversal(match_root, accumulator, trace.children)
}
