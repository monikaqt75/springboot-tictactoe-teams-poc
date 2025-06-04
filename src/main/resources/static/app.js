const cellElements = document.querySelectorAll('[data-cell]');
const board = document.getElementById('board');
const winningMessage = document.getElementById('winning-message');
const winningMessageText = document.getElementById('winning-message-text');
const restartButton = document.getElementById('restart-button');

let isCircleTurn;

const WINNING_COMBINATIONS = [
  [0, 1, 2], [3, 4, 5], [6, 7, 8],
  [0, 3, 6], [1, 4, 7], [2, 5, 8],
  [0, 4, 8], [2, 4, 6]
];

startGame();
restartButton.addEventListener('click', startGame);

function startGame() {
  isCircleTurn = false;
  cellElements.forEach(cell => {
    cell.classList.remove('x', 'o');
    cell.removeEventListener('click', handleClick);
    cell.addEventListener('click', handleClick, { once: true });
  });
  setBoardHoverClass();
  winningMessage.classList.remove('show');
}

function handleClick(e) {
  const cell = e.target;
  const currentClass = isCircleTurn ? 'o' : 'x';
  placeMark(cell, currentClass);
  if (checkWin(currentClass)) {
    endGame(false);
  } else if (isDraw()) {
    endGame(true);
  } else {
    isCircleTurn = !isCircleTurn;
    setBoardHoverClass();
  }
}

function placeMark(cell, currentClass) {
  cell.classList.add(currentClass);
}

function setBoardHoverClass() {
  board.classList.remove('x', 'o');
  board.classList.add(isCircleTurn ? 'o' : 'x');
}

function checkWin(currentClass) {
  return WINNING_COMBINATIONS.some(combination =>
    combination.every(index =>
      cellElements[index].classList.contains(currentClass)
    )
  );
}

function isDraw() {
  return [...cellElements].every(cell =>
    cell.classList.contains('x') || cell.classList.contains('o')
  );
}

function endGame(draw) {
  winningMessageText.textContent = draw ? 'Draw!' : `${isCircleTurn ? 'O' : 'X'} Wins!`;
  winningMessage.classList.add('show');
}