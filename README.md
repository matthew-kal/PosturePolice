# Posture Police

**Transforming posture, enhancing productivity, empowering developers.**

![last-commit](https://img.shields.io/github/last-commit/matthew-kal/Slouch--DEV)
![repo-top-language](https://img.shields.io/github/languages/top/matthew-kal/Slouch--DEV)
![repo-language-count](https://img.shields.io/github/languages/count/matthew-kal/Slouch--DEV)

---

## 🛠 Built With

`JavaScript` `TypeScript` `MediaPipe` `Node.js` `HTML`

---

## 📚 Table of Contents

- [Overview](#-overview)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#-usage)
- [Settings](#-settings)
- [Testing](#-testing)
- [About Us](#-about-us)

---

## 🧾 Overview

**Posture Police** is a lightweight VS Code extension designed to help developers maintain healthy posture during long coding sessions. It uses real-time posture detection powered by MediaPipe and alerts users when slouching is detected.

### Key Features

- 🧘 **Real-time posture monitoring** using your webcam
- 🔔 **Customizable alerts** (audio or visual)
- 💻 **Seamless VS Code integration** without interrupting your workflow
- 🎨 **User-friendly interface** with intuitive controls and settings
- 🔧 **Performance optimized** and runs entirely on your local device — no data is sent or stored

---

## 🚀 Getting Started

### Prerequisites

---

🔧 **Installation (for VS Code users)**

1. Open Visual Studio Code.  
2. Go to the Extensions Marketplace.  
3. Search for `Posture Police`.  
4. Click **Install**.

To run the extension:

1. Open the Command Palette (`Ctrl+Shift+P`).  
2. Search for `Posture Police: Start Monitoring Posture`.

---

## ⚙️ Settings

Posture Police includes a variety of customizable settings for personalized posture detection:

### Monitoring Settings

- **Camera Active**: Enables or disables webcam posture monitoring. When active, your webcam is used locally to detect your posture in real time.

- **Sensitivity**: Adjusts how sensitive the posture detection system is.  
  - **Lower values (e.g., 0.85)** make the system more tolerant—minor slouching won’t trigger alerts.  
  - **Higher values (e.g., 1.15)** make it more strict—even small posture changes will be flagged.  
  Tune this setting to balance comfort and strictness based on your needs.

- **Alert Delay**: Controls how long poor posture must be sustained before an alert is triggered (1–10 seconds).  
  - Shorter delays (1–3s) are more responsive but may be triggered by brief movements.  
  - Longer delays (5–10s) help avoid false alarms caused by quick stretches or shifts.

- **Volume**: Sets the audio volume for alerts, from 0% (mute) to 100% (maximum).  
  - If you prefer silent operation, set volume to 0% and rely on visual alerts.

- **Mirror Image**: Flips the webcam view horizontally to create a mirrored image.  
  - This is useful if you’re used to seeing yourself as in a mirror, especially on laptop webcams.

- **Sound Alerts**: Enables or disables audio notifications for poor posture.  
  - When off, alerts are shown visually only, without sounds.

- **Head Tilt Detection**: When enabled, includes head angle as part of the posture evaluation.  
  - Tilting your head forward (looking down) or to the side (looking at a second monitor) may trigger alerts.  
  - Turn this off if you frequently move your head away from the screen or use a multi-monitor setup.

### Alert Sounds

Choose from a selection of built-in sound alerts:

- Bell
- Radio
- Sigh
- Siren
- Beep

You can preview each sound using the speaker icon beside each option.

### Demo Alert

Test your current alert settings using the **Trigger Demo** button to simulate a posture alert.

---

## ▶️ Usage

Start the extension from the VS Code command palette:

```text
Posture Police: Start Monitoring Posture
```

Adjust your preferences in the **Settings** tab for full control over monitoring behavior and alerts.

---

## 🧪 Testing

You can test your alert settings directly in the extension UI with the **Trigger Demo** button. Functional testing is integrated via built-in tools.

---

## 👨‍💻 About Us

**Joffre Loor** and **Matthew Kalender** are Computer Science students at Rutgers University. They developed **Posture Police** as part of a mission to help developers maintain healthier work habits while coding.

If you enjoy the extension, consider supporting us!

[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-support-yellow?logo=buy-me-a-coffee&style=for-the-badge)](https://buymeacoffee.com/joffreloormatthewkalender)

---
