document.addEventListener("submit", (e) => {
  const form = e.target.closest("#taskForm");
  if (!form) return;

  const titleInput = form.querySelector("#titleInput");
  const title = (titleInput.value || "").trim();

  if (!title) {
    e.preventDefault();
    alert("Title is required.");
    titleInput.focus();
  }
});
