# Screenshots

Screenshots never go on a feature branch or the default branch. They live on
the branch `pr-screenshots`, which shares no history with the default branch,
in one folder per ticket, `pr-<n>/` (the ticket's number).

```sh
git fetch origin pr-screenshots && git worktree add --detach ../pr-shots FETCH_HEAD
mkdir -p ../pr-shots/pr-<n> && cp <files> ../pr-shots/pr-<n>/
cd ../pr-shots && git add pr-<n> && git commit -m "Screenshots for #<n>" \
  && git push origin HEAD:pr-screenshots
```

Link each image in the pull request by that commit, not by the branch name.
Capture invented data only. This repository is public: nothing from a private
repository goes into it.
