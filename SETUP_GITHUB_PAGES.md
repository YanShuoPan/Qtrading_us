# GitHub Pages Setup Guide

Quick guide to deploy US Stocks Autobot to GitHub Pages.

## 📋 Prerequisites

- GitHub account
- Git installed locally

## 🚀 Step-by-Step Setup

### Step 1: Create GitHub Repository

1. Go to [GitHub](https://github.com) and create a new repository
2. Name it `us-stocks-autobot` (or any name you prefer)
3. Set as **Public** (required for free GitHub Pages)
4. Do **NOT** initialize with README (we already have one)

### Step 2: Push Code to GitHub

```bash
# Navigate to project directory
cd us-stocks-autobot

# Initialize git (if not already)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - US Stocks Autobot"

# Add remote repository (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/us-stocks-autobot.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### Step 3: Enable GitHub Pages

1. Go to your repository on GitHub
2. Click **Settings** (top menu)
3. Click **Pages** (left sidebar)
4. Under "Build and deployment":
   - **Source**: Select **GitHub Actions**
5. Click **Save**

### Step 4: Enable GitHub Actions

1. Go to the **Actions** tab in your repository
2. If you see a message about workflows:
   - Click **"I understand my workflows, go ahead and enable them"**

### Step 5: Run the Workflow

#### Option A: Manual Run (Recommended for first time)

1. Go to **Actions** tab
2. Click **"Daily Stock Picks"** workflow (left sidebar)
3. Click **"Run workflow"** button (right side)
4. Select branch: **main**
5. Click **"Run workflow"**
6. Wait 3-5 minutes for completion

#### Option B: Wait for Automatic Run

The workflow automatically runs every day at **9:30 PM EST** (after US market close), Tuesday through Saturday.

### Step 6: View Your GitHub Pages Site

1. After workflow completes successfully
2. Go to **Settings** → **Pages**
3. You'll see: **"Your site is live at https://YOUR_USERNAME.github.io/us-stocks-autobot/"**
4. Click the link to view your site
5. Bookmark it! 📌

## 🔍 Troubleshooting

### Workflow Failed?

1. Go to **Actions** tab
2. Click on the failed run
3. Check the error logs
4. Common issues:
   - **yfinance download errors**: Network timeout, try re-running
   - **Permission denied**: Check repository permissions
   - **Pages not enabled**: Make sure GitHub Pages is set to "GitHub Actions"

### No Data Showing?

1. Make sure the workflow ran successfully
2. Check if `docs/` directory exists in your repository
3. Look for `index.html` in the `docs/` folder

### Changes Not Appearing?

1. GitHub Pages may take 1-2 minutes to update
2. Try hard refresh: `Ctrl+F5` (Windows) or `Cmd+Shift+R` (Mac)
3. Clear browser cache

## 📅 Schedule

The GitHub Action runs automatically:
- **Time**: 9:30 PM EST (2:30 AM UTC next day)
- **Days**: Tuesday to Saturday
- **Covers**: Monday to Friday US trading days

## 🛠️ Customization

### Change Schedule

Edit `.github/workflows/daily-picks.yml`:

```yaml
schedule:
  - cron: '30 2 * * 2-6'  # Change this line
```

Cron format: `minute hour day-of-month month day-of-week`

Example:
- `'0 14 * * 1-5'` = 2:00 PM UTC, Monday-Friday
- `'30 20 * * *'` = 8:30 PM UTC, every day

Use [crontab.guru](https://crontab.guru/) to create custom schedules.

### Change Stock Universe

Edit `.env` or set environment variable:

```bash
US_STOCK_CODES=AAPL,MSFT,GOOGL,AMZN,TSLA,NVDA
```

## ✅ Verification Checklist

- [ ] Repository created and code pushed
- [ ] GitHub Pages enabled with "GitHub Actions" source
- [ ] GitHub Actions enabled
- [ ] Workflow ran successfully (green checkmark)
- [ ] `docs/` directory exists with HTML files
- [ ] GitHub Pages URL accessible
- [ ] Daily picks displayed correctly

## 🎉 Success!

Your US Stocks Autobot is now live! Visit your GitHub Pages URL to see:
- 📊 Daily stock picks
- 📈 Interactive charts
- 📅 30-day historical archive

The site updates automatically every trading day after market close.

## 📞 Need Help?

- Check [GitHub Actions documentation](https://docs.github.com/en/actions)
- Check [GitHub Pages documentation](https://docs.github.com/en/pages)
- Review workflow logs in the Actions tab

---

**Note**: Remember to replace `YOUR_USERNAME` with your actual GitHub username throughout this guide.
