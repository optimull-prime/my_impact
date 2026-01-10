# ✅ OpenSpace Demo Deployment Checklist

Print this out or use it as a reference during deployment!

---

## 📋 Pre-Deployment (Day 1 Evening - 30 min)

### Environment Check
- [ ] Have Azure subscription ready
- [ ] Have Azure CLI installed (`az --version` works)
- [ ] Have GitHub repository access
- [ ] Have your GitHub token available (Settings → Developer settings)

### Documentation Review
- [ ] Read [README_DEPLOYMENT.md](README_DEPLOYMENT.md) (5 min)
- [ ] Skim [OPENSPACE_DAY2_QUICK_START.md](OPENSPACE_DAY2_QUICK_START.md) (5 min)
- [ ] Review [ARCHITECTURE.md](ARCHITECTURE.md) for understanding (10 min)

---

## 🚀 Day 2 Morning Deployment (1-1.5 hours total)

### Phase 1: Azure Setup (30 minutes)
**Follow**: [OPENSPACE_DAY2_QUICK_START.md](OPENSPACE_DAY2_QUICK_START.md) - Phase 1

- [ ] Login to Azure: `az login`
- [ ] Set variables (SUBSCRIPTION_ID, RESOURCE_GROUP_NAME, etc.)
- [ ] Create resource group
- [ ] Create Azure Container Registry
- [ ] Create Container Apps Environment
- [ ] Create Service Principal for CI/CD
- [ ] Get Container Registry credentials

**Save**: These values in a text file
```
AZURE_REGISTRY_LOGIN_SERVER = _____
AZURE_REGISTRY_USERNAME = _____
AZURE_REGISTRY_PASSWORD = _____
AZURE_CREDENTIALS (full JSON) = _____
```

### Phase 2: GitHub Secrets Configuration (10 minutes)
**Go to**: Your GitHub repo → Settings → Secrets and variables → Actions

- [ ] Create secret: `AZURE_CREDENTIALS` (paste full JSON)
- [ ] Create secret: `AZURE_RESOURCE_GROUP` = myimpact-demo-rg
- [ ] Create secret: `AZURE_REGISTRY_LOGIN_SERVER` = (from above)
- [ ] Create secret: `AZURE_REGISTRY_USERNAME` = (from above)
- [ ] Create secret: `AZURE_REGISTRY_PASSWORD` = (from above)
- [ ] Create secret: `CONTAINER_APP_NAME` = myimpact-demo-api
- [ ] Create secret: `CONTAINER_APPS_ENV` = myimpact-demo-env

**Verify**: All 7 secrets exist in Settings → Secrets

### Phase 3: Deploy Code (5 minutes)

```bash
cd z:\Shared\Code\my_impact
git add .
git commit -m "Deploy: Add rate limiting and CI/CD for OpenSpace demo"
git push origin main
```

- [ ] Code pushed successfully
- [ ] No errors in git output

### Phase 4: Monitor Deployment (10 minutes)
**Go to**: Your GitHub repo → Actions tab

- [ ] Wait for workflows to start (should be automatic)
- [ ] Verify test workflow completes (test-backend.yml) ✓
- [ ] Verify backend deployment completes (deploy-backend.yml) ✓
- [ ] Verify frontend deployment completes (deploy-frontend.yml) ✓

**Troubleshooting**: If workflow fails
- [ ] Check workflow logs for errors
- [ ] Verify all secrets are correct (case-sensitive!)
- [ ] Check Azure resource group exists
- [ ] Review [infra/CI_CD_DEPLOYMENT_GUIDE.md](infra/CI_CD_DEPLOYMENT_GUIDE.md) troubleshooting

### Phase 5: Get Your URLs (5 minutes)

```bash
# Backend API URL
CONTAINER_APP_URL=$(az containerapp show \
  --name myimpact-demo-api \
  --resource-group myimpact-demo-rg \
  --query 'properties.configuration.ingress.fqdn' \
  -o tsv)

echo "Backend: https://$CONTAINER_APP_URL"

# Frontend URL
STATIC_APP_URL=$(az staticwebapp show \
  --name myimpact-demo \
  --resource-group myimpact-demo-rg \
  --query 'defaultHostname' \
  -o tsv)

echo "Frontend: https://$STATIC_APP_URL"
```

- [ ] Backend URL obtained: `https://myimpact-demo-api._______.azurecontainerapps.io`
- [ ] Frontend URL obtained: `https://myimpact-demo.azurestaticapps.net`

---

## ✔️ Verification Tests (5 minutes)

### Test 1: Health Check

```bash
curl https://<YOUR_BACKEND_URL>/api/health
```

**Expected**: 
```json
{"status":"healthy","version":"0.1.0"}
```

- [ ] Returns 200 OK
- [ ] Health status is "healthy"

### Test 2: Metadata Endpoint

```bash
curl https://<YOUR_BACKEND_URL>/api/metadata | jq .
```

**Expected**: JSON with scales, levels, growth_intensities, goal_styles, organizations

- [ ] Returns 200 OK
- [ ] All required fields present

### Test 3: Rate Limiting (10 req/min)

```bash
# Run this multiple times in 60 seconds
for i in {1..15}; do
  curl -X POST https://<YOUR_BACKEND_URL>/api/goals/generate \
    -H "Content-Type: application/json" \
    -d '{"scale":"technical","level":"L30–35 (Career)","growth_intensity":"moderate","org":"demo"}' \
    -w "\n"
  sleep 2
done
```

**Expected**: 
- Requests 1-10: 200 OK with JSON response
- Request 11-15: 429 Too Many Requests

- [ ] First 10 requests return 200
- [ ] Requests 11+ return 429
- [ ] Rate limiting is working! ✓

### Test 4: Frontend Load

```bash
# Open in browser
https://<YOUR_FRONTEND_URL>
```

**Expected**: Form loads with:
- [ ] Three input fields visible
- [ ] "Generate Goals" button visible
- [ ] Form is responsive/styled

### Test 5: Form Submission (End-to-End)

1. Open frontend URL in browser
2. Fill out form:
   - Scale: "technical"
   - Level: "L30–35 (Career)"
   - Growth Intensity: "moderate"
   - Organization: "demo"
3. Click "Generate Goals"

**Expected**:
- [ ] Request goes to backend
- [ ] Prompts appear in modal
- [ ] Copy buttons work
- [ ] No JavaScript errors in console (F12)

### Test 6: Update Frontend API Endpoint (if needed)

If backend URL is different from default in code:

1. Edit [webapp/js/api.js](webapp/js/api.js)
2. Find this line:
   ```javascript
   const API_BASE_URL = window.location.hostname === 'localhost'
       ? 'http://localhost:8000'
       : 'https://myimpact-demo.azurestaticapps.net';
   ```
3. Update to use your actual backend URL
4. Commit and push
5. Wait for frontend redeploy (~2 min)

- [ ] API endpoint updated if needed
- [ ] Frontend redeployed if changed
- [ ] Form still works with new endpoint

---

## 🎤 Pre-OpenSpace Check (30 min before)

### Final Verification
- [ ] Backend health check passes (curl /api/health)
- [ ] Frontend loads (browser opens URL)
- [ ] Form submits successfully
- [ ] No JavaScript console errors
- [ ] Mobile view is responsive (F12 → Device Emulation)

### Demo Preparation
- [ ] Have frontend URL written down or bookmarked
- [ ] Test form submission one more time
- [ ] Know your talking points:
  - [ ] "This is live in the cloud, not local"
  - [ ] "No CLI or development tools needed to use"
  - [ ] "Automatically deployed on code push"
  - [ ] "Scaled to handle multiple users"
  - [ ] "Rate-limited to prevent abuse"

### Optional: Show Architecture
- [ ] Have [ARCHITECTURE.md](ARCHITECTURE.md) ready for questions
- [ ] Prepared to show GitHub Actions workflow
- [ ] Ready to discuss cost (~$15/month, <$1 for demo)

---

## 🎉 At OpenSpace

### Share URL
**Tell participants**: "Visit this URL to see MyImpact live!"

```
https://<YOUR_FRONTEND_URL>
```

### Demo Script (5 minutes)

1. **Show the form** (30 seconds)
   - "Here's the MyImpact goal generation app"
   - "It's running live in Azure - no local development needed"

2. **Fill out form** (1 minute)
   - Select scale: "technical"
   - Select level: "L30–35 (Career)"
   - Select growth intensity: "moderate"
   - Keep org as "demo"

3. **Submit form** (1 minute)
   - Click "Generate Goals"
   - "The backend is processing with LLM-aligned prompts"
   - Show the generated output

4. **Show copy functionality** (1 minute)
   - Click copy button
   - "Users can copy these directly to their LLM"
   - Explain how it works in practice

5. **Answer questions** (1.5 minutes)
   - "How is it deployed?" → CI/CD with GitHub Actions
   - "Where does it run?" → Azure Container Apps
   - "How much does it cost?" → ~$15/month, <$1 for this demo
   - "Is it scalable?" → Auto-scales 1-3 replicas based on demand

---

## 🧹 Post-OpenSpace (Optional)

### Keep Resources Running
- Cost: ~$15-20 per month
- Can be deleted anytime with: `az group delete --name myimpact-demo-rg`

### Or Delete Everything
```bash
# Delete entire resource group (all resources)
az group delete --name myimpact-demo-rg --yes --no-wait
```

- [ ] Deleted if desired
- [ ] Kept for ongoing reference

---

## 📞 Emergency Contacts/Resources

If something goes wrong:

### Quick Fixes
- Health check fails → Check container logs: `az containerapp logs show --follow`
- Form doesn't work → Check browser console (F12)
- CORS errors → Update [api/main.py](api/main.py) CORS origins
- Slow response → Container warming up (wait 30 seconds)

### Full Troubleshooting
See: [infra/CI_CD_DEPLOYMENT_GUIDE.md](infra/CI_CD_DEPLOYMENT_GUIDE.md) - Troubleshooting section

### Documentation
1. [README_DEPLOYMENT.md](README_DEPLOYMENT.md) - Full overview
2. [OPENSPACE_DAY2_QUICK_START.md](OPENSPACE_DAY2_QUICK_START.md) - Quick commands
3. [ARCHITECTURE.md](ARCHITECTURE.md) - System design
4. [infra/CI_CD_DEPLOYMENT_GUIDE.md](infra/CI_CD_DEPLOYMENT_GUIDE.md) - Detailed guide

---

## ✨ Success Indicators

You're ready for OpenSpace when:

- ✅ All 7 GitHub secrets configured
- ✅ All 3 workflows completed successfully
- ✅ Health endpoint returns 200
- ✅ Metadata endpoint returns data
- ✅ Rate limiting works (429 after 10 requests)
- ✅ Frontend loads in browser
- ✅ Form submission works end-to-end
- ✅ Frontend URL is bookmarked/written down

---

**YOU'VE GOT THIS! 🚀**

Follow this checklist step-by-step and you'll be demoing at OpenSpace with a live cloud application in less than 2 hours.

Good luck! 🎉
