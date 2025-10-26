
import React from 'react';
import { Dropzone } from './components/Dropzone';
import { FileList } from './components/FileList';
import { UploadButton } from './components/UploadButton';
import { useFileUpload } from './hooks/useFileUpload';

const App: React.FC = () => {
  const {
    files,
    addFiles,
    removeFile,
    uploadFiles,
    isUploading,
    uploadSuccess,
    uploadError,
  } = useFileUpload();

  return (
    <div className="min-h-screen flex items-center justify-center p-4 font-sans">
      <div className="w-full max-w-2xl mx-auto">
        <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-xl border border-slate-200 dark:border-slate-700 p-6 md:p-8 space-y-6">
          <header className="text-center">
            <h1 className="text-3xl font-bold text-slate-800 dark:text-white">
              Upload Your Files
            </h1>
            <p className="text-slate-500 dark:text-slate-400 mt-2">
              Drag & drop files or click to select files from your device.
            </p>
          </header>

          <Dropzone onFilesAdded={addFiles} />

          {files.length > 0 && (
            <>
              <FileList files={files} onRemoveFile={removeFile} />
              <UploadButton
                files={files}
                onUpload={uploadFiles}
                isUploading={isUploading}
              />
            </>
          )}

          {uploadSuccess && (
            <div className="bg-green-100 dark:bg-green-900/50 border border-green-300 dark:border-green-700 text-green-800 dark:text-green-200 px-4 py-3 rounded-lg text-center" role="alert">
              <strong className="font-bold">Success!</strong>
              <span className="block sm:inline ml-2">Files have been "uploaded".</span>
            </div>
          )}

          {uploadError && (
            <div className="bg-red-100 dark:bg-red-900/50 border border-red-300 dark:border-red-700 text-red-700 dark:text-red-200 px-4 py-3 rounded-lg text-center" role="alert">
              <strong className="font-bold">Error!</strong>
              <span className="block sm:inline ml-2">{uploadError}</span>
            </div>
          )}
        </div>
        <footer className="text-center mt-6 text-sm text-slate-500 dark:text-slate-400">
          <p>Powered by React & Tailwind CSS</p>
        </footer>
      </div>
    </div>
  );
};

export default App;
