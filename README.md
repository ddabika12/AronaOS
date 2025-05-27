#  AronaOS - Offline Study and Productivity Assistant

**AronaOS** is an offline desktop assistant designed to help students manage tasks, schedules, and academic conversations through a natural language interface. Powered by a local AI model, AronaOS runs completely offline and provides a clean, intuitive desktop-style experience without relying on cloud services. The files in this GitHub repository is the source code for AronaOS Fragment, which runs a web-based instance of AronaOS Fragment. To actually install AronaOS on your system, follow the instructions given on the "Installation Steps" section of this readme file.

---

##  Key Features

-  Works entirely offline
- ️ Chat interface with a memory-capable local language model
-  To-Do List management with automatic task extraction from chat
-  Visual Calendar for tracking task deadlines
- ️ Lightweight desktop interface using PyWebView
-  No internet required as all data is stored locally

---

## ️ System Requirements

###  AronaOS (Full Version)

**Windows**
- OS: Windows 10/11  
- Minimum: Ryzen 5 / Intel i5, 16 GB RAM, 20 GB Storage  
- Recommended: Ryzen 7 / Intel i7, 32 GB RAM, 30 GB Storage

**macOS**
- OS: macOS Monterey (12) or later  
- Minimum: Apple M1, 16 GB RAM  
- Recommended: M2 Pro / M3, 32 GB RAM

###  AronaOS: Fragment (Lite Version)

**Windows**
- OS: Windows 10/11  
- Minimum: Ryzen 3 / Intel i3, 6 GB RAM  
- Recommended: Ryzen 5 / Intel i5, 8 GB RAM

**macOS**
- OS: macOS Monterey (12) or later  
- Minimum: Apple M1, 6 GB RAM  
- Recommended: Apple M2, 8 GB RAM

---

##  Installation Steps

1. **Download AronaOS or AronaOS: Fragment**

    [Download from Google Drive](https://drive.google.com/drive/folders/1da6655FohV9Kp1Ub3V6pIcepi2ohEmfP?usp=sharing)

2. **Extract the ZIP file**
   - Right-click the downloaded file and choose `Extract All` or use your preferred extraction tool.

3. **Run the App**
   - Inside the extracted folder, double-click:
     - `AronaOS.apk` for full version
     - `AronaOS: Fragment.apk` for the lite version
   - No installation required  the app opens immediately.

 Thats it! Youre ready to use AronaOS.

---

##  Interface Snapshots

###  Main Homepage
Navigate between:
- Chat
- To-Do List
- Calendar View

###  Chat Window
- Offline memory-based chat
- Learn about you (e.g., `Remember my name is Billy`)
- Add tasks via natural language (e.g., `Submit report by tomorrow 3 PM`)

###  To-Do List
- View, edit, and complete tasks
- Automatically syncs with chat input

###  Calendar View
- Displays task deadlines
- Helps visualise scheduling

---

##  Tech Stack

-  Local LLM (trained model, taken from Mistral-7B for AronaOS and Phi-3-mini for AronaOS: Fragment)
- ️ Frontend: HTML/CSS/JS
-  Backend: Flask + SQLite
- ️ UI: PyWebView
- ️ Packaging: Nuitka (for `.apk` generation)

---

##  Documentation

This project was created by:
- Abdualim Alibaev 
- Maleakhi Faith
- Muhammad Naufal Napitupulu
- Oliver You

---

##  Licence

This project is shared for educational purposes. Please contact the authors for any reuse or redistribution permissions.

---

Enjoy using **AronaOS**  your AI-powered study companion that respects your privacy and works even when you're offline.
