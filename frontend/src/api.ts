export interface ProposalData {
  id: Number;
  votes_yes: Number;
  votes_no: Number;
  expires_at: Number;
}

export interface ProposalsResponse {
  proposals: ProposalData[]
}

export async function fetchProposalsList(dao: string): Promise<ProposalsResponse> {
  const params = new URLSearchParams({ dao });
  const result = await fetch("/api/proposals?" + params.toString());
  return await result.json() as ProposalsResponse;
}
