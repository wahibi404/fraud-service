# Secret leak drill

The Lab 6 rehearsal used the fake value `ghp_THIS_IS_A_FAKE_TOKEN_FOR_THE_DRILL` locally. It was added to `configs/dev.env` in one temporary commit and deleted in the next. `git log -p --all -S 'ghp_THIS_IS'` exposed the value in both diffs even after deletion. The two temporary commits were dropped with `git reset --hard HEAD~2` before pushing. The lab guides themselves contain this public example string; no real credential was used.

If a real token leaks:

1. Revoke or rotate it immediately in the issuing service, and audit its use.
2. Remove it from files and history, coordinate with collaborators who cloned it, and purge cached copies where possible.
3. Add a secret scanner to local hooks and CI, and investigate how the leak occurred.

Deleting a line alone does not remove a token from Git history. Never commit a real token or a `.env` file.
