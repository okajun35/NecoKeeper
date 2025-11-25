/**
 * Glitch Effects for Kiroween Theme (Necro-Terminal Edition)
 *
 * This module provides visual glitch effects for the cyberpunk/horror-themed interface.
 * It includes:
 * - GlitchController: Random glitch effects at 5-15 second intervals
 * - BootSequence: Terminal-style boot animation on login page
 *
 * Requirements: 4.3, 4.4, 12.2
 */

/**
 * GlitchController - Manages random glitch visual effects
 *
 * Triggers random visual distortions at intervals between 5-15 seconds,
 * with each glitch lasting 100-300 milliseconds.
 */
class GlitchController {
  constructor() {
    // Interval range: 5-15 seconds (Requirement 4.3)
    this.minInterval = 5000; // 5 seconds
    this.maxInterval = 15000; // 15 seconds

    // Duration range: 100-300ms (Requirement 4.4)
    this.minDuration = 100; // 100ms
    this.maxDuration = 300; // 300ms

    this.isRunning = false;
    this.timeoutId = null;
  }

  /**
   * Start the glitch effect controller
   */
  start() {
    if (this.isRunning) {
      return;
    }
    this.isRunning = true;
    this.scheduleNextGlitch();
  }

  /**
   * Stop the glitch effect controller
   */
  stop() {
    this.isRunning = false;
    if (this.timeoutId) {
      clearTimeout(this.timeoutId);
      this.timeoutId = null;
    }
  }

  /**
   * Schedule the next glitch effect at a random interval
   */
  scheduleNextGlitch() {
    if (!this.isRunning) {
      return;
    }

    const interval = this.randomBetween(this.minInterval, this.maxInterval);
    this.timeoutId = setTimeout(() => this.triggerGlitch(), interval);
  }

  /**
   * Trigger a glitch effect with random duration
   * Uses requestAnimationFrame for smooth rendering (Requirement 12.2)
   */
  triggerGlitch() {
    if (!this.isRunning) {
      return;
    }

    const duration = this.randomBetween(this.minDuration, this.maxDuration);

    // Use requestAnimationFrame for smooth rendering
    requestAnimationFrame(() => {
      document.body.classList.add('glitch-active');

      // Remove glitch class after duration
      setTimeout(() => {
        requestAnimationFrame(() => {
          document.body.classList.remove('glitch-active');
          // Schedule next glitch
          this.scheduleNextGlitch();
        });
      }, duration);
    });
  }

  /**
   * Generate a random integer between min and max (inclusive)
   * @param {number} min - Minimum value
   * @param {number} max - Maximum value
   * @returns {number} Random integer
   */
  randomBetween(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
  }
}

/**
 * BootSequence - Terminal-style boot animation
 *
 * Displays a boot sequence animation overlay on the login page
 * for exactly 2.5 seconds before fading out.
 */
class BootSequence {
  constructor() {
    // Boot sequence duration: 2.5 seconds (Requirement 3.2)
    this.duration = 2500; // 2.5 seconds
    this.fadeOutDuration = 500; // 0.5 seconds fade out
  }

  /**
   * Start the boot sequence animation
   */
  start() {
    const overlay = document.getElementById('boot-sequence');
    if (!overlay) {
      return;
    }

    // Prevent user interaction during boot sequence (Requirement 3.4)
    overlay.style.pointerEvents = 'all';
    overlay.style.display = 'flex';
    overlay.style.opacity = '1';

    // Animate text (typing effect)
    this.animateText();

    // Fade out after duration (Requirement 3.3)
    setTimeout(() => {
      overlay.style.transition = `opacity ${this.fadeOutDuration}ms ease-out`;
      overlay.style.opacity = '0';

      // Remove overlay after fade out
      setTimeout(() => {
        overlay.style.display = 'none';
        overlay.style.pointerEvents = 'none';
      }, this.fadeOutDuration);
    }, this.duration);
  }

  /**
   * Animate boot sequence text with typing effect (Requirement 3.5)
   */
  animateText() {
    const overlay = document.getElementById('boot-sequence');
    if (!overlay) {
      return;
    }

    const textElements = overlay.querySelectorAll('.boot-text p');
    if (textElements.length === 0) {
      return;
    }

    // Stagger the appearance of each line
    const delayPerLine = this.duration / textElements.length;

    textElements.forEach((element, index) => {
      setTimeout(() => {
        element.style.opacity = '1';
        element.classList.add('typing-animation');
      }, delayPerLine * index);
    });
  }
}

/**
 * Initialize glitch effects when page loads
 * Only runs in Kiroween Mode (when body has 'kiroween-mode' class)
 */
(function initializeGlitchEffects() {
  // Check if we're in Kiroween Mode
  if (!document.body.classList.contains('kiroween-mode')) {
    return;
  }

  // Wait for DOM to be fully loaded
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initialize);
  } else {
    initialize();
  }

  function initialize() {
    // Start glitch controller
    const glitchController = new GlitchController();
    glitchController.start();

    // Start boot sequence if on login page
    const bootSequenceElement = document.getElementById('boot-sequence');
    if (bootSequenceElement) {
      const bootSequence = new BootSequence();
      bootSequence.start();
    }

    // Cleanup on page unload
    window.addEventListener('beforeunload', () => {
      glitchController.stop();
    });
  }
})();
