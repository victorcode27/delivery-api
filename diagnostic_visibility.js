// DIAGNOSTIC SCRIPT - Paste this into browser console after login
console.log("=== VISIBILITY DIAGNOSTIC ===");

const landing = document.getElementById('landing-overlay');
const mainContent = document.querySelector('.main-content');
const appContainer = document.querySelector('.app-container');

console.log("Landing Overlay:");
console.log("  - exists:", landing !== null);
if (landing) {
    console.log("  - display:", window.getComputedStyle(landing).display);
    console.log("  - opacity:", window.getComputedStyle(landing).opacity);
    console.log("  - z-index:", window.getComputedStyle(landing).zIndex);
    console.log("  - pointer-events:", window.getComputedStyle(landing).pointerEvents);
    console.log("  - classList:", landing.classList.toString());
}

console.log("\nMain Content:");
console.log("  - exists:", mainContent !== null);
if (mainContent) {
    console.log("  - display:", window.getComputedStyle(mainContent).display);
    console.log("  - visibility:", window.getComputedStyle(mainContent).visibility);
    console.log("  - opacity:", window.getComputedStyle(mainContent).opacity);
    console.log("  - classList:", mainContent.classList.toString());
}

console.log("\nApp Container:");
console.log("  - exists:", appContainer !== null);
if (appContainer) {
    console.log("  - display:", window.getComputedStyle(appContainer).display);
    console.log("  - visibility:", window.getComputedStyle(appContainer).visibility);
}

console.log("=== END DIAGNOSTIC ===");
