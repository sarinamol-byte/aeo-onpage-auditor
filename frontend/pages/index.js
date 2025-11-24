import React, { useState } from 'react';
import axios from 'axios';

export default function Home() {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [report, setReport] = useState(null);
  const [error, setError] = useState(null);

  async function runAudit(e) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setReport(null);

    const endpoint = '/api/aeo-analyze';

    try {
      const res = await axios.post(endpoint, { url });
      setReport(res.data);
    } catch (err) {
      setError(err.response?.data?.error || err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen p-8 bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="max-w-6xl mx-auto">
        
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">
            Answer Engine Optimization Auditor
          </h1>
          <p className="text-gray-600">
            Optimize your content for AI search engines and featured snippets
          </p>
        </div>

        {/* Input Form */}
        <div className="bg-white p-6 rounded-lg shadow-lg mb-8">
          <form onSubmit={runAudit} className="flex gap-4">
            <input
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://example.com/article"
              className="flex-1 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            />
            <button
              type="submit"
              className="px-8 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition"
              disabled={loading}
            >
              {loading ? 'Analyzing...' : 'Audit Page'}
            </button>
          </form>
        </div>

        {/* Error */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-lg mb-8">
            <strong>Error:</strong> {error}
          </div>
        )}

        {/* Report */}
        {report && (
          <div className="space-y-6">
            
            {/* Overall Score */}
            <div className="bg-white p-8 rounded-lg shadow-lg text-center">
              <h2 className="text-2xl font-bold text-gray-700 mb-4">AEO Score</h2>
              <div className={`text-6xl font-bold ${
                report.aeo_score >= 80 ? 'text-green-600' :
                report.aeo_score >= 60 ? 'text-yellow-600' :
                'text-red-600'
              }`}>
                {report.aeo_score}
                <span className="text-3xl">/100</span>
              </div>
              <p className="text-gray-600 mt-2">
                {report.aeo_score >= 80 ? 'Excellent!' :
                 report.aeo_score >= 60 ? 'Good, but could improve' :
                 'Needs improvement'}
              </p>
            </div>

            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-white p-6 rounded-lg shadow">
                <h3 className="text-sm font-semibold text-gray-600 mb-2">Word Count</h3>
                <p className="text-3xl font-bold text-blue-600">{report.word_count}</p>
              </div>
              <div className="bg-white p-6 rounded-lg shadow">
                <h3 className="text-sm font-semibold text-gray-600 mb-2">Snippet Score</h3>
                <p className="text-3xl font-bold text-green-600">{report.snippet_score}</p>
              </div>
              <div className="bg-white p-6 rounded-lg shadow">
                <h3 className="text-sm font-semibold text-gray-600 mb-2">Reading Ease</h3>
                <p className="text-3xl font-bold text-purple-600">{report.flesch_reading_ease}</p>
              </div>
              <div className="bg-white p-6 rounded-lg shadow">
                <h3 className="text-sm font-semibold text-gray-600 mb-2">Entities</h3>
                <p className="text-3xl font-bold text-orange-600">{report.entities_found}</p>
              </div>
            </div>

            {/* Recommendations */}
            {report.recommendations && report.recommendations.length > 0 && (
              <div className="bg-yellow-50 border-l-4 border-yellow-400 p-6 rounded-lg shadow">
                <h3 className="text-xl font-bold text-gray-800 mb-4">
                  🎯 Recommendations
                </h3>
                <ul className="space-y-2">
                  {report.recommendations.map((rec, i) => (
                    <li key={i} className="flex items-start">
                      <span className="text-yellow-600 mr-2">•</span>
                      <span className="text-gray-700">{rec}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Schema Markup */}
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-xl font-bold text-gray-800 mb-4">📋 Schema Markup</h3>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                <div>
                  <p className="text-sm text-gray-600">FAQ Schema</p>
                  <p className={`font-bold ${report.faq_schema_present ? 'text-green-600' : 'text-red-600'}`}>
                    {report.faq_schema_present ? '✓ Present' : '✗ Missing'}
                  </p>
                  {report.faq_schema_present && (
                    <p className="text-xs text-gray-500">{report.faq_count} FAQs</p>
                  )}
                </div>
                <div>
                  <p className="text-sm text-gray-600">HowTo Schema</p>
                  <p className={`font-bold ${report.howto_schema_present ? 'text-green-600' : 'text-red-600'}`}>
                    {report.howto_schema_present ? '✓ Present' : '✗ Missing'}
                  </p>
                  {report.howto_schema_present && (
                    <p className="text-xs text-gray-500">{report.howto_count} steps</p>
                  )}
                </div>
                <div>
                  <p className="text-sm text-gray-600">Article Schema</p>
                  <p className={`font-bold ${report.article_schema_present ? 'text-green-600' : 'text-red-600'}`}>
                    {report.article_schema_present ? '✓ Present' : '✗ Missing'}
                  </p>
                </div>
              </div>
            </div>

            {/* Question Headings */}
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-xl font-bold text-gray-800 mb-4">❓ Question-Based Headings</h3>
              <div className="mb-4">
                <p className="text-gray-700">
                  <strong>{report.question_headings}</strong> out of <strong>{report.total_headings}</strong> headings are questions
                </p>
              </div>
              {report.question_heading_examples && report.question_heading_examples.length > 0 && (
                <div>
                  <p className="text-sm font-semibold text-gray-600 mb-2">Examples:</p>
                  <ul className="space-y-1">
                    {report.question_heading_examples.map((h, i) => (
                      <li key={i} className="text-gray-700 pl-4 border-l-2 border-blue-300">
                        {h}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            {/* Content Structure */}
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-xl font-bold text-gray-800 mb-4">📝 Content Structure</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <p className="text-sm text-gray-600">Lists</p>
                  <p className="text-2xl font-bold text-blue-600">{report.lists}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Tables</p>
                  <p className="text-2xl font-bold text-blue-600">{report.tables}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Has TL;DR</p>
                  <p className={`text-2xl font-bold ${report.has_tldr ? 'text-green-600' : 'text-red-600'}`}>
                    {report.has_tldr ? '✓' : '✗'}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Has TOC</p>
                  <p className={`text-2xl font-bold ${report.has_toc ? 'text-green-600' : 'text-red-600'}`}>
                    {report.has_toc ? '✓' : '✗'}
                  </p>
                </div>
              </div>
            </div>

            {/* E-E-A-T */}
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-xl font-bold text-gray-800 mb-4">⭐ E-E-A-T Signals</h3>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                <div className={`p-3 rounded ${report.has_author_meta ? 'bg-green-50' : 'bg-red-50'}`}>
                  <p className="text-sm font-semibold">Author Meta</p>
                  <p className={report.has_author_meta ? 'text-green-700' : 'text-red-700'}>
                    {report.has_author_meta ? '✓ Present' : '✗ Missing'}
                  </p>
                </div>
                <div className={`p-3 rounded ${report.has_date ? 'bg-green-50' : 'bg-red-50'}`}>
                  <p className="text-sm font-semibold">Publication Date</p>
                  <p className={report.has_date ? 'text-green-700' : 'text-red-700'}>
                    {report.has_date ? '✓ Present' : '✗ Missing'}
                  </p>
                </div>
                <div className={`p-3 rounded ${report.has_author_bio ? 'bg-green-50' : 'bg-red-50'}`}>
                  <p className="text-sm font-semibold">Author Bio</p>
                  <p className={report.has_author_bio ? 'text-green-700' : 'text-red-700'}>
                    {report.has_author_bio ? '✓ Present' : '✗ Missing'}
                  </p>
                </div>
                <div className={`p-3 rounded ${report.has_sources ? 'bg-green-50' : 'bg-red-50'}`}>
                  <p className="text-sm font-semibold">Sources/References</p>
                  <p className={report.has_sources ? 'text-green-700' : 'text-red-700'}>
                    {report.has_sources ? '✓ Present' : '✗ Missing'}
                  </p>
                </div>
                <div className={`p-3 rounded ${report.has_about_link ? 'bg-green-50' : 'bg-red-50'}`}>
                  <p className="text-sm font-semibold">About Page</p>
                  <p className={report.has_about_link ? 'text-green-700' : 'text-red-700'}>
                    {report.has_about_link ? '✓ Linked' : '✗ Not Found'}
                  </p>
                </div>
                <div className={`p-3 rounded ${report.has_contact_link ? 'bg-green-50' : 'bg-red-50'}`}>
                  <p className="text-sm font-semibold">Contact Page</p>
                  <p className={report.has_contact_link ? 'text-green-700' : 'text-red-700'}>
                    {report.has_contact_link ? '✓ Linked' : '✗ Not Found'}
                  </p>
                </div>
              </div>
            </div>

            {/* Entities */}
            {report.entity_examples && report.entity_examples.length > 0 && (
              <div className="bg-white p-6 rounded-lg shadow">
                <h3 className="text-xl font-bold text-gray-800 mb-4">🏷️ Entities ({report.entities_found} found)</h3>
                <div className="flex flex-wrap gap-2">
                  {report.entity_examples.map((entity, i) => (
                    <span key={i} className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                      {entity}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* AEO Checklist */}
            {report.aeo_checks && (
              <div className="bg-white p-6 rounded-lg shadow">
                <h3 className="text-xl font-bold text-gray-800 mb-4">✅ AEO Checklist</h3>
                <div className="space-y-2">
                  {Object.entries(report.aeo_checks).map(([check, passed]) => (
                    <div key={check} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                      <span className="text-gray-700">{check}</span>
                      <span className={`font-bold ${passed ? 'text-green-600' : 'text-red-600'}`}>
                        {passed ? '✓ Pass' : '✗ Fail'}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

          </div>
        )}
      </div>
    </div>
  );
}