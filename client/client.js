const socket = io("http://127.0.0.1:5000");
let board = [];
let currentPlayer = "";
let selectedCharacter = null;

const boardContainer = document.getElementById("board");
const messageElement = document.getElementById("message");
const moveHistoryElement = document.getElementById("move-history");
const validMovesElement = document.getElementById("valid-moves");

document.addEventListener("DOMContentLoaded", () => {
  console.log("Attempting to initialize game");
  socket.emit("initialize_game", {
    player_a_characters: ["P", "H1", "H2"],
    player_b_characters: ["P", "H1", "H2"],
  });
});

socket.on("game_initialized", (data) => {
  board = data.board;
  currentPlayer = data.current_player;
  renderBoard();
  updateMessage(`Player ${currentPlayer}'s turn`);
});

socket.on("update_board", (data) => {
  board = data.board;
  currentPlayer = data.current_player;
  renderBoard();
  updateMessage(`Player ${currentPlayer}'s turn`);
  updateMoveHistory(data.move_history);
});

socket.on("invalid_move", (data) => {
  updateMessage(data.message);
});

socket.on("game_over", (data) => {
  updateMessage(`Game Over! Player ${data.winner} wins!`);
  disableBoard();
});

function renderBoard() {
  boardContainer.innerHTML = "";
  for (let r = 0; r < 5; r++) {
    const row = document.createElement("div");
    row.className = "row";
    for (let c = 0; c < 5; c++) {
      const cell = document.createElement("div");
      cell.className =
        "cell " +
        (board[r][c]
          ? board[r][c].startsWith("A-")
            ? "playerA"
            : "playerB"
          : "empty");
      cell.textContent = board[r][c] || "";
      cell.onclick = () => handleCellClick(r, c);
      row.appendChild(cell);
    }
    boardContainer.appendChild(row);
  }
}

function handleCellClick(r, c) {
  if (
    (currentPlayer === "A" && board[r][c]?.startsWith("A-")) ||
    (currentPlayer === "B" && board[r][c]?.startsWith("B-"))
  ) {
    selectedCharacter = board[r][c];
    highlightValidMoves(r, c);
  } else if (selectedCharacter) {
    const move = getMoveFromCell(r, c);
    if (move) {
      socket.emit("make_move", {
        player: currentPlayer,
        character: selectedCharacter.split("-")[1],
        move: move,
      });
      selectedCharacter = null; // Reset selection
      clearValidMoves();
    }
  }
}

function highlightValidMoves(r, c) {
  clearValidMoves(); // Clear any previous highlights
  const charType = selectedCharacter[2]; // Get character type (P, H1, H2)
  let validMoves = [];

  // Determine valid moves based on character type
  if (charType === "P") {
    validMoves = [
      { r: r - 1, c: c }, // Forward
      { r: r, c: c - 1 }, // Left
      { r: r, c: c + 1 }, // Right
      { r: r + 1, c: c }, // Backward
    ];
  } else if (charType === "H1") {
    validMoves = [
      { r: r - 2, c: c }, // Forward
      { r: r, c: c - 2 }, // Left
      { r: r, c: c + 2 }, // Right
      { r: r + 2, c: c }, // Backward
    ];
  } else if (charType === "H2") {
    validMoves = [
      { r: r - 2, c: c - 2 }, // Forward-Left
      { r: r - 2, c: c + 2 }, // Forward-Right
      { r: r + 2, c: c - 2 }, // Backward-Left
      { r: r + 2, c: c + 2 }, // Backward-Right
    ];
  }

  // Highlight valid moves
  validMoves.forEach((move) => {
    if (isValidCell(move.r, move.c)) {
      const cell = boardContainer.children[move.r].children[move.c];
      cell.classList.add("valid-move");
      cell.onclick = () => handleCellClick(move.r, move.c); // Reassign click handler
    }
  });
}

function clearValidMoves() {
  const validCells = document.querySelectorAll(".valid-move");
  validCells.forEach((cell) => {
    cell.classList.remove("valid-move");
    cell.onclick = null; // Remove click handler
  });
}

function isValidCell(r, c) {
  return r >= 0 && r < 5 && c >= 0 && c < 5;
}

function getMoveFromCell(r, c) {
  const charType = selectedCharacter[2];
  const board = this.board; // Assuming 'board' is accessible within the component's scope

  let validMoves = [];

  switch (charType) {
    case "P":
      validMoves = getPawnMoves(r, c, board);
      break;
    case "H1":
      validMoves = getHero1Moves(r, c);
      break;
    case "H2":
      validMoves = getHero2Moves(r, c);
      break;
    default:
      console.error(`Invalid character type: ${charType}`);
      break;
  }

  const targetCell = { r, c };

  return validMoves.filter((move) => isValidMove(targetCell, move, board));
}

function updateMessage(message) {
  messageElement.textContent = message;
}

function updateMoveHistory(moveHistory) {
  moveHistoryElement.innerHTML =
    "<h3>Move History</h3>" +
    moveHistory.map((move) => `<div>${move}</div>`).join("");
}

function disableBoard() {
  const cells = document.querySelectorAll(".cell");
  cells.forEach((cell) => {
    cell.onclick = null; // Disable all cell clicks
  });
}
