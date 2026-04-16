import { useState } from 'react'
import { motion } from 'framer-motion'
import { Shield, ShieldAlert, CheckCircle, ExternalLink, Activity, Server, FileText, Database } from 'lucide-react'
import axios from 'axios'

function App() {
  const [url, setUrl] = useState('')
  const [isScanning, setIsScanning] = useState(false)
  const [results, setResults] = useState(null)
  const [error, setError] = useState(null)

  const handleScan = async (e) => {
    e.preventDefault()
    if (!url) return
    
    setIsScanning(true)
    setError(null)
    setResults(null)
    
    try {
      // Automatically detect if running locally or on EC2 public IP
      const backendUrl = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
        ? 'http://127.0.0.1:5000/api/scan' 
        : `http://${window.location.hostname}:5000/api/scan`;
        
      const response = await axios.post(backendUrl, { url })
      setResults(response.data)
    } catch (err) {
      console.error(err)
      setError("Failed to reach scanner engine. Ensure backend is running.")
    } finally {
      setIsScanning(false)
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-200 p-8 font-sans">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <header className="flex items-center gap-4 mb-12">
          <div className="p-3 bg-blue-600/20 rounded-xl border border-blue-500/20">
            <Shield className="w-8 h-8 text-blue-400" />
          </div>
          <div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-emerald-400 bg-clip-text text-transparent tracking-tight">
              Nimbus Security
            </h1>
            <p className="text-slate-400 text-sm mt-1">AWS-Integrated Web Vulnerability Scanner</p>
          </div>
        </header>

        {/* Hero / Input Section */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-slate-900 border border-slate-800 rounded-2xl p-8 shadow-2xl mb-8 relative overflow-hidden"
        >
          <div className="absolute top-0 right-0 -mr-20 -mt-20 w-64 h-64 bg-blue-500/10 blur-3xl rounded-full"></div>
          
          <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
             <Activity className="text-blue-400 w-5 h-5"/>
             Initiate New Scan
          </h2>
          <form onSubmit={handleScan} className="flex flex-col sm:flex-row gap-4 relative z-10">
            <div className="flex-1 relative">
              <ExternalLink className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500 w-5 h-5" />
              <input
                type="text"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://example.com"
                className="w-full bg-slate-950 border border-slate-800 rounded-xl py-4 pl-12 pr-4 outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500/50 transition-all text-slate-200 placeholder:text-slate-600 shadow-inner"
              />
            </div>
            <button
              disabled={isScanning || !url}
              className={`px-8 py-4 sm:py-0 rounded-xl font-medium flex items-center justify-center gap-2 transition-all ${
                isScanning 
                  ? 'bg-blue-900/50 text-blue-300 border border-blue-800 cursor-not-allowed'
                  : 'bg-blue-600 hover:bg-blue-500 shadow-lg shadow-blue-500/20 text-white'
              }`}
            >
              {isScanning ? (
                <>
                  <Activity className="w-5 h-5 animate-pulse" />
                  Scanning...
                </>
              ) : (
                'Run Analysis'
              )}
            </button>
          </form>
          {error && <p className="text-red-400 mt-4 text-sm bg-red-400/10 p-3 rounded-lg border border-red-400/20 inline-block">{error}</p>}
        </motion.div>

        {/* Results Section */}
        {results && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
          >
            <h3 className="text-xl font-semibold flex items-center gap-2 border-b border-slate-800 pb-4">
              <Activity className="text-emerald-400 w-5 h-5" />
              Scan Results for <span className="text-blue-400">{results.target}</span>
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-sm">
              
              {/* Security Headers */}
              <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-6 transition-all hover:border-slate-700">
                <div className="flex items-center gap-3 mb-4">
                  <div className="p-2 bg-purple-500/10 rounded-lg">
                    <Server className="text-purple-400 w-5 h-5" />
                  </div>
                  <h4 className="font-medium text-lg">Security Headers</h4>
                </div>
                {results.security_headers?.issues_found?.length ? (
                  <ul className="space-y-3">
                    {results.security_headers.issues_found.map((issue, i) => (
                      <li key={i} className="flex items-start gap-2 text-red-300 bg-red-500/5 p-3 rounded-lg border border-red-500/10">
                        <ShieldAlert className="w-4 h-4 mt-0.5 shrink-0 text-red-400" />
                        {issue}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-emerald-400 flex items-center gap-2 bg-emerald-500/5 p-3 rounded-lg border border-emerald-500/10">
                    <CheckCircle className="w-4 h-4" /> No header issues found.
                  </p>
                )}
              </div>

              {/* XSS & SQLi */}
              <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-6 transition-all hover:border-slate-700">
                 <div className="flex items-center gap-3 mb-4">
                  <div className="p-2 bg-orange-500/10 rounded-lg">
                    <Database className="text-orange-400 w-5 h-5" />
                  </div>
                  <h4 className="font-medium text-lg">Injection Flaws</h4>
                </div>
                {results.xss_vulnerabilities?.issues?.length || results.sqli_vulnerabilities?.issues?.length ? (
                  <ul className="space-y-3">
                    {results.xss_vulnerabilities?.issues?.map((issue, i) => (
                      <li key={i} className="flex items-start gap-2 text-red-300 bg-red-500/5 p-3 rounded-lg border border-red-500/10">
                        <ShieldAlert className="w-4 h-4 mt-0.5 shrink-0 text-red-400" />
                        {issue}
                      </li>
                    ))}
                    {results.sqli_vulnerabilities?.issues?.map((issue, i) => (
                      <li key={`sqli-${i}`} className="flex items-start gap-2 text-red-300 bg-red-500/5 p-3 rounded-lg border border-red-500/10">
                         <ShieldAlert className="w-4 h-4 mt-0.5 shrink-0 text-red-400" />
                        {issue}
                      </li>
                    ))}
                  </ul>
                ) : (
                   <p className="text-emerald-400 flex items-center gap-2 bg-emerald-500/5 p-3 rounded-lg border border-emerald-500/10">
                    <CheckCircle className="w-4 h-4" /> No injection vulnerabilities detected.
                  </p>
                )}
              </div>
              
               {/* Directory Exposure */}
              <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-6 transition-all hover:border-slate-700 md:col-span-2">
                 <div className="flex items-center gap-3 mb-4">
                  <div className="p-2 bg-yellow-500/10 rounded-lg">
                    <FileText className="text-yellow-400 w-5 h-5" />
                  </div>
                  <h4 className="font-medium text-lg">Directory Exposure</h4>
                </div>
                {results.directory_exposure?.issues?.length ? (
                  <ul className="space-y-3 grid grid-cols-1 md:grid-cols-2 gap-4">
                    {results.directory_exposure?.issues?.map((issue, i) => (
                      <li key={i} className="flex items-start gap-2 text-yellow-300 bg-yellow-500/5 p-3 rounded-lg border border-yellow-500/10">
                        <ShieldAlert className="w-4 h-4 mt-0.5 shrink-0 text-yellow-400" />
                        {issue}
                      </li>
                    ))}
                  </ul>
                ) : (
                   <p className="text-emerald-400 flex items-center gap-2 bg-emerald-500/5 p-3 rounded-lg border border-emerald-500/10 inline-block">
                    <CheckCircle className="w-4 h-4 inline mr-2" /> No exposed sensitive directories discovered.
                  </p>
                )}
              </div>

            </div>
          </motion.div>
        )}
      </div>
    </div>
  )
}

export default App
