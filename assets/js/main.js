const WA_NUMBER = '237694836346';

document.addEventListener('DOMContentLoaded', () => {
  const burger = document.querySelector('.burger');
  const nav = document.querySelector('.nav');
  burger?.addEventListener('click', () => {
    const open = nav.classList.toggle('open');
    burger.setAttribute('aria-expanded', open);
  });

  const io = new IntersectionObserver((entries) => {
    entries.forEach((e) => {
      if (e.isIntersecting) { e.target.classList.add('visible'); io.unobserve(e.target); }
    });
  }, { threshold: 0.12 });
  document.querySelectorAll('.reveal').forEach((el) => io.observe(el));

  document.querySelectorAll('[data-tabs]').forEach((group) => {
    const tabs = group.querySelectorAll('.tab');
    const panels = group.querySelectorAll('.tab-panel');
    tabs.forEach((tab) => tab.addEventListener('click', () => {
      tabs.forEach((t) => t.classList.toggle('active', t === tab));
      panels.forEach((p) => p.classList.toggle('active', p.id === tab.dataset.target));
    }));
  });

  document.querySelectorAll('form[data-whatsapp]').forEach((form) => {
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const d = new FormData(form);
      const lines = [
        'Bonjour SCALEON, je souhaite être recontacté(e).',
        `Nom : ${d.get('name')}`,
        d.get('company') ? `Entreprise : ${d.get('company')}` : null,
        `Téléphone : ${d.get('phone')}`,
        d.get('email') ? `Email : ${d.get('email')}` : null,
        `Besoin : ${d.get('need')}`,
        d.get('message') ? `Message : ${d.get('message')}` : null,
      ].filter(Boolean);
      window.open(`https://wa.me/${WA_NUMBER}?text=${encodeURIComponent(lines.join('\n'))}`, '_blank');
    });
  });

  const chips = document.querySelectorAll('.chip[data-filter]');
  chips.forEach((chip) => chip.addEventListener('click', () => {
    chips.forEach((c) => c.classList.toggle('active', c === chip));
    document.querySelectorAll('.post-card').forEach((card) => {
      card.hidden = chip.dataset.filter !== '*' && card.dataset.cat !== chip.dataset.filter;
    });
  }));

  const year = document.getElementById('year');
  if (year) year.textContent = new Date().getFullYear();
});
