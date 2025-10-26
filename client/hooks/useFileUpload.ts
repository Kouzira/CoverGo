import { useState, useCallback } from 'react';
import type { FileWithId } from '../types';

export const useFileUpload = () => {
  const [files, setFiles] = useState<FileWithId[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);

  const addFiles = useCallback((newFiles: FileList) => {
    setUploadSuccess(false);
    setUploadError(null);

    const filesWithIds: FileWithId[] = Array.from(newFiles).map(file => ({
      id: `${file.name}-${file.lastModified}-${Math.random()}`,
      file,
    }));

    setFiles(prevFiles => [...prevFiles, ...filesWithIds]);
  }, []);

  const removeFile = useCallback((id: string) => {
    setFiles(prevFiles => prevFiles.filter(file => file.id !== id));
  }, []);

  const uploadFiles = useCallback(async () => {
    if (files.length === 0) return;

    setIsUploading(true);
    setUploadSuccess(false);
    setUploadError(null);

    const formData = new FormData();
    files.forEach(({ file }) => {
      // The backend expects the files under the 'files' key.
      formData.append('files', file);
    });

        try {
        const response = await fetch('http://127.0.0.1:8000/upload', {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ error: 'Server returned an error' }));
            throw new Error(errorData.error || `Upload failed with status: ${response.status}`);
        }

        // Convert response to Blob
        const blob = await response.blob();

        // Create an object URL for the blob
        const fileURL = window.URL.createObjectURL(blob);

        // Open it in a new tab
        window.open(fileURL, "_blank");

        // Optional: Revoke the URL later to free memory
        setTimeout(() => URL.revokeObjectURL(fileURL), 10000);

        console.log('Upload successful!');
        setUploadSuccess(true);
        setFiles([]); // Clear files on success
    } catch (error) {
      console.error('Upload failed!', error);
      const errorMessage = error instanceof Error ? error.message : 'An unknown error occurred.';
      setUploadError(errorMessage);
    } finally {
      setIsUploading(false);
    }
  }, [files]);

  return {
    files,
    addFiles,
    removeFile,
    uploadFiles,
    isUploading,
    uploadSuccess,
    uploadError,
  };
};
