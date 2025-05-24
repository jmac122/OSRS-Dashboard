OSRS GP/hr Tracker: Project Context and Requirements
Document Version: 1.0
Date: May 24, 2025

1. Project Goal

To create a personalized, locally hosted web application that allows an Old School RuneScape (OSRS) player to track the potential Gold Pieces (GP) per hour for various in-game activities. The system should use near real-time price data from the Grand Exchange (GE) and allow for user-configurable variables to tailor calculations to their specific efficiency and methods.

2. Core Recommended Solution

A locally hosted web application is the chosen solution, to be developed using Python (with Flask) for the backend and standard HTML, CSS (Tailwind CSS), and Vanilla JavaScript for the frontend. Chart.js will be used for visualizations. AI-assisted development (e.g., using Cursor AI) is anticipated.

3. Key Features of the Tracker

Activity Tracking: Initially focused on:
Farming (e.g., Grimy Torstol, Snape Grass)
Hunter (Birdhouse runs)
Runecrafting (Guardians of the Rift - GOTR)
Slayer (task-based, e.g., Rune Dragons, with consideration for varied loot tables)
GE Price Integration: Fetch and use near real-time item prices from the OSRS GE.
User-Editable Variables: Allow the user to input and save their specific efficiency metrics (e.g., kills per hour, yield per patch, time per run, supply costs).
Dynamic Dashboard: Display calculated GP/hr for each tracked activity, updating dynamically based on price changes (simulated or refreshed periodically) and user variable adjustments.
Data Persistence: Store user variables and cached GE prices locally using JSON files.
4. OSRS Grand Exchange (GE) API Details

Recommended API Provider: prices.runescape.wiki
Base API URL (Assumed): https://prices.runescape.wiki/api/v1/osrs/
Key Endpoints:
/latest: Provides current high/low prices for all items. This is the primary endpoint for "real-time" data.
/mapping: Provides item ID to item name mappings.
/timeseries?timestep={5m|1h}&id={itemID}: For historical price data (less critical for immediate GP/hr but useful for context).
Data Format: JSON.
Update Frequency: Data from prices.runescape.wiki is typically updated every ~60 seconds, based on RuneLite client data.
CRITICAL Requirement: User-Agent String: All API requests must include a descriptive User-Agent header (e.g., YourAppName - ContactInfo - Version). This will be set in the application's configuration.
Rate Limiting & Fair Use:
No explicit hard rate limits are published for anonymous use, but fair use is expected.
Polling the /latest endpoint more frequently than once per minute offers no benefit and should be avoided.
Implement local caching of item prices (item_prices.json) to minimize direct API calls.
5. OSRS Activity Data & GP/hr Calculation Logic Summaries

Calculations should generally follow: GP/hr = (Total Value of Outputs per Hour) - (Total Cost of Inputs per Hour)

5.1. Farming (Example: Torstol Herbs)

Inputs:
Seeds (e.g., Torstol seed) - Cost from GE.
Compost (e.g., Ultracompost) - Cost from GE.
Outputs:
Harvested items (e.g., Grimy Torstol) - Value from GE.
User-Editable Variables:
Average yield per patch.
Number of patches farmed per run.
(Optionally: time per farm run, though GP/hr is often normalized over growth cycle).
Key Constants/Mechanics:
Herb growth time (e.g., Torstol ~80 minutes).
Consider boosts like Magic Secateurs (+10% yield) and Farming Cape (+5% herb yield) if user indicates they are used.
GP/hr Logic: ((AvgYield * NumPatches * HerbPrice) - (NumPatches * SeedPrice + NumPatches * CompostPrice)) / (GrowthCycleInHours)
5.2. Hunter (Birdhouse Runs)

Inputs:
Logs (type determines birdhouse tier, e.g., Redwood logs) - Cost from GE.
Clockwork (reusable after initial cost).
Seeds (cheap, e.g., Barley, Jute; 10 low-level or 5 high-level per house) - Cost from GE.
Outputs:
Bird Nests (various types: empty, egg, seed, ring, clue).
Feathers, Raw Bird Meat.
Valuable items from nests (e.g., spirit seeds, god eggs from higher-tier nests).
User-Editable Variables:
(Optionally: Average value per nest, if not calculating from individual nest item drops).
Time per birdhouse run (e.g., ~2 minutes for 4 houses).
Key Constants/Mechanics:
4 birdhouse spots.
Birdhouses full after ~50 minutes.
Yield and nest quality vary by birdhouse tier (e.g., Redwood provides ~2.5 nests average).
GP/hr Logic: ((AvgNestsPerRun * AvgValuePerNest) - (CostOfLogsForRun + CostOfSeedsForRun)) / ((RunTimeMinutes + CycleTimeMinutes) / 60)
5.3. Runecrafting (Guardians of the Rift - GOTR)

Inputs:
Pure Essence - Cost from GE.
Outputs:
Various runes (quantity and type depend on RC level, points, active altars).
Abyssal Pearls (for outfit/rewards).
Potential for unique items (Abyssal Lantern, Needle).
User-Editable Variables:
Games per hour.
Average points earned per game (elemental + catalytic).
(Optionally: Average rune value per game, if not calculating specific runes).
(Optionally: Average Abyssal Pearl value per reward roll, or pearls per hour).
Key Constants/Mechanics:
Runecrafting level impacts output.
Outfit pieces (Raiments of the Eye) provide bonus runes.
GP/hr Logic: ((AvgRuneValuePerGame + AvgOtherRewardsValuePerGame) - PureEssenceCostPerGame) * GamesPerHour
5.4. Slayer (Task-based, e.g., Rune Dragons)

Inputs (per hour or per kill):
Prayer Potions, Antifire Potions, Food - Costs from GE.
Weapon charges, other specific supplies (e.g., cannonballs for some tasks).
Outputs (per kill):
Monster-specific drops (e.g., Dragon bones, Rune items, Dragon limbs, Draconic visage for Rune Dragons). Value from GE.
User-Editable Variables:
Specific monster being killed for the task.
Kills per hour (KPH).
Average supply cost per hour (or per kill).
Key Constants/Mechanics:
Detailed loot tables and drop rates for specific monsters are complex. The application might start with user-inputted "average loot value per kill" for a given monster, or try to calculate it if detailed drop rates are available/manageable.
Example: Rune Dragons (avg. drop ~37k GP before uniques, uniques 1/800 Dragon limbs, 1/5000 D metal lump, 1/8000 Visage). KPH ~33-45.
GP/hr Logic: (AvgLootValuePerKill * KPH) - AvgSupplyCostPerHour
6. Technology Stack Overview

Backend: Python (Flask) - For API routing, business logic (calculations), data management, and GE API interaction.
Frontend:
HTML: Structure.
CSS: Tailwind CSS for styling and responsiveness.
JavaScript (Vanilla): For DOM manipulation, event handling, frontend logic, communication with the Flask backend, and updating charts.
Charting: Chart.js - For displaying GP/hr comparisons and potentially other data visualizations.
Data Persistence: Local JSON files for:
user_variables.json: User-specific settings and efficiency metrics.
item_prices.json: Cache for GE prices to reduce API calls.
activity_config.json: Base configurations for activities (e.g., items involved, default values if any).
7. User Interface (UI) / User Experience (UX) High-Level Goals

Dashboard: A central view providing an overview of GP/hr for all tracked activities.
Clarity: Easy-to-understand presentation of costs, revenues, and net profit/GPhr.
Editability: Intuitive forms or input fields for users to adjust their personal variables for each activity.
Dynamic Updates: GP/hr figures should update automatically (or with a clear refresh action) when user variables are changed or when (simulated/refreshed) GE prices update.
Responsiveness: The application should be usable across different screen sizes (desktop-focused initially).
Minimalism: Avoid clutter; focus on presenting the key information effectively.