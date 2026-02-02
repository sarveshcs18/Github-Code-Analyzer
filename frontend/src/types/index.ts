export interface FileNode {
    path: string;
    type: 'file' | 'directory';
    size?: number;
    children?: FileNode[];
}

export interface ModuleInfo {
    name: string;
    description: string;
}

export interface RepoAnalysisResult {
    overview: string;
    tech_stack: string[];
    architecture: string;
    modules: ModuleInfo[];
    entry_points: string[];
    setup_notes: string;
    raw_structure?: string[];
}

export interface RepoRequest {
    url: string;
}
