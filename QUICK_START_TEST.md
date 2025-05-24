# 🚀 OSRS Dashboard - Quick Start & Test Guide

## 📋 **Pre-Flight Checklist**

Before testing, ensure both servers are running:

### 1. Backend Server (Port 5000)
```bash
# Navigate to backend directory
cd osrs_gp_tracker/backend

# Start Flask server
python app.py
```
**Expected:** Server should start on `http://localhost:5000`

### 2. Frontend Server (Port 3000)  
```bash
# Navigate to frontend directory
cd osrs_gp_tracker/frontend

# Start Vite dev server
npm run dev
```
**Expected:** Server should start on `http://localhost:3000`

---

## ⚡ **30-Second Health Check**

Open your browser and test these URLs:

1. **Backend Health:** http://localhost:5000/api/health
   - Should show: `{"firebase_connected": true, "status": "healthy"}`

2. **Frontend:** http://localhost:3000
   - Should load the OSRS Dashboard homepage

3. **Configuration Page:** http://localhost:3000/configuration
   - Should show settings for all 4 activities

**✅ If all 3 work, your system is healthy!**

---

## 🧪 **Full Feature Test (5 minutes)**

### Test 1: Configuration Management
1. Go to **Configuration** page
2. ✅ Verify you see 4 activity sections: Farming, Birdhouse, GOTR, Slayer  
3. ✅ Change a value (e.g., Farming patches from 9 to 8)
4. ✅ Navigate to another page and back - value should persist

### Test 2: Activity Calculations  
1. Go to **Farming** page
2. ✅ Verify default parameters are loaded and initial calculation shows
3. ✅ Change a parameter (e.g., patches to 10)  
4. ✅ Verify calculation does NOT update automatically (optimized behavior)
5. ✅ Click "Calculate GP/Hour" button  
6. ✅ Verify you see updated results:
   - GP/Hr amount (should be ~300k+)
   - Yellow bar chart updates 
   - Breakdown section with costs/revenue
   - Current market prices

### Test 2.5: Input Field Functionality ⭐ NEW
1. ✅ Try to backspace and clear any numeric field completely
2. ✅ Verify you can clear the field to empty (no forced 0)
3. ✅ Type a new value from scratch (e.g., clear patches and type "12")
4. ✅ Try to calculate with empty fields - should show validation error
5. ✅ Fill all fields and calculate - should work normally

### Test 3: All Activity Types
Repeat Test 2 for each activity:
- **Birdhouse:** Should calculate ~600k/hr
- **GOTR:** Should calculate ~200k+/hr  
- **Slayer:** Should calculate ~1M+/hr (Rune Dragons)

### Test 4: Performance & Visual Elements
1. ✅ Parameter changes are instant (no API delays while typing)
2. ✅ "Recalculate" button appears when changing parameters
3. ✅ Charts only update when button is clicked (not on every keystroke)
4. ✅ All text is clearly visible (no white text on white background)
5. ✅ Breakdown sections show formatted numbers

---

## 🔧 **Troubleshooting**

### If Backend Fails to Start:
- Check Python dependencies: `pip install flask flask-cors firebase-admin requests`
- Verify Firebase credentials in environment variables
- Check port 5000 isn't in use: `netstat -an | findstr 5000`

### If Frontend Fails to Start:  
- Check Node dependencies: `npm install`
- Verify port 3000 isn't in use
- Check environment variables are set with `VITE_` prefix

### If Calculations Don't Work:
- Verify backend health endpoint responds
- Check browser console for error messages
- Ensure CORS is properly configured in Flask

### If Configuration Doesn't Load:
- Check `/api/default_config` endpoint in browser
- Verify UserConfigContext is properly initialized  
- Look for console errors about Firebase connection

---

## 📊 **Expected Performance**

| Activity | Typical GP/Hr | Calculation Time |
|----------|---------------|------------------|
| Farming | 300k-400k | < 2 seconds |  
| Birdhouse | 500k-700k | < 2 seconds |
| GOTR | 200k-300k | < 2 seconds |
| Slayer | 800k-2M+ | < 2 seconds |

**Note:** Actual values depend on current GE prices and your parameters.

---

## ✅ **Success Criteria**

Your application is working correctly if:

- ✅ All 4 activity pages load and calculate
- ✅ Configuration saves and persists  
- ✅ Charts display with data
- ✅ Breakdown sections show detailed cost/revenue
- ✅ Real-time GE prices are fetched
- ✅ UI is responsive and visually appealing
- ✅ No console errors in browser developer tools

---

## 🎯 **Next Steps**

Once testing passes:

1. **Use the Dashboard:** Start tracking your actual GP/hr rates
2. **Customize Settings:** Adjust parameters to match your gameplay
3. **Monitor Performance:** Use the real-time price data for optimal profits
4. **Expand:** Consider adding more activities or features

**🎉 Congratulations! Your OSRS Dashboard is fully operational!** 