let userScore = 0;
let compScore = 0;

const choices = document.querySelectorAll(".choice");

const msg = document.querySelector("#msg");

const userScorepara = document.querySelector("#user-score");
const compScorepara = document.querySelector("#comp-score");


const getCompChoice = () => {

    const options = ["rock", "paper", "scissor"];
    const randIdx = Math.floor(Math.random() * 3);
    return options[randIdx];

}
const drawGame = () => {
    // console.log("Game was draw.");
    msg.innerText = "Game was draw. Play again ?";
    msg.style.backgroundColor = "#081b31";

}

const showWinner = (userwin, userChoice, compChoice) => {
    if (userwin) {
        // console.log("you Win!");
        userScore++;
        userScorepara.innerText = userScore;
        msg.innerText = `You win! Your ${userChoice} beats ${compChoice}`;
        msg.style.backgroundColor = "green";
    } else {
        // console.log("you lose");
        compScore++;
        compScorepara.innerText = compScore;
        msg.innerText = `You lost. ${compChoice} beats Your ${userChoice}`;
        msg.style.backgroundColor = "red";

    }
};



const playgame = (userChoice) => {
    // console.log("User choice = ", userChoice);
    // generate computer choice;
    const compChoice = getCompChoice();
    // console.log("Cmp Choice = ", compChoice);


    if (userChoice === compChoice) {
        drawGame();
    } else {
        let userwin = true;
        if (userChoice === "rock") {
            // scissors,paper
            userwin = compChoice === "paper" ? false : true;
        } else if (userChoice === "paper") {
            // rock,scissors
            userwin = compChoice === "scissor" ? false : true;
        } else {
            // rock,paper

            userwin = compChoice === "rock" ? false : true;
        }

        showWinner(userwin, userChoice, compChoice);
    }
};



choices.forEach((choice) => {
    choice.addEventListener("click", () => {

        const userChoice = choice.getAttribute("id");

        // console.log("choice was clicked", userChoice);
        playgame(userChoice)
    });
});