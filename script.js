const gridElement = document.getElementById('grid');
const userInputElement = document.getElementById('user-input');
const submitButton = document.getElementById('submit-button');
const shareTextContainer = document.getElementById('share-text-container'); 
const sharePopup = document.getElementById('share-popup');
const closePopupButton = document.getElementById('close-popup');
const copyButton = document.getElementById('copy-button');
const backendURL = "https://roffles.pythonanywhere.com";
const baseURL = "https://vsporeddy.github.io/rorschachdle/";
todaysGrid = "";

function getTodaysDateKey() {
  const today = new Date();
  const yyyy = today.getFullYear();
  let mm = today.getMonth() + 1; // Months are zero-indexed
  let dd = today.getDate();

  if (dd < 10) dd = '0' + dd;
  if (mm < 10) mm = '0' + mm;

  return `${yyyy}-${mm}-${dd}`;
}

async function fetchGridFromServer() {
  const dateKey = getTodaysDateKey();
  const response = await fetch(`${backendURL}/daily-grid?date=${dateKey}`); 

  if (!response.ok) {
    throw new Error(`Error fetching grid (Status: ${response.status})`);
  }

  const gridData = await response.text();
  return gridData;
}
function displayGrid(grid) {
    todaysGrid = grid.replaceAll('\n', '\r\n<br>');
    gridElement.innerHTML = todaysGrid;
}

function updateTitle() {
  const today = new Date();
  const months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
  const date = today.getDate();
  const month = months[today.getMonth()];
  const year = today.getFullYear();

  const dateElement = document.querySelector('h3'); 
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
    alert('Text copied to clipboard!');
  } catch (err) {
    console.error('Could not copy text: ', err);
  }
}

async function fetchUniquenessFromServer(text) {
    const response = await fetch(`${backendURL}/uniqueness?text=${text}`); 
    if (!response.ok) {
        throw new Error(`Error fetching uniqueness (Status: ${response.status})`);
    }

    const uniqueness = await response.text();        
    console.log(uniqueness)
    return uniqueness
}

async function fetchSentimentFromServer(text) {
    const response = await fetch(`${backendURL}/sentiment?text=${text}`); 
    if (!response.ok) {
        throw new Error(`Error fetching sentiment (Status: ${response.status})`);
    }

    const sentiment = await response.text();        
    console.log(sentiment)
    return sentiment
}

async function fetchNumberFromServer() {
    const response = await fetch(`${backendURL}/number`); 
    if (!response.ok) {
        throw new Error(`Error fetching number (Status: ${response.status})`);
    }

    const number = await response.text();        
    console.log(number)
    return number
}

submitButton.addEventListener('click', async () => {
    const interpretation = userInputElement.value;
    shareText = "";
    
    try {
        // Use await to get responses
        const uniqueness = await fetchUniquenessFromServer(interpretation); 
        const sentiment = await fetchSentimentFromServer(interpretation);
        const number = await fetchNumberFromServer();

        shareText += `Rorschachdle #${number}`
        shareText += `\r\n<br>Uniqueness: <b>${uniqueness}</b>`;
        shareText += `\r\n<br>Psyche: <b>${sentiment}</b>`;
        shareText += `\r\n<br>\r\n<br>${todaysGrid}`
        shareText += `\r\n<br>What do you see?`
        shareText += `\r\n<br>${baseURL}`; 

        shareTextContainer.innerHTML = shareText; // Update DOM once
        sharePopup.style.display = 'block'; 
    } catch (error) {
        console.error('Error fetching data:', error);
    }
});

closePopupButton.addEventListener('click', () => {
    sharePopup.style.display = 'none'; // Hide the popup
});

copyButton.addEventListener('click', () => {
    const textToCopy = shareTextContainer.textContent; 
    copyToClipboard(textToCopy); 
});

fetchGridFromServer()
  .then((grid) => { 
      displayGrid(grid);
  })
  .catch(error => console.error('Error fetching grid:', error)); 
updateTitle();
