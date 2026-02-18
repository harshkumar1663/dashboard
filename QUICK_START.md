# ⚡ Super Quick Start

For Streamlit Cloud or fast setup, follow these 3 steps:

## Step 1: Run the App
```bash
pip install -r requirements.txt
streamlit run ssc_weekly_planner.py
```

## Step 2: Add Secrets (First Time Only)
When the app loads:
1. **Click the ⚙️ icon** (top-right corner)
2. **Click "Secrets"**
3. **Paste this** and replace with your actual values:
```toml
GITHUB_TOKEN = "ghp_your_actual_token_here"
GITHUB_REPO = "your-username/your-repo"
```

## Step 3: Get GitHub Token (1 minute)
1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Name: `ssc-weekly-planner`
4. Select **ONLY** `repo` checkbox (✅)
5. Click "Generate token"
6. **Copy the token** (appears once!)
7. Paste into Streamlit Secrets above

## Step 4: Refresh
- Press F5 or click the Refresh button
- **Done!** 🎉

---

## Troubleshooting

**"App is in the oven" for >30 seconds?**
- First load takes 5-10 seconds (normal)
- Refresh page if it hangs
- Check GitHub token is valid

**"Data files not found"?**
- Make sure your GitHub repo has:
  - `gk_data.json`
  - `maths_data.json`
- Files must be **committed** to the branch

**"Token is invalid"?**
- Go back to https://github.com/settings/tokens
- Delete old token, create new one
- Make sure you selected `repo` scope
- Copy-paste the full token (don't edit it)

---

## Streamlit Cloud Deployment

To deploy on Streamlit Cloud:

1. **Push to GitHub**:
```bash
git add .
git commit -m "SSC Weekly Planner"
git push
```

2. **Deploy on Streamlit Cloud**:
   - Go to https://share.streamlit.io/
   - Connect your GitHub repo
   - Select branch: `main`
   - File path: `ssc_weekly_planner.py`
   - Click "Deploy"

3. **Add Secrets** in Streamlit Cloud:
   - Dashboard → Settings → Secrets
   - Add `GITHUB_TOKEN` and `GITHUB_REPO`
   - Reboot the app

**Done!** Your dashboard is live 🚀

---

## Performance Tips

- ✅ Data caches for 5 minutes (super fast)
- ✅ Click refresh to clear cache instantly
- ✅ First load: ~5-10 seconds
- ✅ Subsequent loads: <1 second

---

## Need Help?

- Check `SETUP.md` for detailed instructions
- Run `python test_github.py` to test connection
- Check `CONFIG_REFERENCE.md` for data format help
