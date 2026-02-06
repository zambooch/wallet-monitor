# Solana Wallet Token Creation Monitor

A lightweight Python script that monitors a single Solana wallet for new token creations (via Token Program or Token-2022).  
Every few minutes, it checks the wallet's recent transactions and sends a Telegram alert if a new token mint is detected (specifically the `initializeMint` instruction).

## Features

- Monitors recent transactions using public Solana RPC (no API keys required)
- Detects new token creation (`initializeMint` in Token or Token-2022 programs)
- Sends Telegram notifications with:
  - Mint address of the new token
  - Direct link to the transaction on Solscan
  - Timestamp of the event
- All sensitive configuration stored in `.env`
- Runs continuously with a configurable interval (default: 5 minutes)


