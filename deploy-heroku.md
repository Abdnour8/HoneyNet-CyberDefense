# 🚀 HoneyNet Heroku Deployment Guide

## Why Heroku? (Much Simpler than AWS!)
- ✅ **Free tier available** (up to 1000 hours/month)
- ✅ **No credit card required** for basic usage
- ✅ **Simple deployment** with Git
- ✅ **Automatic HTTPS** and domain
- ✅ **Built-in monitoring**

## Step 1: Create Heroku Account
1. Go to: https://signup.heroku.com/
2. Sign up with your email
3. Verify email and set password

## Step 2: Install Heroku CLI
**Windows:**
- Download: https://devcenter.heroku.com/articles/heroku-cli#install-the-heroku-cli
- Or use: `npm install -g heroku` (if you have Node.js)

**Verify installation:**
```bash
heroku --version
```

## Step 3: Login to Heroku
```bash
heroku login
```
This will open a browser window for authentication.

## Step 4: Prepare Your Project
```bash
# Navigate to your project
cd "c:\Users\וינריך\Downloads\מערכת חכמה למלחמה בהאקרים זדוניים"

# Initialize git (if not already done)
git init
git add .
git commit -m "Initial HoneyNet deployment"
```

## Step 5: Create Heroku App
```bash
# Create app with unique name
heroku create honeynet-zeev-2024

# Or let Heroku generate a name
heroku create
```

## Step 6: Set Environment Variables
```bash
heroku config:set DEPLOYMENT_MODE=production
heroku config:set SECRET_KEY=your-super-secret-key-here
heroku config:set REQUIRE_HTTPS=true
heroku config:set LOG_LEVEL=INFO
```

## Step 7: Deploy!
```bash
git push heroku main
```

## Step 8: Open Your App
```bash
heroku open
```

## 🎉 That's It!
Your HoneyNet will be available at: `https://your-app-name.herokuapp.com`

## Heroku Commands Cheat Sheet
```bash
heroku logs --tail          # View live logs
heroku ps                   # Check app status
heroku restart              # Restart app
heroku config               # View environment variables
heroku releases             # View deployment history
```

## Cost Breakdown
- **Free Tier**: 1000 hours/month (enough for testing)
- **Hobby Plan**: $7/month (always on, custom domain)
- **Production**: $25-50/month (better performance)

## Advantages over AWS
- ✅ No complex setup
- ✅ Automatic SSL certificates
- ✅ Built-in CI/CD
- ✅ Easy scaling
- ✅ Integrated monitoring
- ✅ Free tier for testing
