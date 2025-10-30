import React from 'react';
import { MockData } from './mockData';

type Props = {
	data: MockData;
	selectedDocId: string | null;
	onSelect: (docId: string) => void;
};

export const Sidebar: React.FC<Props> = ({ data, selectedDocId, onSelect }) => {
	return (
		<aside className="sidebar">
			<div className="brand">ZiNin AI</div>
			<input className="search" placeholder="Начни вводить..." />
			<div className="tree">
				{data.companies.map(company => (
					<div key={company.id} className="tree-node">
						<div className="node-title">{company.name}</div>
						{data.deals
							.filter(d => d.companyId === company.id)
							.map(deal => (
								<div key={deal.id} className="tree-node nested">
									<div className="node-title">Сделка №{deal.number}</div>
									{data.documents
										.filter(doc => doc.dealId === deal.id)
										.map(doc => (
											<button
												key={doc.id}
												className={
													'doc-link' + (doc.id === selectedDocId ? ' active' : '')
												}
												onClick={() => onSelect(doc.id)}
											>
												{doc.title}
											</button>
										))}
								</div>
							))}
					</div>
				))}
			</div>
			<button className="more">Больше результатов</button>
		</aside>
	);
};


