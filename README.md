# `noosphere` Sample Projects

## Overview

To help developers easily understand and utilize the features of the noosphere platform, this repository provides a set of sample projects covering various use cases. Each project includes all the necessary components to build, run, and deploy a computation node.

## Prerequisites

Before you begin, ensure you have the following installed on your system:

-   Docker
-   Make

## 1. Initial Configuration

Before building or pushing any images, you **must** configure your GitHub username or organization name. This is required for tagging images correctly for GitHub Packages (ghcr.io).

1.  Open the `common.mk` file in the root of this project.
2.  Find the line `GH_OWNER ?= hpp-io`.
3.  Replace `hpp-io` with your actual GitHub username or organization name.

**Example:**
```makefile
# common.mk

# Set your GitHub username or organization name here.
GH_OWNER ?= jjang
```

## 2. Project Structure

The repository is organized as follows:

```
.
├── Makefile              # Top-level Makefile to manage all projects
├── common.mk             # Common logic shared by all project Makefiles
├── projects/
│   ├── hello-world/      # Basic "Hello World" computation project
│   ├── llm/              # A flexible LLM routing service
│   ├── open-ai/          # A dedicated OpenAI computation node
│   └── freqtrade/        # A freqtrade bot with an ML strategy
└── README.md
```

## 3. Getting Started

All commands should be run from the **root directory** of the project. The `project` variable is used to specify which sample project you want to work with.

### Build a Container

To build the Docker image for a specific project:

```sh
make build-container project=<project-name>
```

**Example:**
```sh
make build-container project=freqtrade
```

### Run a Container

To run a container (it will automatically stop any previous instance):

```sh
make run project=<project-name>
```

**Example:**
```sh
make run project=freqtrade
```

### Test the API

Once a container is running, you can send a test request:

```sh
make try-request project=<project-name>
```

### Stop a Container

To stop a running project container:

```sh
make stop-container project=<project-name>
```

### Push an Image to GitHub Packages

To push a built image to your GitHub Packages registry:

1.  **Log in to GitHub Packages**: You only need to do this once. You'll need a Personal Access Token (PAT) with `write:packages` scope.
    
    ```sh
    export CR_PAT=YOUR_PERSONAL_ACCESS_TOKEN
    echo $CR_PAT | docker login ghcr.io -u YOUR_GITHUB_USERNAME --password-stdin
    ```

2.  **Push the image**:
    
    ```sh
    make push-container project=<project-name>
    ```

## 4. Available Projects

### `hello-world`
**Description**: An introductory project that demonstrates how to request a basic computation and receive the result through noosphere.
**Goal**: To help developers understand the minimal functional unit of noosphere and set up their development environment.

### `llm` (Large Language Model)
**Description**: A project that acts as a flexible LLM router. It routes requests to Gemini directly and all other providers (like OpenAI, Anthropic) through a configurable gateway (`LLMROUTER`).
**Goal**: To show how complex computations involving multiple off-chain API interactions can be handled via noosphere.

### `freqtrade`
**Description**: A project that uses the popular trading bot library `freqtrade` to analyze market data and make predictions with a custom ML strategy.
**Goal**: To provide a practical example of how heavy computational tasks, such as data analysis and machine learning, can be leveraged on noosphere.

---