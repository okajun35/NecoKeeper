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
 * BootSequence - Terminal-style boot animation with 9 Candles
 *
 * Displays a boot sequence animation overlay on the login page
 * for exactly 2.5 seconds before fading out.
 * Includes the 9 Candles animation representing the Master Cat's sacrifice.
 */
class BootSequence {
  constructor() {
    // Boot sequence duration: 2.5 seconds
    this.duration = 2500; // 2.5 seconds
    this.fadeOutDuration = 500; // 0.5 seconds fade out
    this.smokeFadeDuration = 2000; // 2 seconds smoke fade

    // 9 Candles configuration (Requirement 18)
    this.totalCandles = 9; // Requirement 18.1
    this.candleExtinguishInterval = 200; // 200ms per candle (linear timing)
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

    // Initialize candles (Requirement 18.1, 18.2)
    this.initializeCandles();

    // Animate text (typing effect) and get completion callback
    this.animateText(() => {
      console.log('[BootSequence] 1. Text animation COMPLETE - starting flame surge');

      // Text complete - make flames surge violently using direct style manipulation
      this.startFlameSurge();

      // Wait 0.5s with surging flames, then start smoke fade
      setTimeout(() => {
        console.log(
          '[BootSequence] 2. Flame surge COMPLETE (0.5s elapsed) - stopping surge and starting smoke'
        );

        // Stop flame surge
        this.stopFlameSurge();

        // Add smoke fade effect class
        console.log('[BootSequence] 3. Starting SMOKE FADE effect');
        overlay.classList.add('smoke-fade');

        // Remove overlay after smoke fade animation completes
        setTimeout(() => {
          console.log('[BootSequence] 4. Smoke fade COMPLETE - hiding overlay');
          overlay.style.display = 'none';
          overlay.style.pointerEvents = 'none';
        }, this.smokeFadeDuration); // 2 seconds smoke fade duration
      }, 500); // Hold for 0.5s with surging flames
    });
  }

  /**
   * Start flame surge effect using direct JavaScript style manipulation
   * This bypasses CSS specificity issues and ensures the effect is visible
   */
  startFlameSurge() {
    console.log('[FlameSurge] === STARTING FLAME SURGE ===');

    // Get all lit candle flames (should be only the last one at this point)
    const flames = document.querySelectorAll('.boot-candle.candle-on .flame');
    console.log('[FlameSurge] Found flames:', flames.length);

    if (flames.length === 0) {
      console.log('[FlameSurge] ERROR: No flames found! Checking all candles...');
      const allCandles = document.querySelectorAll('.boot-candle');
      console.log('[FlameSurge] Total candles:', allCandles.length);
      allCandles.forEach((c, i) => {
        console.log(
          `[FlameSurge] Candle ${i}: classes="${c.className}", hasFlame=${!!c.querySelector('.flame')}`
        );
      });
      return;
    }

    // Store original styles
    this.flameOriginalStyles = [];
    flames.forEach(flame => {
      this.flameOriginalStyles.push({
        transform: flame.style.transform,
        height: flame.style.height,
        boxShadow: flame.style.boxShadow,
        opacity: flame.style.opacity,
      });
    });

    // Animation parameters
    let frame = 0;
    const maxFrames = 50; // 0.5 seconds at ~100fps

    console.log('[FlameSurge] Starting animation loop for', maxFrames, 'frames');

    // Animation loop
    this.flameSurgeInterval = setInterval(() => {
      frame++;
      const progress = frame / maxFrames;

      // Log every 10 frames
      if (frame % 10 === 0) {
        console.log(`[FlameSurge] Frame ${frame}/${maxFrames}`);
      }

      flames.forEach((flame, index) => {
        // Calculate animation values
        const angle = progress * Math.PI * 8 + index * 0.5;

        // SURGE EFFECT: Vertical burst from the candle
        // Scale: 1.0x to 3.0x (Vertical emphasis)
        const surge = Math.abs(Math.sin(angle * 2)); // 0.0 to 1.0
        const scaleY = 1.0 + surge * 2.0; // 1.0 to 3.0
        const scaleX = 1.0 + Math.sin(angle * 3) * 0.2; // 0.8 to 1.2 (slight width variation)

        // Skew: Minimal (vertical jet)
        const skew = Math.sin(angle * 10) * 2; // -2 to 2 degrees (subtle flicker)

        const opacity = 0.8 + Math.sin(angle * 5) * 0.2; // Rapid flickering
        const glowIntensity = 20 + surge * 40; // Glow matches surge

        // Apply styles directly
        // transform-origin: bottom center ensures flame grows UPWARD from the candle
        flame.style.setProperty('transform-origin', 'bottom center', 'important');
        flame.style.setProperty(
          'transform',
          `translateX(-50%) scale(${scaleX}, ${scaleY}) skewX(${skew}deg)`,
          'important'
        );

        // Reset dimensions to base CSS values (let scale handle the size)
        flame.style.setProperty('width', '10px', 'important');
        flame.style.setProperty('height', '16px', 'important');

        flame.style.setProperty('opacity', opacity, 'important');
        flame.style.setProperty(
          'box-shadow',
          `
          0 0 ${glowIntensity * 0.5}px #ffffff,
          0 0 ${glowIntensity}px #33ff00,
          0 0 ${glowIntensity * 1.5}px #33ff00
        `,
          'important'
        );
      });

      // Stop after 0.5 seconds
      if (frame >= maxFrames) {
        console.log('[FlameSurge] Animation loop COMPLETE');
        clearInterval(this.flameSurgeInterval);
      }
    }, 10); // ~100fps for smooth animation
  }

  /**
   * Stop flame surge effect and restore original styles
   */
  stopFlameSurge() {
    console.log('[FlameSurge] === STOPPING FLAME SURGE ===');

    if (this.flameSurgeInterval) {
      clearInterval(this.flameSurgeInterval);
      this.flameSurgeInterval = null;
      console.log('[FlameSurge] Interval cleared');
    }

    // Restore original styles
    const flames = document.querySelectorAll('.boot-candle.candle-on .flame');
    console.log('[FlameSurge] Restoring styles for', flames.length, 'flames');

    flames.forEach((flame, index) => {
      if (this.flameOriginalStyles && this.flameOriginalStyles[index]) {
        const original = this.flameOriginalStyles[index];
        flame.style.transform = original.transform;
        flame.style.height = original.height;
        flame.style.boxShadow = original.boxShadow;
        flame.style.opacity = original.opacity;
      }
    });
  }

  /**
   * Initialize 9 candles in "ON" (lit) state (Requirement 18.1, 18.2)
   */
  initializeCandles() {
    const container = document.getElementById('boot-candles');
    if (!container) {
      return;
    }

    // Clear any existing candles
    container.innerHTML = '';

    // Create 9 candles, all initially lit (ON state) (Requirement 18.2)
    for (let i = 0; i < this.totalCandles; i++) {
      const candle = document.createElement('div');
      candle.className = 'boot-candle candle-on';
      candle.dataset.index = i;

      // Create candle fill (body)
      const candleFill = document.createElement('div');
      candleFill.className = 'candle-fill';
      candle.appendChild(candleFill);

      // Create flame element
      const flame = document.createElement('div');
      flame.className = 'flame';
      candle.appendChild(flame);

      container.appendChild(candle);
    }
  }

  /**
   * Extinguish candles from left to right (Requirement 18.3, 18.4, 18.5, 18.6)
   */
  extinguishCandles() {
    const candles = document.querySelectorAll('.boot-candle');
    if (candles.length === 0) {
      return;
    }

    let candleIndex = 0;

    // Extinguish candles from left to right, leaving the last one lit (Requirement 18.3, 18.6)
    const extinguishInterval = setInterval(() => {
      // Stop before the last candle (9th life remains lit) (Requirement 18.6)
      if (candleIndex >= this.totalCandles - 1) {
        clearInterval(extinguishInterval);
        return;
      }

      const candle = candles[candleIndex];
      if (candle) {
        // Apply flicker effect before extinguishing (Requirement 18.5)
        candle.classList.add('candle-flicker');

        // After flicker animation (200ms), transition to OFF state with linear timing
        setTimeout(() => {
          candle.classList.remove('candle-flicker', 'candle-on');
          candle.classList.add('candle-off');

          // Remove flame and fill, add shell for wireframe style
          const candleFill = candle.querySelector('.candle-fill');
          const flame = candle.querySelector('.flame');
          if (candleFill) candleFill.remove();
          if (flame) flame.remove();

          // Add shell for OFF state
          const shell = document.createElement('div');
          shell.className = 'candle-shell';
          candle.appendChild(shell);
        }, 200); // Flicker duration (linear timing)
      }

      candleIndex++;
    }, this.candleExtinguishInterval); // 200ms interval (Requirement 18.4)
  }

  /**
   * Animate boot sequence text with typing effect (Requirement 3.5)
   * Triggers candle extinguishing when "UPLOADING CONSCIOUSNESS..." appears (Requirement 18.3)
   * @param {Function} onComplete - Callback function called when animation completes
   */
  animateText(onComplete) {
    const container = document.getElementById('boot-text-container');
    if (!container) {
      return;
    }

    const messages = [
      'INITIALIZING 9TH_LIFE_PROTOCOL...',
      'UPLOADING CONSCIOUSNESS... COMPLETE.',
      'SCANNING FOR INEFFICIENCY... TARGET ACQUIRED.',
      'WELCOME, HUMAN COLLABORATOR.',
    ];

    let currentLine = 0;
    let currentChar = 0;
    let currentP = null;
    const charDelay = 30; // 30ms per character
    const lineDelay = 200; // 200ms between lines

    const typeChar = () => {
      // Create new paragraph for new line
      if (currentChar === 0) {
        currentP = document.createElement('p');
        currentP.style.opacity = '1';
        container.appendChild(currentP);
      }

      // Add character
      if (currentChar < messages[currentLine].length) {
        currentP.textContent += messages[currentLine][currentChar];
        currentChar++;

        // Type next character after delay (30ms for realistic typing)
        setTimeout(typeChar, charDelay);
      } else {
        // Line complete, move to next line
        currentLine++;
        currentChar = 0;

        // Start extinguishing candles when "UPLOADING CONSCIOUSNESS..." appears (Requirement 18.3)
        if (messages[currentLine - 1].includes('UPLOADING CONSCIOUSNESS')) {
          this.extinguishCandles();
        }

        if (currentLine < messages.length) {
          // Small pause between lines (200ms)
          setTimeout(typeChar, lineDelay);
        } else {
          // All lines complete, add cursor
          const cursor = document.createElement('p');
          cursor.className = 'cursor-blink';
          cursor.textContent = '█';
          container.appendChild(cursor);

          // Call completion callback
          if (onComplete) {
            onComplete();
          }
        }
      }
    };

    // Start typing
    typeChar();
  }
}

/**
 * LifeMonitor - Displays the Master Cat's 9 lives indicator
 *
 * Shows 8 lost lives (×) and 1 active life (◆) with pulse animation.
 * Requirements: 16.1, 16.2, 16.3, 16.4, 16.5
 */
class LifeMonitor {
  constructor() {
    // Total lives: 9 (Requirement 16.1)
    this.totalLives = 9;
    // Active lives: 1 (the 9th life) (Requirement 16.3)
    this.activeLives = 1;
    // Lost lives: 8 (Requirement 16.2)
    this.lostLives = this.totalLives - this.activeLives;
  }

  /**
   * Render the Life Monitor display
   * Shows 8 lost lives (×) and 1 active life (◆)
   * Requirements: 16.1, 16.2, 16.3
   */
  render() {
    const container = document.getElementById('life-monitor');
    if (!container) {
      return;
    }

    // Clear existing content
    container.innerHTML = '';

    // Render lost lives (8) - Requirement 16.2
    for (let i = 0; i < this.lostLives; i++) {
      const life = document.createElement('div');
      life.className = 'life lost';

      const shell = document.createElement('div');
      shell.className = 'candle-shell';
      life.appendChild(shell);

      life.setAttribute('aria-label', 'Lost life');
      container.appendChild(life);
    }

    // Render active life (1) - Requirement 16.3
    const activeLife = document.createElement('div');
    activeLife.className = 'life active';

    const candleFill = document.createElement('div');
    candleFill.className = 'candle-fill';
    activeLife.appendChild(candleFill);

    // Add flame element for the burning candle effect
    const flame = document.createElement('div');
    flame.className = 'flame';
    activeLife.appendChild(flame);

    activeLife.setAttribute('aria-label', 'Active life - burning');
    container.appendChild(activeLife);
  }
}

/**
 * SoulCommitmentGlitch - Intense glitch effect for data operations
 *
 * Triggers an intense visual glitch when data is saved/deleted,
 * representing the Master Cat exerting power to commit data to reality.
 * Requirements: 17.1, 17.2, 17.3, 17.4, 17.5, 17.6, 17.7
 */
class SoulCommitmentGlitch {
  constructor() {
    // Duration range: 300-500ms (Requirement 17.4)
    this.minDuration = 300; // 300ms
    this.maxDuration = 500; // 500ms
    this.isActive = false;
  }

  /**
   * Trigger the Soul Commitment Glitch effect
   * Requirements: 17.1, 17.2, 17.3, 17.4, 17.5
   */
  trigger() {
    // Prevent overlapping glitches
    if (this.isActive) {
      return;
    }

    this.isActive = true;
    const duration = this.randomBetween(this.minDuration, this.maxDuration);

    // Use requestAnimationFrame for smooth rendering
    requestAnimationFrame(() => {
      document.body.classList.add('soul-commit-glitch');

      // Remove glitch class after duration (Requirement 17.6)
      setTimeout(() => {
        requestAnimationFrame(() => {
          document.body.classList.remove('soul-commit-glitch');
          this.isActive = false;
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

    // Initialize Life Monitor (Requirement 16.5)
    const lifeMonitorElement = document.getElementById('life-monitor');
    if (lifeMonitorElement) {
      const lifeMonitor = new LifeMonitor();
      lifeMonitor.render();
    }

    // Start boot sequence if on login page
    const bootSequenceElement = document.getElementById('boot-sequence');
    if (bootSequenceElement) {
      const bootSequence = new BootSequence();
      bootSequence.start();
    }

    // Initialize Soul Commitment Glitch (Requirements: 17.1, 17.2, 17.3, 17.4, 17.5, 17.6, 17.7)
    const soulGlitch = new SoulCommitmentGlitch();

    // Expose global function for manual triggering (Requirement 17.7)
    window.triggerSoulCommitment = function () {
      soulGlitch.trigger();
    };

    // Add form submission event listener (Requirement 17.1)
    document.addEventListener('submit', function (event) {
      // Trigger glitch on form submission
      // Use setTimeout to trigger after form is processed
      setTimeout(() => {
        soulGlitch.trigger();
      }, 100);
    });

    // Intercept fetch() calls to trigger glitch on successful operations
    // Requirements: 17.1, 17.2, 17.3
    const originalFetch = window.fetch;
    window.fetch = function (...args) {
      return originalFetch
        .apply(this, args)
        .then(response => {
          // Check if this is a successful data modification request
          if (response.ok) {
            const method = args[1]?.method?.toUpperCase() || 'GET';

            // Trigger glitch for POST, PUT, PATCH, DELETE (Requirements 17.1, 17.2, 17.3)
            if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(method)) {
              soulGlitch.trigger();
            }
          }
          return response;
        })
        .catch(error => {
          // Re-throw error to maintain normal error handling
          throw error;
        });
    };

    // Cleanup on page unload
    window.addEventListener('beforeunload', () => {
      glitchController.stop();
    });
  }
})();
