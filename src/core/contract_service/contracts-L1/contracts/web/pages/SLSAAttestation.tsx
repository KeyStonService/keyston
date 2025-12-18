import { useState } from 'react';
import Navbar from '@/components/layout/Navbar';
import Footer from '@/components/layout/Footer';
import { Shield, FileCheck, Upload, Download, Key } from 'lucide-react';

export default function SLSAAttestation() {
  const [selectedTab, setSelectedTab] = useState('create');
  const [attestationData, setAttestationData] = useState(null);
  const [loading, setLoading] = useState(false);

  const createAttestation = async (formData) => {
    setLoading(true);
    try {
      const response = await fetch('/api/v1/slsa/attestations', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      const result = await response.json();
      setAttestationData(result.data);
    } catch (error) {
      console.error('創建認證失敗:', error);
    } finally {
      setLoading(false);
    }
  };

  const verifyAttestation = async (provenance) => {
    setLoading(true);
    try {
      const response = await fetch('/api/v1/slsa/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ provenance })
      });
      const result = await response.json();
      return result.data;
    } catch (error) {
      console.error('驗證認證失敗:', error);
      return { valid: false };
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 text-slate-50">
      <Navbar />
      
      <div className="pt-32 pb-20 container mx-auto px-6">
        <div className="mb-12">
          <span className="text-blue-500 font-mono text-sm tracking-wider uppercase">SLSA Build Provenance</span>
          <h1 className="text-4xl font-bold mt-2 mb-4">供應鏈安全認證</h1>
          <p className="text-slate-400 text-lg max-w-3xl">
            使用 SLSA (Supply-chain Levels for Software Artifacts) 框架為您的軟件構建過程創建可驗證的溯源認證。
            確保軟件供應鏈的完整性和可信度。
          </p>
        </div>

        {/* Tab Navigation */}
        <div className="flex flex-wrap gap-4 mb-8 border-b border-slate-800">
          {[
            { id: 'create', label: '創建認證', icon: FileCheck },
            { id: 'verify', label: '驗證認證', icon: Shield },
            { id: 'contracts', label: '合約認證', icon: Key },
            { id: 'manage', label: '管理認證', icon: Upload }
          ].map(tab => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setSelectedTab(tab.id)}
                className={`flex items-center gap-2 px-4 py-2 rounded-t-lg border-b-2 transition-colors ${
                  selectedTab === tab.id 
                    ? 'border-blue-500 text-blue-400 bg-slate-800/50' 
                    : 'border-transparent text-slate-400 hover:text-slate-300'
                }`}
              >
                <Icon size={16} />
                {tab.label}
              </button>
            );
          })}
        </div>

        {/* Tab Content */}
        <div className="grid lg:grid-cols-2 gap-12">
          
          {selectedTab === 'create' && (
            <>
              <div className="bg-slate-950 p-8 rounded-2xl border border-slate-800">
                <h3 className="text-xl font-semibold mb-6 flex items-center gap-2">
                  <FileCheck className="text-blue-500" /> 創建 SLSA 認證
                </h3>
                
                <form onSubmit={(e) => {
                  e.preventDefault();
                  const formData = new FormData(e.target);
                  createAttestation({
                    subjectName: formData.get('subjectName'),
                    subjectDigest: formData.get('subjectDigest'),
                    builder: {
                      id: formData.get('builderId'),
                      version: formData.get('builderVersion')
                    }
                  });
                }} className="space-y-4">
                  
                  <div>
                    <label className="block text-sm font-medium mb-2">主體名稱</label>
                    <input
                      name="subjectName"
                      type="text"
                      placeholder="contract.sol"
                      className="w-full p-3 rounded-lg bg-slate-800 border border-slate-700 focus:border-blue-500 focus:outline-none"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">SHA256 摘要</label>
                    <input
                      name="subjectDigest"
                      type="text"
                      placeholder="sha256:..."
                      className="w-full p-3 rounded-lg bg-slate-800 border border-slate-700 focus:border-blue-500 focus:outline-none font-mono text-sm"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">構建器 ID</label>
                    <input
                      name="builderId"
                      type="text"
                      placeholder="https://github.com/actions/runner"
                      className="w-full p-3 rounded-lg bg-slate-800 border border-slate-700 focus:border-blue-500 focus:outline-none"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">構建器版本</label>
                    <input
                      name="builderVersion"
                      type="text"
                      placeholder="1.0.0"
                      className="w-full p-3 rounded-lg bg-slate-800 border border-slate-700 focus:border-blue-500 focus:outline-none"
                      required
                    />
                  </div>

                  <button
                    type="submit"
                    disabled={loading}
                    className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-slate-700 text-white py-3 px-4 rounded-lg font-medium transition-colors flex items-center justify-center gap-2"
                  >
                    {loading ? (
                      <div className="w-5 h-5 border-2 border-slate-400 border-t-transparent rounded-full animate-spin"></div>
                    ) : (
                      <>
                        <FileCheck size={18} />
                        創建認證
                      </>
                    )}
                  </button>
                </form>
              </div>

              <div className="bg-slate-950 p-8 rounded-2xl border border-slate-800">
                <h3 className="text-xl font-semibold mb-6">認證結果</h3>
                {attestationData ? (
                  <div className="space-y-4">
                    <div className="bg-green-900/20 border border-green-500/30 p-4 rounded-lg">
                      <div className="flex items-center gap-2 mb-2">
                        <Shield className="text-green-400" size={16} />
                        <span className="text-green-400 font-medium">認證創建成功</span>
                      </div>
                      <p className="text-sm text-slate-300">
                        認證 ID: {attestationData.attestationId}
                      </p>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium mb-2">SLSA 溯源數據</label>
                      <textarea
                        value={JSON.stringify(attestationData.provenance, null, 2)}
                        readOnly
                        className="w-full h-64 p-3 rounded-lg bg-slate-800 border border-slate-700 font-mono text-xs resize-none"
                      />
                    </div>

                    <button
                      onClick={() => {
                        const blob = new Blob([JSON.stringify(attestationData.provenance, null, 2)], 
                          { type: 'application/json' });
                        const url = URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = `attestation-${attestationData.attestationId}.json`;
                        a.click();
                        URL.revokeObjectURL(url);
                      }}
                      className="flex items-center gap-2 bg-slate-800 hover:bg-slate-700 text-slate-300 py-2 px-4 rounded-lg transition-colors"
                    >
                      <Download size={16} />
                      下載認證文件
                    </button>
                  </div>
                ) : (
                  <div className="text-center text-slate-400 py-12">
                    <FileCheck size={48} className="mx-auto mb-4 opacity-50" />
                    <p>填寫表單並提交以創建 SLSA 認證</p>
                  </div>
                )}
              </div>
            </>
          )}

          {selectedTab === 'verify' && (
            <>
              <div className="bg-slate-950 p-8 rounded-2xl border border-slate-800">
                <h3 className="text-xl font-semibold mb-6 flex items-center gap-2">
                  <Shield className="text-green-500" /> 驗證 SLSA 認證
                </h3>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">上傳認證文件 (JSON)</label>
                    <input
                      type="file"
                      accept=".json"
                      onChange={async (e) => {
                        const file = e.target.files[0];
                        if (file) {
                          try {
                            const content = await file.text();
                            const provenance = JSON.parse(content);
                            const result = await verifyAttestation(provenance);
                            setAttestationData({ verification: result, provenance });
                          } catch (error) {
                            console.error('文件讀取失敗:', error);
                          }
                        }
                      }}
                      className="w-full p-3 rounded-lg bg-slate-800 border border-slate-700 focus:border-green-500 focus:outline-none file:bg-green-600 file:text-white file:border-0 file:px-4 file:py-2 file:rounded file:mr-4"
                    />
                  </div>

                  <div className="text-center text-slate-400">
                    <p>或者</p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">貼上認證 JSON</label>
                    <textarea
                      placeholder="貼上 SLSA 溯源 JSON 數據..."
                      onChange={async (e) => {
                        try {
                          const provenance = JSON.parse(e.target.value);
                          const result = await verifyAttestation(provenance);
                          setAttestationData({ verification: result, provenance });
                        } catch (error) {
                          // JSON 格式錯誤，忽略
                        }
                      }}
                      className="w-full h-32 p-3 rounded-lg bg-slate-800 border border-slate-700 focus:border-green-500 focus:outline-none font-mono text-sm"
                    />
                  </div>
                </div>
              </div>

              <div className="bg-slate-950 p-8 rounded-2xl border border-slate-800">
                <h3 className="text-xl font-semibold mb-6">驗證結果</h3>
                {attestationData?.verification ? (
                  <div className="space-y-4">
                    <div className={`p-4 rounded-lg border ${
                      attestationData.verification.valid 
                        ? 'bg-green-900/20 border-green-500/30' 
                        : 'bg-red-900/20 border-red-500/30'
                    }`}>
                      <div className="flex items-center gap-2 mb-2">
                        <Shield className={attestationData.verification.valid ? 'text-green-400' : 'text-red-400'} size={16} />
                        <span className={`font-medium ${attestationData.verification.valid ? 'text-green-400' : 'text-red-400'}`}>
                          {attestationData.verification.valid ? '認證有效' : '認證無效'}
                        </span>
                      </div>
                      <p className="text-sm text-slate-300">
                        驗證時間: {new Date(attestationData.verification.timestamp).toLocaleString()}
                      </p>
                    </div>

                    {attestationData.provenance && (
                      <div>
                        <h4 className="font-medium mb-3">認證詳情</h4>
                        <div className="bg-slate-900 p-4 rounded-lg space-y-2 text-sm">
                          <div><span className="text-slate-400">類型:</span> {attestationData.provenance.predicateType}</div>
                          <div><span className="text-slate-400">主體數量:</span> {attestationData.provenance.subject?.length || 0}</div>
                          <div><span className="text-slate-400">構建類型:</span> {attestationData.provenance.predicate?.buildDefinition?.buildType}</div>
                          <div><span className="text-slate-400">構建器:</span> {attestationData.provenance.predicate?.runDetails?.builder?.id}</div>
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="text-center text-slate-400 py-12">
                    <Shield size={48} className="mx-auto mb-4 opacity-50" />
                    <p>上傳或貼上認證數據以開始驗證</p>
                  </div>
                )}
              </div>
            </>
          )}

          {selectedTab === 'contracts' && (
            <>
              <div className="bg-slate-950 p-8 rounded-2xl border border-slate-800">
                <h3 className="text-xl font-semibold mb-6 flex items-center gap-2">
                  <Key className="text-purple-500" /> 智能合約部署認證
                </h3>
                
                <form onSubmit={(e) => {
                  e.preventDefault();
                  // 處理合約認證邏輯
                }} className="space-y-4">
                  
                  <div>
                    <label className="block text-sm font-medium mb-2">合約名稱</label>
                    <input
                      type="text"
                      placeholder="MyToken"
                      className="w-full p-3 rounded-lg bg-slate-800 border border-slate-700 focus:border-purple-500 focus:outline-none"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">合約版本</label>
                    <input
                      type="text"
                      placeholder="1.0.0"
                      className="w-full p-3 rounded-lg bg-slate-800 border border-slate-700 focus:border-purple-500 focus:outline-none"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">部署者地址</label>
                    <input
                      type="text"
                      placeholder="0x..."
                      className="w-full p-3 rounded-lg bg-slate-800 border border-slate-700 focus:border-purple-500 focus:outline-none font-mono text-sm"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">合約程式碼</label>
                    <textarea
                      placeholder="pragma solidity ^0.8.0; contract MyToken { ... }"
                      className="w-full h-32 p-3 rounded-lg bg-slate-800 border border-slate-700 focus:border-purple-500 focus:outline-none font-mono text-sm"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">部署交易哈希</label>
                    <input
                      type="text"
                      placeholder="0xabc123def456..."
                      className="w-full p-3 rounded-lg bg-slate-800 border border-slate-700 focus:border-purple-500 focus:outline-none font-mono text-sm"
                    />
                  </div>

                  <button
                    type="submit"
                    disabled={loading}
                    className="w-full bg-purple-600 hover:bg-purple-700 disabled:bg-slate-700 text-white py-3 px-4 rounded-lg font-medium transition-colors flex items-center justify-center gap-2"
                  >
                    {loading ? (
                      <div className="w-5 h-5 border-2 border-slate-400 border-t-transparent rounded-full animate-spin"></div>
                    ) : (
                      <>
                        <Key size={18} />
                        創建合約認證
                      </>
                    )}
                  </button>
                </form>
              </div>

              <div className="bg-slate-950 p-8 rounded-2xl border border-slate-800">
                <h3 className="text-xl font-semibold mb-6">合約認證說明</h3>
                <div className="space-y-4 text-slate-400">
                  <p>
                    智能合約部署認證提供了對合約部署過程的完整溯源記錄，包括：
                  </p>
                  <ul className="list-disc pl-6 space-y-2">
                    <li>合約程式碼的完整性驗證</li>
                    <li>部署者身份確認</li>
                    <li>部署時間和環境記錄</li>
                    <li>交易哈希和區塊鏈確認</li>
                  </ul>
                  <div className="bg-purple-900/20 border border-purple-500/30 p-4 rounded-lg mt-6">
                    <div className="flex items-center gap-2 mb-2">
                      <Key className="text-purple-400" size={16} />
                      <span className="text-purple-400 font-medium">重要提示</span>
                    </div>
                    <p className="text-sm">
                      部署認證將創建一個永久的、不可篡改的記錄，證明合約的真實性和部署歷史。
                      請確保所有信息準確無誤。
                    </p>
                  </div>
                </div>
              </div>
            </>
          )}

        </div>
      </div>
      
      <Footer />
    </div>
  );
}