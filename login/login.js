document.getElementById('analyze-btn').addEventListener('click', function() {
    const btn = this;
    const content = document.getElementById('result-content');
    
    // Disable button during processing
    btn.disabled = true;
    btn.textContent = "Processing...";

    // Simulate Step Progression
    const steps = [1, 2, 3, 4];
    steps.forEach((step, index) => {
        setTimeout(() => {
            document.getElementById(`step-${step}`).classList.add('step-active');
        }, index * 800);
    });

    // Show Final Result
    setTimeout(() => {
        content.innerHTML = `
            <div style="animation: fadeIn 0.5s">
                <h3 style="color: #059669; font-size: 2.5rem; margin-bottom: 0.5rem;">Calm</h3>
                <p style="font-weight: 600;">94% Confidence Score</p>
                <p style="font-size: 0.8rem; color: gray; margin-top: 1rem;">Neural activity indicates focused relaxation.</p>
            </div>
        `;
        btn.textContent = "Analyze Emotion";
        btn.disabled = false;
    }, 3500);
});