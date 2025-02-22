use tonlib_core::cell::CellParser;
use tonstruct::fields::{Address, CellRef, Coins, Uint};
use tonstruct::FromCell;

fn load_opcode(parser: &mut CellParser) -> anyhow::Result<u32> {
    <Uint<32> as TryInto<u32>>::try_into(Uint::<32>::load(parser)?)
}

#[derive(FromCell, Debug)]
pub struct ProposalData {
    pub receiver: Address,
    // body: Cell;
}

#[derive(FromCell, Debug)]
pub struct RequestNewProposal {
    pub data: ProposalData,
}

#[derive(FromCell, Debug)]
pub struct VoteForProposal {
    pub proposal_id: Uint<64>,
    pub vote: bool,
}

#[derive(Debug)]
#[repr(u32)]
pub enum ProxyPayload {
    RequestNewProposal(RequestNewProposal) = 0x690401,
    VoteForProposal(VoteForProposal) = 0x690402,
}

impl FromCell for ProxyPayload {
    fn load(parser: &mut CellParser) -> anyhow::Result<Self> {
        let opcode = load_opcode(parser)?;

        match opcode {
            0x690401 => Ok(Self::RequestNewProposal(RequestNewProposal::load(parser)?)),
            0x690402 => Ok(Self::VoteForProposal(VoteForProposal::load(parser)?)),
            _ => Err(anyhow::anyhow!(
                "Unimplemented Skipper message: {:?}",
                opcode,
            )),
        }
    }
}

#[derive(FromCell, Debug)]
pub struct ProxyMessage {
    pub owner: Address,
    pub unlock_date: Uint<64>,
    pub amount: Coins,
    pub payload: CellRef<ProxyPayload>,
}

#[repr(u32)]
#[derive(Debug)]
pub enum SkipperMessages {
    Deploy = 0x946a98b6,
    ProxyMessage(ProxyMessage) = 0x690102,
}

impl FromCell for SkipperMessages {
    fn load(parser: &mut CellParser) -> anyhow::Result<Self> {
        let opcode = load_opcode(parser)?;

        match opcode {
            0x946a98b6 => Ok(SkipperMessages::Deploy),
            0x690102 => Ok(SkipperMessages::ProxyMessage(ProxyMessage::load(parser)?)),
            _ => Err(anyhow::anyhow!(
                "Unimplemented Skipper message: {:?}",
                opcode,
            )),
        }
    }
}
