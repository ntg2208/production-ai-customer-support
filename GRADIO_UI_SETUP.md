# Gradio UI Setup Notes

## Status: ✅ Configured and Ignored by Git

The `gradio_ui` directory has been copied from the base project but is **not tracked by git** in the premium repository.

## What Was Done

1. ✅ **Copied gradio_ui** from `/production-ai-customer-support/gradio_ui`
2. ✅ **Added to .gitignore** - Line 215: `gradio_ui/`
3. ✅ **Verified paths work** - All imports and dependencies verified
4. ✅ **Confirmed git ignores it** - Directory and all files excluded from version control

## Why Not Tracked?

The gradio_ui is maintained in the **base project** (`production-ai-customer-support`) and copied to premium as needed. This prevents:
- Code duplication in version control
- Merge conflicts between repositories
- Diverging UI implementations

## Git Status Verification

```bash
$ git status
# gradio_ui/ does NOT appear (properly ignored)

$ git check-ignore -v gradio_ui/
.gitignore:215:gradio_ui/    gradio_ui/
```

## How to Update Gradio UI

If the base project updates the Gradio UI, update the premium copy:

```bash
# Remove old version
rm -rf gradio_ui/

# Copy latest version
cp -r /Users/ntg/Documents/Personal_Projects/Agents/customer_support/production-ai-customer-support/gradio_ui .

# Verify it works
python -c "from agent import get_master_agent; print('✅ Imports work')"
```

## Launch Commands

The Gradio UI works exactly the same in premium:

```bash
# Option 1: Launch script
./gradio_ui/launch.sh

# Option 2: Direct Python
python gradio_ui/app.py
```

## Important Notes

- ✅ **Paths auto-configure** - No changes needed after copying
- ✅ **Database works** - Accesses premium database automatically
- ✅ **Environment uses premium .env** - Uses premium API key and config
- ✅ **Agents are premium agents** - Uses premium master agent and sub-agents

## Files Excluded from Git

```
gradio_ui/
├── app.py
├── launch.sh
├── launch.bat
├── requirements.txt
├── *.md (all documentation)
├── components/
│   ├── customer_profiles.py
│   ├── agent_visualizer.py
│   └── message_processor.py
└── assets/
```

All files and subdirectories are ignored by git.

---

**Last Updated:** October 11, 2025  
**Git Status:** Properly ignored  
**Working:** Yes
