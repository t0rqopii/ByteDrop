# ByteDrop

**ByteDrop** is a command-line tool that converts any file into a portable text payload and reconstructs the original file later.

The project started with a simple question:

> If every file is ultimately just bytes, can a video, image, PDF, or ZIP file be turned into plain text and recovered perfectly later?

The answer is yes.

ByteDrop reads a file as raw bytes, optionally compresses it, converts it into a text-safe payload, and later restores the exact original file with checksum verification.

---

## Features

* Works with any file type
* Optional zlib compression
* Text-safe payload format
* SHA-256 integrity verification
* Lossless file recovery
* No third-party dependencies

---

## Example

A file such as:

```text
holiday_photo.png
```

can become:

```text
BYTEDROP-1
{"v":1,"name":"holiday_photo.png","size":...}

eJzsvQmYJ...
...
```

and later be restored as the original image.

The same process works for:

* PNG
* JPG
* GIF
* MP4
* PDF
* ZIP
* Any other binary file

---

## How It Works

### Step 1: Read the file

Every file is stored as bytes.

ByteDrop reads the file directly from disk:

```text
File
↓
Raw bytes
```

---

### Step 2: Optional compression

The byte stream can be compressed using zlib.

```text
Raw bytes
↓
Compressed bytes
```

Compression is useful for files that contain repeated patterns, such as text, logs, JSON files, and source code.

---

### Step 3: Convert bytes into text

The bytes are encoded using Base64.

```text
Bytes
↓
Base64 text
```

This creates a payload that can be stored inside a text file or transmitted through text-only channels.

---

### Step 4: Recover the original file

The process is reversed:

```text
Text payload
↓
Base64 decode
↓
Optional decompression
↓
Original bytes
↓
Original file
```

A SHA-256 checksum is used to verify that the recovered file matches the original.

---

## Commands

### Encode a file

```bash
python bytedrop.py encode movie.mp4 -o payload.txt
```

With compression:

```bash
python bytedrop.py encode movie.mp4 --compress -o payload.txt
```

---

### Decode a payload

```bash
python bytedrop.py decode payload.txt -o recovered_movie.mp4
```

---

## Example Workflow

```bash
python bytedrop.py encode movie.mp4 --compress -o payload.txt

python bytedrop.py decode payload.txt -o recovered_movie.mp4
```

If the payload is unchanged:

```text
SHA256(original) == SHA256(recovered)
```

meaning the recovered file is identical to the original.

---

## Why I Built This

I wanted to explore how binary data can be represented, transported, and reconstructed using only text.

Building ByteDrop was a practical way to learn about:

* Binary file formats
* Compression
* Base64 encoding
* Checksums
* Command-line tooling
* Data representation

---

## Limitations

* This is not encryption.
* Anyone with the payload can reconstruct the file.
* Base64 increases size.
* Compression effectiveness depends on the file type.
* Large files produce large payloads.

---

## Future Improvements

* Multi-part payloads for large files
* QR-code export
* Error-correction support
* Payload chunking and reassembly
* Drag-and-drop desktop interface
