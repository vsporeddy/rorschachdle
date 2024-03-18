const gridElement = document.getElementById('grid');
const userInputElement = document.getElementById('user-input');
const alreadySubmittedElement = document.getElementById('already-submitted');
const submitButton = document.getElementById('submit-button');
const shareTextContainer = document.getElementById('share-text-container'); 
const sharePopup = document.getElementById('share-popup');
const closePopupButton = document.getElementById('close-popup');
const copyButton = document.getElementById('copy-button');
const backendURL = "https://roffles.pythonanywhere.com";
const baseURL = "https://vsporeddy.github.io/rorschachdle/";
const dateKey = getTodaysDateKey();
const gridContainer = document.getElementById('grid-container');
gridString = "";

async function fetchJsonGridFromServer() {
  const response = await fetch(`${backendURL}/json-grid?date=${dateKey}`); 

  if (!response.ok) {
    throw new Error(`Error fetching grid (Status: ${response.status})`);
  }

  const gridJson = await response.json();
  return gridJson;
}

function renderGridJson(gridJson) {
for (let row = 0; row < gridJson.length; row++) {
    for (let col = 0; col < gridJson[row].length; col++) {
      const square = document.createElement('div');
      square.classList.add('square'); 

      if (gridJson[row][col] === 1) {
          square.style.backgroundColor = '#F2F2F2'; 
      }
      if (gridJson[row][col] === 3) {
          square.style.backgroundColor = '#C30010'; 
      }
      gridContainer.appendChild(square);
    }
  }
}

function getGridString(gridJson) {
  const blackSquare = '⬛';
  const whiteSquare = '⬜';
  const redSquare = '🟥';

  const gridString = gridJson.map(row => {
    return row.map(cell => {
        if (cell === 3) {
            return redSquare;  
        } else if (cell === 1) {
            return whiteSquare; 
        } else { 
            return blackSquare; // Default to blackSquare
        }
    }).join('');
  }).join('\r\n<br>');

  return gridString;
}



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

function displaySubmission() {
    submitButton.style.display="inline";
    userInputElement.style.display="inline";
    alreadySubmittedElement.style.display="none";
}

function hideSubmission() {
    submitButton.style.display="none";
    userInputElement.style.display="none";
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
    const dateKey = getTodaysDateKey();
    const response = await fetch(`${backendURL}/unique?date=${dateKey}&text=${text}`); 
    if (!response.ok) {
        throw new Error(`Error fetching uniqueness (Status: ${response.status})`);
    }

    const uniqueness = await response.text();        
    // console.log(uniqueness)
    return uniqueness
}

async function fetchAlignmentFromServer(text) {
    const response = await fetch(`${backendURL}/alignment?text=${text}`); 
    if (!response.ok) {
        throw new Error(`Error fetching alignment (Status: ${response.status})`);
    }

    const alignment = await response.text();        
    // console.log(alignment)
    return alignment
}

async function fetchNumberFromServer() {
    const dateKey = getTodaysDateKey();
    const response = await fetch(`${backendURL}/number?date=${dateKey}`); 
    if (!response.ok) {
        throw new Error(`Error fetching number (Status: ${response.status})`);
    }

    const number = await response.text();        
    // console.log(number)
    return number
}

submitButton.addEventListener('click', async () => {
    const interpretation = userInputElement.value;
    shareText = "";
    
    try {
        hideSubmission();
        // Use await to get responses
        const uniqueness = await fetchUniquenessFromServer(interpretation); 
        const alignment = await fetchAlignmentFromServer(interpretation);
        const number = await fetchNumberFromServer();

        shareText += `Rorschachdle #${number}`
        shareText += `\r\n<br>My interpretation: ||${interpretation}||`;
        shareText += `\r\n<br><b>${uniqueness}</b>`;
        shareText += `\r\n<br>Alignment : <b>${alignment}</b>`;
        shareText += `\r\n<br>\r\n<br>${gridString}`
        shareText += `\r\n<br>What do you see?`
        shareText += `\r\n<br>${baseURL}`;
        
        localStorage.setItem(`submission_${getTodaysDateKey()}`, shareText);
        displayPopup(shareText);
    } catch (error) {
        console.error('Error fetching data:', error);
    }

});

function displayPopup(shareText) {
    shareTextContainer.innerHTML = shareText; // Update DOM once
    sharePopup.style.display = 'block';   
    hideSubmission();
}

// function displayElements() {
//     updateTitle();
//     fetchGridFromServer()
//         .then((grid) => { 
//             displayGrid(grid);
//         })
//         .catch(error => console.error('Error fetching grid:', error)); 
//     if (localStorage.getItem(`submission_${dateKey}`)) {
//         const shareText = localStorage.getItem(`submission_${dateKey}`);
//         displayPopup(shareText);
//     } else {
//         displaySubmission();
//     }
// }

function displayElements() {
    updateTitle();
    fetchJsonGridFromServer()
        .then((gridJson) => { 
            renderGridJson(gridJson);
            gridString = getGridString(gridJson);
        })
        .catch(error => console.error('Error fetching grid:', error)); 
    if (localStorage.getItem(`submission_${dateKey}`)) {
        const shareText = localStorage.getItem(`submission_${dateKey}`);
        displayPopup(shareText);
    } else {
        displaySubmission();
    }
}

closePopupButton.addEventListener('click', () => {
    sharePopup.style.display = 'none'; // Hide the popup
    alreadySubmittedElement.style.display="inline"; 
});

copyButton.addEventListener('click', () => {
    const textToCopy = shareTextContainer.textContent; 
    copyToClipboard(textToCopy); 
});

displayElements();

