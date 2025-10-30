import React from 'react';
import { MockData } from './mockData';

type Props = {
	data: MockData;
	selectedDocId: string | null;
	onSelectTab: (docId: string) => void;
};

export const CenterPane: React.FC<Props> = ({ data, selectedDocId, onSelectTab }) => {
	const openDocs = data.documents.slice(0, 6);
	const selected = openDocs.find(d => d.id === selectedDocId) ?? openDocs[0];

	return (
		<main className="center">
			<div className="tabs">
				{openDocs.map(doc => (
					<button
						key={doc.id}
						className={'tab' + (doc.id === selected?.id ? ' active' : '')}
						onClick={() => onSelectTab(doc.id)}
					>
						{doc.title}
					</button>
				))}
			</div>
			<div className="doc-frame">
				{/* In a real app embed PDF. Here we show an image placeholder from mock */}
				<img src={selected.previewUrl} alt={selected.title} />
			</div>
			<div className="doc-toolbar">
				<button>🔍</button>
				<button>🅣</button>
				<button>🖊</button>
			</div>
		</main>
	);
};


