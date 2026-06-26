"use client";

import { ChangeEvent, useRef, useState } from "react";
import { uploadDocument, UploadedDocument } from "../lib/api";

type DocumentUploadProps = {
	disabled?: boolean;
	onUploaded: (document: UploadedDocument) => void;
};

export function DocumentUpload({ disabled = false, onUploaded }: DocumentUploadProps) {
	const inputRef = useRef<HTMLInputElement>(null);
	const [isUploading, setIsUploading] = useState(false);
	const [error, setError] = useState<string | null>(null);

	async function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
		const file = event.target.files?.[0];

		if (!file) {
			return;
		}

		if (file.type !== "application/pdf") {
			setError("Please select a PDF file.");
			event.target.value = "";
			return;
		}

		setError(null);
		setIsUploading(true);

		try {
			const document = await uploadDocument(file);
			onUploaded(document);
		} catch (uploadError) {
			setError(uploadError instanceof Error ? uploadError.message : "The upload failed.");
		} finally {
			setIsUploading(false);
			event.target.value = "";
		}
	}

	return (
		<div className="space-y-3">
			<input
				ref={inputRef}
				type="file"
				accept="application/pdf,.pdf"
				className="hidden"
				onChange={handleFileChange}
			/>

			<button
				type="button"
				disabled={disabled || isUploading}
				onClick={() => inputRef.current?.click()}
				className="rounded-lg bg-black px-4 py-2 text-sm font-medium text-white disabled:cursor-not-allowed disabled:opacity-50"
			>
				{isUploading ? "Processing PDF..." : "Upload PDF"}
			</button>

			{error ? <p className="text-sm text-red-600">{error}</p> : null}

			{isUploading ? (
				<p className="text-sm text-neutral-600">
					Extracting text, creating chunks, generating embeddings, and writing them to
					Pinecone.
				</p>
			) : null}
		</div>
	);
}
