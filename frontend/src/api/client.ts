import { RepoAnalysisResult, RepoRequest } from '../types';

const API_BASE_URL = '/api/v1'; // Relative path for proxying or same-origin

export class ApiError extends Error {
    constructor(public status: number, message: string) {
        super(message);
        this.name = 'ApiError';
    }
}

async function handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
        let errorMessage = 'An error occurred';
        try {
            const errorData = await response.json();
            errorMessage = errorData.detail || errorData.message || errorMessage;
        } catch {
            // ignore json parse error
        }
        throw new ApiError(response.status, errorMessage);
    }
    return response.json();
}

export const api = {
    analyzeRepo: async (url: string): Promise<RepoAnalysisResult> => {
        const response = await fetch(`${API_BASE_URL}/repo/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url } as RepoRequest),
        });
        return handleResponse<RepoAnalysisResult>(response);
    },
};
