function showSection(sectionId) {
  // Hide all sections
  document.querySelectorAll(".content-box").forEach((section) => {
    section.classList.remove("active");
  });

  // Show the selected section
  document.getElementById(sectionId).classList.add("active");
}
function showLetterSection(sectionId) {
  // Hide all letter sections
  document.querySelectorAll(".letter-content-box").forEach((section) => {
    section.classList.remove("active");
  });

  // Show the selected letter section
  document.getElementById(sectionId).classList.add("active");
}

const selectionBoxes = document.querySelectorAll(".selection-checkbox");
const approveBtn = document.getElementById("approveBtn");
const rejectBtn = document.getElementById("rejectBtn");
const delcBtn = document.getElementById("delc");

function updateButtonState() {
  const isChecked = Array.from(selectionBoxes).some(
    (checkbox) => checkbox.checked
  );
  if (isChecked) {
    approveBtn.classList.add("enabled");
    rejectBtn.classList.add("enabled");
    delcBtn.classList.add("enabled");
    approveBtn.disabled = false;
    rejectBtn.disabled = false;
    delcBtn.disabled = false;
  } else {
    approveBtn.classList.remove("enabled");
    rejectBtn.classList.remove("enabled");
    delcBtn.classList.remove("enabled");
    approveBtn.disabled = true;
    rejectBtn.disabled = true;
    delcBtn.disabled = true;
  }
}

selectionBoxes.forEach((box) => {
  box.addEventListener("change", updateButtonState);
});

const selectionBoxesl = document.querySelectorAll(".selection-checkbox-letter");
const markreadbtn = document.getElementById("markreadbtn");
const dellbtn = document.getElementById("dell");


function updatereadButtonState() {
  const isCheckedl = Array.from(selectionBoxesl).some(
    (checkbox) => checkbox.checked
  );
  if (isCheckedl) {
    markreadbtn.classList.add("enabled");
    markreadbtn.disabled = false;
    dellbtn.classList.add("enabled");
    dellbtn.disabled = false;
  } else {
    markreadbtn.classList.remove("enabled");
    markreadbtn.disabled = true;
    dellbtn.classList.remove("enabled");
    dellbtn.disabled = true;
  }
}

selectionBoxesl.forEach((box) => {
  box.addEventListener("change", updatereadButtonState);
});

