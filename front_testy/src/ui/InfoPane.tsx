import React from 'react';
import { DocumentItem } from './mockData';

type Props = { document: DocumentItem | null };

export const InfoPane: React.FC<Props> = ({ document }) => {
	return (
		<section className="info-pane">
			<h3>Информация</h3>
			{!document ? (
				<div className="muted">Документ не выбран</div>
			) : (
				<div className="kv">
					<div><b>Наименование</b><span>{document.title}</span></div>
					<div><b>Тип документа</b><span>{document.type}</span></div>
					<div><b>Дата</b><span>{document.date}</span></div>
					<div><b>Сумма</b><span>{document.amount}</span></div>
					<div><b>Статус</b><span>{document.status}</span></div>
				</div>
			)}
		</section>
	);
};


