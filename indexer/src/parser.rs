use tonapi::models::Trace;
use tonlib_core::TonAddress;

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
        // CORRECT TRANSACTION! PARSE IT!

        return Ok(accumulator);
    }

    childs_traversal(match_root, accumulator, trace.children)
}
