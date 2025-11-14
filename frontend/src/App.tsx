import { Buffer } from 'buffer'
import { useState } from 'react'
import { PeraWalletConnect } from '@perawallet/connect'
import algosdk from 'algosdk'

// @ts-ignore
window.Buffer = Buffer

const peraWallet = new PeraWalletConnect()

export default function App() {
  const [accountAddress, setAccountAddress] = useState<string | null>(null)
  const [workerAddress, setWorkerAddress] = useState('')
  const [ratePerSecond, setRatePerSecond] = useState('1000')
  const [status, setStatus] = useState('')

  const APP_ID = 749515555
  const algodClient = new algosdk.Algodv2('', 'https://testnet-api.algonode.cloud', '')

  peraWallet.reconnectSession().then((accounts) => {
    if (accounts.length) {
      setAccountAddress(accounts[0])
    }
  })

  const connectWallet = async () => {
    try {
      const accounts = await peraWallet.connect()
      setAccountAddress(accounts[0])
      setStatus('✅ Pera Wallet connected!')
    } catch (error) {
      setStatus(`❌ Connection failed: ${error}`)
    }
  }

  const disconnectWallet = () => {
    peraWallet.disconnect()
    setAccountAddress(null)
    setStatus('Disconnected')
  }

  const createStream = async () => {
    if (!accountAddress) return alert('Connect wallet first!')
    
    try {
      setStatus('Creating stream...')
      
      const suggestedParams = await algodClient.getTransactionParams().do()
      
      const appArgs = [
        new Uint8Array(Buffer.from(workerAddress)),
        algosdk.encodeUint64(parseInt(ratePerSecond))
      ]
      
      const txn = algosdk.makeApplicationCallTxnFromObject({
        sender: accountAddress,  // FIXED: from → sender
        appIndex: APP_ID,
        appArgs,
        suggestedParams,
        onComplete: algosdk.OnApplicationComplete.NoOpOC
      })
      
      const singleTxnGroups = [{ txn, signers: [accountAddress] }]
      const signedTxn = await peraWallet.signTransaction([singleTxnGroups])
      
      const response = await algodClient.sendRawTransaction(signedTxn).do()  // FIXED: split into two lines
      const txId = response.txid
      setStatus(`✅ Stream created! TX: ${txId}`)
      console.log('https://testnet.algoexplorer.io/tx/' + txId)
    } catch (error) {
      setStatus(`❌ Error: ${error}`)
    }
  }

  return (
    <div style={{ padding: '40px', maxWidth: '800px', margin: '0 auto', fontFamily: 'Arial', background: '#1a1a1a', color: 'white', minHeight: '100vh' }}>
      <h1>💸 StreamFI - Real-Time Payment Streaming</h1>
      <p><strong>Contract ID:</strong> {APP_ID}</p>
      <p><strong>Network:</strong> Algorand TestNet</p>
      
      {!accountAddress ? (
        <div>
          <button onClick={connectWallet} style={{ padding: '12px 24px', fontSize: '16px', cursor: 'pointer', background: '#FFD23F', color: '#000', border: 'none', borderRadius: '8px', fontWeight: 'bold' }}>
            🔗 Connect Pera Wallet
          </button>
          <p style={{ marginTop: '10px', fontSize: '12px', color: '#888' }}>
            📱 Download Pera Wallet mobile app first: <a href="https://perawallet.app" target="_blank" style={{ color: '#FFD23F' }}>perawallet.app</a>
          </p>
        </div>
      ) : (
        <div>
          <p>✅ Connected: <code style={{ background: '#333', padding: '5px 10px', borderRadius: '5px' }}>{accountAddress.slice(0, 8)}...{accountAddress.slice(-8)}</code></p>
          <button onClick={disconnectWallet} style={{ padding: '8px 16px', marginBottom: '20px', background: '#444', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer' }}>
            Disconnect
          </button>
          
          <h3>Create Payment Stream:</h3>
          <div style={{ marginBottom: '20px' }}>
            <input
              placeholder="Worker Algorand Address"
              value={workerAddress}
              onChange={(e) => setWorkerAddress(e.target.value)}
              style={{ width: '100%', padding: '10px', marginBottom: '10px', fontSize: '14px', borderRadius: '5px', border: '1px solid #444', background: '#2a2a2a', color: 'white' }}
            />
            <input
              placeholder="Rate per second (microALGOs)"
              value={ratePerSecond}
              onChange={(e) => setRatePerSecond(e.target.value)}
              style={{ width: '100%', padding: '10px', marginBottom: '10px', fontSize: '14px', borderRadius: '5px', border: '1px solid #444', background: '#2a2a2a', color: 'white' }}
            />
            <button onClick={createStream} style={{ padding: '12px 24px', fontSize: '16px', cursor: 'pointer', background: '#4CAF50', color: 'white', border: 'none', borderRadius: '8px', fontWeight: 'bold' }}>
              🚀 Create Stream
            </button>
          </div>
          
          {status && (
            <div style={{ 
              padding: '15px', 
              background: status.includes('✅') ? '#1e4620' : '#4a1e1e',
              border: `1px solid ${status.includes('✅') ? '#2e7d32' : '#d32f2f'}`,
              borderRadius: '8px',
              marginTop: '20px'
            }}>
              {status}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
