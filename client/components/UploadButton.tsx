
import React from 'react';
import type { FileWithId } from '../types';

interface UploadButtonProps {
  files: FileWithId[];
  onUpload: () => void;
  isUploading: boolean;
}

const Spinner: React.FC = () => (
  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
  </svg>
);


export const UploadButton: React.FC<UploadButtonProps> = ({ files, onUpload, isUploading }) => {
  const fileCount = files.length;
  const totalSize = files.reduce((acc, { file }) => acc + file.size, 0);

  const formatBytesForButton = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
  }

  return (
    <button
      onClick={onUpload}
      disabled={fileCount === 0 || isUploading}
      className="w-full flex items-center justify-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-slate-400 dark:disabled:bg-slate-600 disabled:cursor-not-allowed transition-all duration-200"
    >
      {isUploading ? (
        <>
          <Spinner />
          Uploading...
        </>
      ) : (
        `Upload ${fileCount} file${fileCount !== 1 ? 's' : ''} (${formatBytesForButton(totalSize)})`
      )}
    </button>
  );
};
