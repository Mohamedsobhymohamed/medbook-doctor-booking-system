// ===== MedBook Frontend JS =====

document.addEventListener('DOMContentLoaded', () => {

  // ===== Flash message auto-dismiss =====
  const flashes = document.querySelectorAll('.flash');
  flashes.forEach(f => {
    setTimeout(() => f.remove(), 4800);
  });

  // ===== Role selector (register page) =====
  const roleOptions = document.querySelectorAll('.role-option');
  roleOptions.forEach(opt => {
    opt.addEventListener('click', () => {
      roleOptions.forEach(o => o.classList.remove('selected'));
      opt.classList.add('selected');
      opt.querySelector('input[type="radio"]').checked = true;
    });
  });

  // ===== Slot picker =====
  const timeSlots = document.querySelectorAll('.time-slot:not(.booked)');
  const slotInput = document.getElementById('selected_slot_id');
  timeSlots.forEach(slot => {
    slot.addEventListener('click', () => {
      timeSlots.forEach(s => s.classList.remove('selected'));
      slot.classList.add('selected');
      if (slotInput) slotInput.value = slot.dataset.slotId;
    });
  });

  // ===== Payment method selector =====
  const paymentMethods = document.querySelectorAll('.payment-method');
  paymentMethods.forEach(m => {
    m.addEventListener('click', () => {
      paymentMethods.forEach(pm => pm.classList.remove('selected'));
      m.classList.add('selected');
    });
  });

  // ===== Modal helpers =====
  window.openModal = id => {
    const modal = document.getElementById(id);
    if (modal) {
      modal.style.display = 'flex';
      document.body.style.overflow = 'hidden';
    }
  };

  window.closeModal = id => {
    const modal = document.getElementById(id);
    if (modal) {
      modal.style.display = 'none';
      document.body.style.overflow = '';
    }
  };

  // Close modal on overlay click
  document.querySelectorAll('.modal-overlay').forEach(overlay => {
    overlay.addEventListener('click', e => {
      if (e.target === overlay) closeModal(overlay.id);
    });
  });

  // ===== Copy meeting link =====
  window.copyLink = () => {
    const linkEl = document.querySelector('.meeting-url');
    if (!linkEl) return;
    navigator.clipboard.writeText(linkEl.textContent.trim()).then(() => {
      showToast('Link copied to clipboard!', 'success');
    });
  };

  // ===== Toast notification =====
  window.showToast = (msg, type = 'info') => {
    const container = document.querySelector('.flash-container') || (() => {
      const c = document.createElement('div');
      c.className = 'flash-container';
      document.body.appendChild(c);
      return c;
    })();

    const icons = { success: '✅', error: '❌', info: 'ℹ️', warning: '⚠️' };
    const toast = document.createElement('div');
    toast.className = `flash flash-${type}`;
    toast.innerHTML = `<span>${icons[type] || 'ℹ️'}</span> ${msg}`;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 4800);
  };

  // ===== Scroll animation (Intersection Observer) =====
  const observer = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.style.animationPlayState = 'running';
        observer.unobserve(e.target);
      }
    });
  }, { threshold: 0.1 });

  document.querySelectorAll('.animate-on-scroll').forEach(el => {
    el.style.animationPlayState = 'paused';
    observer.observe(el);
  });

  // ===== Doctor search filter =====
  const searchInput = document.getElementById('doctorSearch');
  const specializationFilter = document.getElementById('specializationFilter');
  const doctorCards = document.querySelectorAll('.doctor-card[data-name]');

  const filterDoctors = () => {
    const query = searchInput ? searchInput.value.toLowerCase() : '';
    const spec = specializationFilter ? specializationFilter.value.toLowerCase() : '';
    doctorCards.forEach(card => {
      const name = (card.dataset.name || '').toLowerCase();
      const specialization = (card.dataset.spec || '').toLowerCase();
      const matchName = name.includes(query);
      const matchSpec = !spec || specialization.includes(spec);
      card.style.display = matchName && matchSpec ? '' : 'none';
    });
  };

  if (searchInput) searchInput.addEventListener('input', filterDoctors);
  if (specializationFilter) specializationFilter.addEventListener('change', filterDoctors);

  // ===== Confirm delete / cancel actions =====
  document.querySelectorAll('[data-confirm]').forEach(btn => {
    btn.addEventListener('click', e => {
      const msg = btn.dataset.confirm || 'Are you sure?';
      if (!confirm(msg)) e.preventDefault();
    });
  });

  // ===== Animate stat numbers =====
  const animateNumbers = () => {
    document.querySelectorAll('.stat-value[data-target]').forEach(el => {
      const target = parseInt(el.dataset.target, 10);
      let current = 0;
      const increment = Math.ceil(target / 40);
      const timer = setInterval(() => {
        current += increment;
        if (current >= target) { current = target; clearInterval(timer); }
        el.textContent = current.toLocaleString();
      }, 30);
    });
  };
  animateNumbers();

  // ===== Mobile nav toggle =====
  const mobileToggle = document.getElementById('mobileNavToggle');
  const mobileMenu = document.getElementById('mobileMenu');
  if (mobileToggle && mobileMenu) {
    mobileToggle.addEventListener('click', () => {
      mobileMenu.classList.toggle('open');
    });
  }

  // ===== Form validation highlights =====
  document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', e => {
      let valid = true;
      form.querySelectorAll('[required]').forEach(field => {
        if (!field.value.trim()) {
          field.style.borderColor = 'var(--red)';
          valid = false;
        } else {
          field.style.borderColor = '';
        }
      });
      if (!valid) {
        e.preventDefault();
        showToast('Please fill in all required fields.', 'error');
      }
    });
  });

  // ===== Slot chip preview animation =====
  const slotChips = document.querySelectorAll('.slot-chip');
  slotChips.forEach((chip, i) => {
    chip.style.animationDelay = `${i * 60}ms`;
    chip.classList.add('animate-on-scroll');
  });

  // ===== Page load fade-in =====
  document.body.style.opacity = '0';
  requestAnimationFrame(() => {
    document.body.style.transition = 'opacity 0.4s ease';
    document.body.style.opacity = '1';
  });

});