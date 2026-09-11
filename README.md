# 🌙 Loona — AI Desktop Companion

Loona is a personal AI desktop companion designed to understand natural language and interact with a Windows PC.

The goal is to build an AI that can understand what the user wants, use the appropriate tools, perform actions on the computer, verify the result, and respond naturally.

## ✨ Vision

Loona is being developed to become a capable personal AI companion that works alongside the user and interacts with their digital environment.

Her core workflow is:

**Understand → Plan → Act → Verify → Report**

For example:

> "Loona, open the Oblivion movie."

Loona can understand the request, search the user's local drives, identify the appropriate file, open it, verify the action, and report the result.

## 🚀 Current Features

- 🤖 Gemini-powered AI agent
- 🌙 Custom Loona identity and personality
- 🧠 Persistent user profile and memory
- 📁 Local file searching
- 🎬 Media and file opening
- 🖥️ Windows application searching
- ▶️ Application launching
- ⏹️ Application closing
- 🕐 Date and time information
- 💻 System information
- 🔧 Custom Loona tools
- 🛡️ Safety and confirmation rules
- 🔄 Agent tool workflow
- ⚙️ Automation framework support

## 🧩 Architecture

Loona is built on top of the Hermes Agent framework.

```text
User
  ↓
Loona
  ↓
AI Model
  ↓
Agent / Tool Loop
  ↓
Loona Tools
  ↓
Windows PC