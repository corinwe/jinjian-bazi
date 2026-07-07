# GitHub Pages Deployment Pitfalls

## `.nojekyll` file is REQUIRED

GitHub Pages runs Jekyll by default, which may refuse to serve certain files:
- Files in subdirectories like `reports/*.md` can return 404
- Only `index.html` and root-level files may be accessible

**Solution**: Add an empty `.nojekyll` file to the repo root:
```bash
touch .nojekyll
git add .nojekyll
git commit -m "➕ Add .nojekyll (disable Jekyll processing)"
git push
```

After adding `.nojekyll`, Pages deploys files as-is, serving all paths including subdirectory `.md` files.

## Deployment Delay
After `git push`, GitHub Pages takes ~15-30 seconds to deploy. During this window:
- `index.html` may serve stale content
- New files in subdirectories return 404

Wait and refresh.

## Source Settings
Pages can be deployed from:
- `main` branch root (`/`)
- `main` branch `/docs` folder
- `gh-pages` branch

Check current setting: GitHub repo → Settings → Pages → Source
