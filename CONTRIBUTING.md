# Contributing to ZEON

Thank you for your interest in contributing to ZEON (Zero-overhead Encoding Object Notation)! This project focuses on maximizing token efficiency for LLMs.

To ensure code quality and format stability, we enforce a strict and organized workflow. Please read the guidelines below before starting any work.

## Rules and Workflow

1. **No Direct Pushes to Main:**
   Direct pushes to the `main` branch are strictly prohibited (and blocked by repository settings). All new code must be developed in a separate branch.

2. **Creating Pull Requests (PRs):**

   **For External Contributors:**
   - **Fork** the repository to your own GitHub account.
   - Clone your fork locally and create a new branch using the format `feature/feature-name` or `fix/bug-name`.
   - Push your changes to your fork.
   - Open a Pull Request from your fork against our `main` branch.

   **For Organization Members:**
   - Create a new branch locally using the format `feature/feature-name` or `fix/bug-name`.
   - Push your branch directly to this repository and open a Pull Request against `main`.

3. **Review and Approval:**
   - No Pull Request will be merged automatically.
   - Every PR requires explicit review and approval from the project's core maintainer (or designated reviewers).
   - Be open to receiving feedback and making adjustments to your code during the review process.

## Development Environment

To run the project and tests locally:

1. Ensure you have Python 3.10+ and `poetry` installed.
2. Install the dependencies:
   ```bash
   poetry install
   ```
3. Run the benchmarks and local tests before submitting your PR:
   ```bash
   poetry run python tests/test_benchmark.py
   ```

We appreciate your time and effort in making ZEON better!
