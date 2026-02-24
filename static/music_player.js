// Global music player logic
let musicPlayer = null;
let isPlaying = false;
let volume = 0.5;
// Use the user's specified path for the music file
const backgroundMusicPath = '/static/music/background/background.mp3';

function createMusicPlayer() {
    if (!musicPlayer) {
        musicPlayer = new Audio(backgroundMusicPath);
        musicPlayer.loop = true;
        musicPlayer.volume = volume;
        musicPlayer.autoplay = true;
        musicPlayer.addEventListener('ended', () => { isPlaying = false; });
        musicPlayer.addEventListener('play', () => { isPlaying = true; });
        musicPlayer.addEventListener('pause', () => { isPlaying = false; });
    }
}

function playMusic() {
    createMusicPlayer();
    musicPlayer.play();
    isPlaying = true;
}

function pauseMusic() {
    if (musicPlayer) {
        musicPlayer.pause();
        isPlaying = false;
    }
}

// Pause background music when other music is playing
function pauseBackgroundForOtherMusic() {
    pauseMusic();
}

function resumeBackgroundAfterOtherMusic() {
    playMusic();
}

// Autoplay on page load
window.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        playMusic();
    }, 200);
});

window.musicPlayer = {
    play: playMusic,
    pause: pauseMusic,
    pauseForOtherMusic: pauseBackgroundForOtherMusic,
    resumeAfterOtherMusic: resumeBackgroundAfterOtherMusic,
    get isPlaying() { return isPlaying; }
};
