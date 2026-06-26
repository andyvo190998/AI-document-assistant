"use client";

import { useState } from "react";
import { CopilotChat, useAgentContext } from "@copilotkit/react-core/v2";
import { deleteDocument, UploadedDocument } from "../lib/api";
import { DocumentUpload } from "./document-upload";

export function DocumentAssistant() {
	const [document, setDocument] = useState<UploadedDocument | null>(null);

	useAgentContext({
		description:
			"The currently active uploaded PDF. Use its document_id when calling search_document.",
		value: document
			? {
					document_id: document.document_id,
					filename: document.filename,
					page_count: document.page_count,
				}
			: {
					document_id: null,
					message: "No PDF has been uploaded.",
				},
	});

	async function handleReplaceDocument() {
		if (!document) {
			return;
		}

		await deleteDocument(document.document_id);
		setDocument(null);
	}

	return (
		<main className="mx-auto grid min-h-screen max-w-7xl gap-6 p-6 lg:grid-cols-[minmax(0,1fr)_minmax(380px,0.8fr)]">
			<section className="rounded-2xl border border-neutral-200 bg-white p-6">
				<div className="mb-8">
					<p className="mb-2 text-sm font-medium text-neutral-500">PDF AI Assistant</p>

					<h1 className="text-3xl font-semibold tracking-tight text-black">
						Understand a document without reading every page
					</h1>

					<p className="mt-3 max-w-2xl text-neutral-600">
						Upload a text-based PDF to generate a summary and ask grounded questions
						with page references.
					</p>
				</div>

				{!document ? (
					<div className="rounded-xl border border-dashed border-neutral-300 p-8">
						<DocumentUpload onUploaded={setDocument} />
					</div>
				) : (
					<div className="space-y-6">
						<div className="rounded-xl border border-neutral-200 p-4">
							<p className="font-medium">{document.filename}</p>

							<p className="mt-1 text-sm text-neutral-500">
								{document.page_count} pages · {document.chunk_count} searchable
								chunks
							</p>

							<button
								type="button"
								onClick={handleReplaceDocument}
								className="mt-4 text-sm font-medium text-red-600"
							>
								Remove document
							</button>
						</div>

						<article>
							<h2 className="mb-3 text-xl font-semibold">Summary</h2>

							<div className="whitespace-pre-wrap leading-7 text-neutral-700">
								{document.summary}
							</div>
						</article>
					</div>
				)}
			</section>

			<section className="min-h-175 overflow-hidden rounded-2xl border border-neutral-200 bg-white">
				{document ? (
					<CopilotChat
						agentId="default"
						className="h-full"
						labels={{
							welcomeMessageText: "The PDF is ready. Ask me about its content.",
							chatInputPlaceholder: "Ask a question about the PDF...",
						}}
					/>
				) : (
					<div className="flex h-full min-h-175 items-center justify-center p-8 text-center text-neutral-500">
						Upload a PDF to start chatting.
					</div>
				)}
			</section>
		</main>
	);
}
