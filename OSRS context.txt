## OSRS GP/hr Tracker: Project Context & Requirements (React & Firebase Edition)

**Document Version:** 2.0
**Date:** May 24, 2025

**1. Project Goal 🎯**

To create a personalized, locally hosted web application that allows an Old School RuneScape (OSRS) player to track the potential Gold Pieces (GP) per hour for various in-game activities. The system will use near real-time price data from the Grand Exchange (GE) and allow for user-configurable variables (stored in Firebase Firestore) to tailor calculations to their specific efficiency and methods.

**2. Core Recommended Solution & Technology Stack 💻**

* **Overall Architecture:** A locally hosted web application with a separate frontend and backend.
* **Frontend:** **React.js** (using functional components and hooks) for a dynamic and interactive user interface.
  * Styling: **Tailwind CSS**.
  * Charting: **Chart.js**.
  * API Communication: `axios` or `Workspace`.
* **Backend:** **Python with Flask** for API routing, core GP/hr calculation logic, and interaction with the OSRS GE API and Firebase.
* **Data Persistence:** **Firebase Firestore** for storing user-specific configurations and variables.
* **Environment Management:** Root-level `.env` file for environment variables.
* **AI Assistance:** Development will be heavily assisted by Cursor AI.

**3. Key Features of the Tracker ✨**

* **Activity Tracking:** Initially focused on:
  * Farming (e.g., Grimy Torstol, Snape Grass)
  * Hunter (Birdhouse runs)
  * Runecrafting (Guardians of the Rift - GOTR)
  * Slayer (task-based, e.g., Rune Dragons)
* **GE Price Integration:** Fetch and use near real-time item prices from the OSRS GE.
* **User-Editable Variables (via Firestore):** Allow users to input and save their specific efficiency metrics (e.g., kills per hour, yield per patch) to Firestore via the backend.
* **Dynamic Dashboard:** Display calculated GP/hr for each tracked activity, updating dynamically based on price changes (refreshed periodically) and user variable adjustments.
* **Firebase Integration:**
  * Use Firebase Authentication (e.g., anonymous sign-in initially) to associate configurations with a user.
  * Store and retrieve user-specific activity parameters from Firestore.

**4. OSRS Grand Exchange (GE) API Details 📈**

* **Recommended API Provider:** `prices.runescape.wiki`
* **Base API URL:** `https://prices.runescape.wiki/api/v1/osrs/`
* **Key Endpoints for Backend Use:**
  * `/latest?id={item_id}`: To get the latest price for a specific item ID. Can also use `/latest` to get all items, though fetching individual items as needed might be more efficient if only a few are required at a time.
  * `/mapping`: To get item ID to item name mappings (useful for initialization or if item names are used in user configs).
* **Data Format:** JSON.
* **Update Frequency:** Data from `prices.runescape.wiki` is typically updated every ~60 seconds.
* **CRITICAL Requirement: User-Agent String:** All API requests made by the Flask backend *must* include a descriptive User-Agent header (e.g., `YourAppName - YourContact - Version`). This will be configured in the backend.
* **Rate Limiting & Fair Use:**
  * No explicit hard rate limits are published, but fair use is expected.
  * The Flask backend should cache item prices temporarily (e.g., for 1-5 minutes in memory or a simple cache like `cachetools`) to avoid hitting the external API for every internal calculation request if multiple users/sessions were hypothetically active or if the user frequently updates parameters. For a single-user local app, this mainly prevents spamming the API during rapid interactions.

**5. OSRS Activity Data & GP/hr Calculation Logic (for `backend/utils/calculations.py`) ⚙️**

*Calculations should generally follow: GP/hr = (Total Value of Outputs per Hour) - (Total Cost of Inputs per Hour). Item prices are fetched by the backend via `ge_api.py`.*

* **5.1. Farming (Example: Torstol Herbs)**
  * **Inputs from User Config (Firestore) & GE Prices:**
    * Seeds (e.g., Torstol seed ID) - Cost from GE.
    * Compost (e.g., Ultracompost ID) - Cost from GE.
    * User Vars: Average yield per patch, number of patches farmed.
  * **Outputs:** Harvested items (e.g., Grimy Torstol ID) - Value from GE.
  * **Key Constants/Mechanics (can be part of default params or logic):** Herb growth time (e.g., Torstol ~80 mins).
  * **GP/hr Logic Example:** `((User_AvgYield * User_NumPatches * HerbPriceGE) - (User_NumPatches * SeedPriceGE + User_NumPatches * CompostPriceGE)) / (GrowthCycleInHours)`

* **5.2. Hunter (Birdhouse Runs)**
  * **Inputs from User Config (Firestore) & GE Prices:**
    * Logs (type/ID, e.g., Redwood logs ID) - Cost from GE.
    * Seeds (cheap, ID for a common cheap seed) - Cost from GE (10 low-level or 5 high-level seeds per house).
    * User Vars: Time per birdhouse run (active minutes), (optional: override for avg value per nest if not calculating detailed drops).
  * **Outputs:** Average value of nests (this can be a simplified user input or a more complex calculation based on typical nest drop values if itemized).
  * **Key Constants/Mechanics:** 4 birdhouse spots. Birdhouses full after ~50 minutes.
  * **GP/hr Logic Example:** `((AvgNestsPerRun * User_AvgValuePerNest) - (CostOfLogsForRunGE + CostOfSeedsForRunGE)) / ((User_RunTimeMinutes + ApproxCycleTimeMinutes) / 60)`

* **5.3. Runecrafting (Guardians of the Rift - GOTR)**
  * **Inputs from User Config (Firestore) & GE Prices:**
    * Pure Essence ID - Cost from GE.
    * User Vars: Games per hour, average points per game (elemental + catalytic), (optional: specific runes crafted if tracking their individual prices, or an overall avg rune value per game).
  * **Outputs:** Runes (value from GE, or user's avg value), Abyssal Pearls (value can be estimated based on rewards purchased).
  * **Key Constants/Mechanics:** Runecrafting level and outfit impact output.
  * **GP/hr Logic Example:** `((User_AvgRuneValuePerGame + User_AvgPearlValuePerGame) - PureEssenceCostPerGameGE) * User_GamesPerHour`

* **5.4. Slayer (Task-based, e.g., Rune Dragons)**
  * **Inputs from User Config (Firestore) & GE Prices:**
    * User Vars: Monster type/name (for context), Kills per hour (KPH), average supply cost per hour (e.g., potions, food).
    * (Advanced: specific supply item IDs and quantities per hour if itemizing costs).
  * **Outputs (fetched from GE based on typical valuable drops for the monster, or user-inputted avg loot value):**
    * User Vars: Average loot value per kill for the specified monster (simplification), OR the backend could have predefined loot profiles for common monsters.
  * **GP/hr Logic Example:** `(User_AvgLootValuePerKillForMonster * User_KPH) - User_AvgSupplyCostPerHour`

**6. Firebase Firestore Data Structure (Illustrative for `backend/app.py` logic)**

A user's configuration will be stored under their UID (obtained from Firebase Auth).

* Collection: `userConfigurations`
  * Document ID: `{userId}` (from Firebase Authentication)
    * Fields or Subcollection:
      * `farming`: { `avg_yield_per_patch`: 8, `num_patches`: 9, `herb_type_id`: 207, ... }
      * `hunter`: { `log_type_id`: 1513, `avg_nests_per_run`: 10, ... }
      * `gotr`: { `games_per_hour`: 4, `avg_points_per_game`: 350, ... }
      * `slayer`: { `default_task_monster`: "rune_dragons", `rune_dragons_kph`: 40, `rune_dragons_avg_loot_pk`: 37000, `rune_dragons_supply_cost_ph`: 100000, ... }
      * `lastUpdated`: Firestore Timestamp

**7. UI/UX High-Level Goals (for `frontend/src/components/`)**

* **Dashboard (`App.js`):** Central view with navigation (e.g., `Navbar.js`) to different activity calculators.
* **Activity Cards (`ActivityCard.js`):** Dedicated sections/components for each OSRS activity.
  * Display current calculated GP/hr.
  * Show relevant inputs (e.g., seed cost, KPH) and outputs (e.g., herb value, loot value).
  * Allow users to edit their specific variables (e.g., yield, KPH, supply costs). These changes trigger backend calls to save to Firestore and recalculate.
* **Charts (`GPChart.js`):** Visual comparison of GP/hr across activities. Potentially historical trends if timeseries data is ever incorporated.
* **Configuration Editor (`ConfigEditor.js` or integrated into Activity Cards):** A clear interface for managing all user-editable parameters stored in Firestore.
* **Responsiveness:** Ensure usability on desktop primarily, with consideration for smaller screens.