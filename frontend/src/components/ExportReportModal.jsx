import React, { useState } from 'react';
import { Download, FileText, Printer, X, CheckCircle, AlertCircle } from 'lucide-react';

export default function ExportReportModal({ isOpen, onClose, analysis }) {
  const [downloading, setDownloading] = useState(false);
  const [statusMessage, setStatusMessage] = useState(null);

  if (!isOpen || !analysis) return null;

  const analysisId = analysis.id || analysis.saved_analysis_id;
  const assetName = analysis.asset || 'Report';

  const handleExportJSON = async () => {
    setDownloading(true);
    setStatusMessage(null);
    try {
      if (analysisId) {
        const token = localStorage.getItem('token');
        const headers = token ? { Authorization: `Bearer ${token}` } : {};
        const res = await fetch(`/api/export/${analysisId}?format=json`, { headers });
        if (!res.ok) throw new Error('Failed to fetch JSON export');
        const data = await res.json();
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `FinSight_Report_${assetName}_${analysisId}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      } else {
        // Fallback for unpersisted analysis objects
        const blob = new Blob([JSON.stringify(analysis, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `FinSight_Report_${assetName}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      }
      setStatusMessage({ type: 'success', text: 'JSON export downloaded successfully!' });
    } catch (err) {
      console.error(err);
      setStatusMessage({ type: 'error', text: err.message || 'Failed to download JSON export' });
    } finally {
      setDownloading(false);
    }
  };

  const handleExportHTML = async (mode = 'open') => {
    setDownloading(true);
    setStatusMessage(null);
    try {
      if (analysisId) {
        const token = localStorage.getItem('token');
        const headers = token ? { Authorization: `Bearer ${token}` } : {};
        const res = await fetch(`/api/export/${analysisId}?format=html`, { headers });
        if (!res.ok) throw new Error('Failed to fetch HTML export');
        const htmlText = await res.text();

        const blob = new Blob([htmlText], { type: 'text/html' });
        const url = URL.createObjectURL(blob);

        if (mode === 'open') {
          const printWindow = window.open(url, '_blank');
          if (printWindow) {
            printWindow.onload = () => {
              // Optionally trigger print dialog automatically
            };
          }
        } else {
          const a = document.createElement('a');
          a.href = url;
          a.download = `FinSight_Executive_Report_${assetName}_${analysisId}.html`;
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);
        }
      } else {
        // Client-side quick HTML fallback if unsaved
        const htmlText = `
          <!DOCTYPE html>
          <html>
          <head><title>FinSight Report - ${assetName}</title></head>
          <body style="font-family: sans-serif; padding: 20px;">
            <h2>FinSight 2.0 Report — ${assetName}</h2>
            <pre>${JSON.stringify(analysis, null, 2)}</pre>
          </body>
          </html>
        `;
        const blob = new Blob([htmlText], { type: 'text/html' });
        const url = URL.createObjectURL(blob);
        if (mode === 'open') {
          window.open(url, '_blank');
        } else {
          const a = document.createElement('a');
          a.href = url;
          a.download = `FinSight_Report_${assetName}.html`;
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);
        }
      }
      setStatusMessage({ type: 'success', text: mode === 'open' ? 'Report opened for printing!' : 'HTML report downloaded!' });
    } catch (err) {
      console.error(err);
      setStatusMessage({ type: 'error', text: err.message || 'Failed to generate HTML report' });
    } finally {
      setDownloading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <div className="bg-slate-900 border border-slate-700 rounded-xl shadow-2xl max-w-md w-full p-6 text-slate-100 relative">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800 transition"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-center space-x-3 mb-4">
          <div className="p-2.5 bg-blue-600/20 border border-blue-500/30 rounded-lg text-blue-400">
            <FileText className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-white">Export Financial Report</h3>
            <p className="text-xs text-slate-400">Target Asset: <span className="text-blue-400 font-semibold">{assetName}</span></p>
          </div>
        </div>

        <p className="text-sm text-slate-300 mb-6">
          Generate an executive-grade financial analysis report. Choose your preferred export format below:
        </p>

        {statusMessage && (
          <div className={`flex items-center space-x-2 text-xs p-3 rounded-lg mb-4 border ${
            statusMessage.type === 'success'
              ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
              : 'bg-rose-500/10 border-rose-500/30 text-rose-400'
          }`}>
            {statusMessage.type === 'success' ? <CheckCircle className="w-4 h-4 shrink-0" /> : <AlertCircle className="w-4 h-4 shrink-0" />}
            <span>{statusMessage.text}</span>
          </div>
        )}

        <div className="space-y-3 mb-6">
          <button
            onClick={() => handleExportHTML('open')}
            disabled={downloading}
            className="w-full flex items-center justify-between p-3.5 bg-blue-600 hover:bg-blue-500 text-white rounded-lg font-medium shadow-md hover:shadow-blue-500/20 transition disabled:opacity-50"
          >
            <div className="flex items-center space-x-3">
              <Printer className="w-5 h-5" />
              <div className="text-left">
                <div className="text-sm font-semibold">Printable PDF / HTML Executive Report</div>
                <div className="text-[11px] text-blue-100 opacity-90">Open print-ready report in new browser window</div>
              </div>
            </div>
            <FileText className="w-4 h-4 opacity-70" />
          </button>

          <button
            onClick={handleExportJSON}
            disabled={downloading}
            className="w-full flex items-center justify-between p-3.5 bg-slate-800 hover:bg-slate-750 border border-slate-700 text-slate-200 hover:text-white rounded-lg font-medium transition disabled:opacity-50"
          >
            <div className="flex items-center space-x-3">
              <Download className="w-5 h-5 text-blue-400" />
              <div className="text-left">
                <div className="text-sm font-semibold">Structured JSON Data Export</div>
                <div className="text-[11px] text-slate-400">Download formatted JSON raw data payload</div>
              </div>
            </div>
            <Download className="w-4 h-4 text-slate-500" />
          </button>
        </div>

        <div className="flex justify-end pt-2 border-t border-slate-800">
          <button
            onClick={onClose}
            className="px-4 py-2 text-xs font-semibold text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
