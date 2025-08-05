# Song Registry DApp - Algorand

A Flask web application that connects to an Algorand smart contract for registering and viewing songs on the blockchain.

## Quick Start

### Prerequisites
- Python 3.7+
- Pera Wallet (for TestNet ALGO)

### Setup

1. **Clone and install dependencies:**
```bash
git clone https://github.com/edzaniBruce51/song-registry-smart-contract.git
cd song-registry-smart-contract
pip install -r requirements.txt
```

2. **Deploy smart contract:**
```bash
python song_registry_contract.py  # Compile contract
python deploy_contract.py         # Deploy to TestNet
```

3. **Configure environment:**
   - Copy your 24-word mnemonic from Pera Wallet
   - Add it to `.env` file as `ALGOWALLET_MNEMONIC`

4. **Run the app:**
```bash
python app.py
```

Visit `http://127.0.0.1:5000` to use the DApp.

## Features

- Register songs with title, URL, and price on Algorand
- View all registered songs from the blockchain
- Simple web interface for Algorand interaction
- Runs on Algorand TestNet

## Tech Stack

- **Frontend:** Flask, HTML, CSS
- **Blockchain:** Algorand, PyTeal, TEAL
- **Integration:** Algorand Python SDK
- **Wallet:** Pera Wallet

## Algorand Integration

- Smart contract written in PyTeal
- Deployed on Algorand TestNet
- Uses global state for song storage
- Connected via Algorand Python SDK
