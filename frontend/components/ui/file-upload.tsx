'use client';

import { useState, useRef, ChangeEvent } from 'react';
import { Button } from './button';

interface FileUploadProps {
  accept?: string;
  multiple?: boolean;
  maxSize?: number; // in MB
  onUpload: (files: File[]) => Promise<void>;
  className?: string;
}

interface UploadFile {
  file: File;
  progress: number;
  status: 'pending' | 'uploading' | 'success' | 'error';
  error?: string;
}

export function FileUpload({
  accept = '*',
  multiple = false,
  maxSize = 10,
  onUpload,
  className = '',
}: FileUploadProps) {
  const [files, setFiles] = useState<UploadFile[]>([]);
  const [dragActive, setDragActive] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFiles = (fileList: FileList | null) => {
    if (!fileList) return;

    const newFiles: UploadFile[] = Array.from(fileList).map((file) => ({
      file,
      progress: 0,
      status: 'pending' as const,
    }));

    // Validate file sizes
    const validFiles = newFiles.filter((uploadFile) => {
      if (uploadFile.file.size > maxSize * 1024 * 1024) {
        uploadFile.status = 'error';
        uploadFile.error = `File size exceeds ${maxSize}MB`;
        return true;
      }
      return true;
    });

    setFiles((prev) => [...prev, ...validFiles]);
  };

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    handleFiles(e.target.files);
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    handleFiles(e.dataTransfer.files);
  };

  const uploadSingleFile = async (index: number) => {
    const uploadFile = files[index];
    if (uploadFile.status !== 'pending') return;

    // Update status to uploading
    setFiles((prev) =>
      prev.map((f, i) =>
        i === index ? { ...f, status: 'uploading' as const } : f
      )
    );

    try {
      // Simulate upload progress
      const progressInterval = setInterval(() => {
        setFiles((prev) =>
          prev.map((f, i) => {
            if (i === index && f.progress < 90) {
              return { ...f, progress: f.progress + 10 };
            }
            return f;
          })
        );
      }, 200);

      // Call the actual upload function
      await onUpload([uploadFile.file]);

      clearInterval(progressInterval);

      // Update to success
      setFiles((prev) =>
        prev.map((f, i) =>
          i === index
            ? { ...f, progress: 100, status: 'success' as const }
            : f
        )
      );
    } catch (error) {
      setFiles((prev) =>
        prev.map((f, i) =>
          i === index
            ? {
                ...f,
                status: 'error' as const,
                error: error instanceof Error ? error.message : 'Upload failed',
              }
            : f
        )
      );
    }
  };

  const uploadAll = async () => {
    const pendingIndexes = files
      .map((f, i) => (f.status === 'pending' ? i : -1))
      .filter((i) => i !== -1);

    for (const index of pendingIndexes) {
      await uploadSingleFile(index);
    }
  };

  const removeFile = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const clearAll = () => {
    setFiles([]);
    if (inputRef.current) {
      inputRef.current.value = '';
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success': return 'text-green-500';
      case 'error': return 'text-red-500';
      case 'uploading': return 'text-blue-500';
      default: return 'text-gray-400';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success': return '✓';
      case 'error': return '✗';
      case 'uploading': return '↻';
      default: return '○';
    }
  };

  return (
    <div className={className}>
      {/* Drop Zone */}
      <div
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
          dragActive
            ? 'border-blue-500 bg-blue-500/10'
            : 'border-slate-700 bg-slate-900'
        }`}
      >
        <input
          ref={inputRef}
          type="file"
          accept={accept}
          multiple={multiple}
          onChange={handleChange}
          className="hidden"
        />
        
        <div className="mb-4">
          <svg
            className="mx-auto h-12 w-12 text-gray-400"
            stroke="currentColor"
            fill="none"
            viewBox="0 0 48 48"
          >
            <path
              d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
              strokeWidth={2}
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </div>

        <p className="text-gray-300 mb-2">
          Drag and drop files here, or click to select files
        </p>
        <p className="text-sm text-gray-500 mb-4">
          Maximum file size: {maxSize}MB
        </p>

        <Button onClick={() => inputRef.current?.click()}>
          Select Files
        </Button>
      </div>

      {/* File List */}
      {files.length > 0 && (
        <div className="mt-6 space-y-3">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-semibold">
              Files ({files.length})
            </h3>
            <div className="flex gap-2">
              <Button onClick={uploadAll} size="sm">
                Upload All
              </Button>
              <Button onClick={clearAll} size="sm" variant="outline">
                Clear All
              </Button>
            </div>
          </div>

          {files.map((uploadFile, index) => (
            <div
              key={index}
              className="bg-slate-900 border border-slate-700 rounded-lg p-4"
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex-1 min-w-0">
                  <p className="font-medium truncate">{uploadFile.file.name}</p>
                  <p className="text-sm text-gray-500">
                    {formatFileSize(uploadFile.file.size)}
                  </p>
                </div>
                <div className="flex items-center gap-3">
                  <span className={`text-lg ${getStatusColor(uploadFile.status)}`}>
                    {getStatusIcon(uploadFile.status)}
                  </span>
                  <button
                    onClick={() => removeFile(index)}
                    className="text-gray-400 hover:text-red-500 transition-colors"
                  >
                    ✕
                  </button>
                </div>
              </div>

              {uploadFile.status === 'uploading' && (
                <div className="mb-2">
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-blue-400">Uploading...</span>
                    <span className="text-gray-400">{uploadFile.progress}%</span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <div
                      className="bg-blue-500 h-2 rounded-full transition-all"
                      style={{ width: `${uploadFile.progress}%` }}
                    ></div>
                  </div>
                </div>
              )}

              {uploadFile.status === 'error' && uploadFile.error && (
                <p className="text-sm text-red-500">{uploadFile.error}</p>
              )}

              {uploadFile.status === 'pending' && (
                <Button
                  onClick={() => uploadSingleFile(index)}
                  size="sm"
                  className="w-full mt-2"
                >
                  Upload
                </Button>
              )}

              {uploadFile.status === 'success' && (
                <p className="text-sm text-green-500">Upload complete</p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
