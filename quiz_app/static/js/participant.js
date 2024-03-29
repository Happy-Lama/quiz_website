
// Dynamically determine WebSocket URI based on the current page URL
const getWebSocketURI = () => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const hostname = window.location.hostname;
    const port = window.location.port ? `:${window.location.port}` : '';
    return `${protocol}//${hostname}${port}/ws/team/`;
};



// Example usage
const websocketURI = getWebSocketURI();
console.log(websocketURI); // This will log the dynamically generated WebSocket URI

const socket = new WebSocket(getWebSocketURI())

socket.onmessage = function(event) {
    const message = JSON.parse(event.data);
    console.log('Message received from server:', message);
    // Handle the message accordingly
    resolve_events(message)
};

socket.addEventListener('open', function (event) {
    console.log('WebSocket connection opened');
// socket.send(JSON.stringify({type:'current_round'}));
});

socket.addEventListener('close', function (event) {
    console.log('WebSocket connection closed');
});

function resolve_events(event_data){
    console.log(event_data)
    switch(event_data.type){
        case 'question_selected_event':
            question = event_data.message.question_id
            disableQuestion(question)
            break;
        case 'question_selected_event_success':
            // if (!localStorage.getItem('targetDate')) {
                // Set the target date and time (replace with your desired date and time)
            let targetDate = new Date();
            targetDate.setSeconds(targetDate.getSeconds() + event_data.message.question_time); // Example: 5 minutes from now
            localStorage.setItem('targetDate', targetDate);
                //emit event over a django channel about time up
            // }
            window.location.href = `/question/${event_data.message.question_id}`
            break;
        case 'round_started_event':
            round_id = event_data.message.round_id
            localStorage.setItem('round_id', round_id)
            if (!localStorage.getItem('roundTargetDate')) {
                // Set the target date and time (replace with your desired date and time)
                const targetDate = new Date();
                targetDate.setSeconds(targetDate.getSeconds() + event_data.message.duration * 60); // Example: 15 minutes from now
                localStorage.setItem('roundTargetDate', targetDate);
                //emit event over a django channel about time up
            }
            roundTimerInterval = updateRoundTimer()
            window.location.href = '/'
            break;
        case 'no_running_round':
            localStorage.removeItem('round_id')
            localStorage.removeItem('roundTargetDate')
            localStorage.removeItem('targetDate')
            clearInterval(roundTimerInterval)
            window.location.href = '/'
            break;
        case 'round_end_event':
            localStorage.removeItem('round_id')
            localStorage.removeItem('roundTargetDate')
            localStorage.removeItem('targetDate')
            clearInterval(roundTimerInterval)
            window.location.href = '/'
            break;
        case 'reset_round':
            localStorage.removeItem('round_id')
            localStorage.removeItem('roundTargetDate')
            localStorage.removeItem('targetDate')
            clearInterval(roundTimerInterval)
            window.location.href = '/'
            break;
        case 'round':
            localStorage.setItem('round_id', event_data.round_id)
            // targetDate = new Date();
            // targetDate.setSeconds(targetDate.getSeconds() + event_data.message.duration * 60); // Example: 15 minutes from now
            // localStorage.setItem('roundTargetDate', targetDate);
            break;
    }
}

function disableQuestion(question_id){
    const question = document.getElementById(question_id)
    question.onclick = null
    question.classList.add('bg-secondary')
}

// Function to update the countdown timer
function updateRoundTimer() {
// Get the target date and time from localStorage
// Check if target date is stored in localStorage
    
    const targetDate = new Date(localStorage.getItem('roundTargetDate'));
    //send event to server that timer has started
    // Update the countdown every second
    let timerInterval = setInterval(() => {
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
            //inform server that the timer is up

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
    return timerInterval
}

function fetchQn(event){
    console.log(event.target.id)
    console.log(document.getElementById('team_id').innerHTML)
    const message = {
        type: 'QuestionSelected',
        question_id: event.target.id,
        round_id: localStorage.getItem('round_id'),
        team_id: document.getElementById('team_id').innerHTML,
        question_selected_id: event.target.id
    }
    socket.send(JSON.stringify(message)) 
}

let roundTimerInterval = null; 
// Update the countdown timer
window.onload = () => {
    // socket.send(JSON.stringify({type: 'current_round'}))
    if(document.getElementById('round_id').innerHTML != null){
        localStorage.setItem('round_id', document.getElementById('round_id').innerHTML);
    }
    if(localStorage.getItem('roundTargetDate')){
        console.log(localStorage.getItem('roundTargetDate'))
        roundTimerInterval = updateRoundTimer();
    }
}