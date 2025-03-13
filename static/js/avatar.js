class AvatarRenderer {
    constructor(svgElement) {
        this.svg = svgElement;
        this.animationFrame = null;
        this.currentAnimation = null;
        this.lipSyncData = null;
        this.startTime = 0;
    }

    async initialize(avatarUrl) {
        try {
            const response = await fetch(avatarUrl);
            const svgText = await response.text();
            this.svg.innerHTML = svgText;
            
            // Initialize animation transforms
            this.initializeTransforms();
        } catch (error) {
            console.error('Error initializing avatar:', error);
        }
    }

    initializeTransforms() {
        // Add transform groups for animation
        const avatar = this.svg.querySelector('svg');
        if (!avatar) return;

        // Create transform groups for head and body
        this.headGroup = document.createElementNS("http://www.w3.org/2000/svg", "g");
        this.headGroup.setAttribute('id', 'head-group');
        
        this.bodyGroup = document.createElementNS("http://www.w3.org/2000/svg", "g");
        this.bodyGroup.setAttribute('id', 'body-group');

        // Move relevant elements to groups
        const headElements = avatar.querySelectorAll('path[id*="head"], path[id*="face"], path[id*="mouth"]');
        const bodyElements = avatar.querySelectorAll('path[id*="body"], path[id*="cloth"]');

        headElements.forEach(el => this.headGroup.appendChild(el.cloneNode(true)));
        bodyElements.forEach(el => this.bodyGroup.appendChild(el.cloneNode(true)));

        // Clear and rebuild avatar
        avatar.innerHTML = '';
        avatar.appendChild(this.bodyGroup);
        avatar.appendChild(this.headGroup);
    }

    setAnimation(animationData) {
        this.currentAnimation = animationData;
        this.startTime = performance.now();
    }

    setLipSync(lipSyncData) {
        this.lipSyncData = lipSyncData;
    }

    animate() {
        if (!this.currentAnimation || !this.headGroup || !this.bodyGroup) return;

        const currentTime = (performance.now() - this.startTime) / 1000;
        
        // Find current animation frame
        const frame = this.getCurrentFrame(currentTime);
        if (!frame) return;

        // Apply transforms
        this.applyTransforms(frame);

        // Apply lip sync if available
        if (this.lipSyncData) {
            this.applyLipSync(currentTime);
        }

        // Continue animation
        this.animationFrame = requestAnimationFrame(() => this.animate());
    }

    getCurrentFrame(currentTime) {
        if (!this.currentAnimation || this.currentAnimation.length === 0) return null;

        // Find surrounding keyframes
        let prevFrame = null;
        let nextFrame = null;

        for (const frame of this.currentAnimation) {
            if (frame.timestamp <= currentTime) {
                prevFrame = frame;
            }
            if (frame.timestamp > currentTime && !nextFrame) {
                nextFrame = frame;
                break;
            }
        }

        if (!prevFrame) return this.currentAnimation[0];
        if (!nextFrame) return prevFrame;

        // Interpolate between frames
        const t = (currentTime - prevFrame.timestamp) / 
                 (nextFrame.timestamp - prevFrame.timestamp);
        
        return this.interpolateFrames(prevFrame, nextFrame, t);
    }

    interpolateFrames(a, b, t) {
        return {
            position: {
                x: this.lerp(a.position.x, b.position.x, t),
                y: this.lerp(a.position.y, b.position.y, t),
                z: this.lerp(a.position.z, b.position.z, t)
            },
            rotation: {
                x: this.lerp(a.rotation.x, b.rotation.x, t),
                y: this.lerp(a.rotation.y, b.rotation.y, t),
                z: this.lerp(a.rotation.z, b.rotation.z, t)
            }
        };
    }

    lerp(a, b, t) {
        return a + (b - a) * t;
    }

    applyTransforms(frame) {
        if (!this.headGroup || !this.bodyGroup) return;

        // Apply head transforms
        const headTransform = `
            translate(${frame.position.x * 10}px, ${frame.position.y * 10}px)
            rotateX(${frame.rotation.x * 45}deg)
            rotateY(${frame.rotation.y * 45}deg)
            rotateZ(${frame.rotation.z * 45}deg)
        `;
        this.headGroup.style.transform = headTransform;

        // Apply subtle body movement
        const bodyTransform = `
            translate(${frame.position.x * 5}px, ${frame.position.y * 5}px)
            rotateZ(${frame.rotation.z * 10}deg)
        `;
        this.bodyGroup.style.transform = bodyTransform;
    }

    applyLipSync(currentTime) {
        const lipData = this.getLipSyncData(currentTime);
        if (!lipData) return;

        // Find mouth elements
        const mouthElements = this.headGroup.querySelectorAll('path[id*="mouth"]');
        mouthElements.forEach(mouth => {
            // Scale mouth based on lip sync data
            const scale = `scale(${lipData.mouth_shape.width}, ${lipData.mouth_shape.height})`;
            mouth.style.transform = scale;
        });
    }

    getLipSyncData(currentTime) {
        if (!this.lipSyncData || this.lipSyncData.length === 0) return null;

        // Find appropriate lip sync frame
        return this.lipSyncData.find(frame => 
            frame.timestamp <= currentTime && 
            frame.timestamp + 0.1 > currentTime
        ) || this.lipSyncData[this.lipSyncData.length - 1];
    }

    startAnimation() {
        if (this.animationFrame) {
            cancelAnimationFrame(this.animationFrame);
        }
        this.animate();
    }

    stopAnimation() {
        if (this.animationFrame) {
            cancelAnimationFrame(this.animationFrame);
            this.animationFrame = null;
        }
    }
}

// Initialize avatar rendering when page loads
document.addEventListener('DOMContentLoaded', () => {
    const avatarContainer = document.getElementById('avatar-container');
    if (avatarContainer) {
        window.avatarRenderer = new AvatarRenderer(avatarContainer);
    }
});
