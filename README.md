# whispa-ai-notes-app

## Overview

The Whispa AI Notes App is an application designed to analyze screen captures and voice input to generate structured notes. It utilizes Optical Character Recognition (OCR) and / or AI model for image processing and transcribes audio input using Faster Whisper, ensuring all processes are handled in-memory to comply with data privacy standards.

## Features

- **OCR Processing**: Convert images into text using OCR technology.
- **Audio Processing**: Convert voice notes into text using Faster Whisper.
- **Note Generation**: Combine text from images and audio to create structured notes.
- **Data Privacy**: All processing is done in-memory, ensuring compliance with data privacy regulations.

## Project Structure

```
whispa-ai-notes-app
├── app
│   ├── main.py
│   ├── config.py
│   ├── routers
│   │   ├── ocr.py
│   │   ├── audio.py
│   │   └── notes.py
│   ├── services
│   │   ├── ocr_service.py
│   │   ├── audio_service.py
│   │   └── notes_service.py
│   ├── models
│   │   └── schemas.py
│   ├── utils
│   │   └── privacy.py
│   └── deps.py
├── tests
│   ├── test_ocr.py
│   ├── test_audio.py
│   └── test_notes.py
├── .env.example
├── requirements.txt
├── pyproject.toml
└── README.md
```

## Installation

1. Clone the repository:

   ```
   git clone https://github.com/myesua/whispa-ai.git
   cd whispa-ai
   ```

2. Create a virtual environment:

   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required dependencies:

   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables by copying `.env.example` to `.env` and updating the values as needed.

## Usage

To run the application, execute:

```
uvicorn app.main:app --reload
```

You can then access the API at `http://127.0.0.1:8000`.

## API Endpoints

- **POST /ocr**: Process an image to extract text.
- **POST /audio**: Process audio input to convert speech to text.
- **POST /notes**: Generate notes from processed image and audio data.

## Testing

To run the tests, use:

```
pytest
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
