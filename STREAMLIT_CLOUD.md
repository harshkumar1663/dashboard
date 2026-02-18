# 🚀 Deploying to Streamlit Cloud

## 1. Push Your Code to GitHub

```bash
cd /media/harsh/Projects/Dashboard

# If not already a git repo:
git init
git add .
git commit -m "SSC Weekly Planner - Initial commit"
git push -u origin main
```

## 2. Deploy on Streamlit Cloud

1. Go to https://share.streamlit.io/
2. Click "New app"
3. Connect your GitHub account
4. Select:
   - **Repository**: Your Dashboard repo
   - **Branch**: `main`
   - **Main file path**: `ssc_weekly_planner.py`
5. Click "Deploy"

✨ Your app is now live!

## 3. Add Secrets

1. In Streamlit Cloud dashboard, find your app
2. Click **⋮** (more options) → **Settings**
3. Scroll to **Secrets**
4. Paste:
```toml
GITHUB_TOKEN = "ghp_your_token_here"
GITHUB_REPO = "your-username/your-tracker-repo"
```
5. Click "Reboot app"

🎉 Done! Your dashboard is live and configured.

## Tips

- Streamlit Cloud is **100% free** for public repos
- App sleeps after 7 days of inactivity (free plan)
- Secrets are **never shared** or committed to GitHub
- Updates auto-deploy when you push to GitHub

## Custom Domain (Optional)

In Streamlit Cloud app settings:
- Add custom domain
- Configure DNS at your domain provider
- Free SSL included

## Support

For issues with Streamlit Cloud:
- https://docs.streamlit.io/library/get-started/installation
- https://docs.streamlit.io/library/advanced-features/secrets-management
