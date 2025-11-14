
# StreamFi - Real-Time Payment Streaming on Algorand

A decentralized payment streaming platform built on Algorand blockchain, enabling continuous, second-by-second token distribution.

## 🏆 Hackathon Project

This project demonstrates the implementation of ARC-20 token standard with a fully functional smart contract and web interface.

## ✨ Features

- ⛓️ **ARC-20 Token**: StreamFi Payment Token (STRM) - Asset ID: 749531304
- 📜 **Smart Contract**: PyTeal-based payment streaming logic - App ID: 749515555
- 🎨 **Interactive UI**: Real-time token accumulation and claiming
- 💼 **Multi-User Support**: 6 employees with different payment rates
- 🔐 **Wallet Integration**: Pera Wallet compatible

## 🏗️ Architecture

streamfi-simple/
├── contracts/ # Smart contract backend
│ ├── streamfi.py # PyTeal smart contract
│ ├── deploy.py # Deployment script
│ └── create_arc20_token.py # ARC-20 token creator
│
└── frontend/ # HTML/CSS/JS frontend
├── index.html
├── script.js
├── styles.css
└── assets/

text

## 🛠️ Tech Stack

- **Blockchain**: Algorand TestNet
- **Smart Contracts**: PyTeal
- **Token Standard**: ARC-20
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **SDK**: py-algorand-sdk

## 📋 Prerequisites

- Python 3.13+
- Algorand TestNet account with funds

## 🚀 Installation

1. **Clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/streamfi-simple.git
cd streamfi-simple
Install Python dependencies

text
pip install -r requirements.txt
Fund your TestNet account
Get free TestNet ALGO from: https://bank.testnet.algorand.network/

💻 Usage
Deploy Smart Contract
bash
cd contracts
python deploy.py
Create ARC-20 Token
text
python create_arc20_token.py
Run Frontend
bash
cd frontend
python -m http.server 8080
Open browser: http://localhost:8080

🔗 Live Deployment (TestNet)
Smart Contract: App ID 749515555

ARC-20 Token: Asset ID 749531304

👥 Team Members 
Anirudh - Blockchain Developer

Saksham - Frontend Engineer


🎯 Use Cases
💼 Freelancer platforms (pay per minute)

🚗 Gig economy (Uber, DoorDash)

📺 Subscription services

💰 Modern payroll systems

🎮 Gaming rewards

📝 License
MIT License - see LICENSE file for details

🙏 Acknowledgments
Algorand Foundation

PyTeal Documentation

Algorand Developer Community

🔐 Security Note
NEVER commit private keys or mnemonics to Git! Use environment variables or .env files (already in .gitignore).

Built with ❤️ for Algorand Hackathon 2025
