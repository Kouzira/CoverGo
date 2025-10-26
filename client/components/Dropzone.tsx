
import React, { useState, useCallback, useRef } from 'react';
import { UploadCloudIcon } from './icons/UploadCloudIcon';

interface DropzoneProps {
  onFilesAdded: (files: FileList) => void;
}

export const Dropzone: React.FC<DropzoneProps> = ({ onFilesAdded }) => {
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragEnter = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDrop = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    
    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      onFilesAdded(files);
      e.dataTransfer.clearData();
    }
  }, [onFilesAdded]);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      onFilesAdded(files);
    }
  };

  const handleZoneClick = () => {
    fileInputRef.current?.click();
  };

  const baseClasses = "flex flex-col items-center justify-center w-full h-48 border-2 border-dashed rounded-lg cursor-pointer transition-colors duration-200 ease-in-out";
  const inactiveClasses = "border-slate-300 bg-slate-50 hover:bg-slate-100 dark:border-slate-600 dark:bg-slate-700/50 dark:hover:bg-slate-700";
  const activeClasses = "border-blue-500 bg-blue-50 dark:bg-blue-900/50";

  return (
    <div
      className={`${baseClasses} ${isDragging ? activeClasses : inactiveClasses}`}
      onDragEnter={handleDragEnter}
      onDragLeave={handleDragLeave}
      onDragOver={handleDragOver}
      onDrop={handleDrop}
      onClick={handleZoneClick}
    >
      <div className="flex flex-col items-center justify-center pt-5 pb-6 text-center">
        <UploadCloudIcon className="w-10 h-10 mb-4 text-slate-500 dark:text-slate-400" />
        <p className="mb-2 text-sm text-slate-500 dark:text-slate-400">
          <span className="font-semibold">Click to upload</span> or drag and drop
        </p>
        <p className="text-xs text-slate-500 dark:text-slate-400">
          Any file type, up to you
        </p>
      </div>
      <input
        ref={fileInputRef}
        type="file"
        multiple
        className="hidden"
        onChange={handleFileSelect}
      />
    </div>
  );
};
