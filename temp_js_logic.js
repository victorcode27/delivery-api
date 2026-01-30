
// Settings Data Structure - NOW JUST A CACHE
let settingsData = {
    drivers: [],
    assistants: [],
    checkers: [],
    routes: [],
    trucks: [],
    customerRoutes: {}
};

// --- DATA ACCESS LAYER ---
async function fetchSettingList(category) {
    try {
        const res = await fetch(`${API_URL}/settings/${category}`);
        const data = await res.json();
        return data.values || [];
    } catch (e) { console.error(e); return []; }
}

async function addSettingAPI(category, value) {
    try {
        const res = await fetch(`${API_URL}/settings`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ category, value })
        });
        return res.ok;
    } catch (e) { console.error(e); return false; }
}

async function deleteSettingAPI(category, value) {
    try {
        const res = await fetch(`${API_URL}/settings/${category}/${encodeURIComponent(value)}`, {
            method: 'DELETE'
        });
        return res.ok;
    } catch (e) { console.error(e); return false; }
}

// ... Trucks and Customer Routes APIs similar logic ...

// Replace loadSettings with async fetch
async function loadSettings() {
    settingsData.drivers = await fetchSettingList('drivers');
    settingsData.assistants = await fetchSettingList('assistants');
    settingsData.checkers = await fetchSettingList('checkers');
    settingsData.routes = await fetchSettingList('routes');

    // Load Trucks
    const truckRes = await fetch(`${API_URL}/trucks`);
    const truckData = await truckRes.json();
    settingsData.trucks = truckData.trucks || [];

    // Load Customer Routes
    const routeRes = await fetch(`${API_URL}/customer-routes`);
    const routeData = await routeRes.json();
    settingsData.customerRoutes = routeData.routes || {};

    console.log("Settings loaded from Server");
}

function saveSettings() {
    // Deprecated - we now save individually per action
    console.log("saveSettings() is deprecated, data is saved to server immediately.");
}
