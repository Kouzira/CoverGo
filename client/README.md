# Drag & Drop File Uploader with Python Backend

This is a modern, responsive file uploader application built with React and Tailwind CSS for the frontend, and a simple Flask server for the backend.

Users can select files through a file explorer or by dragging and dropping them into a designated area. The app provides a clear preview of selected files and uploads them to a Python Flask server.

## Project Structure

```
.
├── backend/
│   ├── app.py              # Flask server
│   ├── requirements.txt    # Python dependencies
│   └── uploads/            # Directory where uploaded files are stored
├── components/
│   ├── icons/
│   │   ├── FileIcon.tsx
│   │   ├── TrashIcon.tsx
│   │   └── UploadCloudIcon.tsx
│   ├── Dropzone.tsx
│   ├── FileList.tsx
│   └── UploadButton.tsx
├── hooks/
│   └── useFileUpload.ts
├── App.tsx
├── index.html
├── index.tsx
├── metadata.json
├── README.md
├── types.ts
└── utils.ts
```

## How to Run

You need to run both the frontend React app and the backend Flask server simultaneously.

### 1. Backend (Flask)

First, set up and run the Python backend server.

1.  **Navigate to the backend directory:**
    ```sh
    cd backend
    ```

2.  **Create a virtual environment (recommended):**
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

4.  **Run the Flask server:**
    ```sh
    python app.py
    ```

The backend server will start on `http://127.0.0.1:5000`. It will automatically create an `uploads/` directory to store files.

### 2. Frontend (React)

Open a **new terminal window** to run the frontend.

1.  **Install dependencies and start the dev server:**
    The project should be set up with a development server like Vite or Create React App. Assuming a standard setup, run:
    ```sh
    npm install && npm run dev
    ```

2.  **Open the app:**
    Open your browser and navigate to the local development URL provided (e.g., `http://localhost:5173`).

Now you can drag and drop files or click to select them, and they will be uploaded to the running Flask backend.
