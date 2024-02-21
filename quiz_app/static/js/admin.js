// Function to update the countdown timer
let timerInterval = null

function updateRoundTimer() {
    // Get the target date and time from localStorage
    const targetDate = new Date(localStorage.getItem('roundTargetDate'));
    //send event to server that timer has started
    // button.disabled = true
    // Update the countdown every second
    timerInterval = setInterval(() => {
        // Get the current date and time
        const now = new Date().getTime();

        // Calculate the time remaining
        const timeRemaining = targetDate - now;
        console.log(timeRemaining)
        // If the countdown is finished, display a message
        if (timeRemaining <= 0) {
            clearInterval(timerInterval);
            document.getElementById('roundTimer').innerHTML = '00:00';
            localStorage.removeItem('roundTargetDate');
            button.disabled = false
            //inform server that the timer is up
            const message = {
                type: 'roundEnd',
                data: 'RoundEnded'
            }
            socket.send(JSON.stringify(message))

        } else {
            const minutes = Math.floor((timeRemaining % (1000 * 60 * 60)) / (1000 * 60));
            const seconds = Math.floor((timeRemaining % (1000 * 60)) / 1000);

            // Pad minutes and seconds with leading zeros if they are single-digit
            const paddedMinutes = minutes.toString().padStart(2, '0');
            const paddedSeconds = seconds.toString().padStart(2, '0');

            // Display the countdown timer
            document.getElementById('roundTimer').innerHTML = `${paddedMinutes}:${paddedSeconds}`;

            
        }
    }, 1000); // Update every second
}



function resolve_events(event_data){
  console.log(event_data)
  switch(event_data.type){
    case 'question_selected_event':
        question = event_data.message
        updateLiveFeedQuestion(question);
        break;
    case 'choice_selected_event':
        choice = event_data.message
        updateLiveFeedChoice(choice)
        break;
    case 'round_time':
        clearInterval(timerInterval)
        const targetDate = new Date();
        targetDate.setSeconds(targetDate.getSeconds() + (event_data.duration * 60)); // Example: 15 minutes from now
        localStorage.setItem('roundTargetDate', targetDate);
        updateRoundTimer();
        window.location.href = '/'
  }
}

function updateLiveFeedQuestion(question){
    console.log("Question", question)
    qn = document.getElementById(question.team_id + 'qn')
    qn.innerHTML = question.question_selected_text
}

function updateLiveFeedChoice(choice){
    console.log("Choice", choice)
    choice_elmnt = document.getElementById(choice.team_id + 'ans')
    choice_elmnt.innerHTML = choice.choice_selected_text
}

const button = document.getElementById('timerStartBtn')
// Update the countdown timer
// Create WebSocket connection
const getWebSocketURI = () => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const hostname = window.location.hostname;
    const port = window.location.port ? `:${window.location.port}` : '';
    return `${protocol}//${hostname}${port}/ws/admin/`;
};

// socket
const websocketURI = getWebSocketURI();
console.log(websocketURI); // This will log the dynamically generated WebSocket URI

const socket = new WebSocket(getWebSocketURI())

// Connection opened
socket.addEventListener('open', function (event) {
    console.log('WebSocket connection opened');
    
});

// Listen for messages
socket.onmessage = function(event) {
    const message = JSON.parse(event.data);
    console.log('Message received from server:', message);
    // Handle the message accordingly
    resolve_events(message)
};

// Connection closed
socket.addEventListener('close', function (event) {
    console.log('WebSocket connection closed');
});

function startRound(event){
    socket.send(JSON.stringify({type:'start_round', round_id: event.target.id}));
}
function resetRounds(event){
    socket.send(JSON.stringify({type: 'reset_rounds'}))
    clearInterval(timerInterval)
    document.getElementById('roundTimer').innerHTML = '00:00';
    localStorage.removeItem('roundTargetDate');
    window.location.href = '/'
}
window.onload = () => {
    if(localStorage.getItem('roundTargetDate')){
        console.log(localStorage.getItem('roundTargetDate'))
        updateRoundTimer();
    }
}