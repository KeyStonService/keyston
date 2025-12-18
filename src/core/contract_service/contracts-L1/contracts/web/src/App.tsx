import React, { useState } from 'react';
import { Shield, CheckCircle, AlertCircle, Upload, Download, FileText } from 'lucide-react';

interface Attestation {
  id: string;
  type: string;
  timestamp: string;
  data?: any;
}

const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'create' | 'verify' | 'digest' | 'history'>('create');
  const [attestations, setAttestations] = useState<Attestation[]>([]);
  const [result, setResult] = useState<any>(null);

  const createAttestation = async (formData: FormData) => {
    try {
      const response = await fetch('/api/v1/provenance/attestations', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          buildId: formData.get('buildId'),
          version: formData.get('version'),
          environment: formData.get('environment'),
          sourceRepo: formData.get('sourceRepo'),
          metadata: {
            buildTrigger: formData.get('buildTrigger'),
            builder: formData.get('builder')
          }
        }),
      });
      const result = await response.json();
      if (result.success) {
        setAttestations(prev => [result.data, ...prev]);
        setResult(result);
      } else {
        throw new Error(result.error || 'Failed to create attestation');
      }
    } catch (error) {
      alert('認證創建失敗：' + (error as Error).message);
    }
  };

  const verifyAttestation = async (provenance: string) => {
    try {
      const response = await fetch('/api/v1/provenance/verify', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ attestation: provenance }),
      });
      const result = await response.json();
      setResult(result);
    } catch (error) {
      alert('驗證失敗：' + (error as Error).message);
    }
  };

  const generateDigest = async (content: string) => {
    try {
      const response = await fetch('/api/v1/slsa/digest', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ content }),
      });
      const result = await response.json();
      setResult(result);
    } catch (error) {
      alert('生成摘要失敗：' + (error as Error).message);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <header className="bg-slate-900 border-b border-slate-800">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center gap-3">
            <Shield className="h-8 w-8 text-blue-500" />
            <div>
              <h1 className="text-xl font-bold">SLSA Contracts Management</h1>
              <p className="text-sm text-slate-400">Supply Chain Levels for Software Artifacts</p>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-6 py-8">
        <div className="bg-slate-900 rounded-lg border border-slate-800">
          {/* Tabs Navigation */}
          <div className="flex border-b border-slate-800">
            {[
              { key: 'create', label: '創建認證', icon: <Upload className="h-4 w-4" /> },
              { key: 'verify', label: '驗證認證', icon: <CheckCircle className="h-4 w-4" /> },
              { key: 'digest', label: '生成摘要', icon: <FileText className="h-4 w-4" /> },
              { key: 'history', label: '認證歷史', icon: <Download className="h-4 w-4" /> },
            ].map((tab) => (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key as any)}
                className={`flex items-center gap-2 px-4 py-3 text-sm font-medium transition-colors ${
                  activeTab === tab.key
                    ? 'bg-blue-600 text-white'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
                }`}
              >
                {tab.icon}
                {tab.label}
              </button>
            ))}
          </div>

          <div className="p-6">
            {activeTab === 'create' && (
              <div className="space-y-6">
                <h2 className="text-lg font-semibold">創建新的 SLSA 認證</h2>
                <form onSubmit={async (e: React.FormEvent) => {
                  e.preventDefault();
                  const formData = new FormData(e.target as HTMLFormElement);
                  try {
                    await createAttestation(formData);
                  } catch (error) {
                    alert('認證創建失敗：' + (error as Error).message);
                  }
                }}>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <label htmlFor="buildId" className="text-sm font-medium">Build ID</label>
                      <input
                        id="buildId"
                        name="buildId"
                        type="text"
                        className="w-full p-3 bg-slate-800 border border-slate-700 rounded-md"
                        placeholder="build-12345"
                        required
                      />
                    </div>
                    <div className="space-y-2">
                      <label htmlFor="version" className="text-sm font-medium">版本</label>
                      <input
                        id="version"
                        name="version"
                        type="text"
                        className="w-full p-3 bg-slate-800 border border-slate-700 rounded-md"
                        placeholder="1.0.0"
                        required
                      />
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <label htmlFor="environment" className="text-sm font-medium">環境</label>
                      <select
                        id="environment"
                        name="environment"
                        className="w-full p-3 bg-slate-800 border border-slate-700 rounded-md"
                        required
                      >
                        <option value="">選擇環境</option>
                        <option value="dev">開發</option>
                        <option value="staging">測試</option>
                        <option value="prod">生產</option>
                      </select>
                    </div>
                    <div className="space-y-2">
                      <label htmlFor="sourceRepo" className="text-sm font-medium">源碼庫</label>
                      <input
                        id="sourceRepo"
                        name="sourceRepo"
                        type="text"
                        className="w-full p-3 bg-slate-800 border border-slate-700 rounded-md"
                        placeholder="https://github.com/example/repo"
                        required
                      />
                    </div>
                  </div>
                  <button
                    type="submit"
                    className="w-full mt-4 bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-4 rounded-md transition-colors"
                  >
                    創建認證
                  </button>
                </form>
              </div>
            )}

            {activeTab === 'verify' && (
              <div className="space-y-6">
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-5 w-5 text-green-500" />
                  <h2 className="text-lg font-semibold">驗證 SLSA 認證</h2>
                </div>
                <div className="space-y-4">
                  <div className="space-y-2">
                    <label htmlFor="provenance" className="text-sm font-medium">認證數據 (JSON)</label>
                    <textarea
                      id="provenance"
                      className="w-full h-48 p-3 bg-slate-900 border border-slate-700 rounded-md text-sm font-mono"
                      placeholder="貼上您的 SLSA 認證 JSON..."
                    />
                  </div>
                  <button
                    onClick={() => {
                      const textarea = document.getElementById('provenance') as HTMLTextAreaElement;
                      try {
                        verifyAttestation(textarea.value);
                      } catch (error) {
                        alert('驗證失敗：' + (error as Error).message);
                      }
                    }}
                    className="w-full bg-green-600 hover:bg-green-700 text-white font-medium py-3 px-4 rounded-md transition-colors"
                  >
                    驗證認證
                  </button>
                </div>
              </div>
            )}

            {activeTab === 'digest' && (
              <div className="space-y-6">
                <div className="flex items-center gap-2">
                  <FileText className="h-5 w-5 text-yellow-500" />
                  <h2 className="text-lg font-semibold">生成文件摘要</h2>
                </div>
                <div className="space-y-4">
                  <div className="space-y-2">
                    <label htmlFor="content" className="text-sm font-medium">文件內容</label>
                    <textarea
                      id="content"
                      className="w-full h-32 p-3 bg-slate-900 border border-slate-700 rounded-md text-sm"
                      placeholder="輸入要生成摘要的文件內容..."
                    />
                  </div>
                  <button
                    onClick={() => {
                      const textarea = document.getElementById('content') as HTMLTextAreaElement;
                      try {
                        generateDigest(textarea.value);
                      } catch (error) {
                        alert('生成摘要失敗：' + (error as Error).message);
                      }
                    }}
                    className="w-full bg-yellow-600 hover:bg-yellow-700 text-white font-medium py-3 px-4 rounded-md transition-colors"
                  >
                    生成摘要
                  </button>
                </div>
              </div>
            )}

            {activeTab === 'history' && (
              <div className="space-y-6">
                <div className="flex items-center gap-2">
                  <Download className="h-5 w-5 text-purple-500" />
                  <h2 className="text-lg font-semibold">認證歷史記錄</h2>
                </div>
                {attestations.length === 0 ? (
                  <p className="text-slate-400 text-center py-8">尚無認證記錄</p>
                ) : (
                  <div className="space-y-4">
                    {attestations.map((attestation: Attestation, index: number) => (
                      <div
                        key={index}
                        className="bg-slate-800 border border-slate-700 rounded-lg p-4"
                      >
                        <div className="flex justify-between items-start mb-2">
                          <h3 className="font-medium">{attestation.type}</h3>
                          <span className="text-xs text-slate-400">{attestation.timestamp}</span>
                        </div>
                        <p className="text-sm text-slate-300">ID: {attestation.id}</p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Result Display */}
        {result && (
          <div className="mt-6 bg-slate-900 border border-slate-800 rounded-lg p-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              {result.success ? (
                <CheckCircle className="h-5 w-5 text-green-500" />
              ) : (
                <AlertCircle className="h-5 w-5 text-red-500" />
              )}
              操作結果
            </h3>
            <pre className="bg-slate-950 border border-slate-700 rounded p-4 text-sm overflow-x-auto">
              {JSON.stringify(result, null, 2)}
            </pre>
          </div>
        )}
      </main>
    </div>
  );
};

export default App;