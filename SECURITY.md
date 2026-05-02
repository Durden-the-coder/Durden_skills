# Security Policy

This repository may be used with confidential proposal documents and research materials. Please treat that context seriously.

## Do Not Submit Sensitive Materials

Do not submit any of the following to public GitHub issues, pull requests, discussions, screenshots, logs, or examples:

- real NSFC proposal PDFs or extracted text
- unpublished project applications
- personal information
- grant application attachments
- confidential preliminary data
- unpublished figures, gels, blots, microscopy panels, or statistical plots
- passwords for encrypted PDFs
- institutional review materials or reviewer comments

If you want to report a bug, use synthetic examples or heavily redacted snippets.

## Local Workflow Safety

The `nsfc-mianshang-review` workflow is designed to keep generated artifacts inside a user-specified review directory or an inferred proposal-local review directory.

Users should still verify:

- where generated files are written
- whether extracted text contains sensitive information
- whether review outputs should be redacted before sharing
- whether PDF passwords may appear in shell history

## Reporting Problems

If you find a security, privacy, confidentiality, or unsafe file-writing issue, please open a GitHub issue using a minimal reproduction that does not include sensitive proposal content.

If the issue requires private details, contact the repository owner through GitHub without posting confidential materials publicly.

## Scope

Security concerns include:

- unexpected file writes outside the intended review directory
- accidental inclusion of sensitive content in logs or reports
- unsafe handling of encrypted PDF passwords
- instructions that could encourage disclosure of confidential proposal materials

General review-quality disagreements are not security issues, but they are welcome as normal feedback.
