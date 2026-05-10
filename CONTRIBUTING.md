# Contributing to EchoGen

Thank you for your interest in contributing to EchoGen! As an autonomous reasoning layer for Solana, we welcome developers, data scientists, and blockchain enthusiasts to help us bridge the "meaning gap" in Web3.

## How to Contribute

### 1. Reporting Bugs
- Use the GitHub Issue Tracker.
- Provide a clear description of the bug and steps to reproduce.
- Include environment details (Node version, Python version, Browser).

### 2. Feature Requests
- Open an issue with the [Feature] tag.
- Explain the "Why" — what causal intelligence gap does this feature bridge?

### 3. Pull Requests
- Fork the repository.
- Create a new branch: `git checkout -b feature/your-feature-name`.
- Ensure your code follows the existing style (Prettier for Frontend, PEP8 for Backend).
- Update the `README.md` or `docs/` if you are adding new sensors or protocols.
- Submit a PR with a detailed description of your changes.

## Technical Architecture Overview

- **Frontend:** Next.js 15, Tailwind CSS, `@solana/web3.js`.
- **Backend:** FastAPI, Python, Prisma ORM.
- **Sensors:** Located in `backend/sensors/`. New sensors should follow the plug-and-play pattern defined in the existing registry.

## Code of Conduct

Please be respectful and professional in all interactions. We aim to build a community of high-intelligence, high-integrity contributors.

---

*EchoGen is currently in its Hackathon MVP phase. We prioritize stability, verifiable reasoning, and sleek user experience.*
