const $messageArea = $(".message-area");
const BASE_URL = "http://127.0.0.1:5001";
const $likeBtn = $(".btn-like");

/** Make POST request to like */
async function likeMessage(messageId) {
  await axios.post(`${BASE_URL}/messages/${messageId}/like`);
}

async function getUserLikes() {
  const response = await axios.get(`${BASE_URL}/user-likes`);
  return response.data.userLikes
}

function getMessageId(evt) {
  return $(evt.target).closest(".message-area").data("id");
}

async function handleClickLike(evt) {
  evt.preventDefault();
  const msgId = getMessageId(evt);
  const userLikes = await getUserLikes();
  await likeMessage(msgId)
  updateLikeIcon(evt, msgId, userLikes)
}

async function isMsgLiked(msgId, userLikes) {
  return await userLikes.includes(msgId)
}

async function updateLikeIcon(evt, msgId, userLikes) {
  const msgedLiked = await isMsgLiked(msgId, userLikes)
  let currentIcon = $(evt.target)

  if (msgedLiked) {
    currentIcon.removeClass("bi-star-fill")
    currentIcon.addClass("bi-star")
  } else {
    currentIcon.removeClass("bi-star")
    currentIcon.addClass("bi-star-fill")
  }
}

$likeBtn.on("click", handleClickLike);
