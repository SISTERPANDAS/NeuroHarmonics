// --- Video Recommendation Cards Data (Health Tips) ---
const videoRecommendations = [
  {
    file: 'body_movements.mp4',
    topic: 'Body Movements',
    quote: 'Movement is a medicine for creating change in a person’s physical, emotional, and mental states.',
    theme: 'Physical Wellness'
  },
  {
    file: 'Create_a_new_morning_routine.mp4',
    topic: 'Morning Routine',
    quote: 'Win the morning, win the day.',
    theme: 'Mindful Start'
  },
  {
    file: 'finding_goal.mp4',
    topic: 'Finding Your Goal',
    quote: 'The secret of getting ahead is getting started.',
    theme: 'Purpose & Growth'
  },
  {
    file: 'happy_activities.mp4',
    topic: 'Happy Activities',
    quote: 'Happiness is not something ready made. It comes from your own actions.',
    theme: 'Joyful Living'
  },
  {
    file: 'promise_to_a_friend.mp4',
    topic: 'Promise to a Friend',
    quote: 'A real friend is one who walks in when the rest of the world walks out.',
    theme: 'Social Connection'
  },
  {
    file: 'relaxed_time.mp4',
    topic: 'Relaxed Time',
    quote: 'Sometimes the most productive thing you can do is relax.',
    theme: 'Calm & Balance'
  },
  {
    file: 'spending_time_happily.mp4',
    topic: 'Spending Time Happily',
    quote: 'Enjoy the little things, for one day you may look back and realize they were the big things.',
    theme: 'Gratitude'
  }
];

function getRandomCards(arr, n) {
  const shuffled = arr.slice().sort(() => 0.5 - Math.random());
  return shuffled.slice(0, n);
}

function createVideoCard(card) {
  const cardDiv = document.createElement('div');
  cardDiv.className = 'video-card';
  cardDiv.innerHTML = `
    <div style="position:relative;">
      <img class="card-thumb" src="/static/dashboard/video_thumbs/${card.file.replace('.mp4','.jpg')}" alt="${card.topic}">
    </div>
    <div class="card-title">${card.topic}</div>
    <div class="card-theme">${card.theme}</div>
    <div class="card-quote">“${card.quote}”</div>
  `;
  cardDiv.addEventListener('click', function() {
    openVideoModal(card.file);
  });
  return cardDiv;
}

function renderVideoRecommendations() {
  const container = document.querySelector('.video-recommendations-container');
  if (!container) return;
  container.innerHTML = '';
  const cards = getRandomCards(videoRecommendations, 4);
  cards.forEach(card => {
    container.appendChild(createVideoCard(card));
  });
}

function openVideoModal(filename) {
  const modal = document.getElementById('video-modal');
  const video = document.getElementById('modal-video');
  video.src = `/images/${filename}`;
  modal.style.display = 'flex';
  video.play();
}

document.addEventListener('DOMContentLoaded', function() {
  renderVideoRecommendations();
  const modal = document.getElementById('video-modal');
  const closeBtn = document.getElementById('video-modal-close');
  closeBtn.onclick = function() {
    modal.style.display = 'none';
    const video = document.getElementById('modal-video');
    video.pause();
    video.currentTime = 0;
    video.src = '';
  };
  window.onclick = function(event) {
    if (event.target === modal) {
      modal.style.display = 'none';
      const video = document.getElementById('modal-video');
      video.pause();
      video.currentTime = 0;
      video.src = '';
    }
  };
});
