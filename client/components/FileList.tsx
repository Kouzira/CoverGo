
import React from 'react';
import type { FileWithId } from '../types';
import { formatBytes } from '../utils';
import { FileIcon } from './icons/FileIcon';
import { TrashIcon } from './icons/TrashIcon';

interface FileListProps {
  files: FileWithId[];
  onRemoveFile: (id: string) => void;
}

export const FileList: React.FC<FileListProps> = ({ files, onRemoveFile }) => {
  return (
    <div className="space-y-3">
      <h2 className="text-lg font-medium text-slate-700 dark:text-slate-200">Files to Upload</h2>
      <ul className="divide-y divide-slate-200 dark:divide-slate-700 border-t border-b border-slate-200 dark:border-slate-700">
        {files.map(({ id, file }) => (
          <li key={id} className="flex items-center justify-between p-3 hover:bg-slate-50 dark:hover:bg-slate-700/50">
            <div className="flex items-center min-w-0">
              <FileIcon className="w-6 h-6 text-slate-500 flex-shrink-0" />
              <div className="ml-3 min-w-0">
                <p className="text-sm font-medium text-slate-900 dark:text-white truncate">
                  {file.name}
                </p>
                <p className="text-sm text-slate-500 dark:text-slate-400">
                  {formatBytes(file.size)}
                </p>
              </div>
            </div>
            <button
              onClick={() => onRemoveFile(id)}
              className="p-1.5 rounded-full text-slate-500 hover:bg-red-100 hover:text-red-600 dark:hover:bg-red-900/50 dark:hover:text-red-400 transition-colors"
              aria-label={`Remove ${file.name}`}
            >
              <TrashIcon className="w-5 h-5" />
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
};
