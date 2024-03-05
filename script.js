const blackSquare = "⬛";
const whiteSquare = "⬜";
const gridElement = document.getElementById('grid');
const userInputElement = document.getElementById('user-input');
const submitButton = document.getElementById('submit-button');
const shareTextContainer = document.getElementById('share-text-container'); 
const sharePopup = document.getElementById('share-popup');
const closePopupButton = document.getElementById('close-popup');
const copyButton = document.getElementById('copy-button');

function getTodaysDateKey() {
  const today = new Date();
  const yyyy = today.getFullYear();
  let mm = today.getMonth() + 1; // Months are zero-indexed
  let dd = today.getDate();

  if (dd < 10) dd = '0' + dd;
  if (mm < 10) mm = '0' + mm;

  return `${yyyy}-${mm}-${dd}`;
}

function generateTodaysGrid() {
  const dateKey = getTodaysDateKey();

  let storedGrid = loadGrid(dateKey); 
  if (storedGrid) {
    return storedGrid;
  } else {
    // If no grid exists, generate a new one
    let newGrid = generateEmojiGrid();
    saveGrid(dateKey, newGrid); // Store the grid for today
    return newGrid;
  }
}

function loadGrid(dateKey) {
  return localStorage.getItem(dateKey);
}

function saveGrid(dateKey, grid) {
  localStorage.setItem(dateKey, grid);
}

function generateEmojiGrid() {
  let grid = "";

  for (let row = 0; row < 4; row++) {
    for (let col = 0; col < 5; col++) {
      grid += Math.random() < 0.5 ? blackSquare : whiteSquare; 
    }
    grid += "\n";
  }

  return grid;
}

function displayGrid(grid) {
    gridElement.innerHTML = initialGrid.replaceAll('\n', '<br>');
}

function updateTitle() {
  const today = new Date();
  const months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
  const date = today.getDate();
  const month = months[today.getMonth()];
  const year = today.getFullYear();

  const dateElement = document.querySelector('h3'); // Assuming your title is an <h1> 
  dateElement.innerText = `${month} ${date}, ${year}`;
}

function createShareTextArea(text) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();

    try {
        document.execCommand('copy'); 
        alert('Share text copied to clipboard!'); 
    } catch (err) {
        console.error('Unable to copy text: ', err);
    }

    document.body.removeChild(textArea); 
}

async function copyToClipboard(text) {
  try {
    await navigator.clipboard.writeText(text);
    alert('Share text copied to clipboard!');
  } catch (err) {
    console.error('Could not copy text: ', err);
  }
}

submitButton.addEventListener('click', () => {
    const interpretation = userInputElement.value;
    const baseURL = "https://vsporeddy.github.io/rorschachdle/";
    const shareText = `I saw a <b>${interpretation}</b> on today's Rorschachdle. What do you see?\n${baseURL}`; 

    shareTextContainer.innerHTML = shareText;

    console.log("Submit button clicked!", sharePopup);
    sharePopup.style.display = 'block'; // Show the popup
});

closePopupButton.addEventListener('click', () => {
    sharePopup.style.display = 'none'; // Hide the popup
});

copyButton.addEventListener('click', () => {
    const textToCopy = shareTextContainer.textContent; // Get text for copying
    copyToClipboard(textToCopy); 
});

let initialGrid = generateTodaysGrid();
displayGrid(initialGrid);
updateTitle();
