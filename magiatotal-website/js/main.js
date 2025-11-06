/**
 * Magia Total - Modern JavaScript
 */

// Mobile Menu Toggle
document.addEventListener('DOMContentLoaded', function() {
    const mobileToggle = document.querySelector('.mobile-toggle');
    const navMenu = document.querySelector('.nav-menu');

    if (mobileToggle && navMenu) {
        mobileToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');

            // Animate toggle button
            this.classList.toggle('active');
        });

        // Close menu when clicking on a link
        const navLinks = navMenu.querySelectorAll('a');
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                navMenu.classList.remove('active');
                mobileToggle.classList.remove('active');
            });
        });

        // Close menu when clicking outside
        document.addEventListener('click', (e) => {
            if (!mobileToggle.contains(e.target) && !navMenu.contains(e.target)) {
                navMenu.classList.remove('active');
                mobileToggle.classList.remove('active');
            }
        });
    }
});

// Smooth Scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Intersection Observer for animations
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('fade-in');
            observer.unobserve(entry.target);
        }
    });
}, observerOptions);

// Observe elements
document.querySelectorAll('.feature-card, .gallery-item').forEach(el => {
    observer.observe(el);
});

// Image Gallery Modal (if needed)
const galleryItems = document.querySelectorAll('.gallery-item');
if (galleryItems.length > 0) {
    galleryItems.forEach(item => {
        item.addEventListener('click', function() {
            const img = this.querySelector('img');
            if (img) {
                // Simple modal implementation
                const modal = document.createElement('div');
                modal.className = 'image-modal';
                modal.innerHTML = `
                    <div class="modal-overlay">
                        <div class="modal-content">
                            <button class="modal-close">&times;</button>
                            <img src="${img.src}" alt="${img.alt}">
                        </div>
                    </div>
                `;
                document.body.appendChild(modal);
                document.body.style.overflow = 'hidden';

                // Close modal
                const closeBtn = modal.querySelector('.modal-close');
                const overlay = modal.querySelector('.modal-overlay');

                const closeModal = () => {
                    document.body.removeChild(modal);
                    document.body.style.overflow = '';
                };

                closeBtn.addEventListener('click', closeModal);
                overlay.addEventListener('click', (e) => {
                    if (e.target === overlay) {
                        closeModal();
                    }
                });

                // ESC key to close
                document.addEventListener('keydown', function escHandler(e) {
                    if (e.key === 'Escape') {
                        closeModal();
                        document.removeEventListener('keydown', escHandler);
                    }
                });
            }
        });
    });
}

// Form Validation
const contactForm = document.querySelector('#contact-form');
if (contactForm) {
    contactForm.addEventListener('submit', function(e) {
        e.preventDefault();

        // Basic validation
        const name = this.querySelector('[name="name"]');
        const email = this.querySelector('[name="email"]');
        const phone = this.querySelector('[name="phone"]');
        const message = this.querySelector('[name="message"]');

        let isValid = true;

        // Clear previous errors
        document.querySelectorAll('.error-message').forEach(el => el.remove());

        if (!name.value.trim()) {
            showError(name, 'Por favor, informe seu nome');
            isValid = false;
        }

        if (!email.value.trim() || !isValidEmail(email.value)) {
            showError(email, 'Por favor, informe um email válido');
            isValid = false;
        }

        if (!phone.value.trim()) {
            showError(phone, 'Por favor, informe seu telefone');
            isValid = false;
        }

        if (!message.value.trim()) {
            showError(message, 'Por favor, escreva sua mensagem');
            isValid = false;
        }

        if (isValid) {
            // Send via WhatsApp
            const whatsappMessage = `
Olá! Vim pelo site e gostaria de mais informações.

*Nome:* ${name.value}
*Email:* ${email.value}
*Telefone:* ${phone.value}
*Mensagem:* ${message.value}
            `.trim();

            const whatsappUrl = `https://api.whatsapp.com/send?phone=+5547991897333&text=${encodeURIComponent(whatsappMessage)}`;
            window.open(whatsappUrl, '_blank');

            // Reset form
            this.reset();
            showSuccess('Mensagem enviada! Aguarde enquanto abrimos o WhatsApp...');
        }
    });
}

function showError(input, message) {
    const error = document.createElement('div');
    error.className = 'error-message';
    error.style.color = '#E74C3C';
    error.style.fontSize = '0.875rem';
    error.style.marginTop = '0.25rem';
    error.textContent = message;
    input.parentNode.appendChild(error);
    input.style.borderColor = '#E74C3C';
}

function showSuccess(message) {
    const success = document.createElement('div');
    success.className = 'success-message';
    success.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #2ECC71;
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.2);
        z-index: 9999;
        animation: slideIn 0.3s ease;
    `;
    success.textContent = message;
    document.body.appendChild(success);

    setTimeout(() => {
        success.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => document.body.removeChild(success), 300);
    }, 3000);
}

function isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

// Add CSS for modal
const style = document.createElement('style');
style.textContent = `
    .image-modal {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: 10000;
    }

    .modal-overlay {
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.9);
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 20px;
    }

    .modal-content {
        position: relative;
        max-width: 90%;
        max-height: 90%;
    }

    .modal-content img {
        max-width: 100%;
        max-height: 90vh;
        border-radius: 12px;
    }

    .modal-close {
        position: absolute;
        top: -40px;
        right: 0;
        background: white;
        border: none;
        width: 40px;
        height: 40px;
        border-radius: 50%;
        font-size: 24px;
        cursor: pointer;
        color: #333;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.3s;
    }

    .modal-close:hover {
        background: #FF6B9D;
        color: white;
        transform: rotate(90deg);
    }

    .fade-in {
        animation: fadeInUp 0.6s ease forwards;
    }

    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }

    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Lazy loading for images
if ('IntersectionObserver' in window) {
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                if (img.dataset.src) {
                    img.src = img.dataset.src;
                    img.removeAttribute('data-src');
                    imageObserver.unobserve(img);
                }
            }
        });
    });

    document.querySelectorAll('img[data-src]').forEach(img => {
        imageObserver.observe(img);
    });
}
