import type { Address } from "@ton/core";

export function cropTonAddress(address: Address): string {
  const str = address.toString();
  return `${str.slice(0, 6)}...${str.slice(-4)}`;
}
