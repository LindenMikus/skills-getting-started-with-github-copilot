document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      activitiesList.innerHTML = "";
      activitySelect.innerHTML = '<option value="">-- Select an activity --</option>';

      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;

        const participantsSection = document.createElement("div");
        participantsSection.className = "participants-section";

        const participantsHeading = document.createElement("h5");
        participantsHeading.textContent = "Participants";
        participantsSection.appendChild(participantsHeading);

        const participantsList = document.createElement("ul");
        participantsList.className = "participants-list";

        if (details.participants.length > 0) {
          details.participants.forEach((participant) => {
            const participantItem = document.createElement("li");
            participantItem.className = "participant-item";

            const participantName = document.createElement("span");
            participantName.className = "participant-name";
            participantName.textContent = participant;

            const removeButton = document.createElement("button");
            removeButton.type = "button";
            removeButton.className = "participant-remove";
            removeButton.setAttribute("aria-label", `Remove ${participant} from ${name}`);
            removeButton.title = `Remove ${participant}`;
            removeButton.textContent = "✕";
            removeButton.addEventListener("click", async () => {
              await unregisterParticipant(name, participant);
            });

            participantItem.appendChild(participantName);
            participantItem.appendChild(removeButton);
            participantsList.appendChild(participantItem);
          });
        } else {
          const emptyState = document.createElement("p");
          emptyState.className = "participants-empty";
          emptyState.textContent = "No students signed up yet.";
          participantsSection.appendChild(emptyState);
        }

        participantsSection.appendChild(participantsList);

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
        `;

        activityCard.appendChild(participantsSection);
        activitiesList.appendChild(activityCard);

        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  async function unregisterParticipant(activityName, email) {
    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activityName)}/participants?email=${encodeURIComponent(email)}`,
        {
          method: "DELETE",
        }
      );

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.detail || "Unable to unregister participant");
      }

      messageDiv.textContent = result.message;
      messageDiv.className = "success";
      messageDiv.classList.remove("hidden");
      setTimeout(() => messageDiv.classList.add("hidden"), 5000);

      await fetchActivities();
    } catch (error) {
      messageDiv.textContent = error.message || "Failed to unregister participant.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error unregistering participant:", error);
    }
  }

  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        await fetchActivities();
        signupForm.reset();
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  fetchActivities();
});
