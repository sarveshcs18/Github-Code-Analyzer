import { useState } from 'react';
import { api, ApiError } from './api/client';
import { RepoAnalysisResult } from './types';
import './App.css';

function App() {
    const [url, setUrl] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [result, setResult] = useState<RepoAnalysisResult | null>(null);

    const handleAnalyze = async () => {
        if (!url.trim()) return;

        setLoading(true);
        setError(null);
        setResult(null); // Clear previous result? Or keep it for comparison? Let's clear to avoid confusion.

        try {
            const data = await api.analyzeRepo(url);
            setResult(data);
        } catch (err) {
            if (err instanceof ApiError) {
                setError(err.message);
            } else {
                setError('An unexpected error occurred.');
            }
        } finally {
            setLoading(false);
        }
    };

    const handleCopy = () => {
        if (!result) return;
        const text = generateMarkdown(result);
        navigator.clipboard.writeText(text);
        alert('Copied to clipboard!');
    };

    const handleDownload = () => {
        if (!result) return;
        const text = generateMarkdown(result);
        const blob = new Blob([text], { type: 'text/markdown' });
        const href = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = href;
        link.download = 'repo-summary.md';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(href);
    };

    const generateMarkdown = (r: RepoAnalysisResult) => {
        return `# Repository Analysis

## Overview
${r.overview}

## Tech Stack
${r.tech_stack.join(', ')}

## Architecture
${r.architecture}

## Modules
${r.modules.map(m => `- **${m.name}**: ${m.description}`).join('\n')}

## Entry Points
${r.entry_points.join(', ')}

## Setup Notes
${r.setup_notes}
`;
    };

    return (
        <div className="app-container">
            <header>
                <h1>GitHub Repository Analyzer</h1>
            </header>

            <main>
                <div className="input-group">
                    <input
                        type="text"
                        placeholder="Enter GitHub Repository URL (https://... or git@...)"
                        value={url}
                        onChange={(e) => setUrl(e.target.value)}
                        disabled={loading}
                    />
                    <button onClick={handleAnalyze} disabled={loading || !url.trim()}>
                        {loading ? 'Analyzing...' : 'Analyze'}
                    </button>
                </div>

                {error && <div className="error-message">{error}</div>}

                {loading && (
                    <div className="loading-state">
                        <p>Cloning repository...</p>
                        <p>Analyzing structure...</p>
                        <p>Consulting Gemini...</p>
                    </div>
                )}

                {result && (
                    <div className="results-container">
                        <div className="actions">
                            <button onClick={handleCopy} className="secondary">Copy Markdown</button>
                            <button onClick={handleDownload} className="secondary">Download .md</button>
                        </div>

                        <section>
                            <h2>Overview</h2>
                            <p>{result.overview}</p>
                        </section>

                        <section>
                            <h2>Tech Stack</h2>
                            <div className="tags">
                                {result.tech_stack.map(tech => (
                                    <span key={tech} className="tag">{tech}</span>
                                ))}
                            </div>
                        </section>

                        <section>
                            <h2>Architecture</h2>
                            <p>{result.architecture}</p>
                        </section>

                        <section>
                            <h2>Modules</h2>
                            <ul>
                                {result.modules.map((m, i) => (
                                    <li key={i}>
                                        <strong>{m.name}</strong>: {m.description}
                                    </li>
                                ))}
                            </ul>
                        </section>

                        <section>
                            <h2>Setup Notes</h2>
                            <pre>{result.setup_notes}</pre>
                        </section>
                    </div>
                )}
            </main>
        </div>
    );
}

export default App;
