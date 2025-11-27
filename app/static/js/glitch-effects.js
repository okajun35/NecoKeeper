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
      console.log('[BootSequence] Text animation COMPLETE - triggering cooldown');

      // Trigger cooldown for the last flame
      this.triggerCooldown();

      // Wait 1.0s (cooldown duration) before smoke fade
      setTimeout(() => {
        console.log('[BootSequence] Starting smoke fade');
        // Add smoke fade effect class
        overlay.classList.add('smoke-fade');

        // Remove overlay after smoke fade animation completes
        setTimeout(() => {
          overlay.style.display = 'none';
          overlay.style.pointerEvents = 'none';
        }, this.smokeFadeDuration);
      }, 1000);
    });
  }

  /**
   * Start flame surge effect using direct JavaScript style manipulation
   * This bypasses CSS specificity issues and ensures the effect is visible
   */
  startFlameSurge() {
    console.log('[FlameSurge] === STARTING FLAME SURGE ===');

    // Add surging class to all active flames
    const flames = document.querySelectorAll('.boot-candle.candle-on .flame');
    flames.forEach(flame => flame.classList.add('surging'));

    // Animation parameters
    let frame = 0;
    this.isCoolingDown = false;
    this.cooldownProgress = 0;

    // Clear existing interval if any
    if (this.flameSurgeInterval) {
      clearInterval(this.flameSurgeInterval);
    }

    // Animation loop - runs indefinitely until stopped
    this.flameSurgeInterval = setInterval(() => {
      frame++;

      // Target only flames that are still marked as surging
      const surgingFlames = document.querySelectorAll('.flame.surging');

      if (surgingFlames.length === 0) {
        return;
      }

      surgingFlames.forEach((flame, index) => {
        let scaleY, scaleX, opacity, glowIntensity, skew;

        if (this.isCoolingDown) {
          // COOLDOWN MODE: Gradually return towards normal BUT NOT ALL THE WAY
          // IMPROVEMENT 3: Don't stop. Keep breathing heavily.

          this.cooldownProgress += 0.015; // Slower cooldown (approx 1.5s)
          if (this.cooldownProgress > 1) this.cooldownProgress = 1;

          const ease = this.cooldownProgress;

          // Calculate animation values
          const angle = frame * 0.2 + index * 0.5;

          // Surge dampens but doesn't disappear completely
          // It stays "nervous" (0.3 residual surge)
          const rawSurge = Math.abs(Math.sin(angle * 2));
          const residualSurge = rawSurge * 0.3;

          // Interpolate surge influence: Full -> Residual
          const currentSurgeEffect = rawSurge * (1 - ease) + residualSurge * ease;

          // ScaleY: 3.5 (Max) -> 1.5 (Elevated, not 1.0)
          // The flame remains larger than normal (1.5x) to show it's still "hot"
          const targetBaseScale = 1.5;
          const currentBaseScale = 1.0 * (1 - ease) + targetBaseScale * ease;

          scaleY = currentBaseScale + currentSurgeEffect * 2.0;

          // Width: 0.7 -> 0.9 (Still slightly narrow/tense)
          const rawScaleX = 1.0 - rawSurge * 0.3;
          scaleX = rawScaleX * (1 - ease) + 0.9 * ease;

          skew = 0;
          opacity = 0.9;
          glowIntensity = (20 + rawSurge * 40) * (1 - ease) + 15 * ease;

          // Note: We NEVER call stopFlameSurge() here.
          // The animation loop continues until the overlay is removed.
        } else {
          // NORMAL SURGE MODE
          const angle = frame * 0.2 + index * 0.5;
          const surge = Math.abs(Math.sin(angle * 2));
          scaleY = 1.0 + surge * 2.5;
          scaleX = 1.0 - surge * 0.3;
          skew = 0;
          opacity = 0.8 + Math.sin(angle * 5) * 0.2;
          glowIntensity = 20 + surge * 40;
        }

        // Apply styles directly
        flame.style.setProperty('transform-origin', 'bottom center', 'important');
        flame.style.setProperty(
          'transform',
          `translateX(-50%) scale(${scaleX}, ${scaleY}) skewX(${skew}deg)`,
          'important'
        );

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
    }, 20); // ~50fps
  }

  /**
   * Trigger cooldown animation for remaining flames
   */
  triggerCooldown() {
    console.log('[FlameSurge] Triggering cooldown...');
    this.isCoolingDown = true;
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

    // Restore original styles for any remaining flames
    const flames = document.querySelectorAll('.flame');
    console.log('[FlameSurge] Restoring styles for', flames.length, 'flames');

    flames.forEach(flame => {
      flame.classList.remove('surging');
      // Reset styles to normal
      flame.style.removeProperty('transform-origin');
      flame.style.transform = 'translateX(-50%)';
      flame.style.height = '16px';
      flame.style.width = '10px';
      flame.style.boxShadow = '0 0 10px #33ff00';
      flame.style.opacity = '0.9';
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
   * Uses recursive timeout for accelerating effect
   */
  extinguishCandles() {
    const candles = document.querySelectorAll('.boot-candle');
    if (candles.length === 0) {
      return;
    }

    let candleIndex = 0;
    // Start slower to match text reading speed, then accelerate
    let nextDelay = 600;

    const extinguishNext = () => {
      // Stop before the last candle (9th life remains lit) (Requirement 18.6)
      if (candleIndex >= this.totalCandles - 1) {
        return;
      }

      const candle = candles[candleIndex];
      if (candle) {
        // Step 1: Remove from surge loop immediately
        const flame = candle.querySelector('.flame');
        if (flame) {
          flame.classList.remove('surging');

          // IMPROVEMENT 1: No "return to normal".
          // Instead, freeze at current high energy state, then flicker out violently.
          // We do this by NOT resetting the transform/scale here.
          // The CSS transition will handle the 'candle-off' state.
        }

        // Step 2: Apply flicker effect (Violent end)
        candle.classList.add('candle-flicker');

        // Quick extinguish (100ms) - "Snapped out"
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
        }, 100);
      }

      candleIndex++;

      // IMPROVEMENT 2: Sync with text
      // Accelerate less aggressively so it lasts through the text display
      // 600 -> 480 -> 384 -> 307 -> 245 -> 196 -> 157 -> 125
      nextDelay = Math.max(100, nextDelay * 0.8);

      // Schedule next candle
      setTimeout(extinguishNext, nextDelay);
    };

    // Start sequence
    extinguishNext();
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

        // NEW LOGIC: Trigger surge when starting the second line ("UPLOADING...")
        // This gives about 1 second of surge before extinguishing starts
        if (currentLine === 1) {
          console.log('[BootSequence] Starting flame surge (1s before extinguish)');
          this.startFlameSurge();

          // Schedule extinguish to start 1 second later
          setTimeout(() => {
            console.log('[BootSequence] Starting candle extinguish sequence');
            this.extinguishCandles();
          }, 1000);
        }
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
