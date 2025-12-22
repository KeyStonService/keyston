# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [Unreleased] - 2025-12-21

### Added


- Initial AGENTS.md with status marker conventions for AI agents
- CHANGELOG.md for tracking all project changes
- RISK_ASSESSMENT.md for risk management framework
- Enhanced PR template with mobile-friendly design and governance compliance

### Changed
- Updated `.github/PULL_REQUEST_TEMPLATE.md` with improved structure:
  - Added comprehensive status marking guidelines (✅ ⏸️ 🔄 ❌ ⏭️)
  - Enhanced evidence chain requirements
  - Improved mobile device friendliness
  - Added logical consistency rules
- Pinned GitHub Actions to full commit SHAs in aaps-phase1-gates.yml:
  - actions/checkout@v4 → @0ad4b8f3a27c304e21892351cbf9860471245599
  - actions/setup-python@v5 → @82c7e631bb3cdc910f68e0081d534527d238d7a7
  - actions/upload-artifact@v4 → @65462800fd760344b1a7b4382951275a0abb4808

### Fixed
- GitHub Actions SHA pinning compliance issue
- PR template logical inconsistency between completion status and reviewer checklist
- Evidence chain validation gaps in AI delivery process

### Security
- Mitigated dependency drift risk by pinning Actions to specific commit SHAs
- Enhanced supply chain security through immutable action references

### Deprecated
- Removed `.github/PULL_REQUEST_TEMPLATE_IMPROVED.md` (merged into main template)

---

## [Previous Releases]

### Version History
For previous version history, please refer to git commit history and individual component release notes.