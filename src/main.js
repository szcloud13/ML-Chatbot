
export async function setupEventListeners(){
    // // for user to enter query
    document.getElementById("ask_btn").addEventListener("click", readQuery);
      
}

setupEventListeners();

function readQuery(){
  if(document.getElementById("textbox").style.display == ''){

    document.getElementById("textbox").style.display = 'none';
    document.getElementById("ask_btn").style.display = 'none';

    console.log(document.getElementsByTagName('textarea')[0].value);
    var userMsg = document.getElementsByTagName('textarea')[0].value;
    createDialogBox(userMsg, "useravatar.png");

    // wait for chatbot reply
    call_ChatBot(userMsg)
  }
  
}

function makeFeedRequest(userMsg) {
  return fetch(`http://localhost:8080/MLChatBot/ask?expression=${userMsg}`, {
    headers: {
      "Access-Control-Allow-Origin": `*`,
    },
    method: "GET"
  })
  .then(r => r.json())
  .then((r) => {
      return r; //return the json data
  }) 
  .catch((e) => {
      console.log(e);
      return 'Sorry our server is down! Please check again later :(';
  });
}

async function call_ChatBot(userMsg){

  try {
    var chatBot_reply = await makeFeedRequest(userMsg);
    console.log(chatBot_reply);
  }catch (e) {
    console.log(e);
    createDialogBox("Sorry I did not understand you", "chatbotavatar.png");
  }

  if(chatBot_reply != ''){
    createDialogBox(chatBot_reply, "chatbotavatar.png");
  }else{
    createDialogBox("Sorry I did not understand you", "chatbotavatar.png");
  }

  // show the textbox entry again 
  document.getElementById("textbox").style.display = '';
  document.getElementById("ask_btn").style.display = '';
}

function createDialogBox(userMsg, avatar_link){
    
    var container = document.createElement('div');

    var span = document.createElement("span");
    span.innerText = new Date().toLocaleString().replace(',','');

    var img = document.createElement("img");
    img.setAttribute("src", avatar_link);
    img.setAttribute("alt", "Avatar");
    img.style.width = "100%";
    
    if(avatar_link.match('chatbotavatar.png')){ 
      container.setAttribute("class", "container darker");
      img.setAttribute("class", "right"); 
      span.setAttribute("class", "time-left");
    }else{
      container.setAttribute("class", "container"); 
      span.setAttribute("class", "time-right");
    }

    var p = document.createElement("p");
    p.innerText = 'Please give me a minute'
    p.innerText = userMsg;

    container.appendChild(img);
    container.appendChild(p);
    container.appendChild(span);

    document.getElementById("chat_dialog").appendChild(container);
}

