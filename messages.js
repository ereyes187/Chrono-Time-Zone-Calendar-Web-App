// Get access to user_id and convo_id variables from template

const user_id = document.getElementById("sendMessageForm").dataset.userId;
const convo_id = document.getElementById("sendMessageForm").dataset.convoId;

document.getElementById("sendMessageForm").addEventListener("keydown", function(event) {

  if (event.key === "Enter" && !event.shiftKey) {
    console.log("Im working")
    // event.preventDefault();

    // // Update form action to reply route
    // document.getElementById("sendMessageForm").action = "/dashboard/messages/" + user_id + "/" + convo_id + "/reply";
    
    // document.getElementById("sendMessageForm").submit(); 
  }

});