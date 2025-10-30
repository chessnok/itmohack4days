import React, { useMemo, useState } from 'react';
import { Sidebar } from './Sidebar';
import { CenterPane } from './CenterPane';
import { InfoPane } from './InfoPane';
import { ActionLog } from './ActionLog';
import { MockData, loadMock } from './mockData';
import { UploadPane } from './UploadPane';
import { FindingsPane } from './FindingsPane';
import { UploadedDoc } from './pipeline/types';
import { extractPartiesFromDocs } from './pipeline/extract';
import { enrichWithDadata } from './pipeline/enrich';
import { validate } from './pipeline/validate';
import { makeDealSummary, makeDocSummaries } from './pipeline/summarize';

export const App: React.FC = () => {
	const data: MockData = useMemo(loadMock, []);
	const [selectedDocId, setSelectedDocId] = useState<string | null>(data.documents[0]?.id ?? null);
	const selectedDoc = data.documents.find(d => d.id === selectedDocId) ?? null;

	const [uploads, setUploads] = useState<UploadedDoc[]>([]);
	const [findings, setFindings] = useState<ReturnType<typeof validate>>([]);
	const [dealSummary, setDealSummary] = useState<string>('');

	async function runPipeline() {
		const token = import.meta.env.VITE_DADATA_TOKEN as string | undefined;
		const extractions = await extractPartiesFromDocs(uploads);
		const enrichments = await enrichWithDadata(extractions, token);
		const v = validate(enrichments);
		setFindings(v);
		const docSummaries = makeDocSummaries(enrichments, v);
		setDealSummary(makeDealSummary({
			extractions,
			enrichments,
			findings: v,
			docSummaries,
			dealSummary: { text: '' },
		} as any));
	}

	return (
		<>
		<div className="layout">
			<Sidebar data={data} selectedDocId={selectedDocId} onSelect={setSelectedDocId} />
			<CenterPane data={data} selectedDocId={selectedDocId} onSelectTab={setSelectedDocId} />
			<div className="right-column">
				<InfoPane document={selectedDoc} />
				<UploadPane uploaded={uploads} onUpload={setUploads} />
				<div style={{ padding: 8, background: 'var(--panel)', borderTop: '1px solid var(--border)' }}>
					<button onClick={runPipeline} disabled={uploads.length === 0}>Запустить проверку</button>
				</div>
				<ActionLog />
			</div>
		</div>
		<FindingsPane findings={findings} dealSummary={dealSummary} />
		</>
	);
};


