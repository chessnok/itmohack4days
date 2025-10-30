export type UploadedDoc = {
	id: string;
	name: string;
	content?: string; // optional extracted text (placeholder)
};

export type ExtractedParty = {
	inn?: string;
	kpp?: string;
	ogrn?: string;
	name?: string;
	address?: string;
};

export type ExtractionResult = {
	documentId: string;
	party: ExtractedParty;
};

export type EnrichedParty = ExtractedParty & {
	validatedInn?: boolean;
	fullName?: string;
	status?: string;
	founded?: string;
	okved?: string;
};

export type EnrichmentResult = {
	documentId: string;
	party: EnrichedParty;
};

export type Finding = {
	id: string;
	severity: 'info' | 'warn' | 'error';
	message: string;
	documentId?: string;
};

export type DocumentSummary = {
	documentId: string;
	text: string;
};

export type DealSummary = {
	text: string;
};

export type PipelineOutput = {
	extractions: ExtractionResult[];
	enrichments: EnrichmentResult[];
	findings: Finding[];
	docSummaries: DocumentSummary[];
	dealSummary: DealSummary;
};


