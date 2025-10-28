# Legacy Install System Files

**Date Archived:** October 27, 2025
**Reason:** Migration from single-component to unified dual-component installer

---

## Overview

This folder contains deprecated files from the original `install.bat`/`uninstall.bat` system that has been replaced by the new `MasterInstall.bat`/`MasterUninstall.bat` unified installer.

## Why These Files Are Here

The AI Environment Installer project evolved through several phases:

### Original System (v1.x - v2.x)
- **Entry Point:** `install.bat` → `install_manager.py`
- **Purpose:** Install AI_Environment only (runtime environment)
- **Components:** Miniconda, VS Code, Ollama, Python packages
- **Location:** Single installation at `Drive:\AI_Environment`

### New Unified System (v3.x+)
- **Entry Point:** `MasterInstall.bat` → `master_installer.py` → `install_manager.py` + `ai_lab_installer.py`
- **Purpose:** Install both AI_Environment (runtime) AND AI_Lab (source code from GitHub)
- **Components:** Everything from v1.x PLUS AI_Lab repository
- **Modes:**
  - External Drive (Student): `F:\AI_Lab\AI_Environment\`
  - Internal Drive (Standard): `D:\AI_Environment\` + `D:\AI_Lab\`

---

## Folder Structure

```
legacy_install_system/
├── batch_files/          # Deprecated .bat entry points
├── status_files/         # Old status tracking and temp files
├── documentation/        # Development phase documentation
└── README_LEGACY.md      # This file
```

---

## What's Deprecated

### Batch Files (`batch_files/`)

| File | Replaced By | Notes |
|------|-------------|-------|
| `install.bat` | `MasterInstall.bat` | Original single-component installer |
| `uninstall.bat` | `MasterUninstall.bat` | Original uninstaller |
| `update_status.bat` | Built into master installer | Status update utility |
| `validate.bat` | May be re-integrated | Installation validator |
| `find_ai_env.bat` | Built into automated_uninstaller.py | Path detection utility |

### Status Files (`status_files/`)

| File | Replaced By | Notes |
|------|-------------|-------|
| `installation_status.json` | `master_installation_status.json` | Old single-component status |
| `QUICK_RESUME.json` | Development notes | Phase 1 resume tracking |
| `QUICK_RESUME_PHASE2.json` | Development notes | Phase 2 resume tracking |
| `IMPLEMENTATION_STATUS.json` | Development notes | Implementation progress |
| `PHASE2_IMPLEMENTATION_STATUS.json` | Development notes | Phase 2 progress |
| `REMAINING_WORK.json` | Development notes | TODO tracking |
| `REMAINING_WORK_PHASE2.json` | Development notes | Phase 2 TODO tracking |
| `C:temp_*.txt` | N/A | Temporary comparison files |
| `temp_packages.txt` | N/A | Temporary package list |

### Documentation (`documentation/`)

| File | Type | Notes |
|------|------|-------|
| `Development_stages.txt` | Development notes | Historical development stages |
| `GIMINI-AI Environment Installer - Software Definition Document.txt` | Old spec | Alternate/old specification |
| `INSTALLER_ENHANCEMENTS.md` | Development notes | Enhancement tracking |
| `PHASE1_COMPLETE.md` | Milestone doc | Phase 1 completion summary |
| `PHASE2_COMPLETE.md` | Milestone doc | Phase 2 completion summary |
| `TEST_PLAN.json` | Testing doc | Original test plan |
| `PHASE2_TESTING_PLAN.json` | Testing doc | Phase 2 test plan |
| `TEST_RESULTS.md` | Testing results | Test execution results |
| `TESTING_RESULTS_PHASE2.json` | Testing results | Phase 2 test results |
| `TESTING_RESUME_GUIDE.json` | Testing guide | Resume testing guide |
| `UNINSTALLER_V2_COMPLETE.md` | Milestone doc | Uninstaller v2.0 completion |

---

## What's Still Active

The following components remain active in the main system:

### Active Entry Points
- `MasterInstall.bat` - Main unified installer
- `MasterUninstall.bat` - Main unified uninstaller

### Active Python Modules (all in `src/`)
All Python modules in the `src/` directory are still active and used by the master installer:
- `master_installer.py` - Main orchestration
- `installation_status_manager.py` - Unified status tracking
- `ai_lab_installer.py` - GitHub repository cloning
- `install_manager.py` - AI_Environment installation (8 steps)
- `automated_uninstaller.py` - Smart uninstaller with auto-detection
- All specialized installers: `conda_installer.py`, `vscode_installer.py`, `ollama_installer.py`, etc.

### Active Status Files
- `master_installation_status.json` - Unified status for both AI_Environment and AI_Lab

### Active Documentation
- `README.md` - Main user documentation
- `Claude-AI Environment Installer - Software Definition Document.txt` - Current specification
- `ARCHITECTURE_SUMMARY.json` - System architecture reference

---

## Migration Notes

### For Developers

If you need to reference old implementation details:
1. Check `documentation/` for phase completion summaries
2. Check `status_files/` for old tracking data
3. The old `install.bat` logic is preserved in `batch_files/install.bat`

### Backward Compatibility

The new system maintains backward compatibility:
- `automated_uninstaller.py` can detect and remove old installations
- Fallback mechanisms look for legacy `installation_status.json` files
- Old installations can be upgraded by running `MasterInstall.bat`

### If You Need to Restore

If you need to temporarily restore the old single-component installer:
1. Copy `batch_files/install.bat` back to root
2. Copy `batch_files/uninstall.bat` back to root
3. Note: May not be fully compatible with v3.x Python modules

---

## Timeline

- **v1.0 - v2.0:** Single-component installer (AI_Environment only)
- **v3.0.x:** Transition to dual-component system
- **v3.0.28:** Master installer completed, old files archived (October 2025)

---

## Questions?

For current installation procedures, see the main `README.md` in the project root.

For technical details about the new architecture, see `ARCHITECTURE_SUMMARY.json`.
