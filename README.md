# Project Manager Assistant Agent

<div align="center">

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)
[![Managed with: uv](https://img.shields.io/badge/managed%20with-uv-ef.svg)](https://github.com/astral-sh/uv)
[![Framework: FastAPI](https://img.shields.io/badge/Framework-FastAPI-teal)](https://fastapi.tiangolo.com/)

</div>

<p align="center">
  <a href="#-english-readme">English</a> •
  <a href="#-简体中文-readme">简体中文</a>
</p>

---

## 🇬🇧 English README

### Overview

This project is an AI agent designed to assist with project management. It can take a natural language project description, break it down into actionable tasks, analyze dependencies, create a schedule, and assign tasks to team members based on their skills. The agent uses an iterative self-reflection loop to assess and reduce project risks, transforming complex requirements into a structured, optimized plan.

### ✨ Key Features

-   **Automated Task Extraction**: Converts project descriptions into a detailed list of actionable tasks.
-   **Intelligent Dependency Analysis**: Automatically identifies and maps dependencies between tasks.
-   **Optimized Scheduling & Allocation**: Creates an efficient timeline and assigns tasks to the best-suited team members.
-   **Iterative Risk Reduction**: Employs a self-reflection loop to assess risks and refine the plan for a better outcome.
-   **Modern Tech Stack**: Built with FastAPI for the API, LangGraph for the agent workflow, and Redis Queue for asynchronous processing.
-   **Interactive UI**: Includes a Streamlit application for easy interaction and visualization of the results.

### 🏗️ Architecture

This project follows a modern, scalable architecture designed for production AI applications:

-   **FastAPI Backend**: Serves the core agent logic via a robust, asynchronous API.
-   **Streamlit UI**: Provides a user-friendly interface for rapid prototyping and demonstration.
-   **LangGraph**: Orchestrates the complex, cyclical workflow of the agent.
-   **Redis Queue (RQ)**: Handles long-running agent tasks asynchronously to prevent API timeouts.
-   **Pydantic**: Ensures data integrity and powers the structured outputs from the LLM.
-   **Docker**: Containerizes the application for consistent development and deployment environments.

![Agent Graph](https://raw.githubusercontent.com/langchain-ai/langgraph/main/docs/static/img/compiler_xray.png)
*Agent graph visualization.*

### 🚀 Getting Started

#### Prerequisites

-   [uv](https://github.com/astral-sh/uv) - An extremely fast Python package installer and resolver.
-   [Redis](https://redis.io/topics/quickstart) server running.
-   Python 3.9+

#### Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-repo/project-manager-assistant.git
    cd project-manager-assistant
    ```

2.  **Create virtual environment and install dependencies using `uv`:**
    This single command creates a virtual environment in `.venv` and installs all dependencies from `pyproject.toml`.
    ```bash
    uv pip sync pyproject.toml
    ```

3.  **Configure environment variables:**
    Copy the example `.env.example` file to `.env` and fill in your API keys.

### ▶️ How to Run

Use the provided shell script to launch the entire application stack (API, Worker, and UI).

```bash
bash run.sh
```

-   The **API** will be available at `http://127.0.0.1:8000/docs`.
-   The **Streamlit UI** will be available at `http://127.0.0.1:8501`.

Navigate to the Streamlit UI, provide a project description and a team CSV file, and click "Generate Plan" to see the agent in action.

---

## 🇨🇳 简体中文 README

### 项目概览

本项目是一个用于辅助项目管理的AI智能体（Agent）。它能够接收自然语言描述的项目需求，并自动将其分解为可执行的任务列表、分析任务依赖、创建时间计划，并根据团队成员的技能进行任务分配。该智能体通过一个迭代式的自我反思循环来评估和降低项目风险，从而将复杂需求转化为结构化、最优化的项目计划。

### ✨ 核心功能

-   **自动任务提取**: 将项目描述转化为详细、可执行的任务清单。
-   **智能依赖分析**: 自动识别并构建任务之间的依赖关系图。
-   **优化排期与分配**: 创建高效的项目时间线，并将任务分配给最合适的团队成员。
-   **迭代式风险降低**: 采用自我反思循环来评估计划风险，并持续优化以获得更好的结果。
-   **现代化技术栈**: 基于 FastAPI 构建API，使用 LangGraph 编排智能体工作流，并通过 Redis Queue 处理异步任务。
-   **交互式用户界面**: 包含一个 Streamlit 应用，便于用户交互和结果可视化。

### 🏗️ 系统架构

本项目遵循为生产级AI应用设计的现代化、可扩展的架构：

-   **FastAPI 后端**: 通过健壮的异步API提供核心智能体服务。
-   **Streamlit 前端**: 提供用户友好的界面，用于快速原型设计和功能演示。
-   **LangGraph**: 编排智能体复杂的、循环式的工作流。
-   **Redis 队列 (RQ)**: 异步处理耗时的智能体任务，防止API请求超时。
-   **Pydantic**: 保证数据模型的完整性，并驱动LLM的结构化输出。
-   **Docker**: 将应用容器化，确保开发与部署环境的一致性。

![Agent Graph](https://raw.githubusercontent.com/langchain-ai/langgraph/main/docs/static/img/compiler_xray.png)
*智能体工作流图的可视化展示。*

### 🚀 快速开始

#### 环境要求

-   [Poetry](https://python-poetry.org/) (用于依赖管理)
-   正在运行的 [Redis](https://redis.io/topics/quickstart) 服务
-   Python 3.9+

#### 安装与配置

1.  **克隆项目仓库:**
    ```bash
    git clone https://github.com/your-repo/project-manager-assistant.git
    cd project-manager-assistant
    ```

2.  **使用 `uv` 创建虚拟环境并安装依赖:**
    下面这个命令会创建一个 `.venv` 虚拟环境，并安装 `pyproject.toml` 中定义的所有依赖。
    ```bash
    uv pip sync pyproject.toml
    ```

3.  **配置环境变量:**
    复制 `.env.example` 文件为 `.env`，并填入您的API密钥。

### ▶️ 如何运行

使用我们提供的脚本来一键启动整个应用（API, Worker, 和前端UI）。

```bash
bash run.sh
```

-   **API** 将运行在 `http://127.0.0.1:8000/docs`。
-   **Streamlit UI** 将运行在 `http://127.0.0.1:8501`。

在浏览器中打开 Streamlit 界面，输入项目描述、上传团队CSV文件，然后点击“生成项目计划”即可体验智能体的强大功能。
